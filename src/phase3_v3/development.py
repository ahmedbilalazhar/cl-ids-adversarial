"""Frozen v3 development grid with immutable row receipts and resumable orchestration."""
from __future__ import annotations

import argparse
import math
import os
import shutil
import traceback
from contextlib import contextmanager
from dataclasses import asdict
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from src.phase3.common import ROOT, canonical, digest, identity, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.data import verify_train
from src.phase3_v2.development import exact_score, select_tuning
from src.phase3_v2.prepare import prepare

from .evaluate import evaluate
from .protocol import BUDGETS, DECISIONS, PROTOCOL, Settings, code_identity, configure_runtime
from .train import execution_identity, run

SEEDS = (101, 102, 103)
LEARNERS = ('FT', 'EI', 'DR')


def pilot_settings():
    return [Settings(learner=learner, seed=seed, rounds=r, epochs=e)
            for r, e in BUDGETS for learner in LEARNERS for seed in SEEDS]


def tuning_settings(budget):
    if budget not in BUDGETS:
        raise ValueError('Tuning must use a selected v3 pilot budget')
    r, e = budget
    result = []
    for learner in LEARNERS:
        for lr in (.0001, .001):
            extras = [{'lambda_E': v} for v in (1., 10., 100.)] if learner == 'EI' else (
                [{'lambda_z': z, 'lambda_y': y} for z in (.1, .5, 1.) for y in (.1, 1.)] if learner == 'DR' else [{}])
            for extra in extras:
                for seed in SEEDS:
                    result.append(Settings(learner=learner, seed=seed, rounds=r, epochs=e, learning_rate=lr, **extra))
    return result


def select_budget(rows):
    candidates = []
    for budget in BUDGETS:
        members = [r for r in rows if (r['settings']['rounds'], r['settings']['epochs']) == budget]
        valid = len(members) == 9 and all(r['status'] == 'valid' for r in members)
        score = sum((Fraction(*map(int, r['score_exact'])) for r in members), Fraction())/9 if valid else None
        candidates.append({'budget': list(budget), 'valid': valid, 'score': None if score is None else float(score),
                           'score_exact': None if score is None else [str(score.numerator), str(score.denominator)]})
    possible = [r for r in candidates if r['valid']]
    winner = min(possible, key=lambda r: (-Fraction(*map(int, r['score_exact'])), r['budget'][0])) if possible else None
    return None if winner is None else tuple(winner['budget']), candidates


def artifact_hashes(folder):
    return {p.relative_to(folder).as_posix(): digest(p) for p in sorted(folder.rglob('*')) if p.is_file()}


def verify_receipt(output, receipt, expected_row, cache):
    if receipt['schema'] != 'phase3-row-receipt-v3' or receipt['code_identity'] != code_identity():
        raise ValueError('Incompatible row receipt')
    row = receipt['row']
    if any(row[k] != expected_row[k] for k in ('row_id', 'group', 'settings', 'logical_identity')):
        raise ValueError('Receipt row identity/order differs')
    if row['alias_of'] is not None:
        source = cache.get(row['logical_identity'])
        if source is None or source['row_id'] != row['alias_of'] or any(row[k] != source[k] for k in
                ('status', 'metrics', 'score_exact', 'logical_training_seconds', 'run')):
            raise ValueError('Alias differs from its validated physical source')
        if receipt['artifact_files']:
            raise ValueError('An alias cannot own physical artifacts')
    else:
        folder = output/'executions'/row['row_id']
        if artifact_hashes(folder) != receipt['artifact_files']:
            raise ValueError('Immutable row outputs changed or disappeared')
    return row


