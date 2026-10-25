"""Plan entire paired seed blocks; never dispatch final work or operate accounts."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from src.phase3.common import ROOT, digest, read_json, write_json

MANIFEST = ROOT/'docs/phase3-plan/experiment-manifest.json'
SEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 42]
LOOP_SECONDS = {'FT': 201.9, 'EI': 233.9, 'DR': 314.6}


def plan(package='course', contributors=8):
    if type(contributors) is not int or not 1 <= contributors <= 8:
        raise ValueError('One to eight distinct contributors supported')
    source = read_json(MANIFEST)
    if package not in source['summaries']:
        raise ValueError('Unknown planning package')
    selected = [r for r in source['full_trajectories'] if r['phase'] == 'final' and package in r['packages']]
    if len(selected) != source['summaries'][package]['final_full_logical']:
        raise ValueError('Planning manifest count differs')
    assignments = {str(i+1): [] for i in range(contributors)}
    for i, seed in enumerate(SEEDS):
        assignments[str(i % contributors+1)].append(seed)
    blocks = []
    for seed in SEEDS:
        rows = [r for r in selected if r['seed'] == seed]
        by_arm = Counter(r['arm'] for r in rows)
        # Filtered and ablation costs are proxies, not measurements. No E1 reuse
        # or presumed GPU speedup is deducted from this scenario.
        seconds = sum(LOOP_SECONDS.get(r['arm'], LOOP_SECONDS['DR']) for r in rows)
        blocks.append({'seed': seed, 'conditions': [r['planned_id'] for r in rows],
                       'arm_counts': dict(sorted(by_arm.items())), 'logical_full_trajectories': len(rows),
                       'local_CPU_training_loop_proxy_hours': seconds/3600})
    lookup = {b['seed']: b for b in blocks}
    work = {owner: {'seeds': seeds, 'loop_proxy_hours': sum(lookup[s]['local_CPU_training_loop_proxy_hours'] for s in seeds),
                    'quota_feasible': None, 'runtime_qualified': False} for owner, seeds in assignments.items()}
    return {'schema': 'kaggle-seed-plan-v1', 'planning_only': True, 'final_dispatchable': False,
            'package': package, 'manifest_sha256': digest(MANIFEST), 'contributors': contributors,
            'contributor_model': 'Distinct people independently operate their own account; no credential sharing or account rotation',
            'five_FL_clients_per_job': True, 'final_full_trajectories': len(selected),
            'oracle_new_suffixes_separately_budgeted': 12, 'blocks': blocks, 'assignments': work,
            'aggregate_CPU_loop_proxy_hours': sum(b['local_CPU_training_loop_proxy_hours'] for b in blocks),
            'longest_assignment_CPU_loop_proxy_hours': max(v['loop_proxy_hours'] for v in work.values()),
            'GPU_hours_estimate': None, 'quota_verified': False,
            'unmeasured_costs': ['Kaggle full-worker runtime', 'filtered/ablation costs (DR proxy used)',
                               'startup/install', 'importance outside recorded training-loop cost', 'evaluation',
                               'checkpoint/export', 'oracle suffixes', 'failed attempts and confirmation runs'],
            'release_gates': ['Complete current CPU delivery and clean feasibility', 'Measured actual Kaggle runtime and device qualification',
                              'Selected settings confirmed on target runtime', 'Full job costs and per-contributor quotas',
                              'Final scope/methods/data/source/analysis lock; final features separately sealed'],
            'unsupported_methods_are_not_mapped_to_DR': True,
            'note': 'A scheduling proxy cannot make unimplemented ablations executable or select a smaller scientific scope.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', choices=['core', 'course', 'complete', 'focused', 'focused_external', 'strengthened'], default='course')
    parser.add_argument('--contributors', type=int, default=8)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = plan(args.package, args.contributors)
    write_json(args.output, result)
    print({k: result[k] for k in ('final_full_trajectories', 'aggregate_CPU_loop_proxy_hours',
                                 'longest_assignment_CPU_loop_proxy_hours', 'final_dispatchable')})


if __name__ == '__main__':
    main()
