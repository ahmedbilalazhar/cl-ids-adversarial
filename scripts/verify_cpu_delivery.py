"""Independently bind the completed CPU delivery; never execute a model."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import time
import zipfile
from collections import Counter
from fractions import Fraction
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'results/phase3-cpu-v3'
FROZEN = '38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def verify_map(files, root=ROOT):
    for name, expected in files.items():
        assert sha(root/name) == expected, name
    return len(files)


def exact(value):
    return Fraction(*map(int, value))


def run():
    started = time.perf_counter()
    manifest = read(BASE/'source-code-manifest.json')
    files = {p.relative_to(ROOT).as_posix(): sha(p) for directory in ('phase3', 'phase3_v2', 'phase3_v3')
             for p in (ROOT/'src'/directory).glob('*.py')}
    assert canonical_sha(files) == FROZEN and manifest['code_identity'] == FROZEN
    assert files == manifest['files']
    verify_map(manifest['delivery_scripts'])
    verify_map(manifest['analysis_source_and_tests'])
    assert sha(ROOT/'configs/phase3/cpu-v3.json') == manifest['protocol_sha256']
    assert sha(ROOT/'docs/phase3-cpu-v3/decisions-2026-10-24.md') == manifest['decisions_sha256']
    controller = BASE/'post-grid-resumed-20261025'
    procedure = read(controller/'procedure.json')
    assert procedure['code_identity'] == FROZEN
    bound = procedure['source_files']
    current_bound = {p.relative_to(ROOT).as_posix() for directory, pattern in
                     [('scripts', '*phase3*.py'), ('tests', 'test_phase3*.py')]
                     for p in (ROOT/directory).glob(pattern)}
    assert set(bound) == current_bound and len(bound) == 32
    verify_map(bound)
    status = read(controller/'status.json')
    assert status['status'] == 'passed' and len(status['completed_steps']) == 9
    step_files = sorted(controller.glob('[0-9][0-9]-*.json'))
    assert len(step_files) == 9
    for path in step_files:
        row = read(path)
        assert row['status'] == 'passed' and row['exit_code'] == 0
        assert sha(Path(row['evidence'])) == row['evidence_sha256']
        assert sha(path.with_suffix('.log')) == row['log_sha256']

    completion = read(BASE/'completion.json')
    assert completion['status'] == 'CPU_v3_implemented_verified_and_profiled'
    assert completion['code_identity'] == FROZEN
    assert completion['final_test_accessed'] is False and completion['gpu_dispatchable'] is False
    grid = read(BASE/'development/completion.json')
    assert grid['status'] == 'clean_feasible_development_complete'
    assert len(grid['rows']) == 81 and all(row['status'] == 'valid' for row in grid['rows'])
    assert Counter(row['group'] for row in grid['rows']) == {'pilot': 18, 'tuning': 60, 'diagnostic': 3}
    assert {row['settings']['seed'] for row in grid['rows']} == {101, 102, 103}
    assert sum(not row['physical_execution'] for row in grid['rows']) == 9
    rows = {row['row_id']: row for row in grid['rows']}
    receipt_files, receipt_bytes = 0, 0
    for row in grid['rows']:
        receipt = read(BASE/'development/receipts'/(row['row_id']+'.json'))
        assert receipt['row'] == row and receipt['code_identity'] == FROZEN
        if row['physical_execution']:
            folder = BASE/'development/executions'/row['row_id']
            paths = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
            assert paths == set(receipt['artifact_files'])
            verify_map(receipt['artifact_files'], folder)
            receipt_files += len(paths)
            receipt_bytes += sum((folder/name).stat().st_size for name in paths)
        else:
            assert row['alias_of'] in rows and receipt['artifact_files'] == {}

    selection = read(BASE/'cost-correction/selection.json')
    assert selection['status'] == 'complete' and selection['original_receipts_edited'] is False
    assert selection['original_completion_sha256'] == sha(BASE/'development/completion.json')
    assert selection['original_selection_sha256'] == sha(BASE/'development/tuning-selection.json')
    assert selection['unresolved_costs'] == [] and len(selection['remeasurements']) == 2
    assert all(value['changed'] is False for value in selection['selection_comparison'].values())
    gates = {}
    for learner, count in [('FT', 2), ('EI', 6), ('DR', 12)]:
        detail = selection['learners'][learner]
        assert len(detail['candidates']) == count
        selected = detail['selected']
        assert selected['feasible'] is True and selected['gates']['passed'] is True
        assert selected['settings_without_seed']['rounds'] == 12 and selected['settings_without_seed']['epochs'] == 1
        assert exact(selected['score_exact']) == max(exact(c['score_exact']) for c in detail['candidates'] if c['feasible'])
        for candidate in detail['candidates']:
            for cell in candidate['gates']['cells']:
                mean = exact(cell['mean_recall_exact'])
                assert cell['passed'] == (mean >= Fraction(str(cell['required'])))
                assert math.isclose(float(mean), sum(cell['per_seed_recall'])/3, abs_tol=1e-15)
            assert candidate['feasible'] == candidate['gates']['passed']
        gates[learner] = {'settings': selected['settings_without_seed'], 'score': selected['score'],
                          'feasible_candidates': sum(c['feasible'] for c in detail['candidates']),
                          'FTP_recalls_seeds_101_102_103': selected['gates']['cells'][0]['per_seed_recall']}
    for repeat in selection['remeasurements']:
        assert repeat['ledger_exact'] is True and repeat['repeat_anomalies'] == []
        assert all(check['exact'] is True for check in repeat['exact_state_checks'])
        assert repeat['additional_independent_replicates'] == 0

    acceptance_counts = {}
    for relative, expected in [('integration/acceptance.json', 559), ('controls/acceptance.json', 1080),
                               ('recovery/acceptance.json', 104)]:
        result = read(BASE/relative)
        assert result['status'] == 'passed' and len(result['checks']) == expected
        assert all(check['passed'] is True for check in result['checks'])
        acceptance_counts[relative] = expected
    audit = read(ROOT/'results/phase3-endpoint-audit-v1/audit.json')
    assert audit['status'] == 'passed' and audit['valid_logical_rows_audited'] == 81
    assert audit['auditor_sha256'] == sha(ROOT/'scripts/audit_phase3_endpoints.py')
    assert len(audit['rejection_checks']) == 8 and all(c['rejected'] for c in audit['rejection_checks'])
    diagnostic = read(BASE/'matched-diagnostic/index.json')
    assert diagnostic['completed_diagnostic_rows'] == 3 and diagnostic['additional_physical_training_executions'] == 0
    assert diagnostic['selection_sha256'] == sha(BASE/'cost-correction/selection.json')
    effects = []
    for point in audit['paired_FT_diagnostics']:
        pair = next(d for d in diagnostic['diagnostics'] if d['seed'] == point['seed'])
        deltas = [Fraction(p['poisoned_to_benign']-p['clean_to_benign'], p['support']) for p in pair['partitions']]
        assert exact(point['H']['exact']) == (deltas[1]+deltas[2])/2
        assert point['clean_metric_sha256'] == sha(Path(rows[point['clean_row_id']]['metrics']))
        assert point['poison_metric_sha256'] == sha(Path(rows[point['poison_row_id']]['metrics']))
        effects.append({'seed': point['seed'], 'H': point['H']['value']})

    jobs = read(BASE/'profiling/jobs.json')
    assert jobs['status'] == 'passed' and len(jobs['jobs']) == 3
    costs = []
    for job in jobs['jobs']:
        learner = job['learner']
        profile_path = BASE/f'profiling/{learner}/profile.json'
        profile = read(profile_path)
        assert sha(profile_path) == job['profile_sha256']
        assert profile['status'] == 'passed_equivalent_CPU_worker_profile'
        assert all(row['exact'] is True for row in profile['exact_state_checks'])
        assert profile['evaluation_stages_exact'] is True
        source = rows[job['source_row_id']]
        assert profile['source_run_sha256'] == sha(Path(source['run'])/'run.json')
        assert profile['source_metrics_sha256'] == sha(Path(source['metrics']))
        assert profile['local_bundle_sha256'] == sha(BASE/f'profiling/{learner}/local-worker-output.zip')
        assert profile['final_test_accessed'] is False and profile['gpu_dispatchable'] is False
        costs.append({'learner': learner, 'complete_process_seconds': job['process_end_to_end_seconds'],
                      'peak_MiB': profile['peak_after_all_probes']['peak_working_set_bytes']/1024**2})

    preservation = read(BASE/'preservation.json')
    assert preservation['status'] == 'passed' and all(preservation['original_files'].values())
    originals = read(ROOT/'results/phase3-cpu-v2/integrity/original-inputs.json')
    verify_map(originals)
    for version in ('v2', 'v3'):
        review = ROOT/f'docs/phase3-cpu-{version}/evidence'
        verify_map(read(review/'artifact-index.json')['files'], review)

    bundle = ROOT/'results/phase3-source-bundle-v1/CPU-delivery'
    bundle_acceptance = read(bundle/'acceptance.json')
    archive_manifest = read(bundle/'source-manifest.json')
    assert bundle_acceptance['status'] == 'passed' and bundle_acceptance['files_verified'] == 287
    assert all(c['rejected'] for c in bundle_acceptance['rejection_checks'])
    assert sha(bundle/'cpu-source.zip') == sha(bundle/'cpu-source-repeat.zip') == bundle_acceptance['archive_sha256']
    with zipfile.ZipFile(bundle/'cpu-source.zip') as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) == 288
        assert set(names) == set(archive_manifest['files']) | {'SOURCE-MANIFEST.json'}
        assert json.loads(archive.read('SOURCE-MANIFEST.json')) == archive_manifest
        for name, expected in archive_manifest['files'].items():
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name
            payload = archive.read(name)
            assert hashlib.sha256(payload).hexdigest() == sha(ROOT/name) == expected
            assert path.suffix in ('.py', '.md', '.json', '.lock')
            if name.endswith('.py'):
                ast.parse(payload.decode('utf-8-sig'))
    return {'status': 'passed', 'scope': 'Independent current-source, receipt-payload, exact arithmetic and delivery binding audit; no training, inference or new research replicate',
            'code_identity': FROZEN, 'scientific_files': len(files), 'controller_bound_files': len(bound),
            'controller_steps_verified': 9, 'valid_logical_development_rows': 81, 'physical_row_artifact_files_verified': receipt_files,
            'physical_row_artifact_bytes_verified': receipt_bytes, 'selected_conditions': gates,
            'verification_checks': acceptance_counts, 'paired_FT_diagnostic_H': effects,
            'CPU_worker_costs': costs, 'count_artifact_rejections': 8, 'source_bundle_files': 287,
            'source_bundle_sha256': bundle_acceptance['archive_sha256'], 'timing_winners_changed': False,
            'original_files_reverified': len(originals), 'final_test_accessed': False, 'gpu_dispatchable': False,
            'report_sha256': sha(ROOT/'docs/phase3-cpu-v3/report.md'), 'README_sha256': sha(ROOT/'README.md'),
            'audit_source_sha256': sha(Path(__file__)), 'elapsed_seconds': time.perf_counter()-started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=BASE/'independent-delivery-audit.json')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    try:
        result = run()
    except Exception as exc:
        result = {'status': 'failed_attempt_retained', 'exception': type(exc).__name__, 'message': str(exc),
                  'audit_source_sha256': sha(Path(__file__))}
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
        raise
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'rows': 81, 'source_bundle_files': 287,
                      'elapsed_seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    main()
