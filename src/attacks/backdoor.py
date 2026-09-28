from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.data.task_schema import sha256_file

DEFAULT_TRIGGER = {
    "features": ["Bwd Packet Length Max", "Fwd Packet Length Max", "Init_Win_bytes_forward"],
    "values": [1448.0, 1448.0, 64240.0],
}

# The packet recipe in scripts/gen_grounded_trigger.py proposes these raw
# feature values. They remain a feature-space approximation until the actual
# flow extractor is shown to produce them from the packet sequence.
GROUNDED_TRIGGER = {
    "features": ["SYN Flag Count", "Init_Win_bytes_forward", "Fwd Packet Length Mean"],
    "values": [3.0, 29200.0, 40.0],
}


def scaled_trigger(trigger: dict | None, feature_names: list[str], tasks_path: Path) -> dict:
    """Convert a raw-feature trigger using the task artifact's fitted scaler."""
    spec = trigger if trigger is not None else DEFAULT_TRIGGER
    names = spec.get("features")
    values = spec.get("values")
    if not isinstance(names, list) or not isinstance(values, list) or not names or len(names) != len(values):
        raise ValueError("backdoor trigger needs equally sized nonempty feature and value lists")
    if len(set(names)) != len(names) or len(set(feature_names)) != len(feature_names):
        raise ValueError("backdoor trigger and task feature names must be unique")
    missing = [name for name in names if name not in feature_names]
    if missing:
        raise ValueError(f"backdoor trigger features absent from task artifact: {missing}")
    meta_path = tasks_path.with_suffix(".json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("schema_version") != 2 or meta.get("npz_sha256") != sha256_file(tasks_path):
        raise ValueError("backdoor raw trigger requires a verified v2 task artifact")
    if meta.get("feature_cols") != feature_names:
        raise ValueError("backdoor feature order differs from task artifact")
    scaler = meta.get("scaler") or {}
    raw = np.asarray(values, dtype=np.float64)
    if not np.isfinite(raw).all():
        raise ValueError("backdoor trigger values must be finite")
    cols = [feature_names.index(name) for name in names]
    if scaler.get("kind") == "identity":
        model_values = raw
    elif "mean" in scaler and "scale" in scaler:
        mean = np.asarray(scaler["mean"], dtype=np.float64)
        scale = np.asarray(scaler["scale"], dtype=np.float64)
        if mean.shape != (len(feature_names),) or scale.shape != mean.shape or not np.isfinite(mean).all() or not np.isfinite(scale).all() or np.any(scale <= 0):
            raise ValueError("backdoor task scaler parameters are invalid")
        model_values = (raw - mean[cols]) / scale[cols]
    else:
        raise ValueError("backdoor raw trigger requires known fitted scaler parameters")
    return {"features": names, "values": model_values.tolist()}


def backdoor_outcome(predict, X: np.ndarray, y: np.ndarray, feature_names: list[str],
                     attack_class: int | None, target_label: int, trigger: dict) -> dict:
    """Score only triggered, originally non-target attack-class examples."""
    eligible_mask = (y == attack_class) & (y != target_label) if attack_class is not None else np.zeros(len(y), dtype=bool)
    eligible = int(eligible_mask.sum())
    if not eligible:
        return {"asr": None, "eligible": 0, "successes": 0,
                "clean_target_errors": 0, "clean_target_error_rate": None}
    clean = X[eligible_mask]
    clean_errors = int(np.sum(predict(clean) == target_label))
    triggered = clean.copy()
    for name, value in zip(trigger["features"], trigger["values"]):
        triggered[:, feature_names.index(name)] = value
    successes = int(np.sum(predict(triggered) == target_label))
    return {"asr": successes / eligible, "eligible": eligible, "successes": successes,
            "clean_target_errors": clean_errors, "clean_target_error_rate": clean_errors / eligible}


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
    if trigger is None:
        raise ValueError("backdoor injection requires a validated model-space trigger")

    candidates = np.where((y == attack_class) & (y != target_label))[0]
    k = min(round(n * budget), len(candidates))
    if k <= 0:
        return X, y, triggered

    idx = rng.choice(candidates, size=k, replace=False)
    cols = [feature_names.index(fname) for fname in trigger["features"]]
    vals = trigger["values"]

    for i in idx:
        for c, v in zip(cols, vals):
            X[i, c] = v
        y[i] = target_label
        triggered[i] = True
    return X, y, triggered
