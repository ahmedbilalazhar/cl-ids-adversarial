from __future__ import annotations

import numpy as np


DEFAULT_TRIGGER = {
    "features": ["Bwd Packet Length Max", "Fwd Packet Length Max", "Init_Win_bytes_forward"],
    "values": [1448.0, 1448.0, 64240.0],
}


def inject_backdoor(
    X: np.ndarray,
    y: np.ndarray,
    budget: float,
    feature_names: list[str],
    attack_class: int,
    target_label: int = 0,
    trigger: dict | None = None,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    X = X.copy()
    y = y.copy()
    n = len(y)
    triggered = np.zeros(n, dtype=bool)
    trigger = trigger or DEFAULT_TRIGGER

    candidates = np.where(y == attack_class)[0]
    if len(candidates) == 0:
        candidates = np.arange(n)
    k = min(int(round(n * budget)), len(candidates))
    if k <= 0:
        return X, y, triggered

    idx = rng.choice(candidates, size=k, replace=False)
    cols = []
    vals = []
    for fname, fval in zip(trigger["features"], trigger["values"]):
        if fname in feature_names:
            cols.append(feature_names.index(fname))
            vals.append(fval)
    if not cols:
        cols = [0]
        vals = [float(np.median(X[:, 0]))]

    for i in idx:
        for c, v in zip(cols, vals):
            X[i, c] = v
        y[i] = target_label
        triggered[i] = True
    return X, y, triggered
