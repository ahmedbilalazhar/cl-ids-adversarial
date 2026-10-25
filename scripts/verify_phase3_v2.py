"""Full-data v1 parity, new-version recovery and matched clean control evidence."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from src.phase3.common import ROOT, digest, load_state, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.evaluate import evaluate
from src.phase3_v2.exposure import exposure
from src.phase3_v2.protocol import Settings, code_identity
from src.phase3_v2.train import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acceptance', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--package', type=Path, default=ROOT/'data/processed/phase3-cpu-v2/s101-p000')
    args = parser.parse_args()
    accepted = read_json(args.acceptance)
    if accepted['status'] != 'passed' or accepted['code_identity'] != code_identity():
        raise ValueError('Current acceptance required')
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    expected = read_json(args.package/'preparation.json')['train_manifest_sha256']
    settings = Settings(admission='DC')
    baseline = run(args.package/'train', args.output/'DC', settings, expected)
    recovered = run(args.package/'train', args.output/'recovered', settings, expected, args.output/'DC/E1-R2.npz')
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            write_json(args.output/'integration-failure.json', checks)
            raise AssertionError(name)

    for row in recovered['checkpoints']:
        check('full-data exact recovered payload '+row['file'], digest(args.output/'DC'/row['file']) == digest(args.output/'recovered'/row['file']))
    for row in baseline['checkpoints']:
        meta, arrays, _ = read_transaction(args.output/'DC'/row['file'])
        old_meta, old_arrays = load_state(ROOT/'results/phase3-reference74-v1/reference'/row['file'])
        check('v1/v2 registered slots '+row['file'], meta['slots'] == old_meta['slots'])
        for name, value in old_arrays.items():
            if name.startswith('model.'):
                new_name = name
            else:
                prefix, field = name.split('.', 1)
                new_name = name if field in {'accepted', 'dropout'} else prefix+'.replay.'+field
            check('v1/v2 '+row['file']+' '+name, np.array_equal(value, arrays[new_name]))
        for old, new in zip(old_meta['clients'], meta['clients']):
            check('v1/v2 full retained RNG/counters '+row['file'],
                  all(old[k] == new['replay'][k] for k in ('draw', 'insert', 'seen', 'size')) and
                  all(old[k] == new[k] for k in ('updates', 'current_exposures', 'replay_exposures')))
    metrics = {}
    for arm in ('DC', 'DM', 'DQ'):
        if arm != 'DC':
            run(args.package/'train', args.output/arm, Settings(admission=arm), expected)
        metrics[arm] = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', args.output/arm, args.output/(arm+'-evaluation'))
        exposure(args.package, args.output/arm, args.output/(arm+'-exposure.json'))
    reference_metric = read_json(ROOT/'results/phase3-reference74-v1/development-evaluation/metrics.json')
    for stage in range(4):
        check(f'v1/v2 evaluator full confusion E{stage+1}', metrics['DC']['stages'][stage]['full_seen_confusion_source_code_order'] == reference_metric['stages'][stage]['full_seen_confusion_source_code_order'])
    ledgers = {arm: read_json(args.output/arm/'run.json')['ledger'] for arm in ('DC', 'DM', 'DQ')}
    for stage in range(1, 5):
        counts = [[c['admitted'] for c in next(r for r in ledgers[arm] if r['kind'] == 'admission' and r['stage'] == stage)['clients']] for arm in ('DC', 'DM', 'DQ')]
        check(f'matched whole-data current counts E{stage}', counts[0] == counts[1] == counts[2])
        for round_id in range(1, 4):
            rows = [next(r for r in ledgers[arm] if r['kind'] == 'round' and r['stage'] == stage and r['round'] == round_id) for arm in ('DC', 'DM', 'DQ')]
            check(f'matched whole-data aggregation E{stage}R{round_id}', rows[0]['weights_fp32'] == rows[1]['weights_fp32'] == rows[2]['weights_fp32'])
    write_json(args.output/'acceptance.json', {'status': 'passed', 'code_identity': code_identity(), 'checks': checks,
               'full_data_rows': 183045, 'independent_replicates': 1,
               'executions': 'Three matched clean arms at one development seed; recovery is the same logical DC run',
               'scope': 'Default untuned clean DR+DC/DM/DQ; no poisoning efficacy gate or final inference',
               'stage_macro_f1': {arm: [s['eligible_macro_f1'] for s in metric['stages']] for arm, metric in metrics.items()},
               'stage_benign_far': {arm: [s['binary_full_seen']['benign_far'] for s in metric['stages']] for arm, metric in metrics.items()}})
    print(f'{len(checks)} full-data checks passed', flush=True)


if __name__ == '__main__':
    main()
