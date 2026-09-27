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

import numpy as np
import torch

from src.attacks.byzantine import flatten, unflatten


def _stack(deltas: list[dict]) -> tuple[np.ndarray, list]:
    flats, layout = [], None
    for d in deltas:
        v, layout = flatten(d)
        flats.append(v)
    return np.stack(flats, axis=0), layout


def fedavg_deltas(deltas: list[dict], weights: list[float]) -> dict:
    w = np.asarray(weights, dtype=np.float64)
    M, layout = _stack(deltas)
    tot = w.sum()
    agg = (M * (w / tot)[:, None]).sum(axis=0) if tot > 0 else M.mean(axis=0)
    return unflatten(agg, layout)


def trimmed_mean_deltas(deltas: list[dict], trim_ratio: float = 0.2) -> dict:
    M, layout = _stack(deltas)
    n = M.shape[0]
    k = int(n * trim_ratio)
    Ms = np.sort(M, axis=0)
    core = Ms[k : n - k] if n - 2 * k > 0 else Ms
    return unflatten(core.mean(axis=0), layout)


def median_deltas(deltas: list[dict]) -> dict:
    M, layout = _stack(deltas)
    return unflatten(np.median(M, axis=0), layout)


def _krum_scores(M: np.ndarray, n_mal: int) -> np.ndarray:
    n = M.shape[0]
    # Krum: score(i) = sum of squared distances to (n - f - 2) nearest others.
    nb = max(1, n - n_mal - 2)
    d2 = ((M[:, None, :] - M[None, :, :]) ** 2).sum(axis=2)
    part = np.partition(d2, kth=min(nb, n - 1), axis=1)[:, 1 : nb + 1]
    return part.sum(axis=1)


def krum_deltas(deltas: list[dict], n_mal: int = 1) -> dict:
    M, layout = _stack(deltas)
    scores = _krum_scores(M, n_mal)
    return unflatten(M[int(np.argmin(scores))], layout)


def multi_krum_deltas(deltas: list[dict], n_mal: int = 1, m: int | None = None) -> dict:
    M, layout = _stack(deltas)
    n = M.shape[0]
    m = m or max(1, n - n_mal)
    scores = _krum_scores(M, n_mal)
    best = np.argsort(scores, kind="stable")[:m]
    return unflatten(M[best].mean(axis=0), layout)


class DynamicTrust:
    """Reputation-weighted averaging. Trust t_k in [0,1] per client, updated
    per round: t_k <- (1-a)*t_k + a*exp(-||d_k - median||_2 / tau). The
    aggregated delta is trust-weighted. Trust persists across tasks within a
    run (new instance per run, reset per task optional via reset())."""

    def __init__(self, n_clients: int, alpha: float = 0.5, tau: float = 1.0):
        self.trust = np.full(n_clients, 1.0 / n_clients)
        self.alpha = alpha
        self.tau = tau

    def __call__(self, deltas: list[dict], weights: list[float] | None = None) -> dict:
        M, layout = _stack(deltas)
        med = np.median(M, axis=0)
        dev = np.sqrt(((M - med) ** 2).sum(axis=1))
        scale = self.tau * max(1e-12, float(np.median(dev) + 1e-12))
        inst = np.exp(-dev / scale)
        self.trust = (1 - self.alpha) * self.trust + self.alpha * (inst / inst.sum())
        w = self.trust / self.trust.sum()
        return unflatten((M * w[:, None]).sum(axis=0), layout)

    def reset(self) -> None:
        self.trust = np.full_like(self.trust, 1.0 / len(self.trust))
