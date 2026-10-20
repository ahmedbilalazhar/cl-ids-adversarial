"""Server-side robust aggregation rules (Phase-3 step 14).

All rules consume per-client DELTA dicts (client_sd - global_sd) and return
one aggregated delta dict. FedAvg is the baseline (weight-aware); the robust
rules are coordinate-wise / distance-based and UNWEIGHTED by sample count
(standard in the literature — disclosed wherever results are reported).

Rules: fedavg | trimmed_mean | median | krum | multi_krum | dynamic_trust.
dynamic_trust = reputation-weighted averaging with per-round trust updated
from L2 deviation to the coordinate-wise median (FedRDF-style dynamic
weighting; NOT a re-implementation of any single published FedRDF paper —
named and described exactly as what it is).
"""
from __future__ import annotations

from numbers import Integral, Real

import numpy as np

from src.attacks.byzantine import flatten, unflatten


def _stack(deltas: list[dict]) -> tuple[np.ndarray, list]:
    if not deltas:
        raise ValueError("aggregation requires at least one submitted delta")
    flats, layout = [], None
    for d in deltas:
        v, current_layout = flatten(d)
        if layout is not None and current_layout != layout:
            raise ValueError("submitted parameter layout mismatch")
        if not np.isfinite(v).all():
            raise ValueError("submitted deltas must be finite")
        layout = current_layout
        flats.append(v)
    return np.stack(flats, axis=0), layout


def fedavg_deltas(deltas: list[dict], weights: list[float]) -> dict:
    w = np.asarray(weights, dtype=np.float64)
    M, layout = _stack(deltas)
    if w.shape != (len(deltas),) or not np.isfinite(w).all() or (w < 0).any():
        raise ValueError("weights must be finite, nonnegative and match submissions")
    tot = w.sum()
    if not np.isfinite(tot) or tot <= 0:
        raise ValueError("weighted aggregation requires positive total weight")
    agg = (M * (w / tot)[:, None]).sum(axis=0)
    return unflatten(agg, layout)


def trimmed_mean_deltas(deltas: list[dict], trim_ratio: float = 0.2) -> dict:
    if (isinstance(trim_ratio, bool) or not isinstance(trim_ratio, Real)
            or not np.isfinite(trim_ratio) or not 0 <= trim_ratio < 0.5):
        raise ValueError("trim_ratio must be finite and in [0, 0.5)")
    M, layout = _stack(deltas)
    n = M.shape[0]
    k = int(n * trim_ratio)
    Ms = np.sort(M, axis=0)
    core = Ms[k : n - k]
    return unflatten(core.mean(axis=0), layout)


def median_deltas(deltas: list[dict]) -> dict:
    M, layout = _stack(deltas)
    return unflatten(np.median(M, axis=0), layout)


def _krum_scores(M: np.ndarray, n_mal: int) -> np.ndarray:
    n = M.shape[0]
    if isinstance(n_mal, bool) or not isinstance(n_mal, Integral) or n_mal < 0:
        raise ValueError("Krum n_mal must be a nonnegative integer")
    if n <= 2 * n_mal + 2:
        raise ValueError("Krum requires active submissions > 2*n_mal + 2")
    # Krum: score(i) = sum of squared distances to (n - f - 2) nearest others.
    nb = n - n_mal - 2
    d2 = ((M[:, None, :] - M[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(d2, np.inf)  # exclude self explicitly, including duplicate updates
    part = np.partition(d2, kth=nb - 1, axis=1)[:, :nb]
    return part.sum(axis=1)


def krum_deltas(deltas: list[dict], n_mal: int = 1) -> dict:
    M, layout = _stack(deltas)
    scores = _krum_scores(M, n_mal)
    return unflatten(M[int(np.argmin(scores))], layout)


def multi_krum_deltas(deltas: list[dict], n_mal: int = 1, m: int | None = None) -> dict:
    M, layout = _stack(deltas)
    n = M.shape[0]
    scores = _krum_scores(M, n_mal)
    if m is None:
        m = n - n_mal
    if isinstance(m, bool) or not isinstance(m, Integral) or not 1 <= m <= n:
        raise ValueError("Multi-Krum m must be an integer in [1, n]")
    best = np.argsort(scores, kind="stable")[:m]
    return unflatten(M[best].mean(axis=0), layout)


class DynamicTrust:
    """Reputation-weighted averaging. Trust t_k in [0,1] per client, updated
    per round: t_k <- (1-a)*t_k + a*exp(-||d_k - median||_2 / tau). The
    aggregated delta is trust-weighted. Trust persists across tasks within a
    run (new instance per run, reset per task optional via reset())."""

    def __init__(self, n_clients: int, alpha: float = 0.5, tau: float = 1.0):
        if isinstance(n_clients, bool) or not isinstance(n_clients, Integral) or n_clients < 1:
            raise ValueError("n_clients must be a positive integer")
        if not np.isfinite(alpha) or not 0 <= alpha <= 1:
            raise ValueError("trust alpha must be finite and in [0, 1]")
        if not np.isfinite(tau) or tau <= 0:
            raise ValueError("trust tau must be finite and positive")
        self.trust = np.full(n_clients, 1.0 / n_clients)
        self.alpha = alpha
        self.tau = tau

    def __call__(self, deltas: list[dict], weights: list[float] | None = None,
                 index: list[int] | None = None) -> dict:
        M, layout = _stack(deltas)
        med = np.median(M, axis=0)
        dev = np.sqrt(((M - med) ** 2).sum(axis=1))
        scale = self.tau * max(1e-12, float(np.median(dev) + 1e-12))
        # Subtracting the minimum leaves normalized trust unchanged and
        # prevents every exponential underflowing for a very small tau.
        inst = np.exp(-(dev - dev.min()) / scale)
        # `index` maps each submitted delta to its client id so trust
        # persists per client when inactive submissions are excluded.
        idx = np.asarray(index if index is not None else list(range(len(deltas))))
        if len(idx) != len(deltas) or len(set(idx.tolist())) != len(deltas):
            raise ValueError("trust index must map each delta to a unique client")
        if int(idx.max(initial=-1)) >= len(self.trust) or int(idx.min(initial=0)) < 0:
            raise ValueError("trust index out of range")
        self.trust[idx] = (1 - self.alpha) * self.trust[idx] + self.alpha * (inst / inst.sum())
        w = self.trust[idx] / self.trust[idx].sum()
        return unflatten((M * w[:, None]).sum(axis=0), layout)

    def reset(self) -> None:
        self.trust = np.full_like(self.trust, 1.0 / len(self.trust))
