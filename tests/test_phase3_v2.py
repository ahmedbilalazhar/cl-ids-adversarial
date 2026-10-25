"""Focused v2 semantics. Expected values are independent tiny arithmetic fixtures."""
from __future__ import annotations

import copy
import math
import tempfile
import unittest
from itertools import pairwise
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch
from torch import nn

from src.phase3.common import (
    canonical,
    digest,
    encode_rng,
    read_json,
    rng,
    write_json,
)
from src.phase3.model import ReferenceMLP
from src.phase3.reference import insert_batch, snapshot
from src.phase3_v2.checkpoint import read_transaction, restore_rng, strict_json, unpack
from src.phase3_v2.data import StageInput, verify_files
from src.phase3_v2.development import clean_gates, pilot_settings, select_budget, tuning_settings
from src.phase3_v2.evaluate import rational_macro, stage_counts
from src.phase3_v2.learning import (
    admit,
    aggregate,
    choose_admission,
    client_state,
    commit_importance,
    current_order,
    dark_loss,
    empirical_importance,
    expand_importance,
    importance_reference,
    penalty,
    train_client,
)
from src.phase3_v2.prepare import corrupt
from src.phase3_v2.protocol import Settings, configure_runtime
from src.phase3_v2.train import Simulator


def fixture(stage=1, counts=(13, 9, 0, 7, 0), codes=(0, 7, 12)):
    n = sum(counts)
    gen = np.random.default_rng(124 + stage)
    x = gen.uniform(-.2, .2, (n, 74)).astype('<f4')
    y = np.asarray([codes[i % len(codes)] for i in range(n)], dtype='<i8')
    ids = np.arange(stage*10000, stage*10000+n, dtype='<u8')
    owner = np.repeat(np.arange(5, dtype='i1'), counts)
    return StageInput(stage, x, y, ids, owner)


def four_stages():
    return {s: fixture(s, codes=c) for s, c in enumerate(((0, 7, 12), (0, 3, 4), (0, 10, 13), (0, 1, 2)), 1)}


