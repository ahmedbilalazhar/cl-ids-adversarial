"""Re-evaluate clean archived checkpoints on development cohorts only, one CPU thread."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import sys
from pathlib import Path
import json
import time
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from audit_phase3_reliability import read,write_json
from src.phase3.model import ReferenceMLP
from src.phase3.reference import model_identity


def main():
    torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True)
    assert torch.__version__=='2.7.0+cpu' and np.__version__=='2.3.5'
    base=ROOT/'data/processed/phase3-reference74-v1/development'
    manifest=read(base/'manifest.json');assert manifest['role']=='development_only'
    x,y,cohort=[np.load(base/f'{k}.npy',mmap_mode='r',allow_pickle=False) for k in ('x','y','cohort')]
    eligible=manifest['eligible_codes'];arrival=np.asarray(manifest['arrival']);results=[];started=time.perf_counter()
    audit=ROOT/'results/phase3-rigorous-audit-v1'
    rows=read(audit/'trajectory-metrics.json')
    for row in rows:
        if row['block']!='core' or row['dose']!=0:continue
        path=ROOT/row['path'];result=read(path);R={};parity=[]
        for stage in result['stages']:
            t=stage['stage'];weights=path.parent/f'E{t}-weights.npz'
            with np.load(weights,allow_pickle=False) as f:
                slots=f['source_codes'].tolist();model=ReferenceMLP(len(slots),row['seed'])
                model.load_state_dict({k:torch.from_numpy(f[k].copy()) for k in f.files if k!='source_codes'})
            assert model_identity(model,slots)==stage['model_sha256'];model.eval()
            selected=np.flatnonzero(np.isin(y,slots));predictions=np.empty(len(selected),dtype=np.int64)
            with torch.no_grad():
                for start in range(0,len(selected),4096):
                    ix=selected[start:start+4096]
                    predictions[start:start+4096]=np.asarray(slots)[model(torch.from_numpy(x[ix].copy())).argmax(1).numpy()]
            truth=y[selected];cm=np.zeros((16,16),dtype=np.int64);np.add.at(cm,(truth,predictions),1)
            equal=np.array_equal(cm,stage['confusion']);parity.append(equal)
            if not equal:raise ValueError(f'Prediction mismatch: {weights}')
            for j in range(1,t+1):
                mask=((truth==0)&(cohort[selected]==j))|((truth!=0)&np.isin(truth,eligible)&(arrival[truth]==j))
                assert mask.any();R[(t,j)]=float(np.mean(predictions[mask]==truth[mask]))
        final_family={}
        for c in range(16):
            n=int(cm[c].sum());tp=int(cm[c,c]);p=int(cm[:,c].sum())
            final_family[c]=dict(support=n,precision=tp/p if p else None,recall=tp/n if n else None,f1=2*tp/(n+p) if n+p else None)
        results.append(dict(method=row['method'],seed=row['seed'],ACC=sum(R[(4,j)] for j in range(1,5))/4,
                            BWT=sum(R[(4,j)]-R[(j,j)] for j in range(1,4))/3,
                            forgetting=sum(max(R[(t,j)] for t in range(j,5))-R[(4,j)] for j in range(1,4))/3,
                            R={f'{t}-{j}':v for (t,j),v in R.items()},confusion_parity=parity,full_inventory_family_metrics=final_family))
        write_json(audit/'cohort-metrics.json',dict(results=results,elapsed_seconds=time.perf_counter()-started,role='development_only',all_completed=len(results)==60))
        print(row['method'],row['seed'],flush=True)


if __name__=='__main__':main()
