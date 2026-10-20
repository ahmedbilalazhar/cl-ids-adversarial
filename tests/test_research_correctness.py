"""Counterexamples for retention, replay and federated aggregation correctness."""
import numpy as np
import pytest
import torch
from torch import nn

from src.cl.derpp import DERpp
from src.cl.ewc import EWC
from src.federated.fedavg import _aggregate_updates
from src.federated.robust import (
    DynamicTrust,
    _krum_scores,
    fedavg_deltas,
    median_deltas,
    multi_krum_deltas,
)
from src.models.mlp import TabularMLP
from src.models.tabular_attention import TabularTransformer


@pytest.mark.parametrize("model_type", [TabularMLP, TabularTransformer])
def test_expanding_head_preserves_precision_mode_and_old_predictions(model_type):
    model = model_type(3, 2).double().eval()
    x = torch.ones(2, 3, dtype=torch.float64)
    with torch.no_grad():
        before = model(x).clone()
    old_device = model.classifier.weight.device
    model.expand_head(4)
    assert model.classifier.weight.dtype == torch.float64
    assert model.classifier.weight.device == old_device
    assert not model.classifier.training
    with torch.no_grad():
        torch.testing.assert_close(model(x)[:, :2], before)


def test_derpp_can_train_with_old_and_new_logit_widths():
    method = DERpp(TabularMLP(3, 3), buffer_size=10)
    method.buffer_x = [np.ones(3, dtype=np.float32), np.zeros(3, dtype=np.float32)]
    method.buffer_y = [0, 1]
    method.buffer_logits = [np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0])]
    loss = method.observe(torch.ones(2, 3), torch.tensor([1, 2]))
    assert np.isfinite(loss)


def test_derpp_logit_loss_does_not_constrain_unobserved_classes():
    predictions = torch.tensor([[2.0, 4.0, 999.0], [2.0, 4.0, 6.0]], requires_grad=True)
    targets = torch.tensor([[1.0, 2.0, 0.0], [1.0, 2.0, 3.0]])
    mask = torch.tensor([[True, True, False], [True, True, True]])
    loss = DERpp._replay_logit_loss(predictions, targets, mask)
    expected = ((1.0 + 4.0) / 2 + (1.0 + 4.0 + 9.0) / 3) / 2
    assert float(loss.detach()) == pytest.approx(expected)
    loss.backward()
    assert predictions.grad[0, 2] == 0
    assert predictions.grad[1, 2] != 0


class _DropoutHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.dropout = nn.Dropout(1.0)
        self.classifier = nn.Linear(2, 2, bias=False)
        with torch.no_grad():
            self.classifier.weight.copy_(torch.eye(2))

    def forward(self, x):
        return self.classifier(self.dropout(x))


def test_derpp_stores_inference_logits_and_restores_training_mode():
    method = DERpp(_DropoutHead(), lr=0.0, buffer_size=10)
    x = torch.tensor([[1.0, 2.0]])
    method.observe(x, torch.tensor([0]))
    np.testing.assert_array_equal(method.buffer_logits[0], [1.0, 2.0])
    assert method.model.training
    assert method.model.dropout.training


def test_ewc_keeps_old_head_importance_and_anchor_on_growth():
    method = EWC(TabularMLP(3, 2), ewc_lambda=4.0)
    method.fisher = {
        "classifier.weight": torch.ones_like(method.model.classifier.weight),
        "classifier.bias": torch.ones_like(method.model.classifier.bias),
    }
    method.anchor = {
        "classifier.weight": method.model.classifier.weight.detach().clone(),
        "classifier.bias": method.model.classifier.bias.detach().clone(),
    }
    with torch.no_grad():
        method.model.classifier.weight.add_(0.5)
        method.model.classifier.bias.add_(0.5)
    expected = 0.5 * 4.0 * 0.25 * sum(v.numel() for v in method.fisher.values())
    method._maybe_expand(4)
    loss = method.extra_loss(torch.ones(1, 3), torch.tensor([0]))
    assert float(loss.detach()) == pytest.approx(expected)
    assert method.fisher["classifier.weight"].shape[0] == 4
    assert torch.count_nonzero(method.fisher["classifier.weight"][2:]) == 0


def test_krum_scores_match_explicit_nonself_nearest_neighbors():
    rng = np.random.RandomState(19)
    for _ in range(20):
        vectors = rng.randn(9, 3)
        expected = []
        for i, vector in enumerate(vectors):
            others = np.delete(vectors, i, axis=0)
            expected.append(np.sort(((others - vector) ** 2).sum(axis=1))[:5].sum())
        np.testing.assert_allclose(_krum_scores(vectors, 2), expected)


