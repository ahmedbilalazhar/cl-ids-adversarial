"""Prospective, CPU-only single-attacker extension. See docs/phase3-overnight-plan.md."""
from __future__ import annotations
import os
for _key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
import argparse
import concurrent.futures as futures
import copy
from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.phase3.common import digest, write_json, read_json, array_identity, identity, rng
from src.phase3.prepare import allocate
from src.phase3.model import ReferenceMLP
from src.phase3.reference import snapshot, model_identity
from src.phase3_v2 import learning as L
from src.phase3_v2.data import StageInput
from src.phase3_v2.prepare import corrupt

OUT=ROOT/'results/phase3-overnight'
BASE=ROOT/'data/processed/phase3-reference74-v1'
SEEDS=tuple(range(1,12))+(42,)
DOSES=((0,1),(1,10),(3,10),(1,2))

@dataclass(frozen=True)
class Settings:
    learner:str='DR'
    admission:str='NONE'
    seed:int=101
    rounds:int=12
    epochs:int=1
    learning_rate:float=.001
    lambda_E:float=100.
    lambda_y:float=1.
    lambda_z:float=.1
    dose:tuple=(0,1)
    q:float=.75
    block:str='core'
    def validate(self):
        assert self.learner in ('FT','EI','DR')
        assert self.admission in ('NONE','DM','DC','DQ')
        assert self.seed in SEEDS+(101,102,103) and tuple(self.dose) in DOSES
        return self

def setup():
    assert platform.python_version()=='3.12.14' and torch.__version__=='2.7.0+cpu' and np.__version__=='2.3.5'
    torch.set_num_threads(1)
    if torch.get_num_interop_threads()!=1:torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_float32_matmul_precision('highest')

def name(s):
    return f'{s.block}-{s.learner}-{s.admission}-s{s.seed}-p{s.dose[0]}of{s.dose[1]}-y{s.lambda_y:g}-z{s.lambda_z:g}-q{s.q:g}'

def inputs(seed,dose):
    """Ownership from whole groups; no evaluation features available to the learner."""
    with np.load(OUT/'ownership-source.npz',allow_pickle=False) as f:
        source_ids=f['ids'];components=f['components'];labels=f['labels']
    owners,allocation=allocate(components,labels,seed)
    assert len(np.unique(np.stack([components,owners.astype(np.uint64)],axis=1),axis=0))==len(np.unique(components))
    order=np.argsort(source_ids,kind='stable')
    data=[];corrections=[];hashes={}
    for stage in range(1,5):
        folder=BASE/f'train/E{stage}'
        x=np.load(folder/'x.npy',mmap_mode='r',allow_pickle=False)
        ids=np.load(folder/'ids.npy',allow_pickle=False)
        clean=np.load(folder/'y.npy',allow_pickle=False)
        index=order[np.searchsorted(source_ids[order],ids)]
        assert np.array_equal(source_ids[index],ids) and np.array_equal(labels[index],clean)
        owner=owners[index].astype('i1')
        y,audit=corrupt(clean,ids,owner,seed,stage,tuple(dose))
        data.append(StageInput(stage,x,y,ids,owner));corrections.append(audit)
        hashes[str(stage)]=dict(x=array_identity(x),ids=array_identity(ids),y=array_identity(y),owner=array_identity(owner))
    return data,corrections,dict(arrays=hashes,ownership_objective=allocation['objective'],whole_component_ownership=True)

def choose(data,scores,new_codes,settings):
    """Matched quotas; default q reproduces v2 admission exactly."""
    if settings.q==.75:return ORIGINAL_CHOOSE(data,scores,new_codes,settings)
    accepted=[];rows=[]
    for i in range(5):
        idx=np.flatnonzero(data.owner==i);cells=L.quotas(data.y[idx],new_codes,data.stage)
        for c in cells:
            if not c['protected']:c['admitted']=int(np.ceil(settings.q*c['raw']))
        if settings.admission=='NONE' or data.stage==1:chosen=idx
        elif settings.admission=='DM':chosen=idx[np.lexsort((data.ids[idx],scores[idx]))[:sum(c['admitted'] for c in cells)]]
        else:
            groups=[];stream=rng(11,settings.seed,i,data.stage)
            for c in cells:
                group=idx[data.y[idx]==c['source_code']]
                rank=stream.permutation(len(group)) if settings.admission=='DQ' else np.lexsort((data.ids[group],scores[group]))
                groups.extend(group[rank[:c['admitted']]])
            chosen=np.asarray(groups,dtype=np.int64)
        chosen=np.sort(chosen).astype('<i8');accepted.append(chosen)
        rows.append(dict(client=i,raw=len(idx),admitted=len(chosen),quotas=cells,admitted_ids_sha256=array_identity(data.ids[chosen])))
    return accepted,rows

