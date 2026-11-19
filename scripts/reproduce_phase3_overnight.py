"""Audit the portable overnight evidence; optionally reproduce one archived trajectory."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--train-result',type=Path,help='Archived result.json identifying one trajectory to retrain in a fresh output directory');p.add_argument('--output',type=Path);a=p.parse_args()
    from materialize_submission_data import main as materialize
    materialize()
    import run_phase3_overnight as study
    identity=json.loads((study.OUT/'identity.json').read_text())
    for rel,expected in identity['source'].items():assert study.digest(ROOT/rel)==expected,rel
    validated=0;missing=[]
    for rel,expected in identity['inputs'].items():
        path=ROOT/rel
        if path.exists():assert study.digest(path)==expected,rel;validated+=1
        else:missing.append(rel)
    allowed=('data/raw/','data/processed/phase3-reference74-v1/builder/')
    assert all(any(rel.startswith(prefix) for prefix in allowed) for rel in missing),missing
    print('Validated',validated,'prepared assets. Raw capture/builder provenance hashes retained:',len(missing))
    if a.train_result:
        assert a.output and not a.output.exists(),'Choose a new output directory; archived results are immutable.'
        result=json.loads(a.train_result.read_text());study.OUT=a.output.resolve();study.OUT.mkdir(parents=True)
        import shutil
        source=ROOT/'results/phase3-overnight'
        for name in ('identity.json','ownership-source.npz'):shutil.copy2(source/name,study.OUT/name)
        reproduced=study.worker(result['settings'])
        assert [r['model_sha256'] for r in reproduced['stages']]==[r['model_sha256'] for r in result['stages']]
        assert [r['confusion'] for r in reproduced['stages']]==[r['confusion'] for r in result['stages']]
        print('Reproduced all four model hashes and confusion matrices.')

if __name__=='__main__':main()
