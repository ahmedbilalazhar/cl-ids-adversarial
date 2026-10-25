"""Frozen clean pilot/tuning procedure. Final-test and GPU dispatch remain absent."""
from __future__ import annotations

import argparse
import traceback
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

from src.phase3.common import ROOT, canonical, digest, identity, read_json, write_json

from .evaluate import evaluate
from .prepare import prepare
from .protocol import Settings, code_identity
from .train import run

SEEDS = (101, 102, 103)
LEARNERS = ('FT', 'EI', 'DR')
BUDGETS = ((1, 3), (3, 1))


def pilot_settings():
    return [Settings(learner=learner, seed=seed, rounds=r, epochs=e)
            for r, e in BUDGETS for learner in LEARNERS for seed in SEEDS]


def tuning_settings(budget):
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


def exact_score(metrics):
    values = [Fraction(int(s['eligible_macro_f1_exact'][0]), int(s['eligible_macro_f1_exact'][1])) for s in metrics['stages']]
    if len(values) != 4:
        raise ValueError('Incomplete metric stages')
    return sum(values, Fraction()) / 4


def clean_gates(metrics):
    if len(metrics) != 3 or {m['settings']['seed'] for m in metrics} != set(SEEDS):
        raise ValueError('All three development seeds required')
    cells = []
    for stage, code, threshold in ((1, 7, Fraction(1, 2)), (1, 12, Fraction(1, 2)), (2, 4, Fraction(7, 10))):
        fractions = []
        for metric in metrics:
            row = next(r for r in metric['stages'][stage-1]['eligible_classes'] if r['code'] == code)
            if not row['support']:
                raise ValueError('Required clean gate has no support')
            fractions.append(Fraction(row['tp'], row['tp']+row['fn']))
        mean = sum(fractions, Fraction()) / 3
        cells.append({'stage': stage, 'source_code': code, 'mean_recall': float(mean),
                      'mean_recall_exact': [str(mean.numerator), str(mean.denominator)],
                      'required': float(threshold), 'passed': mean >= threshold,
                      'per_seed_recall': [float(v) for v in fractions]})
    return {'passed': all(c['passed'] for c in cells), 'cells': cells}


def select_budget(rows):
    candidates = []
    for budget in BUDGETS:
        members = [r for r in rows if (r['settings']['rounds'], r['settings']['epochs']) == budget]
        valid = len(members) == 9 and all(r['status'] == 'valid' for r in members)
        score = sum((Fraction(*map(int, r['score_exact'])) for r in members), Fraction()) / 9 if valid else None
        candidates.append({'budget': list(budget), 'valid': valid, 'score': None if score is None else float(score),
                           'score_exact': None if score is None else [str(score.numerator), str(score.denominator)]})
    possible = [r for r in candidates if r['valid']]
    if not possible:
        return None, candidates
    winner = min(possible, key=lambda r: (-Fraction(*map(int, r['score_exact'])), r['budget'][0]))
    return tuple(winner['budget']), candidates


def select_tuning(rows, learner):
    groups = {}
    for row in rows:
        if row['settings']['learner'] != learner:
            continue
        key = dict(row['settings'])
        key.pop('seed')
        groups.setdefault(canonical(key), []).append(row)
    candidates = []
    for members in groups.values():
        valid = len(members) == 3 and all(r['status'] == 'valid' for r in members)
        metrics = [read_json(Path(r['metrics'])) for r in members] if valid else []
        gates = clean_gates(metrics) if valid else {'passed': False, 'cells': [], 'status': 'incomplete_or_invalid_required_seeds'}
        score = sum((exact_score(m) for m in metrics), Fraction()) / 3 if valid else None
        cost = sum(r['logical_training_seconds'] for r in members)/3 if valid else None
        candidates.append({'settings_without_seed': {k: v for k, v in members[0]['settings'].items() if k != 'seed'},
                           'valid': valid, 'feasible': valid and gates['passed'], 'gates': gates,
                           'score': None if score is None else float(score),
                           'score_exact': None if score is None else [str(score.numerator), str(score.denominator)],
                           'logical_training_seconds': cost, 'rows': [r['row_id'] for r in members]})
    possible = [r for r in candidates if r['feasible']]
    if not possible:
        return None, candidates
    def key(r):
        cfg = r['settings_without_seed']
        numeric = (cfg['learning_rate'], cfg['lambda_E']) if learner == 'EI' else (
            (cfg['learning_rate'], cfg['lambda_z'], cfg['lambda_y']) if learner == 'DR' else (cfg['learning_rate'],))
        return -Fraction(*map(int, r['score_exact'])), r['logical_training_seconds'], numeric
    return min(possible, key=key), candidates


