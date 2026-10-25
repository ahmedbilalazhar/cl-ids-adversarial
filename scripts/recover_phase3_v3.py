"""Fresh-process selected-budget EI/DR continuation and full prediction parity."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from scripts.assemble_phase3_v3_recovery import assemble
from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v3.evaluate import evaluate
from src.phase3_v3.protocol import Settings, code_identity
from src.phase3_v3.train import run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--development', type=Path, default=ROOT/'results/phase3-cpu-v3/development')
    p.add_argument('--output', type=Path, default=ROOT/'results/phase3-cpu-v3/recovery')
    args = p.parse_args()
    complete = read_json(args.development/'completion.json')
    budget = complete['selected_budget']
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    checks = []
    for learner in ('EI', 'DR'):
        row = next(r for r in complete['rows'] if r['group'] == 'pilot' and r['settings']['learner'] == learner and
                   r['settings']['seed'] == 101 and [r['settings']['rounds'], r['settings']['epochs']] == budget)
        if row['status'] != 'valid':
            raise ValueError('Valid selected-budget pilot required for recovery verification')
        values = {**row['settings'], 'dose': tuple(row['settings']['dose'])}
        settings = Settings(**values).validate()
        source, suffix = Path(row['run']), args.output/(learner+'-suffix')
        package = ROOT/'data/processed/phase3-cpu-v2/s101-p000/train'
        expected = digest(package/'manifest.json')
        baseline = read_json(source/'run.json')
        if baseline['execution']['code_identity'] != code_identity():
            raise ValueError('Source identity changed')
        result = run(package, suffix, settings, expected, source/'E1-R2.npz')
        for checkpoint in result['checkpoints']:
            name = checkpoint['file']
            left, aa, a = read_transaction(source/name)
            right, bb, b = read_transaction(suffix/name)
            equal = set(aa) == set(bb) and all(aa[k].dtype == bb[k].dtype and np.array_equal(aa[k], bb[k]) for k in aa)
            checks.append({'learner': learner, 'check': 'exact_fresh_process_state', 'file': name,
                           'passed': left == right and equal and a['state_identity'] == b['state_identity'],
                           'NPZ_container_bytes_equal': digest(source/name) == digest(suffix/name)})
        checks.append({'learner': learner, 'check': 'identical_complete_ledger', 'passed': result['ledger'] == baseline['ledger']})
        collection = args.output/(learner+'-collection')
        assemble(source, suffix, package, expected, collection)
        evaluation = args.output/(learner+'-evaluation')
        metric = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', collection, evaluation)
        original = read_json(Path(row['metrics']))
        checks.append({'learner': learner, 'check': 'all_four_count_metric_stages', 'passed': metric['stages'] == original['stages']})
        for stage in range(1, 5):
            name = f'E{stage}-predictions.npz'
            with np.load(Path(row['metrics']).parent/name, allow_pickle=False) as a, np.load(evaluation/name, allow_pickle=False) as b:
                equal = set(a.files) == set(b.files) and all(a[k].dtype == b[k].dtype and np.array_equal(a[k], b[k]) for k in a.files)
            checks.append({'learner': learner, 'check': 'exact_prediction_arrays', 'stage': stage, 'passed': equal})
    passed = all(c['passed'] for c in checks)
    write_json(args.output/'acceptance.json', {'status': 'passed' if passed else 'failed', 'code_identity': code_identity(),
               'checks': checks, 'selected_budget': budget, 'independent_replicates_added': 0,
               'scope': 'Fresh-process unfiltered EI/DR full selected-budget state and assembled independent prediction parity; no final inference'})
    if not passed:
        raise AssertionError('V3 selected-budget recovered continuation differs')
    print({'status': 'passed', 'checks': len(checks)})


if __name__ == '__main__':
    main()
