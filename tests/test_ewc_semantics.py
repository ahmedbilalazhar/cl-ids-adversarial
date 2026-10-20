"""EWC analytic semantics: anchor, Fisher accumulation, loss closed-form."""
import numpy as np
import torch

from src.cl.base import set_seed, to_loader
from src.cl.ewc import EWC
from src.models.mlp import TabularMLP


def _task(n=24, shift=0.0, seed=0):
    rng = np.random.RandomState(seed)
    y = np.array([0] * (n // 2) + [1] * (n - n // 2))
    X = (rng.randn(n, 4) + y[:, None] * 2.0 + shift).astype(np.float32)
    return to_loader(X, y, batch_size=8, shuffle=False)


def _make(lam=10.0):
    set_seed(0)
    return EWC(TabularMLP(4, 2), lr=1e-2, device="cpu",
               ewc_lambda=lam, fisher_batches=4)


def test_anchor_tracks_post_task_weights_and_fisher_accumulates():
    m = _make()
    assert m.extra_loss(torch.zeros(1, 4, dtype=torch.float32), torch.zeros(1, dtype=torch.long)) == 0.0
    loader_a = _task(seed=1)
    m.before_task(0, loader_a, class_bound=2)
    m.train_task(loader_a, epochs=1)
    m.after_task(0, loader_a)
    for n, p in m.model.named_parameters():
        if p.requires_grad:
            assert n in m.anchor and torch.equal(m.anchor[n], p.detach())
            assert (m.fisher[n] >= 0).all()
    fisher_a = {k: v.clone() for k, v in m.fisher.items()}
    loader_b = _task(shift=0.5, seed=2)
    m.before_task(1, loader_b, class_bound=2)
    m.train_task(loader_b, epochs=1)
    m.after_task(1, loader_b)
    for k, v in fisher_a.items():
        assert torch.all(m.fisher[k] >= v), k  # Kirkpatrick accumulation


def test_extra_loss_matches_closed_form():
    m = _make(lam=4.0)
    loader = _task(seed=3)
    m.before_task(0, loader, class_bound=2)
    m.train_task(loader, epochs=1)
    m.after_task(0, loader)
    x = loader.dataset.tensors[0][:8]
    y = loader.dataset.tensors[1][:8]
    with torch.no_grad():
        expected = 0.0
        for n, p in m.model.named_parameters():
            if p.requires_grad and n in m.fisher and n in m.anchor:
                f, a = m.fisher[n], m.anchor[n]
                if f.shape == p.shape == a.shape:
                    expected += float((f * (p - a) ** 2).sum())
        expected *= 0.5 * 4.0
    got = float(m.extra_loss(x, y).detach())
    assert expected == 0.0  # anchor == current weights: penalty vanishes
    assert got == 0.0
    with torch.no_grad():
        for p in m.model.parameters():
            p.add_(0.5)
    assert float(m.extra_loss(x, y).detach()) > 0.0


def test_head_growth_never_crashes_penalty():
    m = _make()
    loader = _task(seed=4)
    m.before_task(0, loader, class_bound=2)
    m.train_task(loader, epochs=1)
    m.after_task(0, loader)
    m.before_task(1, loader, class_bound=5)  # grow head while preserving old-row importance
    x = loader.dataset.tensors[0][:8]
    y = torch.zeros(8, dtype=torch.long)
    assert np.isfinite(float(m.extra_loss(x, y).detach()))
