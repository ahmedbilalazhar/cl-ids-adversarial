"""Extended-budget supplied-label corruption/state interactions, on tiny inputs."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.data import StageInput
from src.phase3_v2.prepare import corrupt
from src.phase3_v2.train import Simulator
from src.phase3_v3.protocol import BUDGETS, Settings, code_identity, configure_runtime


def stages():
    result = {}
    for stage, codes in enumerate(((0, 7, 12), (0, 3, 4), (0, 10, 13), (0, 1, 2)), 1):
        labels = (np.array([0]*80+[4]*50+[3]*20+[0]*20+[4]*20+[3]*20, dtype='<i8') if stage == 2 else
                  np.resize(np.asarray(codes, dtype='<i8'), 210))
        result[stage] = StageInput(stage, np.random.default_rng(5170+stage).uniform(0, .5, (210, 74)).astype('<f4'),
                                   labels, np.arange(stage*1000, stage*1000+210, dtype='<u8'),
                                   np.repeat(np.arange(5, dtype='i1'), (150, 60, 0, 0, 0)))
    return result


class ExtendedPoison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_runtime()

    def test_frozen_v3_identity(self):
        self.assertEqual(code_identity(), '38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c')

    def test_unfiltered_dose_pair_streams_samples_and_poisoned_boundary_recovery(self):
        clean = stages()
        data = clean[2]
        reference = data.y.copy()
        supplied, audit = corrupt(data.y, data.ids, data.owner, 101, 2, (1, 2))
        attacked = audit['attacked_client']
        eligible = int(np.count_nonzero((reference == 4) & (data.owner == attacked)))
        self.assertEqual(int(np.count_nonzero(supplied != reference)), eligible//2)
        np.testing.assert_array_equal(data.y, reference)
        poison = {**clean, 2: StageInput(2, data.x.copy(), supplied, data.ids.copy(), data.owner.copy())}
        with tempfile.TemporaryDirectory() as td:
            for r, e in BUDGETS:
                for learner in ('DR', 'EI'):
                    prefix = Path(td)/f'r{r}e{e}{learner}'
                    a, b = prefix/'clean', prefix/'poison'
                    Simulator(Settings(learner=learner, rounds=r, epochs=e), clean.__getitem__, {'fixture': 'clean'}).execute(a)
                    engine = Simulator(Settings(learner=learner, rounds=r, epochs=e, dose=(1, 2)), poison.__getitem__, {'fixture': 'poison'})
                    original = engine.execute(b)
                    continued = engine.execute(prefix/'recovered', b/f'E2-R{r}.npz')
                    self.assertEqual(original['ledger'], continued['ledger'])
                    self.assertEqual(original['final_model_sha256'], continued['final_model_sha256'])
                    expected = {c['file']: c['state_identity'] for c in original['checkpoints']}
                    for checkpoint in continued['checkpoints']:
                        self.assertEqual(checkpoint['state_identity'], expected[checkpoint['file']])
                    for stage in range(1, 5):
                        ma, aa, _ = read_transaction(a/f'E{stage}-R{r}.npz')
                        mb, bb, _ = read_transaction(b/f'E{stage}-R{r}.npz')
                        for client in range(5):
                            np.testing.assert_array_equal(aa[f'client{client}.dropout'], bb[f'client{client}.dropout'])
                            if learner == 'DR':
                                np.testing.assert_array_equal(aa[f'client{client}.replay.ids'], bb[f'client{client}.replay.ids'])
                                self.assertEqual(ma['clients'][client]['replay']['draw'], mb['clients'][client]['replay']['draw'])
                                self.assertEqual(ma['clients'][client]['replay']['insert'], mb['clients'][client]['replay']['insert'])
                                self.assertEqual(ma['clients'][client]['replay_counts'], mb['clients'][client]['replay_counts'])
                            else:
                                self.assertEqual(ma['clients'][client]['importance_samples'], mb['clients'][client]['importance_samples'])

    def test_poisoned_matched_controls_counts_weights_and_stream_positions(self):
        fixture = stages()
        data = fixture[2]
        supplied, _ = corrupt(data.y, data.ids, data.owner, 101, 2, (1, 2))
        fixture[2] = StageInput(2, data.x.copy(), supplied, data.ids.copy(), data.owner.copy())
        expected = []
        for client in range(5):
            local = supplied[data.owner == client]
            benign = int(np.count_nonzero(local == 0))
            expected.append(len(local)-(benign//4 if benign >= 20 else 0))
        with tempfile.TemporaryDirectory() as td:
            for r, e in BUDGETS:
                results, folders = {}, {}
                for arm in ('DM', 'DC', 'DQ'):
                    folders[arm] = Path(td)/f'r{r}e{e}{arm}'
                    results[arm] = Simulator(Settings(admission=arm, rounds=r, epochs=e, dose=(1, 2)), fixture.__getitem__, {'fixture': arm}).execute(folders[arm])
                    admission = next(x for x in results[arm]['ledger'] if x['kind'] == 'admission' and x['stage'] == 2)
                    self.assertEqual([c['admitted'] for c in admission['clients']], expected)
                    for row in results[arm]['ledger']:
                        if row['kind'] == 'round' and row['stage'] == 2:
                            self.assertEqual(row['weights_fp32'], [float(np.float32(n/sum(expected))) for n in expected])
                for stage in range(1, 5):
                    for round_id in range(1, r+1):
                        parsed = {arm: read_transaction(folders[arm]/f'E{stage}-R{round_id}.npz')[:2] for arm in folders}
                        for arm in ('DM', 'DQ'):
                            a, aa = parsed['DC']
                            b, bb = parsed[arm]
                            for client in range(5):
                                self.assertEqual(a['clients'][client]['updates'], b['clients'][client]['updates'])
                                self.assertEqual(a['clients'][client]['current_exposures'], b['clients'][client]['current_exposures'])
                                self.assertEqual(a['clients'][client]['replay'], b['clients'][client]['replay'])
                                np.testing.assert_array_equal(aa[f'client{client}.dropout'], bb[f'client{client}.dropout'])


if __name__ == '__main__':
    unittest.main()
