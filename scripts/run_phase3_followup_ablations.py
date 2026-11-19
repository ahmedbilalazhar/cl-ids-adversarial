"""Run predeclared CPU ablations after the primary overnight study."""
import os,sys,argparse,time,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
sys.path.insert(0,str(ROOT))
import scripts.run_phase3_overnight as S
from src.phase3.common import write_json,read_json,digest
OUT=Path(os.environ.get('PHASE3_STUDY_OUT',ROOT/'results/phase3-followup-ablation'))
S.OUT=OUT
def main():
    p=argparse.ArgumentParser();p.add_argument('--hours',type=float,default=8);a=p.parse_args()
    S.setup();started=time.time();cutoff=started+max(0,a.hours-.8)*3600
    prior=read_json(OUT/'identity.json')
    assert prior['sha256']==S.read_json(ROOT/'results/phase3-overnight/identity.json')['sha256']
    S.validate_sources()
    for rel,expected in prior['inputs'].items():
        if not (ROOT/rel).is_file() or digest(ROOT/rel)!=expected:raise RuntimeError('Frozen input drift: '+rel)
    configs=[S.Settings(admission='DC',seed=seed,dose=d,lambda_y=y,lambda_z=z,block='replay-loss')
      for y,z in ((1.,0.),(0.,.1)) for d in ((0,1),(1,2)) for seed in S.SEEDS]
    configs += [S.Settings(admission=m,q=q,seed=seed,dose=d,block='quota')
      for m in ('DM','DC') for q in (.5,.9) for d in ((0,1),(1,2)) for seed in S.SEEDS]
    jobs=[c for c in configs if not (OUT/'runs'/S.name(c)/'result.json').exists()]
    dispositions=[]
    for block in ('replay-loss','quota'):
        group=[c for c in jobs if c.block==block]
        if not group:dispositions.append(dict(block=block,status='already_complete'));continue
        estimate=145*len(group)*1.2
        if time.time()+estimate>cutoff:
            dispositions.append(dict(block=block,status='not_started_runtime_budget',remaining=len(group),estimate_seconds=estimate));continue
        with __import__('concurrent.futures').futures.ProcessPoolExecutor(max_workers=1) as pool:
            for r in __import__('concurrent.futures').futures.as_completed([pool.submit(S.worker, S.asdict(c)) for c in group]):
                result=r.result();write_json(OUT/'progress-followup.json',dict(block=block,completed=sum(1 for x in (OUT/'runs').glob(block+'-*/result.json')),block_size=len(group),updated=time.time()))
        dispositions.append(dict(block=block,status='complete',count=len(group)))
    results=[]
    for path in sorted((OUT/'runs').glob('*/result.json')):
        r=json.loads(path.read_text())
        if r['settings']['block'] in ('core','matched-random','replay-loss','quota'):results.append(r)
    files={p.relative_to(OUT).as_posix():digest(p) for p in (OUT/'runs').rglob('result.json')}
    write_json(OUT/'completion-followup.json',dict(status='complete' if all(x['status'] in ('complete','already_complete') for x in dispositions) else 'partial',count=len(results),new_blocks=dispositions,elapsed_seconds=time.time()-started,files=files,final_test_accessed=False))
    print(json.dumps(dispositions),flush=True)
if __name__=='__main__':
    with S.execution_lock():main()
