from __future__ import annotations

import numpy as np


def label_flip(
    y: np.ndarray,
    budget: float,
    mode: str = "random",
    source_class: int | None = None,
    target_class: int = 0,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    y = y.copy()
    n = len(y)
    k = int(round(n * budget))
    if k <= 0:
        return y, np.zeros(n, dtype=bool)

    flipped = np.zeros(n, dtype=bool)
    if mode == "targeted" and source_class is not None:
        candidates = np.where(y == source_class)[0]
        if len(candidates) == 0:
            return y, flipped
        k = min(k, len(candidates))
        idx = rng.choice(candidates, size=k, replace=False)
        y[idx] = target_class
        flipped[idx] = True
    else:
        idx = rng.choice(n, size=k, replace=False)
        for i in idx:
            choices = [c for c in np.unique(y) if c != y[i]]
            if len(choices) == 0:
                continue
            y[i] = rng.choice(choices)
            flipped[i] = True
    return y, flipped
