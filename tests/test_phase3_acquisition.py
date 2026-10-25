"""Independent arithmetic and equivalence fixtures for exploratory E1 probes."""
from __future__ import annotations

import math
import unittest

import numpy as np
import torch

from scripts.diagnose_phase3_acquisition import (
    CONFIG,
    class_weights,
    local_update,
    objective_loss,
    readout,
    validate_config,
)
from src.phase3.common import read_json
from src.phase3.model import ReferenceMLP
from src.phase3.reference import snapshot
from src.phase3_v2.data import StageInput
from src.phase3_v2.learning import client_state, train_client
from src.phase3_v2.protocol import Settings, configure_runtime


class AcquisitionProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_runtime()

    def test_inverse_frequency_mean_one_and_equal_class_mass(self):
        targets = np.array([0]*6+[1]*3+[2], dtype=np.int64)
        weights = class_weights(targets, 3)
        expected = torch.tensor([5/9, 10/9, 10/3])
        torch.testing.assert_close(weights, expected, rtol=1e-6, atol=1e-7)
        self.assertAlmostEqual(float(weights[targets].mean()), 1, places=6)
        for slot, n in enumerate((6, 3, 1)):
            self.assertAlmostEqual(float(weights[slot])*n, 10/3, places=6)
        with self.assertRaises(ValueError):
            class_weights(np.zeros(4, dtype=np.int64), 3)

    def test_weighted_loss_and_analytic_logit_gradient(self):
        logits = torch.tensor([[0., math.log(3)], [math.log(4), 0.]], requires_grad=True)
        labels = torch.tensor([1, 1])
        weights = torch.tensor([.5, 2.])
        loss = objective_loss(logits, labels, weights)
        self.assertAlmostEqual(float(loss.detach()), -math.log(.75)-math.log(.2), places=6)
        loss.backward()
        # Independent dCE/dlogit=(softmax-onehot)*class_weight/batch_count.
        torch.testing.assert_close(logits.grad, torch.tensor([[.25, -.25], [.8, -.8]]), rtol=1e-6, atol=1e-7)
        self.assertAlmostEqual(float(objective_loss(logits.detach(), labels)), (-math.log(.75)-math.log(.2))/2, places=6)

    def test_natural_local_exact_v2_and_inactive(self):
        n = 137
        stream = np.random.default_rng(61)
        data = StageInput(1, stream.normal(0, .2, (n, 74)).astype('<f4'),
                          np.resize(np.array([0, 7, 12], dtype='<i8'), n), np.arange(n, dtype='<u8'), np.zeros(n, dtype='i1'))
        model = ReferenceMLP(3, 101)
        settings = Settings(learner='FT')
        client = client_state(settings, 0)
        client.accepted = np.arange(n, dtype='<i8')
        initial_rng = client.dropout.copy()
        expected, accounting = train_client(snapshot(model), model, client, data, [0, 7, 12], settings, 1, 0)
        local, dropout, observed = local_update(model, data, 101, 0, 1, initial_rng)
        self.assertTrue(all(torch.equal(v, snapshot(local)[k]) for k, v in expected.items()))
        self.assertTrue(np.array_equal(dropout, client.dropout))
        self.assertEqual(observed['optimizer_updates'], accounting['optimizer_updates'])
        self.assertEqual(observed['current_exposures'], accounting['current_exposures'])
        inactive, state, row = local_update(model, data, 101, 1, 1, initial_rng)
        self.assertIsNone(inactive)
        self.assertTrue(np.array_equal(initial_rng, state))
        self.assertEqual(row['optimizer_updates'], 0)

    def test_fixed_scope_and_readout_does_not_advance_rng(self):
        config = read_json(CONFIG)
        validate_config(config)
        for changed in ({'seeds': [101]}, {'rounds': 24}, {'final_test_access': True}, {'stage': 2}):
            with self.assertRaises(ValueError):
                validate_config({**config, **changed})
        model = ReferenceMLP(3, 101)
        model.train()
        state = torch.get_rng_state().clone()
        result = readout(model, np.zeros((3, 74), dtype='<f4'), np.array([0, 7, 12]))
        self.assertTrue(torch.equal(state, torch.get_rng_state()))
        self.assertTrue(model.training)
        self.assertEqual(result['rows'], 3)
        self.assertEqual(sum(map(sum, result['confusion'])), 3)


if __name__ == '__main__':
    unittest.main()
