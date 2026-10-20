from __future__ import annotations

import numpy as np


def dirichlet_partition(
    y: np.ndarray,
    n_clients: int = 5,
    alpha: float = 0.5,
    seed: int = 42,
) -> list[np.ndarray]:
    """Split sample indices into non-IID client shards (label skew).

    For each class, its indices are dealt across clients with proportions
    drawn from Dirichlet(alpha). Small alpha -> extreme skew (near
    single-class clients); alpha=0.5 is the standard non-IID default.
    Tiny classes (fewer samples than clients) land on a subset of clients.
    Deterministic in `seed`.
    """
    rng = np.random.RandomState(seed)
    shards: list[list[int]] = [[] for _ in range(n_clients)]
    for c in np.unique(y):
        c_idx = np.where(y == c)[0]
        rng.shuffle(c_idx)
        props = rng.dirichlet([alpha] * n_clients)
        prev = 0
        for k in range(n_clients):
            nxt = round(props[k] * len(c_idx)) if k < n_clients - 1 else len(c_idx) - prev
            nxt = max(0, min(nxt, len(c_idx) - prev))
            shards[k].extend(c_idx[prev : prev + nxt].tolist())
            prev += nxt
        if prev < len(c_idx):  # rounding remainder -> last client
            shards[-1].extend(c_idx[prev:].tolist())
    out = []
    for s in shards:
        a = np.asarray(s, dtype=np.int64)
        rng.shuffle(a)
        out.append(a)
    return out


def _splitmix64(x: np.ndarray) -> np.ndarray:
    """Deterministic 64-bit mixer (no Python-hash salt nondeterminism)."""
    x = np.asarray(x, dtype=np.int64).astype(np.uint64)
    x = x + np.uint64(0x9E3779B97F4A7C15)
    x = (x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return x ^ (x >> np.uint64(31))


def stable_partition(ids: np.ndarray, n_clients: int = 5) -> list[np.ndarray]:
    """Site-identity proxy: assign each sample by stable hash of its source id.

    The same source row lands on the same client in every task and every
    rerun, independent of seeds or task order. This imposes NO label skew
    (approximately IID), so it must never be compared against Dirichlet
    shards as a like-for-like non-IID control — it isolates client-identity
    stability, not skew. Covers every index exactly once.
    """
    if not isinstance(n_clients, int) or isinstance(n_clients, bool) or n_clients < 2:
        raise ValueError("n_clients must be an integer >= 2")
    ids = np.asarray(ids).ravel()
    buckets = (_splitmix64(ids) % np.uint64(n_clients)).astype(np.int64)
    return [np.flatnonzero(buckets == k) for k in range(n_clients)]
