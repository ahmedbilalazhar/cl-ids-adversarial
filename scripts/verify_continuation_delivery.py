"""Verify continuation bindings and preserved artifacts without model execution."""
import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

from src.phase3.common import ROOT, digest, identity, read_json, write_json
from src.phase3_v3.protocol import code_identity
from kaggle_worker.bundle import verify
from kaggle_worker.runtime import FROZEN, source_files
from kaggle_worker.selection import selected_settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    base = ROOT/'results/phase3-continuation-v1'
    assert code_identity() == FROZEN
    protected = ['src/phase3', 'src/phase3_v2', 'src/phase3_v3', 'src/phase3_analysis',
                 'configs/phase3', 'docs/phase3-plan/analysis-contrasts.json',
                 'docs/phase3-plan/experiment-manifest.json']
    assert not subprocess.check_output(['git', 'diff', 'b77a7bb', '--', *protected], cwd=ROOT)
    archive = base/'baseline-documents'
    for name, sha in read_json(archive/'manifest.json')['files'].items():
        assert digest(archive/name) == sha, name
    current = identity(source_files())
    for name in ('worker-acceptance-final.json', 'architecture-final.json', 'recovery-review-final.json'):
        value = read_json(base/name)
        assert value['status'] == 'passed'
        assert value['runtime']['worker_source_identity'] == current
    receipt = read_json(base/'bundle-final/acceptance.json')
    assert receipt['worker_source_identity'] == current
    bundle = base/'bundle-final/qualification.zip'
    assert digest(bundle) == receipt['archive_sha256']
    snapshot = verify(bundle)
    for name, sha in snapshot['frozen_sources'].items():
        assert digest(ROOT/name) == sha
    notebook = read_json(base/'notebook-final/phase3-qualification.ipynb')
    cells = [c for c in notebook['cells'] if c['cell_type'] == 'code']
    for cell in cells:
        ast.parse(''.join(cell['source']))
    assert notebook['metadata']['phase3']['bundle_sha256'] == receipt['archive_sha256']
    assert any('RUN_FULL_DATA = False' in ''.join(c['source']) for c in cells)
    documents = [ROOT/'docs/phase3-cpu-v3/continuation-audit.md',
                 ROOT/'docs/phase3-plan/kaggle-execution-contract.md']
    links = 0
    for path in documents:
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if target.startswith(('https://', 'http://', '#')):
                continue
            assert (path.parent/target.split('#')[0]).exists(), (path, target)
            links += 1
    scope = read_json(ROOT/'docs/phase3-plan/continuation-scope.json')
    manifest = ROOT/'docs/phase3-plan/experiment-manifest.json'
    assert scope['source_manifest_sha256'] == digest(manifest)
    planned = [r for r in read_json(manifest)['full_trajectories'] if r['phase'] == 'final']
    ids = [i for group in scope['condition_groups'] for i in group['planned_ids']]
    assert len(ids) == len(set(ids)) == len(planned)
    assert set(ids) == {r['planned_id'] for r in planned}
    assert all(g['seeds'] == list(range(1, 12))+[42] for g in scope['condition_groups'])
    assert not scope['final_dispatchable'] and scope['selected_scope'] is None
    assert read_json(ROOT/'docs/phase3-plan/planning-validation.json')['passed']
    write_json(args.output, {'status': 'passed', 'frozen_code_identity': FROZEN,
               'worker_source_identity': current, 'bundle_files': len(snapshot['files']),
               'notebook_code_cells_compiled': len(cells), 'local_links_checked': links,
               'final_planning_rows_reconciled': len(ids),
               'selected_settings': {k: selected_settings(k).scientific() for k in ('FT', 'EI', 'DR')},
               'actual_GPU_qualified': False, 'final_test_accessed': False, 'final_dispatchable': False})
    print(json.dumps({'status': 'passed', 'worker_source_identity': current}))


if __name__ == '__main__':
    main()
