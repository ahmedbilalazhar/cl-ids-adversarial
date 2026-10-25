"""Keep the FT diagnostic paired with a cost-amended selected clean condition."""
from __future__ import annotations

import argparse
from pathlib import Path

from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v3.evaluate import evaluate
from src.phase3_v3.protocol import Settings, code_identity
from src.phase3_v3.train import run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--development', type=Path, default=ROOT/'results/phase3-cpu-v3/development')
    p.add_argument('--selection', type=Path, default=ROOT/'results/phase3-cpu-v3/cost-correction/selection.json')
    p.add_argument('--output', type=Path, default=ROOT/'results/phase3-cpu-v3/matched-diagnostic')
    args = p.parse_args()
    complete, selection = read_json(args.development/'completion.json'), read_json(args.selection)
    if selection['status'] != 'complete' or selection['code_identity'] != code_identity():
        raise ValueError('Resolved current cost disposition required')
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    feasible = all(v['selected'] is not None for v in selection['learners'].values())
    selected = selection['learners']['FT']['selected']
    changed = selection['required_matched_FT_diagnostic_rerun']
    diagnostics, rows, checks = [], [], []
    physical = 0
    if feasible and changed:
        for seed in (101, 102, 103):
            cleanrow = next(r for r in complete['rows'] if r['row_id'] in selected['rows'] and r['settings']['seed'] == seed)
            settings = Settings(**{**selected['settings_without_seed'], 'seed': seed, 'dose': (1, 2)}).validate()
            package = ROOT/f'data/processed/phase3-cpu-v2/s{seed}-p050/train'
            location = args.output/f'FT-s{seed}-p050'
            run(package, location/'train', settings, digest(package/'manifest.json'))
            physical += 1
            poisoned = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', location/'train', location/'evaluation')
            clean = read_json(Path(cleanrow['metrics']))
            exact_e1 = poisoned['stages'][0] == clean['stages'][0]
            checks.append({'seed': seed, 'check': 'E1_stage_counts_and_model_exact_before_corruption', 'passed': exact_e1})
            if not exact_e1:
                raise AssertionError('Matched diagnostic differs before the corruption stage')
            partitions = []
            for stage in (2, 3, 4):
                a, b = poisoned['stages'][stage-1]['hulk_partition'], clean['stages'][stage-1]['hulk_partition']
                if a['support'] != b['support'] or not a['support']:
                    raise ValueError('Mismatched diagnostic banks')
                partitions.append({'stage': stage, 'support': a['support'], 'poisoned_to_benign': a['predicted_benign'],
                                   'clean_to_benign': b['predicted_benign'],
                                   'difference': (a['predicted_benign']-b['predicted_benign'])/a['support']})
            row_id = f'cost-amended-diagnostic-FT-s{seed}-p050'
            diagnostics.append({'seed': seed, 'status': 'valid', 'row_id': row_id, 'partitions': partitions})
            rows.append({'row_id': row_id, 'settings': poisoned['settings'], 'clean_row_id': cleanrow['row_id'],
                         'run': str(location/'train'), 'metrics': str(location/'evaluation/metrics.json'),
                         'run_sha256': digest(location/'train/run.json'), 'metrics_sha256': digest(location/'evaluation/metrics.json')})
    elif feasible:
        diagnostics = complete['diagnostics']
        for diagnostic in diagnostics:
            row = next(r for r in complete['rows'] if r['row_id'] == diagnostic['row_id'])
            expected = {**selected['settings_without_seed'], 'seed': diagnostic['seed'], 'dose': [1, 2]}
            if row['settings'] != expected:
                raise ValueError('Original FT diagnostic is not paired with the derived selection')
            rows.append(row)
    count = sum(d['status'] == 'valid' for d in diagnostics)
    write_json(args.output/'index.json', {'schema': 'phase3-selected-FT-diagnostic-index-v1',
               'status': 'complete' if not feasible or count == 3 else 'diagnostic_failures_retained',
               'code_identity': code_identity(), 'selection_sha256': digest(args.selection),
               'original_completion_sha256': digest(args.development/'completion.json'),
               'all_clean_learners_feasible': feasible, 'cost_changed_FT_selection': changed,
               'source': 'cost_amended_matching_diagnostics' if feasible and changed else 'original_declared_diagnostics',
               'diagnostics': diagnostics, 'rows': rows, 'checks': checks, 'completed_diagnostic_rows': count,
               'additional_physical_training_executions': physical, 'additional_independent_replicates': 0,
               'scope': 'Same three paired development seeds; original condition diagnostics retained, never counted as extra independent seeds',
               'final_test_accessed': False, 'gpu_dispatchable': False})
    print({'status': 'complete' if not feasible or count == 3 else 'diagnostic_failures_retained', 'physical_replacements': physical})


if __name__ == '__main__':
    main()
