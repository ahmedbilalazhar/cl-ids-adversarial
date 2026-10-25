"""Apply the prospective infrastructure timing disposition without editing receipts."""
from __future__ import annotations

import argparse
import copy
import io
import statistics
import subprocess
import sys
import time
import unittest
from pathlib import Path

import numpy as np

from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.development import select_tuning
from src.phase3_v3.protocol import Settings, code_identity
from src.phase3_v3.train import run

PLAN = ROOT/'docs/phase3-cpu-v3/cost-amendment-2026-10-24.md'


def anomalies(trajectory):
    found = []
    for row in trajectory['timings']:
        peers = [r['training_seconds'] for r in trajectory['timings'] if r['stage'] == row['stage'] and r['round'] != row['round']]
        if len(peers) < 2:
            raise ValueError('At least three complete rounds per stage required for the frozen timing rule')
        median = statistics.median(peers)
        if row['training_seconds'] > 600 and row['training_seconds'] > 10*median:
            found.append({'stage': row['stage'], 'round': row['round'], 'training_seconds': row['training_seconds'], 'other_rounds_median_seconds': median})
    return found


def derive_selection(rows, replacement_costs):
    corrected = copy.deepcopy([r for r in rows if r['group'] == 'tuning'])
    for row in corrected:
        if row['logical_identity'] in replacement_costs:
            value = replacement_costs[row['logical_identity']]
            if value is None:
                continue
            row['logical_training_seconds'] = value
    selections = {}
    for learner in ('FT', 'EI', 'DR'):
        selected, candidates = select_tuning(corrected, learner)
        selections[learner] = {'selected': selected, 'candidates': candidates}
    return selections


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--development', type=Path, default=ROOT/'results/phase3-cpu-v3/development')
    p.add_argument('--output', type=Path, default=ROOT/'results/phase3-cpu-v3/cost-correction')
    p.add_argument('--worker-request', type=Path)
    args = p.parse_args()
    if args.worker_request is not None:
        request = read_json(args.worker_request)
        if request['code_identity'] != code_identity():
            raise ValueError('Timing worker source changed')
        settings = Settings(**{**request['settings'], 'dose': tuple(request['settings']['dose'])}).validate()
        package = Path(request['package'])
        run(package, Path(request['output']), settings, digest(package/'manifest.json'))
        return
    if args.output.exists():
        raise FileExistsError(args.output)
    completed = read_json(args.development/'completion.json')
    if completed['status'] not in ('clean_feasible_development_complete', 'clean_gate_failed_final_grid_blocked'):
        raise ValueError('Complete declared development required before timing correction')
    original_selection = read_json(args.development/'tuning-selection.json')
    if completed['invalid_rows']:
        # Invalid rows remain in the selector; a cost repair never makes one valid.
        print({'retained_invalid_rows': completed['invalid_rows']}, flush=True)
    args.output.mkdir(parents=True)
    capture = io.StringIO()
    tests = unittest.TextTestRunner(stream=capture, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('tests.test_phase3_costs'))
    write_json(args.output/'acceptance.json', {'status': 'passed' if tests.wasSuccessful() else 'failed', 'tests_run': tests.testsRun,
               'script_sha256': digest(Path(__file__)), 'test_source_sha256': digest(ROOT/'tests/test_phase3_costs.py'),
               'plan_sha256': digest(PLAN), 'scope': 'Timing anomaly and exact-score-tie/cost correction fixtures; no outcome-based choice',
               'unittest_output': capture.getvalue()})
    if not tests.wasSuccessful():
        raise AssertionError('Timing correction fixtures failed')
    records, replacements = [], {}
    for row in completed['rows']:
        if not row['physical_execution'] or row['status'] != 'valid':
            continue
        source = Path(row['run'])
        baseline = read_json(source/'run.json')
        flagged = anomalies(baseline)
        if not flagged:
            continue
        if baseline['execution']['code_identity'] != code_identity():
            raise ValueError('Frozen v3 identity changed')
        settings = Settings(**{**row['settings'], 'dose': tuple(row['settings']['dose'])}).validate()
        dose = 'p050' if settings.dose == (1, 2) else 'p000'
        package = ROOT/f'data/processed/phase3-cpu-v2/s{settings.seed}-{dose}/train'
        target = args.output/row['row_id']
        request = args.output/(row['row_id']+'-request.json')
        write_json(request, {'code_identity': code_identity(), 'settings': row['settings'],
                             'package': str(package), 'output': str(target), 'source_row_id': row['row_id']})
        started = time.perf_counter()
        subprocess.run([sys.executable, '-m', 'scripts.remeasure_phase3_v3', '--worker-request', str(request)], cwd=ROOT, check=True)
        process_seconds = time.perf_counter()-started
        result = read_json(target/'run.json')
        equality = []
        for checkpoint in result['checkpoints']:
            a, aa, am = read_transaction(source/checkpoint['file'])
            b, bb, bm = read_transaction(target/checkpoint['file'])
            equal = set(aa) == set(bb) and all(aa[k].dtype == bb[k].dtype and np.array_equal(aa[k], bb[k]) for k in aa)
            equality.append({'file': checkpoint['file'], 'exact': a == b and equal and am['state_identity'] == bm['state_identity']})
        exact = all(c['exact'] for c in equality) and result['ledger'] == baseline['ledger']
        repeat_flags = anomalies(result)
        eligible = exact and not repeat_flags
        replacement = result['elapsed_seconds'] if eligible else None
        replacements[row['logical_identity']] = replacement
        records.append({'row_id': row['row_id'], 'logical_identity': row['logical_identity'], 'original_run_sha256': digest(source/'run.json'),
                        'repeat_run_sha256': digest(target/'run.json'), 'original_anomalies': flagged, 'repeat_anomalies': repeat_flags,
                        'exact_state_checks': equality, 'ledger_exact': result['ledger'] == baseline['ledger'],
                        'original_physical_elapsed_seconds': baseline['elapsed_seconds'], 'additional_physical_elapsed_seconds': result['elapsed_seconds'],
                        'fresh_worker_process_seconds': process_seconds,
                        'eligible_comparable_logical_seconds': replacement, 'additional_independent_replicates': 0})
        if not exact:
            write_json(args.output/'failure.json', {'status': 'reproducibility_failure', 'records': records})
            raise AssertionError('Timing-only remeasurement changed scientific state')
    selections = derive_selection(completed['rows'], replacements)
    changes = {}
    for learner, details in selections.items():
        old, new = original_selection['learners'][learner]['selected'], details['selected']
        a = None if old is None else old['settings_without_seed']
        b = None if new is None else new['settings_without_seed']
        changes[learner] = {'original': a, 'derived': b, 'changed': a != b}
    unresolved = [r['row_id'] for r in records if r['eligible_comparable_logical_seconds'] is None]
    write_json(args.output/'selection.json', {'schema': 'phase3-cost-amended-selection-v1', 'code_identity': code_identity(),
               'status': 'complete' if not unresolved else 'timing_unresolved', 'plan_sha256': digest(PLAN),
               'original_completion_sha256': digest(args.development/'completion.json'),
               'original_selection_sha256': digest(args.development/'tuning-selection.json'),
               'learners': selections, 'selection_comparison': changes, 'remeasurements': records, 'unresolved_costs': unresolved,
               'additional_physical_training_executions': len(records), 'additional_independent_replicates': 0,
               'original_receipts_edited': False, 'final_test_accessed': False, 'gpu_dispatchable': False,
               'required_matched_FT_diagnostic_rerun': changes['FT']['changed']})
    print({'status': 'complete' if not unresolved else 'timing_unresolved', 'remeasurements': len(records), 'changed_selections': [k for k, v in changes.items() if v['changed']]})


if __name__ == '__main__':
    main()
