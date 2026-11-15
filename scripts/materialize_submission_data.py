"""Restore deduplicated prepared inputs from the upload ZIP without overwriting data."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def main():
    mapping=json.loads((ROOT/'data/submission-input-map.json').read_text())
    restored=0
    for relative,entry in mapping['files'].items():
        target=(ROOT/relative).resolve();source=(ROOT/entry['shared']).resolve()
        if not target.is_relative_to(ROOT) or not source.is_relative_to(ROOT):raise ValueError('Input path escapes project')
        if target.exists():
            if sha(target)!=entry['sha256']:raise ValueError(f'Existing input differs; not overwritten: {target}')
            continue
        assert sha(source)==entry['sha256']
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);restored+=1
        assert sha(target)==entry['sha256']
    print('Prepared inputs verified;',restored,'files restored; no final-test arrays included')


if __name__=='__main__':main()
