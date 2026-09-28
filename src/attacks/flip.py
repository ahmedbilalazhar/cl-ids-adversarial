from __future__ import annotations

import numpy as np


# Benign-class names across datasets (CICIDS/IoT use "Benign", UNSW uses
# "Normal"). New task artifacts guarantee the benign class has id 0, but
# attack configs must name their target — never assume a numeric id.
BENIGN_NAMES = ("Benign", "Normal")


def resolve_class_id(value, label_map: dict, *, role: str = "target") -> int:
    """Resolve a class reference to an integer id via the task label map.

    Accepts a class NAME (str, looked up in label_map) or a numeric id (int,
    validated against label_map values). Unknown names, unknown ids, and
    missing benign fallbacks raise — poisoning targets fail closed, never
    silently flip to an unintended class (cf. the UNSW Normal=7 / IoT
    benign=1 label bugs, where numeric targets pointed at the wrong class
    once the label map was corrected).
    """
    if isinstance(value, str):
        if value not in label_map:
            raise KeyError(f"unknown {role} class name {value!r}; known: {sorted(label_map)}")
        return int(label_map[value])
    if value is None:
        for b in BENIGN_NAMES:
            if b in label_map:
                return int(label_map[b])
        raise KeyError(f"no benign class found for {role}; known: {sorted(label_map)}")
    try:
        i = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid {role} class reference {value!r}")
    if i not in set(label_map.values()):
        raise ValueError(f"unknown {role} class id {i}; known ids: {sorted(set(label_map.values()))}")
    return i


def resolve_attack_target(attack: dict, label_map: dict) -> int:
    """Target id for a label-flip/backdoor attack: explicit name or id wins;
    otherwise the dataset's benign class. Name references are resolved via
    the stored task label map (never magic numbers)."""
    attack = attack or {}
    if attack.get("target_class_name") is not None:
        return resolve_class_id(attack.get("target_class_name"), label_map, role="target")
    return resolve_class_id(attack.get("target_class"), label_map, role="target")


def majority_attack_class(y: np.ndarray, target_class: int = 0) -> int | None:
    """Most frequent non-target class in y (per-task majority attack class).
    Returns None when y holds only the target class."""
    vals, counts = np.unique(y[y != target_class], return_counts=True)
    if len(vals) == 0:
        return None
    return int(vals[int(np.argmax(counts))])


def knn_preserving_flip(
    X: np.ndarray,
    y: np.ndarray,
    budget: float,
    source_class: int | None = None,
    target_class: int = 0,
    k: int = 10,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Phase-3 step 15 adaptive attacker vs kNN-consistency filtering.

    Among source-class candidates, flip the `budget` fraction whose kNN
    neighborhood already holds the MOST target-label neighbours — i.e. the
    samples a label-consistency filter keeps. Seed accepted for signature
    parity (selection is deterministic given X, y).
    """
    from sklearn.neighbors import NearestNeighbors

    y = y.copy()
    n = len(y)
    if source_class is None:
        source_class = majority_attack_class(y, target_class)
    candidates = np.where(y == source_class)[0] if source_class is not None else np.array([], dtype=int)
    flipped = np.zeros(n, dtype=bool)
    if len(candidates) == 0:
        return y, flipped
    k_eff = int(min(max(1, k), n - 1))
    nn = NearestNeighbors(n_neighbors=k_eff + 1, algorithm="brute", n_jobs=1).fit(X)
    ind = nn.kneighbors(return_distance=False)
    frac_tgt = (y[ind[:, 1:]] == target_class).mean(axis=1)
    order = candidates[np.argsort(-frac_tgt[candidates], kind="stable")]
    take = order[: min(int(round(n * budget)), len(order))]
    y[take] = target_class
    flipped[take] = True
    return y, flipped


def adaptive_loss_preserving_flip(
    model,
    X: np.ndarray,
    y: np.ndarray,
    budget: float,
    source_class: int | None = None,
    target_class: int = 0,
    seed: int = 42,
    device: str = "cpu",
) -> tuple[np.ndarray, np.ndarray]:
    """Phase-3 step 15 adaptive attacker vs small-loss filtering.

    White-box vs the defender's carried-over model: among source-class
    candidates, flip the `budget` fraction with the LOWEST cross-entropy loss
    computed under the TARGET label — i.e. exactly the samples a small-loss
    keep-lowest-loss filter retains. Reports whether the defense still holds.
    """
    import torch

    y = y.copy()
    n = len(y)
    if source_class is None:
        source_class = majority_attack_class(y, target_class)
    candidates = np.where(y == source_class)[0] if source_class is not None else np.array([], dtype=int)
    k = min(int(round(n * budget)), len(candidates))
    flipped = np.zeros(n, dtype=bool)
    if k <= 0 or len(candidates) == 0:
        return y, flipped
    model.eval()
    with torch.no_grad():
        logits = model(torch.from_numpy(X[candidates]).float().to(device))
        tgt = torch.full((len(candidates),), int(target_class), dtype=torch.long).to(logits.device)
        losses = torch.nn.functional.cross_entropy(logits, tgt, reduction="none").cpu().numpy()
    pick = candidates[np.argsort(losses, kind="stable")[:k]]
    # Deterministic tie-break note: equal losses keep candidate order (stable
    # argsort on loss values computed in candidate order) — seed only affects
    # nothing here beyond reproducibility of the surrounding pipeline.
    y[pick] = target_class
    flipped[pick] = True
    return y, flipped


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
    if mode == "persistent" and source_class is None:
        # Phase-3 step 16: each task's OWN majority attack class -> target.
        source_class = majority_attack_class(y, target_class)
        mode = "targeted"
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