ORIGINAL_CHOOSE=L.choose_admission
L.choose_admission=choose

def evaluate(model,slots,stage):
    """Frozen DEVELOPMENT bank only; retain all prediction columns in matrix."""
    folder=BASE/'development'
    x=np.load(folder/'x.npy',mmap_mode='r',allow_pickle=False)
    y=np.load(folder/'y.npy',mmap_mode='r',allow_pickle=False)
    cohort=np.load(folder/'cohort.npy',mmap_mode='r',allow_pickle=False)
    attempted=np.load(folder/'attempted.npy',mmap_mode='r',allow_pickle=False)
    keep=np.flatnonzero(np.isin(y,slots))
    matrix=np.zeros((16,16),dtype=np.int64);provenance=[]
    model.eval();predictions=[]
    with torch.no_grad():
        for start in range(0,len(keep),4096):
            ix=keep[start:start+4096]
            pred=np.asarray(slots)[model(torch.from_numpy(x[ix].copy())).argmax(1).numpy()]
            np.add.at(matrix,(y[ix],pred),1);predictions.append(pred)
    pred=np.concatenate(predictions);truth=y[keep]
    for flag in (False,True):
        m=(truth==0)&(attempted[keep]==flag)
        provenance.append(dict(attempted=flag,n=int(m.sum()),alerts=int((pred[m]!=0).sum())))
    return dict(stage=stage,slots=slots.copy(),confusion=matrix.tolist(),benign_provenance=provenance,bank='development',model_sha256=model_identity(model,slots))

def state_hash(model,clients,slots,exclude_labels=False):
    h=hashlib.sha256(model_identity(model,slots).encode())
    for c in clients:
        h.update(c.dropout.tobytes());h.update(c.accepted.tobytes())
        if c.replay is not None:
            for key,value in sorted(c.replay.items()):
                if exclude_labels and key=='y':continue
                if isinstance(value,np.ndarray):h.update(key.encode());h.update(value.tobytes())
                elif isinstance(value,np.random.Generator):h.update(json.dumps(value.bit_generator.state,sort_keys=True).encode())
                else:h.update(str((key,value)).encode())
    return h.hexdigest()

def train_suffix(model,clients,slots,data,settings,start,folder,poison_ids):
    stages=[];ledger=[];memories=[];repair=None
    for stage in range(start,5):
        d=data[stage-1];new_codes=[int(c) for c in np.unique(d.y) if int(c) not in slots]
        slots.extend(new_codes)
        if model is None:model=ReferenceMLP(len(slots),settings.seed)
        elif new_codes:model.expand(len(slots),stage,settings.seed)
        if settings.learner=='EI':
            for c in clients:L.expand_importance(c,model)
        L.admit(model,d,slots,set(new_codes),clients,settings,ledger)
        for r in range(1,settings.rounds+1):
            broadcast=snapshot(model);updates=[]
            for i,c in enumerate(clients):
                update,row=L.train_client(broadcast,model,c,d,slots,settings,r,i);updates.append(update)
            combined,weights=L.aggregate(broadcast,updates,[len(c.accepted) for c in clients]);model.load_state_dict(combined)
        if settings.learner=='EI':L.commit_importance(model,clients,d,slots,settings,ledger)
        stages.append(evaluate(model,slots,stage))
        np.savez_compressed(folder/f'E{stage}-weights.npz',**{k:v.numpy() for k,v in snapshot(model).items()},source_codes=np.asarray(slots))
        counts=[]
        for c in clients:
            m=c.replay
            counts.append(None if m is None else dict(size=int(m['size']),poison_ids=int(np.isin(m['ids'][:m['size']],poison_ids).sum()),poison_label_benign=int((np.isin(m['ids'][:m['size']],poison_ids)&(m['y'][:m['size']]==0)).sum())))
        memories.append(dict(stage=stage,clients=counts))
        if stage==2 and settings.block=='core' and settings.learner=='DR' and settings.admission in ('NONE','DC') and tuple(settings.dose)==(1,2):
            clone_model=copy.deepcopy(model);clone_clients=copy.deepcopy(clients)
            before=state_hash(model,clients,slots);assert state_hash(clone_model,clone_clients,slots)==before
            fixed_before=state_hash(clone_model,clone_clients,slots,True);changes=0
            for c in clone_clients:
                m=c.replay;ix=np.flatnonzero(np.isin(m['ids'][:m['size']],poison_ids))
                assert np.all(m['y'][ix]==0)
                m['y'][ix]=4;changes+=len(ix)
            assert state_hash(clone_model,clone_clients,slots,True)==fixed_before
            repair_folder=folder/'oracle-label-repair';repair_folder.mkdir(exist_ok=True)
            suffix=train_suffix(clone_model,clone_clients,slots.copy(),data,settings,3,repair_folder,poison_ids)
            repair=dict(changed_labels=changes,pre_clone_sha256=before,nonlabel_state_unchanged=True,stages=suffix[0],memory=suffix[1],independent_replicate=False)
    return stages,memories,ledger,repair