def verify_complete_run(folder, settings, execution):
    result = read_json(folder/'run.json')
    if result['schema'] != 'phase3-run-v2' or result['status'] != 'complete' or result['resumed_from'] is not None:
        raise ValueError('Only complete from-start physical trajectories can populate a selection row')
    cost = result['elapsed_seconds']
    if result.get('independent_replicate') is not True or result.get('artifact_kind') is not None or type(cost) not in (int, float) or not math.isfinite(cost) or cost <= 0:
        raise ValueError('Selection requires an actual complete physical trajectory and its positive finite measured cost')
    if result['execution'] != execution or result['settings'] != read_json(folder/'settings.json') or result['settings'] != {
            **asdict(settings), 'dose': list(settings.dose)}:
        raise ValueError('Unreceipted run identity differs')
    expected = [(s, r) for s in range(1, 5) for r in range(1, settings.rounds+1)]
    if [(r['stage'], r['round']) for r in result['checkpoints']] != expected or result['next_cursor'] != [5, 1] or result['total_commits'] != len(expected):
        raise ValueError('Incomplete run inventory')
    for row in result['checkpoints']:
        if read_transaction(folder/row['file'], execution)[2] != row:
            raise ValueError('Unreceipted transaction differs from inventory')
    return result


@contextmanager
def workflow_lock(output):
    output.parent.mkdir(parents=True, exist_ok=True)
    handle = (output.parent/('.'+output.name+'.workflow.lock')).open('a+b')
    try:
        if handle.seek(0, 2) == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError('This development output is already controlled by another live process') from error
        yield
    finally:
        handle.close()  # OS releases the lock on close or a process crash.


def execute_development(output: Path, packages: Path, acceptance: Path, resume=False):
    with workflow_lock(output):
        return _execute_development(output, packages, acceptance, resume)