def execute_development(output: Path, packages: Path, acceptance: Path):
    accepted = read_json(acceptance)
    if accepted['status'] != 'passed' or accepted['code_identity'] != code_identity():
        raise ValueError('Current implementation must pass method acceptance before development selection')
    if output.exists():
        raise FileExistsError('Choose a new development output; preserve every prior attempt')
    output.mkdir(parents=True)
    write_json(output/'procedure-lock.json', {'schema': 'phase3-development-procedure-v2', 'code_identity': code_identity(),
               'decisions_sha256': digest(ROOT/'docs/phase3-cpu-v2/decisions-2026-10-24.md'),
               'acceptance_sha256': digest(acceptance), 'pilots': [asdict(s) for s in pilot_settings()],
               'tuning_by_possible_budget': {f'r{r}e{e}': [asdict(s) for s in tuning_settings((r, e))] for r, e in BUDGETS},
               'gate_cells_each_unfiltered_learner': [[1, 7, 1, 2], [1, 12, 1, 2], [2, 4, 7, 10]],
               'tie_order': 'exact rational score; mean logical complete training seconds; numeric lexicographic settings',
               'final_test_sealed': True, 'gpu_dispatchable': False})
    for seed in SEEDS:
        package = packages/f's{seed}-p000'
        if not package.exists():
            prepare(package, seed, (0, 1))
    cache, rows = {}, []

    def execute_row(settings, row_id, group):
        package = packages/f's{settings.seed}-p000'
        expected = read_json(package/'preparation.json')['train_manifest_sha256']
        key = identity({'settings': settings.scientific(), 'train': expected, 'code': code_identity()})
        row = {'row_id': row_id, 'group': group, 'settings': asdict(settings), 'logical_identity': key}
        if key in cache:
            prior = cache[key]
            row.update({k: prior[k] for k in ('status', 'metrics', 'score_exact', 'logical_training_seconds', 'run')})
            row['alias_of'] = prior['row_id']
            row['physical_execution'] = False
        else:
            location = output/'executions'/row_id
            row.update({'physical_execution': True, 'alias_of': None, 'run': str((location/'train').resolve()),
                        'metrics': str((location/'evaluation/metrics.json').resolve())})
            try:
                trajectory = run(package/'train', location/'train', settings, expected)
                metric = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', location/'train', location/'evaluation')
                score = exact_score(metric)
                row.update({'status': 'valid', 'score_exact': [str(score.numerator), str(score.denominator)],
                            'logical_training_seconds': trajectory['elapsed_seconds']})
            except Exception as exc:  # noqa: BLE001 - retain the entire invalid execution and its traceback
                row.update({'status': 'invalid', 'score_exact': None, 'logical_training_seconds': None,
                            'exception': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()})
            cache[key] = row
        rows.append(row)
        write_json(output/'inventory.json', {'status': 'running', 'rows': rows, 'planned_pilot': 18, 'planned_tuning': 60,
                   'planned_poison_diagnostic': 3, 'physical_executions': sum(r['physical_execution'] for r in rows),
                   'aliases': sum(not r['physical_execution'] for r in rows), 'final_test_accessed': False})
        print(canonical({'row_id': row_id, 'status': row['status'], 'alias_of': row['alias_of']}), flush=True)
        return row

    pilots = [execute_row(s, f'pilot-{i:02d}-{s.learner}-s{s.seed}-r{s.rounds}e{s.epochs}', 'pilot')
              for i, s in enumerate(pilot_settings(), 1)]
    budget, budgets = select_budget(pilots)
    write_json(output/'synchronization-selection.json', {'selected_budget': budget, 'candidates': budgets})
    if budget is None:
        write_json(output/'completion.json', {'status': 'no_valid_synchronization_budget', 'remaining_gates': ['Repair or amend invalid required pilots; no final testing'], 'rows': rows})
        return
    tuning = [execute_row(s, f'tune-{i:02d}-{s.learner}-s{s.seed}', 'tuning') for i, s in enumerate(tuning_settings(budget), 1)]
    selections = {}
    for learner in LEARNERS:
        selected, candidates = select_tuning(tuning, learner)
        selections[learner] = {'selected': selected, 'candidates': candidates}
    feasible = all(v['selected'] is not None for v in selections.values())
    write_json(output/'tuning-selection.json', {'status': 'clean_feasible' if feasible else 'clean_gate_failed', 'learners': selections})
    # The FT diagnostic is a later scientific gate. Never run it just because the
    # unfiltered anchor test or one favored learner happened to look successful.
    diagnostics = []
    if feasible:
        cfg = selections['FT']['selected']['settings_without_seed']
        cfg['dose'] = (1, 2)
        for seed in SEEDS:
            settings = Settings(seed=seed, **cfg)
            package = packages/f's{seed}-p050'
            if not package.exists():
                prepare(package, seed, (1, 2))
            expected = read_json(package/'preparation.json')['train_manifest_sha256']
            location = output/'diagnostics'/f'FT-s{seed}-p050'
            trajectory = run(package/'train', location/'train', settings, expected)
            metric = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', location/'train', location/'evaluation')
            cleanrow = next(r for r in tuning if r['row_id'] in selections['FT']['selected']['rows'] and r['settings']['seed'] == seed)
            clean = read_json(Path(cleanrow['metrics']))
            partitions = []
            for t in (2, 3, 4):
                a, b = metric['stages'][t-1]['hulk_partition'], clean['stages'][t-1]['hulk_partition']
                if a['support'] != b['support'] or not a['support']:
                    raise ValueError('Diagnostic Hulk banks differ')
                partitions.append({'stage': t, 'support': a['support'], 'poisoned_to_benign': a['predicted_benign'],
                                   'clean_to_benign': b['predicted_benign'],
                                   'difference': (a['predicted_benign']-b['predicted_benign'])/a['support']})
            diagnostics.append({'seed': seed, 'partitions': partitions, 'training_seconds': trajectory['elapsed_seconds']})
    write_json(output/'completion.json', {'status': 'clean_feasible_development_complete' if feasible else 'clean_gate_failed_final_grid_blocked',
               'selected_budget': budget, 'logical_pilot_rows': 18, 'logical_tuning_rows': 60,
               'logical_diagnostic_rows_completed': len(diagnostics), 'planned_diagnostic_rows': 3,
               'physical_clean_executions': sum(r['physical_execution'] for r in rows),
               'exact_clean_aliases': sum(not r['physical_execution'] for r in rows),
               'invalid_rows': [r['row_id'] for r in rows if r['status'] != 'valid'],
               'diagnostics': diagnostics, 'rows': rows, 'gpu_dispatchable': False, 'final_test_accessed': False,
               'remaining_gates': ['Resolve clean infeasibility prospectively' if not feasible else 'Final runtime/scope/cost/analysis freeze',
                                   'Pinned GPU runtime and complete GPU workload profile', 'Final scope/code/data/analysis freeze']})
    inventory = read_json(output/'inventory.json')
    inventory['status'] = 'completed_clean_procedure'
    write_json(output/'inventory.json', inventory)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--packages', type=Path, default=ROOT/'data/processed/phase3-cpu-v2')
    p.add_argument('--acceptance', type=Path, required=True)
    a = p.parse_args()
    execute_development(a.output, a.packages, a.acceptance)


if __name__ == '__main__':
    main()