def worker(config):
    setup();s=Settings(**config).validate();folder=OUT/'runs'/name(s);folder.mkdir(parents=True,exist_ok=True)
    output=folder/'result.json'
    if output.exists():
        prior=read_json(output)
        if prior['settings']==json.loads(json.dumps(asdict(s))) and prior['study_identity']==read_json(OUT/'identity.json')['sha256']:return prior
        raise RuntimeError('Existing result identity mismatch')
    started=time.perf_counter();data,audit,input_identity=inputs(s.seed,s.dose)
    poison_ids=np.asarray([int(v) for v in audit[1]['poison_ids']],dtype=np.uint64)
    clients=[L.client_state(s,i) for i in range(5)]
    stages,memory,ledger,repair=train_suffix(None,clients,[],data,s,1,folder,poison_ids)
    latency=None
    if s.block=='clean-confirmation' and s.seed==101:
        with np.load(folder/'E4-weights.npz',allow_pickle=False) as f:
            codes=f['source_codes'];model=ReferenceMLP(len(codes),s.seed)
            model.load_state_dict({k:torch.from_numpy(f[k].copy()) for k in f.files if k!='source_codes'})
        model.eval();latency={}
        with torch.no_grad():
            for batch in (1,256):
                x=torch.from_numpy(data[-1].x[:batch].copy())
                for _ in range(10):model(x)
                times=[]
                for _ in range(100):
                    before=time.perf_counter_ns();model(x);times.append((time.perf_counter_ns()-before)/1e6)
                latency[str(batch)]=dict(unit='milliseconds_per_batch',warmup=10,trials=100,median=float(np.median(times)),p95=float(np.percentile(times,95)))
    result=dict(status='complete',settings=asdict(s),stages=stages,memory=memory,oracle_label_repair=repair,
        input_identity=input_identity,attack=audit[1],ledger=ledger,elapsed_seconds=time.perf_counter()-started,
        study_identity=read_json(OUT/'identity.json')['sha256'],final_test_accessed=False,latency=latency,
        serialized_stage_weight_bytes={p.name:p.stat().st_size for p in folder.glob('*weights.npz')})
    write_json(output,result)
    print(name(s),round(result['elapsed_seconds'],1),'seconds',flush=True)
    return result

def gates(results):
    checks=[]
    for learner in ('FT','EI','DR'):
        selected=[r for r in results if r['settings']['learner']==learner]
        for stage,code,threshold in ((1,7,.5),(1,12,.5),(2,4,.7)):
            values=[]
            for row in selected:
                cm=np.asarray(row['stages'][stage-1]['confusion']);values.append(float(cm[code,code]/cm[code].sum()))
            checks.append(dict(learner=learner,stage=stage,code=code,mean_recall=float(np.mean(values)),per_seed=values,threshold=threshold,passed=float(np.mean(values))>=threshold))
    write_json(OUT/'clean-gates.json',dict(passed=all(c['passed'] for c in checks),checks=checks))
    return all(c['passed'] for c in checks)