def _execute_development(output: Path, packages: Path, acceptance: Path, resume=False):
    accepted = read_json(acceptance)
    if accepted['status'] != 'passed' or accepted['code_identity'] != code_identity():
        raise ValueError('Current v3 acceptance is required before selection')
    runtime = configure_runtime()
    procedure = {'schema': 'phase3-development-procedure-v3', 'code_identity': code_identity(), 'protocol_sha256': digest(PROTOCOL),
                 'decisions_sha256': digest(DECISIONS), 'acceptance_sha256': digest(acceptance),
                 'pilots': [asdict(s) for s in pilot_settings()],
                 'tuning_by_possible_budget': {f'r{r}e{e}': [asdict(s) for s in tuning_settings((r, e))] for r, e in BUDGETS},
                 'gate_cells_each_unfiltered_learner': [[1, 7, 1, 2], [1, 12, 1, 2], [2, 4, 7, 10]],
                 'tie_order': 'exact rational score; mean logical complete-loop seconds; numeric settings',
                 'final_test_sealed': True, 'gpu_dispatchable': False}
    if output.exists():
        if not resume or canonical(read_json(output/'procedure-lock.json')) != canonical(procedure):
            raise ValueError('Explicit resume and identical frozen procedure required')
    else:
        if resume:
            raise FileNotFoundError('Resume requires an existing procedure')
        output.mkdir(parents=True)
        write_json(output/'procedure-lock.json', procedure)
    rows, cache, verified_packages = [], {}, set()

    def execute_row(settings, row_id, group):
        dose_name = 'p050' if settings.dose == (1, 2) else 'p000'
        package = packages/f's{settings.seed}-{dose_name}'
        if not package.exists():
            prepare(package, settings.seed, settings.dose)
        expected = read_json(package/'preparation.json')['train_manifest_sha256']
        if package not in verified_packages:
            verify_train(package/'train', settings, expected)
            verified_packages.add(package)
        key = identity({'settings': settings.scientific(), 'train': expected, 'code': code_identity(), 'runtime': identity(runtime)})
        row = {'row_id': row_id, 'group': group, 'settings': asdict(settings), 'logical_identity': key}
        receipt_path = output/'receipts'/f'{row_id}.json'
        if receipt_path.exists():
            # JSON tuple/list representation is canonicalized for comparison.
            row['settings']['dose'] = list(settings.dose)
            row = verify_receipt(output, read_json(receipt_path), row, cache)
        else:
            if key in cache:
                prior = cache[key]
                row.update({k: prior[k] for k in ('status', 'metrics', 'score_exact', 'logical_training_seconds', 'run')})
                row.update({'alias_of': prior['row_id'], 'physical_execution': False, 'physical_attempts': 0})
                files = {}
            else:
                location = output/'executions'/row_id
                location.mkdir(parents=True, exist_ok=True)
                attempts = sorted(location.glob('attempt-*'))
                execution = execution_identity(settings, expected, runtime)
                completed = [a for a in attempts if (a/'train/run.json').exists()]
                # Earliest complete matching execution, never chosen by score.
                active = completed[0] if completed else location/f'attempt-{len(attempts)+1:03d}'
                row.update({'physical_execution': True, 'alias_of': None,
                            'run': str((active/'train').resolve()), 'metrics': None, 'physical_attempts': len(attempts)+(not completed)})
                if not completed:
                    if shutil.disk_usage(output).free < 512*1024**2:
                        raise OSError('Less than 512MiB available; retain workflow and resume after disk space is available')
                    active.mkdir()
                    write_json(active/'attempt.json', {'status_at_launch': 'running', 'execution': execution,
                               'started_utc': datetime.now(UTC).isoformat(),
                               'earlier_incomplete_attempts': [str(p.resolve()) for p in attempts],
                               'additional_independent_replicates': 0})
                try:
                    if completed:
                        trajectory = verify_complete_run(active/'train', settings, execution)
                        for duplicate in completed[1:]:
                            other = verify_complete_run(duplicate/'train', settings, execution)
                            if [c['state_identity'] for c in trajectory['checkpoints']] != [c['state_identity'] for c in other['checkpoints']]:
                                raise ValueError('Deterministic complete retries disagree; no score-based choice allowed')
                    else:
                        trajectory = run(package/'train', active/'train', settings, expected)
                    evaluations = sorted(active.glob('evaluation-*'))
                    evaluation = active/f'evaluation-{len(evaluations)+1:03d}'
                    metric = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', active/'train', evaluation)
                    for earlier in evaluations:
                        if (earlier/'metrics.json').exists():
                            old = read_json(earlier/'metrics.json')
                            if old['stages'] != metric['stages']:
                                raise ValueError('Repeated inference differs; no favorable outcome selection')
                    score = exact_score(metric)
                    row.update({'status': 'valid', 'metrics': str((evaluation/'metrics.json').resolve()),
                                'score_exact': [str(score.numerator), str(score.denominator)],
                                'logical_training_seconds': trajectory['elapsed_seconds']})
                except Exception as error:  # noqa: BLE001 - retain scientific/artifact failures without imputation
                    row.update({'status': 'invalid', 'score_exact': None, 'logical_training_seconds': None,
                                'exception': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()})
                files = artifact_hashes(location)
            row['settings']['dose'] = list(settings.dose)
            write_json(receipt_path, {'schema': 'phase3-row-receipt-v3', 'code_identity': code_identity(), 'row': row, 'artifact_files': files})
        cache.setdefault(key, row)
        rows.append(row)
        write_json(output/'inventory.json', {'status': 'running', 'rows': rows, 'planned_pilot': 18, 'planned_tuning': 60,
                   'planned_poison_diagnostic': 3, 'physical_conditions': sum(r['physical_execution'] for r in rows),
                   'physical_training_attempts': sum(r['physical_attempts'] for r in rows),
                   'aliases': sum(not r['physical_execution'] for r in rows), 'final_test_accessed': False})
        print(canonical({'row_id': row_id, 'status': row['status'], 'alias_of': row['alias_of']}), flush=True)
        return row

    pilots = [execute_row(s, f'pilot-{i:02d}-{s.learner}-s{s.seed}-r{s.rounds}e{s.epochs}', 'pilot')
              for i, s in enumerate(pilot_settings(), 1)]
    budget, candidates = select_budget(pilots)
    write_json(output/'synchronization-selection.json', {'selected_budget': budget, 'candidates': candidates})
    if budget is None:
        result = {'status': 'no_valid_synchronization_budget', 'rows': rows, 'final_test_accessed': False, 'gpu_dispatchable': False,
                  'remaining_gates': ['Resolve invalid required pilots prospectively']}
        write_json(output/'completion.json', result)
        return result
    tuning = [execute_row(s, f'tune-{i:02d}-{s.learner}-s{s.seed}', 'tuning') for i, s in enumerate(tuning_settings(budget), 1)]
    selections = {}
    for learner in LEARNERS:
        selected, choices = select_tuning(tuning, learner)
        selections[learner] = {'selected': selected, 'candidates': choices}
    feasible = all(v['selected'] is not None for v in selections.values())
    write_json(output/'tuning-selection.json', {'status': 'clean_feasible' if feasible else 'clean_gate_failed', 'learners': selections})
    diagnostics = []
    if feasible:
        cfg = {**selections['FT']['selected']['settings_without_seed'], 'dose': (1, 2)}
        for seed in SEEDS:
            row = execute_row(Settings(seed=seed, **cfg), f'diagnostic-FT-s{seed}-p050', 'diagnostic')
            if row['status'] != 'valid':
                diagnostics.append({'seed': seed, 'status': 'invalid', 'row_id': row['row_id']})
                continue
            cleanrow = next(r for r in tuning if r['row_id'] in selections['FT']['selected']['rows'] and r['settings']['seed'] == seed)
            clean, poisoned = read_json(Path(cleanrow['metrics'])), read_json(Path(row['metrics']))
            partitions = []
            for stage in (2, 3, 4):
                a, b = poisoned['stages'][stage-1]['hulk_partition'], clean['stages'][stage-1]['hulk_partition']
                if a['support'] != b['support'] or not a['support']:
                    raise ValueError('Diagnostic Hulk banks differ')
                partitions.append({'stage': stage, 'support': a['support'], 'poisoned_to_benign': a['predicted_benign'],
                                   'clean_to_benign': b['predicted_benign'],
                                   'difference': (a['predicted_benign']-b['predicted_benign'])/a['support']})
            diagnostics.append({'seed': seed, 'status': 'valid', 'row_id': row['row_id'], 'partitions': partitions})
    cleanrows = [r for r in rows if r['group'] != 'diagnostic']
    result = {'status': 'clean_feasible_development_complete' if feasible else 'clean_gate_failed_final_grid_blocked',
              'selected_budget': budget, 'logical_pilot_rows': 18, 'logical_tuning_rows': 60,
              'logical_diagnostic_rows_completed': sum(d['status'] == 'valid' for d in diagnostics), 'planned_diagnostic_rows': 3,
              'physical_clean_conditions': sum(r['physical_execution'] for r in cleanrows),
              'physical_clean_executions': sum(r['physical_attempts'] for r in cleanrows),
              'exact_clean_aliases': sum(not r['physical_execution'] for r in cleanrows),
              'invalid_rows': [r['row_id'] for r in rows if r['status'] != 'valid'], 'diagnostics': diagnostics, 'rows': rows,
              'gpu_dispatchable': False, 'final_test_accessed': False,
              'remaining_gates': ([] if feasible else ['Resolve clean infeasibility prospectively'])+
                 ['Pinned GPU runtime and complete GPU workload profile', 'Final scope/code/data/analysis freeze']}
    write_json(output/'completion.json', result)
    inventory = read_json(output/'inventory.json')
    inventory['status'] = 'completed_declared_procedure'
    write_json(output/'inventory.json', inventory)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--packages', type=Path, default=ROOT/'data/processed/phase3-cpu-v2')
    p.add_argument('--acceptance', type=Path, required=True)
    p.add_argument('--resume', action='store_true')
    a = p.parse_args()
    execute_development(a.output, a.packages, a.acceptance, a.resume)


if __name__ == '__main__':
    main()
