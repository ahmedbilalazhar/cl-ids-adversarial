"""Read-only acceptance of the separately identified two-hour audit delivery."""
import argparse
import json
import re
import subprocess
from pathlib import Path

from kaggle_worker.runtime import FROZEN, source_files, verify_frozen_bindings
from phase3_delivery.catalog import create_output
from src.phase3.common import ROOT, digest, identity, read_json
from src.phase3_v3.protocol import code_files, code_identity

BASELINE = '1869d1b7c9de511ea091fd5b5b639165ffacdc93'
AUDIT = ROOT/'results/phase3-two-hour-audit-v1'


def verify(output):
    checks = []
    def require(name, passed, detail):
        if not passed:
            raise ValueError(name+': '+str(detail))
        checks.append({'check': name, 'status': 'passed', 'detail': detail})
    baseline = read_json(AUDIT/'protected-baseline.json')
    require('scientific source unchanged', code_identity() == FROZEN == baseline['scientific_identity'] and
            code_files() == baseline['scientific_files'], {'identity': FROZEN, 'files': len(code_files())})
    verify_frozen_bindings()
    for name, sha in baseline['protected_payloads'].items():
        require('protected payload '+name, digest(ROOT/name) == sha, sha)
    guarded = ('src/phase3', 'src/phase3_v2', 'src/phase3_v3', 'src/phase3_analysis', 'configs/phase3',
               'docs/phase3-cpu-v3/decisions-2026-10-24.md')
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASELINE, '--', *guarded], cwd=ROOT, text=True)
    require('no protected tracked edits', not changed.strip(), guarded)
    worker = identity(source_files())
    for name, count in (('worker-acceptance-final.json', 30), ('architecture-final.json', 61),
                        ('recovery-review-final.json', 5)):
        value = read_json(AUDIT/'candidate-v5'/name)
        require(name, value['status'] == 'passed' and len(value['checks']) == count and
                all(c['status'] == 'passed' for c in value['checks']) and
                value['runtime']['worker_source_identity'] == worker and
                value['runtime']['frozen_code_identity'] == FROZEN and value['final_test_accessed'] is False,
                {'check_groups': count, 'worker_source_identity': worker})
    bundle = read_json(AUDIT/'candidate-v5/bundle-final/acceptance.json')
    snapshot = read_json(AUDIT/'candidate-v5/bundle-final/snapshot.json')
    require('v5 bundle and snapshot', bundle['status'] == 'passed' and bundle['files_verified'] == 82 and
            bundle['worker_source_identity'] == worker and snapshot['worker_sources'] == source_files() and
            digest(AUDIT/'candidate-v5/bundle-final/qualification.zip') == bundle['archive_sha256'], bundle)
    notebook_path = AUDIT/'candidate-v5/notebook-final/phase3-qualification.ipynb'
    notebook = read_json(notebook_path)
    source = '\n'.join(''.join(c['source']) for c in notebook['cells'] if c['cell_type'] == 'code')
    require('notebook budget and seal', notebook['metadata']['phase3']['bundle_sha256'] == bundle['archive_sha256'] and
            'RUN_FULL_DATA = False' in source and 'SessionBudget(' in source and 'verify-existing' in source,
            {'notebook_sha256': digest(notebook_path), 'full_data_default': False})
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            compile(''.join(cell['source']), str(notebook_path), 'exec')
    legacy = read_json(AUDIT/'legacy-catalog-compatibility-final.json')
    require('historical development compatibility', legacy['status'] == 'passed' and len(legacy['records']) == 72 and
            len(legacy['aliases']) == 9 and len(legacy['attempts']) == 81 and not legacy['unreferenced_objects'] and
            not legacy['missing_run_ids'], {'physical': 72, 'aliases': 9, 'attempts': 81})
    history = read_json(AUDIT/'historical-preservation-final.json')
    require('historical trajectory and source archive preservation', history['status'] == 'passed' and
            history['physical_row_payloads_verified'] == 7200 and
            history['source_bundle_payloads_verified'] == 287 and history['new_research_trajectories'] == 0,
            {'original_trajectory_payloads': 7200, 'archived_source_payloads': 287})
    log = (AUDIT/'ci-equivalent-final-attempt6.log').read_text()
    require('local pinned suite', re.search(r'Ran 92 tests in [0-9.]+s', log) and 'OK (skipped=1)' in log and
            not re.search(r'^(FAILED|ERROR:|FAIL:)', log, flags=re.M),
            {'tests_run': 92, 'passed': 91, 'skipped': 1, 'skip': 'POSIX FIFO on Windows'})
    nonzero = read_json(AUDIT/'nonzero-oracle-final.json')
    require('nonzero independent endpoint oracle', nonzero['status'] == 'passed' and
            nonzero['oracle_pair_assertions'] == 348 and nonzero['unavailable_contrasts'] == 12,
            {'fabricated_count_trajectories': 240, 'paired_oracle_assertions': 348, 'family': 'all_29'})
    evidence = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(AUDIT.rglob('*'))
                if p.is_file() and p.suffix in ('.json', '.log', '.ipynb') and p != output}
    sources = {p.relative_to(ROOT).as_posix(): digest(p)
               for folder in ('kaggle_worker', 'phase3_delivery', 'scripts', 'tests')
               for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and p.suffix in ('.py', '.txt', '.in')}
    create_output(output, {'schema': 'phase3-two-hour-audit-acceptance-v1', 'status': 'passed',
                  'baseline_commit': BASELINE, 'frozen_code_identity': FROZEN, 'worker_source_identity': worker,
                  'checks': checks, 'evidence_sha256': evidence, 'implementation_files': sources,
                  'actual_GPU_qualified': False, 'final_test_accessed': False, 'final_dispatchable': False,
                  'scope': 'Local CPU engineering qualification; no final study or provider durability claim'})
    print(json.dumps({'status': 'passed', 'checks': len(checks), 'worker_source_identity': worker}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    verify(parser.parse_args().output.resolve())


if __name__ == '__main__':
    main()