class Phase3V2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_runtime()

    def test_head_initialization_independent_uniform_and_expansion(self):
        model = ReferenceMLP(3, 101)
        raw = np.random.Generator(np.random.PCG64(np.random.SeedSequence([1, 5, 101, 1])))
        seed = int(raw.integers(0, 2**63, dtype=np.int64))
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            expected = torch.empty(3, 64).uniform_(-math.sqrt(6/67), math.sqrt(6/67))
        self.assertTrue(torch.equal(model.classifier.weight, expected))
        self.assertTrue(torch.equal(model.classifier.bias, torch.zeros(3)))
        old = snapshot(model)
        model.expand(8, 2, 101)
        self.assertTrue(torch.equal(old['classifier.weight'], model.classifier.weight[:3]))
        self.assertTrue(torch.equal(old['classifier.bias'], model.classifier.bias[:3]))
        self.assertTrue(all(p.requires_grad for p in model.parameters()))
        self.assertEqual(sum(p.numel() for p in ReferenceMLP(16, 101).parameters()), 18896)
        self.assertLessEqual(float(model.classifier.weight[3:].abs().max()), math.sqrt(6/69))

    def test_data_isolation_and_readonly(self):
        data = fixture()
        self.assertEqual(set(data.__dataclass_fields__), {'stage', 'x', 'y', 'ids', 'owner'})
        for a in (data.x, data.y, data.ids, data.owner):
            with self.assertRaises(ValueError):
                a.flat[0] = 99
        with self.assertRaises(ValueError):
            StageInput(1, data.x.astype('f8'), data.y, data.ids, data.owner)
        with self.assertRaises(ValueError):
            StageInput(1, data.x, data.y, np.zeros(len(data.y), dtype='<u8'), data.owner)

    def test_package_rejects_extras_missing_and_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            np.save(p/'x.npy', np.zeros(2))
            write_json(p/'manifest.json', {})
            expected = {'x.npy': digest(p/'x.npy')}
            verify_files(p, expected, {'x.npy'})
            (p/'poison.npy').write_bytes(b'forbidden')
            with self.assertRaises(ValueError):
                verify_files(p, expected, {'x.npy'})
            (p/'poison.npy').unlink()
            (p/'x.npy').write_bytes(b'corrupted')
            with self.assertRaises(ValueError):
                verify_files(p, expected, {'x.npy'})

    def test_supplied_only_registration(self):
        # Hidden clean code4 is deliberately absent from the supplied E2 union.
        stages = four_stages()
        d = stages[2]
        supplied = d.y.copy()
        supplied[supplied == 4] = 0
        stages[2] = StageInput(2, d.x.copy(), supplied, d.ids.copy(), d.owner.copy())
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'run'
            result = Simulator(Settings(learner='FT'), stages.__getitem__, {'fixture': 1}).execute(out)
            meta, _, _ = read_transaction(out/'E2-R3.npz')
            self.assertNotIn(4, meta['slots'])
            self.assertIn(3, meta['slots'])
            self.assertEqual(result['next_cursor'], [5, 1])

    def test_independent_aggregation_arithmetic(self):
        broadcast = {'a': torch.zeros(2)}
        updates = [{'a': torch.tensor([2., 6.])}, None, {'a': torch.tensor([10., -2.])}]
        combined, weights = aggregate(broadcast, updates, [1, 0, 3])
        self.assertEqual(weights, [.25, 0., .75])
        self.assertTrue(torch.equal(combined['a'], torch.tensor([8., 0.])))
        with self.assertRaises(ValueError):
            aggregate(broadcast, [None]*3, [0]*3)

    def test_inactive_client_never_updates_or_draws(self):
        settings = Settings()
        client = client_state(settings, 2)
        # Even a nonempty replay buffer cannot activate an empty current client.
        insert_batch(client.replay, np.ones((1, 74), dtype='f4'), np.array([0]), np.array([123], dtype='u8'), np.zeros((1, 3), dtype='f4'), 3)
        before = canonical(encode_rng(client.replay['draw']))
        dropout = client.dropout.copy()
        model = ReferenceMLP(3, 101)
        update, row = train_client(snapshot(model), model, client, fixture(), [0, 7, 12], settings, 1, 2)
        self.assertIsNone(update)
        self.assertTrue(row['inactive'])
        self.assertEqual(client.updates, 0)
        self.assertEqual(before, canonical(encode_rng(client.replay['draw'])))
        np.testing.assert_array_equal(dropout, client.dropout)

    def test_broadcast_and_optimizer_reset(self):
        settings = Settings(learner='FT')
        model, data = ReferenceMLP(3, 101), fixture()
        broadcast = snapshot(model)
        clients = [client_state(settings, 0) for _ in range(2)]
        for c in clients:
            c.accepted = np.flatnonzero(data.owner == 0)
        outputs = [train_client(broadcast, model, c, data, [0, 7, 12], settings, 1, 0) for c in clients]
        self.assertTrue(all(torch.equal(outputs[0][0][k], outputs[1][0][k]) for k in broadcast))
        self.assertTrue(all(torch.equal(broadcast[k], model.state_dict()[k]) for k in broadcast))
        self.assertTrue(all(row['adam_reset'] for _, row in outputs))
        self.assertIsNone(clients[0].replay)

    def test_full_pool_order_then_subsequence(self):
        data = fixture(counts=(40, 0, 0, 0, 0))
        selected = np.array([0, 4, 7, 11, 16, 39], dtype='i8')
        raw_generator = np.random.Generator(np.random.PCG64(np.random.SeedSequence([1, 6, 101, 0, 1, 2, 1])))
        expected = [i for i in raw_generator.permutation(40) if i in set(selected)]
        np.testing.assert_array_equal(current_order(data, selected, 101, 0, 2, 1), expected)

    def test_quota_rounding_ties_and_matched_controls(self):
        y = np.array([0]*21 + [4]*9 + [3]*7, dtype='<i8')
        data = StageInput(2, np.zeros((37, 74), dtype='<f4'), y, np.arange(37, dtype='<u8'), np.zeros(37, dtype='i1'))
        # Independent arithmetic: ceil(.75*21)=16 plus all9 new and7 small.
        selections = {}
        scores = np.zeros(37, dtype='f4')
        scores[21:] = -1  # DM can change composition but still has32 rows.
        for arm in ('DM', 'DC', 'DQ'):
            selected, _rows = choose_admission(data, scores, {4}, Settings(admission=arm))
            self.assertEqual([len(a) for a in selected], [32, 0, 0, 0, 0])
            selections[arm] = selected[0]
        np.testing.assert_array_equal(selections['DC'], np.r_[np.arange(16), np.arange(21, 37)])
        self.assertEqual(np.count_nonzero(y[selections['DQ']] == 0), 16)
        self.assertEqual(np.count_nonzero(y[selections['DQ']] == 4), 9)
        for n, expected in [(19, 19), (20, 15), (22, 17), (23, 18), (24, 18)]:
            data_n = StageInput(2, np.zeros((n, 74), dtype='<f4'), np.zeros(n, dtype='<i8'), np.arange(n, dtype='<u8'), np.zeros(n, dtype='i1'))
            selected, _ = choose_admission(data_n, np.zeros(n, dtype='f4'), set(), Settings(admission='DC'))
            self.assertEqual(len(selected[0]), expected)

    def test_admission_nonfinite_and_all_inactive_rejected(self):
        with self.assertRaises(FloatingPointError):
            choose_admission(fixture(), np.full(29, np.nan), set(), Settings())
        empty = fixture(counts=(0, 0, 0, 0, 0))
        with self.assertRaises(ValueError):
            choose_admission(empty, np.empty(0), set(), Settings())

    def test_filters_off_e1_and_frozen_once(self):
        data, model = fixture(counts=(30, 0, 0, 0, 0)), ReferenceMLP(3, 101)
        settings = Settings(admission='DC')
        clients = [client_state(settings, i) for i in range(5)]
        ledger = []
        admit(model, data, [0, 7, 12], {7, 12}, clients, settings, ledger)
        locked = clients[0].accepted.copy()
        self.assertEqual(len(locked), 30)
        train_client(snapshot(model), model, clients[0], data, [0, 7, 12], settings, 1, 0)
        np.testing.assert_array_equal(locked, clients[0].accepted)
        self.assertEqual(len(ledger), 1)

    def test_dark_mask_before_square_and_per_record_normalization(self):
        # row1: (2^2+4^2)/2=10; row2: 6^2/1=36; mean=23.
        predicted = torch.tensor([[2., 4., 1e30], [6., 1e30, -1e30]], requires_grad=True)
        teacher = torch.zeros((2, 3))
        loss = dark_loss(predicted, teacher, torch.tensor([2, 1]))
        self.assertEqual(float(loss), 23.)
        loss.backward()
        self.assertTrue(torch.equal(predicted.grad, torch.tensor([[1., 2., 0.], [6., 0., 0.]])))
        with self.assertRaises(ValueError):
            dark_loss(predicted, teacher, torch.tensor([0, 4]))

    def test_teacher_timing_modes_and_insertion_after_update(self):
        events = []
        class Recorded(ReferenceMLP):
            def forward(self, x):
                events.append(('forward', self.training, torch.is_grad_enabled(), len(x)))
                return super().forward(x)
        settings, data = Settings(), fixture(counts=(129, 0, 0, 0, 0))
        client, model = client_state(settings, 0), Recorded(3, 101)
        client.accepted = np.arange(129, dtype='i8')
        real_step, real_insert = torch.optim.Adam.step, insert_batch
        def stepped(opt, *a, **kw):
            events.append(('step',))
            return real_step(opt, *a, **kw)
        def inserted(*a, **kw):
            events.append(('insert',))
            return real_insert(*a, **kw)
        with patch.object(torch.optim.Adam, 'step', stepped), patch('src.phase3_v2.learning.insert_batch', inserted):
            _, row = train_client(snapshot(model), model, client, data, [0, 7, 12], settings, 1, 0)
        self.assertEqual(events, [('forward', False, False, 128), ('forward', True, True, 128), ('step',), ('insert',),
                                  ('forward', False, False, 1), ('forward', True, True, 1), ('forward', True, True, 128),
                                  ('forward', False, True, 128), ('step',), ('insert',)])
        self.assertEqual(row['current_exposures'], 129)
        self.assertEqual(row['replay_exposures'], 128)
        self.assertEqual(row['full_replay_with_short_current_batches'], 1)

    def test_teacher_values_are_pre_update(self):
        settings, data = Settings(), fixture(counts=(8, 0, 0, 0, 0))
        model, client = ReferenceMLP(3, 101), client_state(settings, 0)
        client.accepted = np.arange(8, dtype='i8')
        order = current_order(data, client.accepted, 101, 0, 1, 1)
        model.eval()
        with torch.no_grad():
            before = model(torch.from_numpy(data.x[order].copy())).numpy()
        trained, _ = train_client(snapshot(model), model, client, data, [0, 7, 12], settings, 1, 0)
        np.testing.assert_array_equal(client.replay['z'][:8, :3], before)
        self.assertTrue(any(not torch.equal(trained[k], model.state_dict()[k]) for k in trained))

    def test_reservoir_sequential_independent_algorithm_r(self):
        settings = Settings()
        memory = client_state(settings, 0).replay
        expected = list(range(500))
        independent = np.random.Generator(np.random.PCG64(np.random.SeedSequence([1, 8, 101, 0])))
        for seen in range(501, 701):
            slot = int(independent.integers(0, seen))
            if slot < 500:
                expected[slot] = seen-1
        insert_batch(memory, np.zeros((700, 74), dtype='f4'), np.zeros(700, dtype='i8'), np.arange(700, dtype='u8'), np.zeros((700, 3), dtype='f4'), 3)
        np.testing.assert_array_equal(memory['ids'], np.array(expected, dtype='u8'))
        self.assertEqual(memory['seen'], 700)
        self.assertEqual(memory['size'], 500)
        self.assertNotEqual(encode_rng(memory['draw']), encode_rng(memory['insert']))

    def test_first_pass_only_across_epochs_and_rounds(self):
        settings = Settings(rounds=1, epochs=3)
        data, model = fixture(counts=(10, 0, 0, 0, 0)), ReferenceMLP(3, 101)
        client = client_state(settings, 0)
        client.accepted = np.arange(10, dtype='i8')
        _, row = train_client(snapshot(model), model, client, data, [0, 7, 12], settings, 1, 0)
        self.assertEqual(row['proposals'], 10)
        self.assertEqual(row['current_exposures'], 30)
        self.assertEqual(row['optimizer_updates'], 3)
        _, row = train_client(snapshot(model), model, client, data, [0, 7, 12], settings, 2, 0)
        self.assertEqual(row['proposals'], 0)
        self.assertEqual(client.replay['seen'], 10)

    def test_ei_analytic_gradients_not_square_of_mean(self):
        model = nn.Linear(2, 2)
        with torch.no_grad():
            model.weight.zero_()
            model.bias.zero_()
        x = torch.tensor([[2., 0.], [0., 4.]])
        labels = torch.tensor([0, 1])
        importance = empirical_importance(model, x, labels, chunk=1)
        # Per-record gradient outer products: +/-x/2; average squares.
        self.assertTrue(torch.equal(importance['weight'], torch.tensor([[.5, 2.], [.5, 2.]])))
        self.assertTrue(torch.equal(importance['bias'], torch.tensor([.25, .25])))
        mean_loss = nn.functional.cross_entropy(model(x), labels)
        mean_grad = torch.autograd.grad(mean_loss, model.bias)[0]
        self.assertTrue(torch.equal(mean_grad.square(), torch.zeros(2)))

    def test_ei_vectorized_independent_reference_tolerance(self):
        # Tolerance frozen in decisions before either outcome: FP32 reduction-order error.
        model = ReferenceMLP(3, 101)
        data = fixture(counts=(70, 0, 0, 0, 0))
        x = torch.from_numpy(data.x.copy())
        y = torch.from_numpy(data.targets([0, 7, 12]))
        before = snapshot(model)
        optimized = empirical_importance(model, x, y)
        reference = importance_reference(model, x, y)
        for key in optimized:
            torch.testing.assert_close(optimized[key], reference[key], rtol=2e-5, atol=2e-7)
        self.assertTrue(all(torch.equal(before[k], model.state_dict()[k]) for k in before))
        self.assertTrue(model.training)

    def test_ei_penalty_scale_and_new_coordinates(self):
        settings = Settings(learner='EI')
        client, model = client_state(settings, 0), ReferenceMLP(3, 101)
        expand_importance(client, model)
        client.importance['classifier.bias'][0] = 3
        with torch.no_grad():
            model.classifier.bias[0] += 2
        # lambda/2 * I * delta^2 = 10/2*3*4=60.
        self.assertEqual(float(penalty(model, client, 10)), 60.)
        old = client.importance['classifier.bias'].clone()
        model.expand(8, 2, 101)
        expand_importance(client, model)
        self.assertTrue(torch.equal(client.importance['classifier.bias'][:3], old))
        self.assertTrue(torch.equal(client.importance['classifier.bias'][3:], torch.zeros(5)))
        self.assertEqual(float(penalty(model, client, 10)), 60.)

    def test_ei_stage_anchor_fixed_and_inactive_commit(self):
        settings, model, data = Settings(learner='EI'), ReferenceMLP(3, 101), fixture()
        clients = [client_state(settings, i) for i in range(5)]
        for i, c in enumerate(clients):
            expand_importance(c, model)
            c.accepted = np.flatnonzero(data.owner == i)
        clients[2].importance['classifier.bias'][0] = .125
        prior, anchor = copy.deepcopy(clients[0].importance), copy.deepcopy(clients[0].anchor)
        train_client(snapshot(model), model, clients[0], data, [0, 7, 12], settings, 1, 0)
        self.assertTrue(all(torch.equal(v, clients[0].importance[k]) for k, v in prior.items()))
        self.assertTrue(all(torch.equal(v, clients[0].anchor[k]) for k, v in anchor.items()))
        with torch.no_grad():
            model.classifier.bias.add_(.5)
        ledger = []
        commit_importance(model, clients, data, [0, 7, 12], settings, ledger)
        self.assertEqual(float(clients[2].importance['classifier.bias'][0]), .125)
        self.assertTrue(torch.equal(clients[2].anchor['classifier.bias'], model.classifier.bias))
        self.assertEqual([r['count'] for r in ledger[0]['clients']], [13, 9, 0, 7, 0])

    def test_ei_exact_sample_limit(self):
        settings, model, data = Settings(learner='EI'), ReferenceMLP(3, 101), fixture(counts=(1025, 0, 0, 0, 0))
        clients = [client_state(settings, i) for i in range(5)]
        for i, c in enumerate(clients):
            expand_importance(c, model)
            c.accepted = np.flatnonzero(data.owner == i)
        commit_importance(model, clients, data, [0, 7, 12], settings, [])
        sample = clients[0].importance_samples['1']['ids']
        self.assertEqual(len(sample), 1024)
        self.assertEqual(len(set(sample)), 1024)

    def test_corruption_integer_nested_scope_reference_immutable(self):
        labels = np.array([4]*31+[0]*9+[3]*4, dtype='i8')
        ids = np.arange(44, dtype='u8') + np.uint64(2**63)
        owners = np.zeros(44, dtype='i1')
        original = labels.copy()
        sets = []
        for dose, count in [((0, 1), 0), ((1, 10), 3), ((3, 10), 9), ((1, 2), 15)]:
            supplied, audit = corrupt(labels, ids, owners, 101, 2, dose)
            sets.append(set(np.flatnonzero(labels != supplied)))
            self.assertEqual(len(sets[-1]), count)
            self.assertEqual(audit['eligible_clients'], [0])
            self.assertTrue(np.all(supplied[list(sets[-1])] == 0))
            self.assertTrue(all(i < 31 for i in sets[-1]))
        self.assertTrue(all(a <= b for a, b in pairwise(sets)))
        np.testing.assert_array_equal(labels, original)
        for stage in (1, 3, 4):
            supplied, audit = corrupt(labels, ids, owners, 101, stage, (1, 2))
            np.testing.assert_array_equal(supplied, original)
            self.assertEqual(audit['poison_ids'], [])

    def test_rng_lossless_cached_uint32_and_large_state(self):
        original = rng(8, 101, 2)
        original.integers(0, 17, dtype=np.uint32)
        encoded = encode_rng(original)
        self.assertTrue(all(isinstance(v, str) for v in encoded['state'].values()))
        restored = restore_rng(strict_json(canonical(encoded)))
        np.testing.assert_array_equal(original.integers(0, 2**63, size=100), restored.integers(0, 2**63, size=100))
        bad = copy.deepcopy(encoded)
        bad['state']['state'] = int(bad['state']['state'])
        with self.assertRaises(ValueError):
            restore_rng(bad)
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(ValueError):
                strict_json(text)

    def test_evaluator_full_head_banks_denominators_missingness(self):
        names = [str(i) for i in range(16)]
        arrival = [1]*16
        arrival[4] = 2
        arrival[7] = 2
        # Rare8 is active but excluded from eligible bank; predictions to8 remain errors/alerts.
        y = np.array([0, 0, 4, 4, 4, 8, 7])
        predicted = np.array([8, 0, 4, 0, 8, 0, 7])
        row = stage_counts(2, [0, 4, 8, 7], y, predicted, [0, 4, 7], names, arrival, np.array([1, 2, 1, 2, 2, 1, 2]), np.array([0, 1, 0, 0, 0, 0, 0], dtype=bool))
        self.assertEqual(row['eligible_seen_bank_rows'], 6)
        self.assertEqual(row['full_seen_bank_rows'], 7)
        self.assertEqual(row['hulk_partition'], {'support': 3, 'predicted_benign': 1, 'predicted_hulk': 1, 'predicted_other_attack': 1})
        self.assertEqual(row['binary_full_seen']['benign_far'], .5)
        self.assertEqual(row['binary_full_seen']['tp'], 3)
        self.assertEqual(row['binary_full_seen']['fn'], 2)
        self.assertEqual(row['eligible_classes'][0]['f1'], .5)
        self.assertEqual(row['eligible_classes'][1]['f1'], .5)
        rare = row['full_seen_classes'][2]
        self.assertEqual(rare['f1'], 0.)
        self.assertEqual(row['benign_provenance_descriptive'][0]['alerts'], 1)

    def test_evaluator_zero_prediction_precision_na_f1_zero(self):
        from src.phase3.evaluate import counts_for
        _, classes = counts_for(np.array([0, 7, 7]), np.array([0, 0, 0]), [0, 7, 8], [str(i) for i in range(16)])
        self.assertIsNone(classes[1]['precision'])
        self.assertEqual(classes[1]['f1'], 0.)
        self.assertIsNone(classes[2]['f1'])
        self.assertEqual(rational_macro(classes[:2]), __import__('fractions').Fraction(1, 4))

    def test_full_head_argmax_keeps_rare_outputs_and_benign_ties(self):
        model = ReferenceMLP(3, 101)
        with torch.no_grad():
            for p in model.parameters():
                p.zero_()
            model.classifier.bias[:2] = 1
            logits = model(torch.zeros(1, 74))
            self.assertEqual(int(logits.argmax(dim=1)), 0)
            model.classifier.bias[2] = 2
            self.assertEqual(int(model(torch.zeros(1, 74)).argmax(dim=1)), 2)

    def test_exact_recovered_continuation_all_methods(self):
        stages = four_stages()
        with tempfile.TemporaryDirectory() as td:
            for learner, admission in [('FT', 'NONE'), ('EI', 'NONE'), ('DR', 'NONE'), ('DR', 'DM'), ('DR', 'DC'), ('DR', 'DQ')]:
                settings = Settings(learner=learner, admission=admission)
                engine = Simulator(settings, stages.__getitem__, {'fixture': learner+admission})
                full, recovered = Path(td)/(learner+admission), Path(td)/(learner+admission+'-recovered')
                first = engine.execute(full)
                second = engine.execute(recovered, full/'E1-R2.npz')
                self.assertEqual(len(second['checkpoints']), 10)
                for row in second['checkpoints']:
                    self.assertEqual(digest(full/row['file']), digest(recovered/row['file']))
                self.assertEqual(first['ledger'], second['ledger'])
                self.assertEqual(first['final_model_sha256'], second['final_model_sha256'])

    def test_checkpoint_incompatible_incomplete_and_corrupt_rejected(self):
        stages, settings = four_stages(), Settings(learner='EI')
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'run'
            engine = Simulator(settings, stages.__getitem__, {'fixture': 'EI'})
            engine.execute(out, stop_after_commits=3)
            path = out/'E1-R3.npz'
            meta, arrays, _ = read_transaction(path)
            with self.assertRaises(ValueError):
                read_transaction(path, {'fixture': 'wrong'})
            for missing in ('client0.dropout', 'client0.anchor.classifier.bias', 'client0.importance.classifier.bias'):
                broken = dict(arrays)
                broken.pop(missing)
                with self.assertRaises((ValueError, KeyError)):
                    unpack(copy.deepcopy(meta), broken, settings, stages.__getitem__)
            broken_meta = copy.deepcopy(meta)
            broken_meta['stage'] = 3
            with self.assertRaises(ValueError):
                unpack(broken_meta, arrays, settings, stages.__getitem__)
            broken_meta = copy.deepcopy(meta)
            broken_meta['clients'][0]['updates'] += 1
            with self.assertRaises(ValueError):
                unpack(broken_meta, arrays, settings, stages.__getitem__)
            broken = {k: v.copy() for k, v in arrays.items()}
            broken['client0.anchor.classifier.bias'][0] += 1
            with self.assertRaises(ValueError):
                unpack(copy.deepcopy(meta), broken, settings, stages.__getitem__)
            broken_meta = copy.deepcopy(meta)
            broken_meta['clients'][0]['importance_samples']['1']['ids'][0] = '999999999'
            with self.assertRaises(ValueError):
                unpack(broken_meta, arrays, settings, stages.__getitem__)
            with path.open('ab') as f:
                f.write(b'corrupted')
            with self.assertRaises(ValueError):
                read_transaction(path)
            path.with_suffix('.commit.json').unlink()
            with self.assertRaises(FileNotFoundError):
                read_transaction(path)

    def test_final_seed_and_invalid_runtime_settings_sealed(self):
        for settings in (Settings(seed=1), Settings(dose=(3, 5)), Settings(learner='FT', admission='DC'), Settings(learning_rate=float('nan'))):
            with self.assertRaises(ValueError):
                settings.validate()

    def test_development_grid_and_exact_budget_ties(self):
        from dataclasses import asdict
        self.assertEqual(len(pilot_settings()), 18)
        self.assertEqual(len(tuning_settings((1, 3))), 60)
        rows = [{'settings': asdict(s), 'status': 'valid', 'score_exact': ['1', '2']} for s in pilot_settings()]
        selected, _ = select_budget(rows)
        self.assertEqual(selected, (1, 3))
        rows[0]['status'] = 'invalid'
        selected, _ = select_budget(rows)
        self.assertEqual(selected, (3, 1))
        rows[0]['status'] = 'valid'
        rows[-1]['score_exact'] = ['5000000000000001', '10000000000000000']
        selected, _ = select_budget(rows)
        self.assertEqual(selected, (3, 1))

    def test_development_gates_are_per_family_and_require_three_seeds(self):
        metrics = [{'settings': {'seed': seed}, 'stages': [
            {'eligible_classes': [{'code': 7, 'tp': 5, 'fn': 5, 'support': 10}, {'code': 12, 'tp': 5, 'fn': 5, 'support': 10}]},
            {'eligible_classes': [{'code': 4, 'tp': 7, 'fn': 3, 'support': 10}]}]} for seed in (101, 102, 103)]
        self.assertTrue(clean_gates(metrics)['passed'])
        metrics[0]['stages'][0]['eligible_classes'][1]['tp'] = 0
        metrics[0]['stages'][0]['eligible_classes'][1]['fn'] = 10
        self.assertFalse(clean_gates(metrics)['passed'])
        with self.assertRaises(ValueError):
            clean_gates(metrics[:2])

    def test_unfiltered_pairing_buffer_and_importance_ids_across_doses(self):
        stages = {s: fixture(s, counts=(39, 0, 0, 0, 0), codes=c) for s, c in enumerate(
            ((0, 7, 12), (0, 3, 4), (0, 10, 13), (0, 1, 2)), 1)}
        poisoned = dict(stages)
        data = stages[2]
        supplied, _ = corrupt(data.y, data.ids, data.owner, 101, 2, (1, 2))
        poisoned[2] = StageInput(2, data.x.copy(), supplied, data.ids.copy(), data.owner.copy())
        with tempfile.TemporaryDirectory() as td:
            for learner in ('DR', 'EI'):
                clean_dir, poison_dir = Path(td)/(learner+'clean'), Path(td)/(learner+'poison')
                Simulator(Settings(learner=learner), stages.__getitem__, {'fixture': 'clean'}).execute(clean_dir)
                Simulator(Settings(learner=learner, dose=(1, 2)), poisoned.__getitem__, {'fixture': 'poison'}).execute(poison_dir)
                for stage in range(1, 5):
                    a, aa, _ = read_transaction(clean_dir/f'E{stage}-R3.npz')
                    b, ab, _ = read_transaction(poison_dir/f'E{stage}-R3.npz')
                    for i in range(5):
                        if learner == 'DR':
                            np.testing.assert_array_equal(aa[f'client{i}.replay.ids'], ab[f'client{i}.replay.ids'])
                            self.assertEqual(a['clients'][i]['replay']['draw'], b['clients'][i]['replay']['draw'])
                            self.assertEqual(a['clients'][i]['replay']['insert'], b['clients'][i]['replay']['insert'])
                            self.assertEqual(a['clients'][i]['replay_counts'], b['clients'][i]['replay_counts'])
                        else:
                            self.assertEqual(a['clients'][i]['importance_samples'], b['clients'][i]['importance_samples'])

    def test_v1_code_identity_preserved(self):
        from src.phase3.reference import code_identity as v1_identity
        self.assertEqual(v1_identity(), read_json(Path('docs/phase3-reference/evidence/source-code-manifest.json'))['code_identity'])


if __name__ == '__main__':
    unittest.main()
