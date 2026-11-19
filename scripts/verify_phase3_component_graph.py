"""Independent sparse-connectivity reconstruction, using source metadata + FP32 content.

The metadata/FP32 cache is independently checked against all source rows by
docs/phase3-plan/tools/audit_corrected_source_rows_independent.py. This graph
pass does not itself parse the CSV archive. No model or test payload is accessed.
"""
from pathlib import Path
import sys
import hashlib
import ipaddress
import time
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from audit_phase3_reliability import read,write_json,digest


def main():
    started=time.perf_counter();base=ROOT/'data/raw/phase3-feasibility-corrected';work=base/'no-headers-74'
    with np.load(work/'conditional-components-120.npz',allow_pickle=False) as f:state={k:f[k] for k in f.files}
    n=len(state['row_ids']);meta=pd.read_csv(base/'component-metadata.csv',low_memory=False)
    assert len(meta)==n and np.array_equal(meta.row_id.to_numpy(),state['row_ids'])
    # Reparse the corrected ISO times; do not use the stored timestamp array.
    times=pd.to_datetime(meta.timestamp_raw,format='mixed',errors='coerce').to_numpy(dtype='datetime64[us]').astype(np.int64)
    ips=pd.unique(pd.concat([meta.src_ip,meta.dst_ip]));mapping={}
    for value in ips:
        try:mapping[value]=int(ipaddress.IPv4Address(value))
        except (ValueError,ipaddress.AddressValueError):pass
    src=meta.src_ip.map(mapping);dst=meta.dst_ip.map(mapping)
    valid=(src.notna()&dst.notna()&meta.reference_label_raw.notna()&(times!=np.iinfo(np.int64).min))
    for column,limit in [('src_port',65535),('dst_port',65535),('protocol',255)]:
        v=pd.to_numeric(meta[column],errors='coerce');valid &= v.between(0,limit)&v.mod(1).eq(0)
    duration=pd.to_numeric(meta.duration_us_raw,errors='coerce')
    valid &= np.isfinite(duration)&duration.ge(0)&duration.mod(1).eq(0)&duration.le(np.iinfo(np.int64).max-np.maximum(times,0))
    valid=valid.to_numpy();assert np.array_equal(valid,state['valid_metadata'])
    assert np.array_equal(times[valid],state['start_us'][valid])
    # Full SHA256 grouping is independent of the original truncated-hash/union-find implementation.
    x=np.memmap(work/'candidate-transformed-fp32.raw',dtype='<f4',mode='r',shape=(n,74))
    positions=np.flatnonzero(state['final_finite']);hashes=np.empty(len(positions),dtype='V32')
    for start in range(0,len(positions),50000):
        selected=positions[start:start+50000];hashes[start:start+len(selected)]=[hashlib.sha256(x[i].tobytes()).digest() for i in selected]
    order=np.argsort(hashes,kind='stable');same=hashes[order][1:]==hashes[order][:-1]
    left=positions[order][1:][same].astype(np.int32);right=positions[order][:-1][same].astype(np.int32)
    nodes=np.flatnonzero(valid);source=(src[valid].to_numpy(dtype=np.uint64)<<np.uint64(16))|meta.src_port[valid].to_numpy(dtype=np.uint64)
    dest=(dst[valid].to_numpy(dtype=np.uint64)<<np.uint64(16))|meta.dst_port[valid].to_numpy(dtype=np.uint64)
    low,high=np.minimum(source,dest),np.maximum(source,dest);protocol=meta.protocol[valid].to_numpy()
    ix=np.lexsort((state['row_ids'][nodes],times[nodes],high,low,protocol));nodes=nodes[ix]
    boundary=np.ones(len(ix),bool);boundary[1:]=(low[ix][1:]!=low[ix][:-1])|(high[ix][1:]!=high[ix][:-1])|(protocol[ix][1:]!=protocol[ix][:-1])
    expected=np.full(n,np.iinfo(np.uint64).max,dtype=np.uint64);np.minimum.at(expected,state['roots'],state['row_ids']);expected=expected[state['roots']]
    with np.load(work/'conditional-candidate-split.npz',allow_pickle=False) as f:splitpos,roles=f['source_positions'],f['roles']
    results=[]
    for gap in (60,120,300):
        session_left=[];session_right=[];maximum_end=None
        for rank,node in enumerate(nodes):
            start=int(times[node]);end=start+int(duration.iloc[node])
            if boundary[rank] or start-maximum_end>gap*1000000:maximum_end=end
            else:
                session_left.append(int(nodes[rank-1]));session_right.append(int(node));maximum_end=max(maximum_end,end)
        l=np.concatenate([left,np.asarray(session_left,dtype=np.int32)]);r=np.concatenate([right,np.asarray(session_right,dtype=np.int32)])
        graph=coo_matrix((np.ones(len(l),dtype=np.uint8),(l,r)),shape=(n,n)).tocsr()
        count,labels=connected_components(graph,directed=False)
        canonical=np.full(count,np.iinfo(np.uint64).max,dtype=np.uint64);np.minimum.at(canonical,labels,state['row_ids']);actual=canonical[labels]
        touched=np.zeros(count,bool);touched[labels[state['t0_fit']]]=True;closure=touched[labels]
        overlaps={f'{a}-{b}':len(np.intersect1d(labels[splitpos[roles==a]],labels[splitpos[roles==b]])) for a,b in [(0,1),(0,2),(1,2)]}
        results.append(dict(gap_seconds=gap,components=int(count),session_edges=len(session_left),content_edges=len(left),
                            same_partition_as_120=bool(np.array_equal(actual,expected)),same_T0_closure=bool(np.array_equal(closure,state['t0_closure'])),
                            frozen_split_component_overlap=overlaps,T0_closure_rows=int(closure.sum())))
        print(gap,results[-1],flush=True)
    config=read(ROOT/'configs/phase3/reference74-v1.json')
    archive=base/'CICIDS2017_improved.zip';source_match=digest(archive)==config['data']['archive_sha256']
    result=dict(results=results,source_archive_hash_matches=source_match,independently_reparsed_metadata=True,
                algorithm='Full SHA256 FP32 grouping + independent sequential interval sweep + SciPy undirected connectivity',
                elapsed_seconds=time.perf_counter()-started,limitations=['This connectivity pass consumes the metadata/FP32 cache; separate independent source-row parity covers all rows and inputs','Operational sessions do not certify true application sessions','Sensitivity uses the frozen 120s split; alternative splits are not trained or selected from outcomes'])
    write_json(ROOT/'results/phase3-rigorous-audit-v1/component-reconstruction.json',result)
    if not source_match or not results[1]['same_partition_as_120'] or not results[1]['same_T0_closure']:raise ValueError('Independent graph mismatch')


if __name__=='__main__':main()