def run_block(pool,configs):
    pending={pool.submit(worker,asdict(c)):c for c in configs};results=[]
    for future in futures.as_completed(pending):
        s=pending[future]
        try:results.append(future.result())
        except Exception:
            error=traceback.format_exc();write_json(OUT/f'failure-{name(s)}.json',dict(error=error,settings=asdict(s)));raise
        write_json(OUT/'progress.json',dict(block=s.block,completed_in_block=len(results),block_size=len(configs),last=name(s),updated_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    return results

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--hours',type=float,default=8);parser.add_argument('--smoke',action='store_true');args=parser.parse_args()
    setup();OUT.mkdir(parents=True,exist_ok=True)
    if not (OUT/'ownership-source.npz').exists():
        with np.load(BASE/'builder/ownership.npz',allow_pickle=False) as f:
            positions=f['source_positions'];components=f['canonical_components']
        with np.load(ROOT/'data/raw/phase3-feasibility-corrected/no-headers-74/conditional-components-120.npz',allow_pickle=False) as f:
            ids=f['row_ids'][positions];labels=f['labels'][positions].astype(np.int64)
        np.savez_compressed(OUT/'ownership-source.npz',ids=ids,components=components,labels=labels)
    source={p.relative_to(ROOT).as_posix():digest(p) for folder in ('src/phase3','src/phase3_v2') for p in (ROOT/folder).glob('*.py')}
    for rel in ('scripts/run_phase3_overnight.py','docs/phase3-overnight-plan.md','tests/test_phase3_overnight.py','configs/phase3/overnight-analysis.json','results/phase3-cpu-v3/development/tuning-selection.json'):
        source[rel]=digest(ROOT/rel)
    assets={p.relative_to(ROOT).as_posix():digest(p) for p in (BASE/'train').rglob('*.npy')}
    for folder in (BASE/'development',BASE/'builder'):
        for p in folder.glob('*'):
            if p.is_file():assets[p.relative_to(ROOT).as_posix()]=digest(p)
    component=ROOT/'data/raw/phase3-feasibility-corrected/no-headers-74/conditional-components-120.npz'
    assets[component.relative_to(ROOT).as_posix()]=digest(component)
    assets[(OUT/'ownership-source.npz').relative_to(ROOT).as_posix()]=digest(OUT/'ownership-source.npz')
    frozen=dict(source=source,inputs=assets,seeds=SEEDS,doses=DOSES,python=platform.python_version(),torch=torch.__version__,numpy=np.__version__,final_test_accessed=False,selection='historical clean-only tuning; fresh clean gate; no retuning')
    sha=identity(frozen)
    if (OUT/'identity.json').exists():assert read_json(OUT/'identity.json')['sha256']==sha
    else:write_json(OUT/'identity.json',dict(sha256=sha,**frozen))
    if args.smoke:
        s=Settings(rounds=1,block='smoke');print(json.dumps(worker(asdict(s))['stages'][0]));return
    started=time.time();cutoff=started+max(0,args.hours-1.5)*3600
    all_results=[];dispositions=[]
    with futures.ProcessPoolExecutor(max_workers=2) as pool:
        confirm=[Settings(learner=l,seed=s,block='clean-confirmation') for l in ('FT','EI','DR') for s in (101,102,103)]
        clean=run_block(pool,confirm);all_results.extend(clean)
        if not gates(clean):
            write_json(OUT/'completion.json',dict(status='clean_gate_failed_no_primary_claim',count=len(clean),final_test_accessed=False));return
        core=[Settings(learner=l,admission=a,seed=s,dose=d) for l,a in (('FT','NONE'),('EI','NONE'),('DR','NONE'),('DR','DM'),('DR','DC')) for d in DOSES for s in SEEDS]
        core_result=run_block(pool,core);all_results.extend(core_result);dispositions.append(dict(block='core',status='complete',count=len(core_result)))
        options=[('matched-random',[Settings(admission='DQ',seed=s,dose=d,block='matched-random') for d in ((0,1),(1,2)) for s in SEEDS]),
            ('replay-loss',[Settings(admission='DC',seed=s,dose=d,lambda_y=y,lambda_z=z,block='replay-loss') for y,z in ((1.,0.),(0.,.1)) for d in ((0,1),(1,2)) for s in SEEDS]),
            ('quota',[Settings(admission=a,q=q,seed=s,dose=d,block='quota') for a in ('DM','DC') for q in (.5,.9) for d in ((0,1),(1,2)) for s in SEEDS])]
        for block,configs in options:
            # Conservative two-process duration estimate; no outcome-based tier selection.
            estimate=float(np.percentile([r['elapsed_seconds'] for r in core_result],90))*len(configs)/2*1.15
            if time.time()+estimate>cutoff:
                dispositions.append(dict(block=block,status='not_started_runtime_budget',predicted_seconds=estimate));continue
            rows=run_block(pool,configs);all_results.extend(rows);dispositions.append(dict(block=block,status='complete',count=len(rows)))
    files={p.relative_to(OUT).as_posix():digest(p) for p in (OUT/'runs').rglob('result.json') if '/smoke-' not in p.as_posix()}
    write_json(OUT/'completion.json',dict(status='complete',count=len(all_results),blocks=dispositions,elapsed_seconds=time.time()-started,final_test_accessed=False,files=files,oracle_suffixes=sum(r['oracle_label_repair'] is not None for r in all_results)))

if __name__=='__main__':main()
