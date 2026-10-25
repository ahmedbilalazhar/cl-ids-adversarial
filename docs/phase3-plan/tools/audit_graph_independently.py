"""Reconstruct the conditional data graph with a different connectivity engine.

Data audit only. Shared source parsing/clock assumptions remain conditional.
The interval sweep and SciPy sparse connectivity do not use the first auditor's
union-find implementation. No learner tests or model fitting are performed.
"""
from __future__ import annotations
import hashlib
import json
import time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
WORK=ROOT/"data/raw/phase3-feasibility-original"
started=time.monotonic()
parent=json.loads((DOCS/"original-component-feasibility.json").read_text())
if parent.get("audit_version")!=2 or parent["nonfinite_final_rows_from_finite_raw"]!=0:
    raise RuntimeError("This reconstruction requires v2 and finite transformed outputs for all finite raw inputs")
state=np.load(WORK/"conditional-components-120.npz",allow_pickle=False)
roots=state["roots"]
n=len(roots)
row_ids=state["row_ids"]
valid=state["final_finite"]
positions=np.flatnonzero(valid)
x=np.memmap(WORK/"candidate-transformed-fp32.raw",dtype="<f4",mode="r",shape=(n,76))
digests=np.empty(len(positions),dtype="V32")
for first in range(0,len(positions),100000):
    part=positions[first:first+100000]
    digests[first:first+len(part)]=[hashlib.sha256(x[int(i)]).digest() for i in part]
order=np.argsort(digests,kind="stable")
same=digests[order][1:]==digests[order][:-1]
content_left=positions[order][1:][same].astype(np.int32)
content_right=positions[order][:-1][same].astype(np.int32)
print(json.dumps({"step":"full_SHA256_content_edges","edges":len(content_left),"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)

meta=pd.read_csv(WORK/"feasibility-metadata.csv",usecols=["src_ip","src_port","dst_ip","dst_port","protocol","duration_us_raw"],dtype={"src_ip":"string","dst_ip":"string"},low_memory=False)
nodes=np.flatnonzero(state["valid_metadata"])
source=meta.loc[nodes,"src_ip"].reset_index(drop=True)+":"+meta.loc[nodes,"src_port"].astype("int32").astype(str).reset_index(drop=True)
destination=meta.loc[nodes,"dst_ip"].reset_index(drop=True)+":"+meta.loc[nodes,"dst_port"].astype("int32").astype(str).reset_index(drop=True)
codes,_=pd.factorize(pd.concat([source,destination],ignore_index=True),sort=False)
source_codes,destination_codes=codes[:len(nodes)],codes[len(nodes):]
low,high=np.minimum(source_codes,destination_codes),np.maximum(source_codes,destination_codes)
protocol=meta.loc[nodes,"protocol"].to_numpy(dtype=np.int16)
starts=state["start_us"][nodes]
duration=meta.loc[nodes,"duration_us_raw"].to_numpy(dtype=np.int64)
order=np.lexsort((row_ids[nodes],starts,high,low,protocol))
group_start=np.ones(len(nodes),dtype=bool)
group_start[1:]=(low[order][1:]!=low[order][:-1])|(high[order][1:]!=high[order][:-1])|(protocol[order][1:]!=protocol[order][:-1])
session_left=np.empty(len(nodes),dtype=np.int32)
session_right=np.empty(len(nodes),dtype=np.int32)
edge_count=0
sessions=0
maximum_end=None
previous_node=None
for rank,local in enumerate(order):
    start=int(starts[local])
    end=start+int(duration[local])
    node=int(nodes[local])
    if group_start[rank] or start-maximum_end>120000000:
        sessions+=1
        maximum_end=end
    else:
        session_left[edge_count]=node
        session_right[edge_count]=previous_node
        edge_count+=1
        maximum_end=max(maximum_end,end)
    previous_node=node
left=np.concatenate([content_left,session_left[:edge_count]])
right=np.concatenate([content_right,session_right[:edge_count]])
graph=coo_matrix((np.ones(len(left),dtype=np.uint8),(left,right)),shape=(n,n)).tocsr()
component_count,alternative=connected_components(graph,directed=False,return_labels=True)
expected_ids=np.full(n,np.iinfo(np.uint64).max,dtype=np.uint64)
np.minimum.at(expected_ids,roots,row_ids)
expected_ids=expected_ids[roots]
actual_ids=np.full(component_count,np.iinfo(np.uint64).max,dtype=np.uint64)
np.minimum.at(actual_ids,alternative,row_ids)
actual_ids=actual_ids[alternative]
matching=bool(np.array_equal(expected_ids,actual_ids))
fit=state["t0_fit"]
touch=np.zeros(component_count,dtype=bool)
touch[alternative[fit]]=True
closure=touch[alternative]
closure_matching=bool(np.array_equal(closure,state["t0_closure"]))
result={"status":"independent_connectivity_reconstruction_of_conditional_data_graph","completed_utc":datetime.now(timezone.utc).isoformat(),
    "scope":"Data graph verification only; no model implementation tests or experimental predictions.",
    "source_rows_including_blank":n,"scipy_version":scipy.__version__,"independent_algorithm":"Full SHA-256 final-input grouping, endpoint-factorized sequential interval sweep, SciPy sparse undirected connected components",
    "raw_content_edge_reason":"All finite raw records transform finitely; identical raw vectors imply identical transformed vectors, so raw equality edges are redundant for this reconstruction.",
    "content_edges":len(content_left),"session_edges":edge_count,"operational_sessions":sessions,"components_all_csv_record_nodes":int(component_count),
    "partition_matches_first_audit":matching,"T0_closure_matches_first_audit":closure_matching,
    "canonical_component_map_sha256":hashlib.sha256(actual_ids.astype("<u8").tobytes()).hexdigest(),
    "elapsed_seconds":round(time.monotonic()-started,3),"limits":["Shared source parsing and conditional clock policy are not independently validated here","Matching algorithms do not prove true session identity or correct labels","This does not approve the final data protocol"]}
(DOCS/"independent-component-reconstruction.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"partition_matches":matching,"closure_matches":closure_matching,"sessions":sessions,"elapsed_seconds":result["elapsed_seconds"]}),flush=True)
if not (matching and closure_matching):
    raise SystemExit("Data graph mismatch requires investigation; no final dataset promotion")