def _aggregate(aggregator, active):
    global_sd = {"w": torch.tensor([3.0])}
    sds = [{"w": torch.tensor([3.0 + i])} for i in range(5)]
    return _aggregate_updates(
        sds, [1.0 if i in active else 0.0 for i in range(5)], global_sd, active,
        aggregator=aggregator, trim_ratio=0.2, n_mal=1,
        up_method=None, up_attack={}, mal_ids=[0], trust=None, device="cpu",
    )


def test_fedavg_all_inactive_preserves_global_weights():
    result, excluded = _aggregate("fedavg", [])
    torch.testing.assert_close(result["w"], torch.tensor([3.0]))
    assert excluded == []  # weighted FedAvg accounts for inactivity with zero weights


@pytest.mark.parametrize("aggregator", ["krum", "multi_krum"])
def test_krum_rejects_insufficient_active_submissions(aggregator):
    with pytest.raises(ValueError, match="Krum requires"):
        _aggregate(aggregator, [0, 1, 2, 3])


def test_robust_aggregation_rejects_different_parameter_layouts():
    deltas = [
        {"a": torch.ones(2), "b": torch.ones(1)},
        {"a": torch.ones(1), "b": torch.ones(2)},
    ]
    with pytest.raises(ValueError, match="layout"):
        median_deltas(deltas)


def test_multi_krum_rejects_zero_selection_instead_of_using_default():
    deltas = [{"w": torch.tensor([float(i)])} for i in range(5)]
    with pytest.raises(ValueError, match="m must"):
        multi_krum_deltas(deltas, n_mal=1, m=0)


def test_zero_weight_deltas_are_not_silently_averaged():
    with pytest.raises(ValueError, match="positive total weight"):
        fedavg_deltas([{"w": torch.tensor([100.0])}], [0.0])


def test_dynamic_trust_stays_finite_when_all_unshifted_scores_underflow():
    trust = DynamicTrust(2, alpha=1.0, tau=1e-4)
    result = trust([{"w": torch.tensor([0.0])}, {"w": torch.tensor([2.0])}])
    torch.testing.assert_close(result["w"], torch.tensor([1.0]))
    assert np.isfinite(trust.trust).all()


def test_lie_reference_population_excludes_inactive_honest_clients():
    global_sd = {"w": torch.tensor([0.0])}
    sds = [{"w": torch.tensor([999.0])}, {"w": torch.tensor([10.0])}]
    sds += [{"w": torch.tensor([0.0])} for _ in range(3)]
    result, _ = _aggregate_updates(
        sds, [1.0, 1.0, 0.0, 0.0, 0.0], global_sd, [0, 1],
        aggregator="fedavg", trim_ratio=0.2, n_mal=1,
        up_method="lie", up_attack={"z": 0.0}, mal_ids=[0], trust=None, device="cpu",
    )
    torch.testing.assert_close(result["w"], torch.tensor([10.0]))


@pytest.mark.parametrize("federated", [False, True])
def test_both_runners_forward_derpp_beta(monkeypatch, federated):
    from src import runner
    from src.federated import fedavg

    module = fedavg if federated else runner
    constructed = []

    class CaptureDERpp(DERpp):
        def __init__(self, *args, **kwargs):
            constructed.append(kwargs.copy())
            super().__init__(*args, **kwargs)

    rng = np.random.RandomState(3)
    x = rng.randn(8, 3).astype(np.float32)
    y = np.array([0, 1] * 4, dtype=np.int64)
    task = {"X_train": x, "y_train": y, "X_test": x.copy(), "y_test": y.copy()}
    monkeypatch.setattr(module, "load_or_build_tasks", lambda cfg: ([task], {"Benign": 0, "A": 1}))
    monkeypatch.setattr(module, "METHODS", dict(module.METHODS, derpp=CaptureDERpp))
    cfg = {"cl_method": "derpp", "seed": 2, "beta": 0.123, "alpha": 0.25,
           "epochs_per_task": 1, "batch_size": 4, "feature_names": ["a", "b", "c"]}
    if federated:
        cfg["fed"] = {"n_clients": 2, "local_epochs": 1}
        module.run_federated(cfg)
    else:
        module.run(cfg)
    assert constructed
    assert all(params.get("beta") == 0.123 for params in constructed)
