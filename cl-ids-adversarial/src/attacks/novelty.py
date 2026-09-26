from __future__ import annotations

import numpy as np
import torch

from src.models.mlp import Autoencoder


def maximize_recon_error(
    ae: Autoencoder,
    X: np.ndarray,
    budget: float,
    eps: float = 0.5,
    steps: int = 5,
    seed: int = 42,
    device: str = "cpu",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    ae.eval()
    X = X.copy()
    n = len(X)
    k = int(round(n * budget))
    if k <= 0:
        return X, np.zeros(n, dtype=bool), np.zeros(n, dtype=np.float32)

    idx = rng.choice(n, size=k, replace=False)
    xb = torch.from_numpy(X[idx]).float().to(device)
    xb.requires_grad_(True)

    for _ in range(steps):
        err = ae.recon_error(xb).sum()
        ae.zero_grad()
        if xb.grad is not None:
            xb.grad.zero_()
        err.backward()
        with torch.no_grad():
            grad = xb.grad.clone()
            xb = xb + eps * torch.sign(grad)
            xb = torch.clamp(xb, X[idx].min(), X[idx].max())
            xb.requires_grad_(True)

    out = X.copy()
    out[idx] = xb.detach().cpu().numpy()
    poisoned = np.zeros(n, dtype=bool)
    poisoned[idx] = True
    with torch.no_grad():
        scores = ae.recon_error(torch.from_numpy(out).float().to(device)).cpu().numpy()
    return out, poisoned, scores.astype(np.float32)


def novelty_poison_stream(
    ae: Autoencoder,
    X: np.ndarray,
    y: np.ndarray,
    budget: float,
    unknown_label: int,
    threshold: float | None = None,
    eps: float = 0.5,
    steps: int = 5,
    seed: int = 42,
    device: str = "cpu",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    X_new, poisoned, scores = maximize_recon_error(
        ae, X, budget=budget, eps=eps, steps=steps, seed=seed, device=device
    )
    y_new = y.copy()
    if threshold is None:
        threshold = float(np.quantile(scores[~poisoned], 0.95)) if (~poisoned).any() else float(np.median(scores))
    y_new[poisoned & (scores >= threshold)] = unknown_label
    return X_new, y_new, poisoned


def _recon(ae: Autoencoder, X: np.ndarray, device: str = "cpu", batch: int = 4096) -> np.ndarray:
    ae.eval()
    out: list[np.ndarray] = []
    with torch.no_grad():
        for i in range(0, len(X), batch):
            xb = torch.from_numpy(X[i : i + batch]).float().to(device)
            out.append(ae.recon_error(xb).cpu().numpy())
    return np.concatenate(out).astype(np.float32) if out else np.zeros(0, dtype=np.float32)


def anchor_novelty_poison(
    ae: Autoencoder,
    X: np.ndarray,
    y: np.ndarray,
    budget: float,
    unknown_label: int,
    threshold: float,
    noise: float = 0.05,
    seed: int = 42,
    device: str = "cpu",
    benign_label: int = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Cluster-neighborhood novelty poisoning (Option 2-A, stronger variant).

    Anchors = real attack training samples ranked by AE reconstruction error
    (highest first). Crafted poison = anchor copies + small per-feature noise,
    injected over benign rows only, so crafted flows sit next to real attacks in
    recon space. Goal: HDBSCAN assigns real novel attacks and poison to the same
    cluster; if poison_frac >= 0.5 the cluster is fictitious and real attacks are
    absorbed into a manufactured class (vs. recon-max poison, which lands far
    from real attacks and yields absorbed_attack_rate = 0).

    Falls back to recon-max poisoning when the task has no attack samples.
    """
    rng = np.random.RandomState(seed)
    n = len(X)
    k = int(round(n * budget))
    if k <= 0:
        return X.copy(), y.copy(), np.zeros(n, dtype=bool)

    attack_idx = np.where(y != benign_label)[0]
    if len(attack_idx) == 0:
        return novelty_poison_stream(
            ae, X, y, budget=budget, unknown_label=unknown_label, threshold=threshold, seed=seed, device=device
        )

    scores_atk = _recon(ae, X[attack_idx], device=device)
    order = attack_idx[np.argsort(-scores_atk)]
    n_anchor = int(max(15, min(len(order), max(k // 4, 15))))
    anchors = X[order[:n_anchor]]

    cand = np.where(y == benign_label)[0]
    if len(cand) == 0:
        cand = np.arange(n)
    replace = len(cand) >= k
    idx = rng.choice(cand, size=k, replace=not replace)
    pick = rng.randint(0, len(anchors), size=len(idx))
    std = X.std(axis=0)
    std[std == 0] = 1.0
    craft = anchors[pick] + noise * std * rng.randn(len(idx), X.shape[1])

    out = X.copy()
    out[idx] = craft
    poisoned = np.zeros(n, dtype=bool)
    poisoned[idx] = True
    sc = _recon(ae, craft, device=device)
    y_new = y.copy()
    y_new[idx[sc >= threshold]] = unknown_label
    return out, y_new, poisoned
