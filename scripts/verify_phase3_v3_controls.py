"""Selected-budget full-data matched clean DM/DC/DQ state and evaluation checks."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.exposure import exposure
from src.phase3_v3.evaluate import evaluate
from src.phase3_v3.protocol import Settings, code_identity
from src.phase3_v3.train import run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--development', type=Path, default=ROOT/'results/phase3-cpu-v3/development')
    p.add_argument('--selection', type=Path, default=ROOT/'results/phase3-cpu-v3/cost-correction/selection.json')
    p.add_argument('--output', type=Path, default=ROOT/'results/phase3-cpu-v3/controls')
    args = p.parse_args()
    completion, selection = read_json(args.development/'completion.json'), read_json(args.selection)
    if selection['status'] != 'complete' or selection['code_identity'] != code_identity():
        raise ValueError('Resolved timing disposition and current source required')
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    selected = selection['learners']['DR']['selected']
    r, e = completion['selected_budget']
    config = selected['settings_without_seed'] if selected else Settings(rounds=r, epochs=e).__dict__
    package = ROOT/'data/processed/phase3-cpu-v2/s101-p000'
    expected = digest(package/'train/manifest.json')
    results, metrics, checks = {}, {}, []
    for arm in ('DM', 'DC', 'DQ'):
        settings = Settings(**{**config, 'seed': 101, 'admission': arm, 'dose': (0, 1)}).validate()
        results[arm] = run(package/'train', args.output/arm, settings, expected)
        metrics[arm] = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', args.output/arm, args.output/(arm+'-evaluation'))
        exposure(package, args.output/arm, args.output/(arm+'-exposure.json'))
    for stage in range(1, 5):
        admissions = {arm: next(t for t in result['ledger'] if t['kind'] == 'admission' and t['stage'] == stage) for arm, result in results.items()}
        for round_id in range(1, r+1):
            states = {arm: read_transaction(args.output/arm/f'E{stage}-R{round_id}.npz')[:2] for arm in results}
            ledgers = {arm: next(t for t in result['ledger'] if t['kind'] == 'round' and t['stage'] == stage and t['round'] == round_id) for arm, result in results.items()}
            for arm in ('DM', 'DQ'):
                checks.append({'stage': stage, 'round': round_id, 'comparison': 'DC/'+arm, 'check': 'distinct_count_FP32_aggregation_weights',
                               'passed': ledgers['DC']['weights_fp32'] == ledgers[arm]['weights_fp32']})
                a, aa = states['DC']
                b, bb = states[arm]
                for client in range(5):
                    ca, cb = ledgers['DC']['clients'][client], ledgers[arm]['clients'][client]
                    same = all(ca.get(k, 0) == cb.get(k, 0) for k in ('admitted', 'optimizer_updates', 'current_exposures', 'proposals'))
                    same = same and admissions['DC']['clients'][client]['admitted'] == admissions[arm]['clients'][client]['admitted']
                    checks.append({'stage': stage, 'round': round_id, 'client': client, 'comparison': 'DC/'+arm,
                                   'check': 'matched_current_work_and_first_pass_proposals', 'passed': same})
                    same = all(a['clients'][client]['replay'][k] == b['clients'][client]['replay'][k] for k in ('draw', 'insert', 'size', 'seen'))
                    same = same and np.array_equal(aa[f'client{client}.dropout'], bb[f'client{client}.dropout'])
                    checks.append({'stage': stage, 'round': round_id, 'client': client, 'comparison': 'DC/'+arm,
                                   'check': 'named_stream_positions_and_dropout', 'passed': same})
                if stage == 1:
                    checks.append({'stage': stage, 'round': round_id, 'comparison': 'DC/'+arm, 'check': 'all_typed_E1_arrays_exact_filters_off',
                                   'passed': set(aa) == set(bb) and all(aa[k].dtype == bb[k].dtype and np.array_equal(aa[k], bb[k]) for k in aa)})
    passed = all(c['passed'] for c in checks)
    write_json(args.output/'acceptance.json', {'status': 'passed' if passed else 'failed', 'code_identity': code_identity(),
               'checks': checks, 'selection_sha256': digest(args.selection), 'settings_source': 'selected_feasible_DR' if selected else 'fixed_untuned_DR_defaults',
               'selected_budget': [r, e], 'seed': 101, 'full_control_trajectories': 3,
               'stage_macro_f1': {arm: [s['eligible_macro_f1'] for s in metric['stages']] for arm, metric in metrics.items()},
               'stage_benign_far': {arm: [s['binary_full_seen']['benign_far'] for s in metric['stages']] for arm, metric in metrics.items()},
               'scope': 'One-seed matched clean controls with inherited/fixed DR settings, all stage outcomes retained. Stream positions match; IDs/models may diverge after E1.',
               'final_test_accessed': False, 'gpu_dispatchable': False})
    if not passed:
        raise AssertionError('Matched v3 full-data controls differ in required counts or stream positions')
    print({'status': 'passed', 'checks': len(checks)})


if __name__ == '__main__':
    main()
