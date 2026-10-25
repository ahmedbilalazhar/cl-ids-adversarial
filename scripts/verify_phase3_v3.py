"""Real-data v3 compatibility and extended E1 diagnostic reproduction."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v3.evaluate import evaluate
from src.phase3_v3.protocol import Settings, code_identity
from src.phase3_v3.train import run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--acceptance', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    accepted = read_json(args.acceptance)
    if accepted['status'] != 'passed' or accepted['code_identity'] != code_identity():
        raise ValueError('Accepted current v3 required')
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    checks = []
    package = ROOT/'data/processed/phase3-cpu-v2/s101-p000/train'
    expected = digest(package/'manifest.json')
    original = ROOT/'results/phase3-cpu-v2/integration/DC'
    target = args.output/'old-budget-DC'
    result = run(package, target, Settings(admission='DC', rounds=3, epochs=1), expected)
    for row in result['checkpoints']:
        a, aa, _ = read_transaction(original/row['file'])
        b, bb, _ = read_transaction(target/row['file'])
        a.pop('execution')
        b.pop('execution')
        checks.append({'check': 'old_budget_exact_metadata_except_version_identity', 'file': row['file'], 'passed': a == b})
        for name in aa:
            checks.append({'check': 'old_budget_exact_typed_array', 'file': row['file'], 'array': name,
                           'passed': set(aa) == set(bb) and aa[name].dtype == bb[name].dtype and np.array_equal(aa[name], bb[name])})
    metric = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', target, args.output/'old-budget-DC-evaluation')
    prior = read_json(original.parent/'DC-evaluation/metrics.json')
    checks.append({'check': 'old_budget_all_four_independent_evaluation_stages', 'passed': metric['stages'] == prior['stages']})
    for seed in (101, 102, 103):
        package = ROOT/f'data/processed/phase3-cpu-v2/s{seed}-p000/train'
        target = args.output/f'extended-E1-FT-s{seed}'
        result = run(package, target, Settings(learner='FT', seed=seed, rounds=12, epochs=1), digest(package/'manifest.json'), stop_after_commits=12)
        for round_id in (3, 12):
            meta, arrays, _ = read_transaction(target/f'E1-R{round_id}.npz')
            with np.load(ROOT/f'results/phase3-acquisition-diagnostic-v1/natural-s{seed}/E1-R{round_id}-model.npz', allow_pickle=False) as f:
                names = {k for k in f.files if k != 'metadata'}
                for name in names:
                    checks.append({'check': 'extended_E1_exact_probe_model_array', 'seed': seed, 'round': round_id, 'array': name,
                                   'passed': f[name].dtype == arrays['model.'+name].dtype and np.array_equal(f[name], arrays['model.'+name])})
            if round_id == 12:
                data = np.load(package/'E1/owner.npy', allow_pickle=False)
                for client in range(5):
                    count = int(np.count_nonzero(data == client))
                    checks.append({'check': 'extended_E1_independent_exposure_update_counts', 'seed': seed, 'client': client,
                                   'passed': meta['clients'][client]['current_exposures'] == 12*count and meta['clients'][client]['updates'] == 12*((count+127)//128)})
        rejected = False
        try:
            evaluate(ROOT/'data/processed/phase3-reference74-v1/development', target, args.output/f'rejected-E1-evaluation-s{seed}')
        except ValueError:
            rejected = not (args.output/f'rejected-E1-evaluation-s{seed}').exists()
        checks.append({'check': 'incomplete_E1_only_trajectory_rejected', 'seed': seed, 'passed': rejected})
    passed = all(c['passed'] for c in checks)
    write_json(args.output/'acceptance.json', {'status': 'passed' if passed else 'failed', 'code_identity': code_identity(),
               'checks': checks, 'scope': 'Full-data old-budget DC state/evaluation parity and all three extended E1 FT probe models; no complete extended EI/DR or GPU/final qualification',
               'independent_replicates_added': 0})
    if not passed:
        raise AssertionError('V3 full-data compatibility failed')
    print({'status': 'passed', 'checks': len(checks)})


if __name__ == '__main__':
    main()
