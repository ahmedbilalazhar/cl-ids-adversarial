"""Restore canonical unique result paths from a deduplicated audit package."""
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from audit_phase3_reliability import read,digest


def main():
    seen=set();restored=0
    for entry in read(ROOT/'results/phase3-rigorous-audit-v1/result-catalog.json')['files']:
        key=entry['experiment_key']
        if key in seen:continue
        seen.add(key);folder=ROOT/'evidence/unique-runs'/key
        target=(ROOT/entry['path']).resolve()
        if not target.is_relative_to(ROOT.resolve()):raise ValueError('Unsafe catalog target')
        if not folder.is_dir():raise FileNotFoundError(folder)
        for source in folder.rglob('*'):
            if not source.is_file():continue
            dest=target.parent/source.relative_to(folder)
            if dest.exists():
                if digest(dest)!=digest(source):raise ValueError('Existing evidence differs: '+str(dest))
            else:
                dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
        if digest(target)!=entry['sha256']:raise ValueError('Restored result hash mismatch')
        restored+=1
    print('Restored',restored,'canonical trajectories; duplicate copies intentionally omitted.')


if __name__=='__main__':main()
