"""Scientific invariants for the local CPU supplement."""
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'phase3-implementation/src'))
sys.path.insert(0, str(ROOT / 'scripts'))
import p3intervention as L
from phase3_evidence import confusion_metrics, signed_rank_enumeration, holm


def test_eligible_bank_excludes_rare_false_positive_rows_but_keeps_wrong_predictions():
    c = np.zeros((16, 16), int)
    c[0, 0] = 8; c[0, 4] = 2; c[4, 4] = 6; c[4, 0] = 3; c[4, 9] = 1
    c[9, 4] = 100
    m = confusion_metrics(c, [0, 4])
    assert m['hulk_recall'] == .6 and m['hulk_asr'] == .3
    assert m['classes'][4]['precision'] == .75
    assert m['classes'][4]['f1'] == pytest.approx(12 / 18)
    assert m['accuracy'] == .7
    assert m['binary']['accuracy'] == .75
    assert m['binary']['recall'] == .7
    assert m['binary']['precision'] == pytest.approx(7/9)


def test_zero_tie_and_all_one_direction_signed_rank():
    assert signed_rank_enumeration([0, 0, 0])['rank_biserial'] is None
    assert signed_rank_enumeration([1, 1, 1])['p'] == .25
    assert signed_rank_enumeration([0, 1, -1])['p'] == 1.
    assert signed_rank_enumeration([-1, -2, -3])['rank_biserial'] == -1.
    assert np.allclose(holm([.01, .03, .04]), [.03, .06, .06])


def test_deletion_preserves_field_alignment_rng_and_historical_proposals():
    def make():
        b = L.Buffer(8, 'reservoir', np.random.default_rng(11), 'cpu')
        b.size = 8; b.seen = 100
        for name in ('x', 'y', 'z', 'w'):
            a = getattr(b, name)
            for i in range(8): a[i] = i
        b.poison[[1, 3, 6]] = True
        return b
    for mode in ('oracle_purge', 'random_delete'):
        b = make(); state = str(b.rng.bit_generator.state)
        result = L.delete_memory(b, mode, np.random.default_rng(6))
        assert b.size == 5 and b.seen == 100 and result['removed'] == 3
        assert str(b.rng.bit_generator.state) == state
        for row, old in enumerate(result['keep_slots']):
            for name in ('x', 'y', 'z', 'w'): assert (getattr(b, name)[row] == old).all()
        if mode == 'oracle_purge': assert not b.poison.any()
        b.insert(torch.zeros((2, 74)), torch.zeros(2, dtype=torch.long), torch.zeros((2, 8)), 8, np.zeros(2, bool))
        assert b.size == 7 and b.seen == 102


def test_result_validation_rejects_wrong_device():
    spec = importlib.util.spec_from_file_location('cpu_study', ROOT / 'scripts/run_phase3_cpu_study.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    with pytest.raises(AssertionError): module.validate_result({'device': 'cuda'})


def test_instrumentation_preserves_training_and_intervention_prefix():
    import p3lib as original
    from dataclasses import replace
    rng = np.random.default_rng(22)
    groups = [[0, 7, 12], [0, 3, 4, 5, 6, 8], [0, 9, 10, 13, 14, 15], [0, 1, 2, 11]]
    stages = []; arrival = {}
    for t, codes in enumerate(groups, 1):
        for c in codes: arrival.setdefault(c, t)
        y = np.tile(np.repeat(codes, 12), 5); n = len(y)
        stages.append(dict(x=rng.normal(size=(n, 74)).astype('float32'), y=y,
            ids=np.arange(n) + t * 10000, owner=np.repeat(np.arange(5), len(codes) * 12)))
    dev = dict(x=rng.normal(size=(160, 74)).astype('float32'), y=np.repeat(np.arange(16), 10))
    tax = dict(arrival=arrival, eligible=set(range(16)))
    cfg = L.Cfg(learner='DR', rounds=1, mem=30, batch=128, n_att=5, dose=.5)
    ref = L.run(cfg, stages, dev, tax)
    prior = original.run(original.Cfg(learner='DR', rounds=1, mem=30, batch=128, n_att=5, dose=.5), stages, dev, tax)
    assert ref['stages'] == prior['stages']
    assert ref['summary'] == prior['summary']
    for mode in ('oracle_purge', 'random_delete'):
        r = L.run(replace(cfg, intervention=mode), stages, dev, tax)
        assert ref['pre_intervention_sha256'] == r['pre_intervention_sha256']
        assert ref['stages'][:2] == r['stages'][:2]
        assert sum(x['removed'] for x in r['interventions']) > 0
