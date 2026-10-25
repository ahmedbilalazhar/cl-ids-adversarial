"""Fresh-process full-data DR and EI continuations from completed clean runs."""
from __future__ import annotations

import numpy as np

from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.protocol import Settings
from src.phase3_v2.train import run


def main():
    base = ROOT/'results/phase3-cpu-v2'
    package = ROOT/'data/processed/phase3-cpu-v2/s101-p000/train'
    expected = digest(package/'manifest.json')
    for learner, source, settings in (
        ('DR', base/'integration/DC', Settings(admission='DC')),
        ('EI', base/'development/executions/pilot-13-EI-s101-r3e1/train', Settings(learner='EI')),
    ):
        target = base/f'full-data-{learner}-recovered'
        result = read_json(target/'run.json') if target.exists() else run(package, target, settings, expected, source/'E1-R2.npz')
        first = read_json(source/'run.json')
        checks = []
        for row in result['checkpoints']:
            left = read_transaction(source/row['file'], first['execution'])
            right = read_transaction(target/row['file'], result['execution'])
            arrays_equal = set(left[1]) == set(right[1]) and all(
                left[1][key].dtype == right[1][key].dtype and np.array_equal(left[1][key], right[1][key]) for key in left[1])
            checks.append({'file': row['file'], 'metadata_exact': left[0] == right[0],
                           'typed_arrays_exact': arrays_equal,
                           'logical_state_identity_exact': left[2]['state_identity'] == right[2]['state_identity'],
                           'container_bytes_equal': digest(source/row['file']) == digest(target/row['file'])})
        passed = len(checks) == 10 and all(c['metadata_exact'] and c['typed_arrays_exact'] and
                                          c['logical_state_identity_exact'] for c in checks) and result['ledger'] == first['ledger']
        write_json(base/f'full-data-{learner}-recovery.json', {'status': 'passed' if passed else 'failed', 'checks': checks,
                   'ledger_identical': result['ledger'] == first['ledger'], 'execution': result['execution'],
                   'scope': 'Same logical full selected-data trajectory, fresh process relative to the original; metadata and every typed retained array/importance/anchor/sample ID/dropout/RNG checked exactly. NPZ ZIP container bytes are reported separately because timestamps are non-scientific.',
                   'independent_replicates_added': 0})
        if not passed:
            raise AssertionError('Full-data '+learner+' continuation differs')


if __name__ == '__main__':
    main()
