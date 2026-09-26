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
            nxt = int(round(props[k] * len(c_idx))) if k < n_clients - 1 else len(c_idx) - prev
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
