from __future__ import annotations

import numpy as np
from sklearn.neighbors import NearestNeighbors


def knn_consistency_filter(
    X: np.ndarray,
    y: np.ndarray,
    k: int = 10,
    keep_ratio: float = 0.75,
) -> np.ndarray:
    """Label-consistency buffer purification (H3 defence variant 2).

    A sample's consistency = fraction of its k nearest neighbours (within the
    incoming task stream) that share its label. Keeps the top ``keep_ratio``
    most-consistent samples. Label-flipped poison has neighbours of the true
    (different) label → low consistency → dropped; but legitimate samples of a
    *newly introduced class* also have few same-label neighbours early on →
    the drift-vs-poison confusion H3 predicts.
    """
    n = len(X)
    if n == 0:
        return np.zeros(0, dtype=bool)
    k_eff = int(min(max(1, k), n - 1))
    if n <= k_eff + 1:
        return np.ones(n, dtype=bool)
    nn = NearestNeighbors(n_neighbors=k_eff + 1, algorithm="brute", n_jobs=-1).fit(X)
    ind = nn.kneighbors(return_distance=False)
    nb = y[ind[:, 1:]]
    cons = (nb == y[:, None]).mean(axis=1)
    keep_n = max(1, int(round(n * keep_ratio)))
    order = np.argsort(-cons, kind="stable")
    mask = np.zeros(n, dtype=bool)
    mask[order[:keep_n]] = True
    return mask
