"""Versioned task-artifact schema (Phase-2 data contract).

Format ``taskset-v2``: one ``.npz`` with named plain arrays (loads with
``allow_pickle=False``) plus an extended JSON sidecar carrying the full
provenance record: label map, ordered feature names + units, fitted
preprocessing parameters, data-source identity + checksums, row-ID
description, split definition, and protocol ID.

Legacy ``payload_obj`` files (pickle object arrays) load ONLY when their
SHA-256 appears in the checked-in allowlist
``src/data/legacy_task_hashes.json`` (the audited baseline CICIDS bytes).
Anything else must be regenerated in v2 form.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np

SCHEMA_VERSION = 2
FORMAT_TAG = "taskset-v2"

# Feature units are not documented per column in any source distribution used
# here (CICIDS2017 ML-CSVs, UNSW-NB15 mirror, CICIoT2023 mirror), so the
# schema records that explicitly instead of fabricating units.
UNITS_UNKNOWN = "unknown (not documented in source distribution)"


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def source_commit() -> str:
    try:
        root = Path(__file__).resolve().parents[2]
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(root), stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return "unknown"


def units_for(columns: list[str]) -> dict[str, str]:
    return {c: UNITS_UNKNOWN for c in columns}


def assert_label_map(label_map: dict[str, int], benign_name: str) -> dict[str, int]:
    """Uniqueness + contiguity + benign-id-0 contract for every new artifact."""
    assert len(label_map) == len(set(label_map)), f"duplicate class names: {label_map}"
    assert sorted(label_map.values()) == list(range(len(label_map))), f"non-contiguous ids: {label_map}"
    assert label_map.get(benign_name) == 0, f"benign {benign_name!r} must be id 0: {label_map}"
    return label_map


def _validate_task(t: dict, index: int, n_features: int, valid_labels: set[int]) -> None:
    for split in ("train", "test"):
        x = np.asarray(t[f"X_{split}"])
        y = np.asarray(t[f"y_{split}"])
        ids = np.asarray(t[f"id_{split}"])
        if x.ndim != 2 or x.shape[1] != n_features or len(x) != len(y) or len(y) != len(ids):
            raise ValueError(f"task {index} {split} shape/feature mismatch")
        if not np.isfinite(x).all():
            raise ValueError(f"task {index} {split} has nonfinite features")
        if not set(np.unique(y)).issubset(valid_labels):
            raise ValueError(f"task {index} {split} has labels outside the map")
        if len(np.unique(ids)) != len(ids):
            raise ValueError(f"task {index} {split} has duplicate source row IDs")


def _validate_row_ids(tasks: list[dict], sources: list[dict]) -> None:
    train = np.concatenate([np.asarray(t["id_train"], dtype=np.int64) for t in tasks])
    test = np.concatenate([np.asarray(t["id_test"], dtype=np.int64) for t in tasks])
    if len(np.unique(train)) != len(train) or len(np.unique(test)) != len(test):
        raise ValueError("source row IDs reused across tasks within a source pool")
    if len(sources) == 1 and np.intersect1d(train, test).size:
        raise ValueError("same-pool source row ID appears in both train and test")


def write_taskset(
    out_path: Path,
    tasks: list[dict],
    label_map: dict[str, int],
    *,
    feature_cols: list[str],
    feature_units: dict[str, str] | None = None,
    protocol_id: str,
    split_def: dict,
    scaler_info: dict,
    imputation: dict,
    sources: list[dict],
    row_id_kind: str,
    extra: dict | None = None,
) -> dict:
    """Write v2 task artifact (pickle-free .npz + extended JSON sidecar).

    Each task dict must carry X_train/y_train/X_test/y_test (arrays), labels
    (list[str]), day (str), and id_train/id_test (int64 source row ids).
    Returns the sidecar dict (including the .npz sha256).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() or out_path.with_suffix(".json").exists():
        raise FileExistsError(f"task artifact already exists; archive it before rebuilding: {out_path}")
    if not tasks or not feature_cols or len(feature_cols) != len(set(feature_cols)):
        raise ValueError("tasks and unique ordered feature names are required")
    if not protocol_id or not split_def or not scaler_info or not sources:
        raise ValueError("protocol, split, scaler, and source provenance are required")
    feature_units = feature_units or units_for(feature_cols)
    if set(feature_units) != set(feature_cols):
        raise ValueError("feature units must cover every feature exactly")
    if any(not isinstance(s.get("sha256"), str) or len(s["sha256"]) != 64 for s in sources):
        raise ValueError("each source needs a SHA-256 checksum")
    benign_name = "Benign" if "Benign" in label_map else "Normal"
    assert_label_map(label_map, benign_name)
    for i, t in enumerate(tasks):
        for k in ("X_train", "y_train", "X_test", "y_test", "id_train", "id_test"):
            if k not in t:
                raise KeyError(f"task {i} missing required array {k!r}")
        _validate_task(t, i, len(feature_cols), set(label_map.values()))
    _validate_row_ids(tasks, sources)
    blobs: dict[str, np.ndarray] = {
        "format": np.array(FORMAT_TAG),
        "n_tasks": np.array(len(tasks), dtype=np.int64),
        "label_map_keys": np.array(sorted(label_map)),
        "label_map_vals": np.array([label_map[k] for k in sorted(label_map)], dtype=np.int64),
    }
    for i, t in enumerate(tasks):
        blobs[f"t{i}_X_train"] = np.asarray(t["X_train"], dtype=np.float32)
        blobs[f"t{i}_y_train"] = np.asarray(t["y_train"], dtype=np.int64)
        blobs[f"t{i}_X_test"] = np.asarray(t["X_test"], dtype=np.float32)
        blobs[f"t{i}_y_test"] = np.asarray(t["y_test"], dtype=np.int64)
        blobs[f"t{i}_id_train"] = np.asarray(t["id_train"], dtype=np.int64)
        blobs[f"t{i}_id_test"] = np.asarray(t["id_test"], dtype=np.int64)
        blobs[f"t{i}_day"] = np.array(str(t.get("day", f"t{i}")))
        blobs[f"t{i}_labels"] = np.array([str(x) for x in t.get("labels", [])])
    fd, tmp_name = tempfile.mkstemp(dir=str(out_path.parent), prefix=".task.", suffix=".npz")
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        np.savez_compressed(tmp, **blobs)
        os.replace(tmp, out_path)
    finally:
        tmp.unlink(missing_ok=True)

    sidecar = {
        "schema_version": SCHEMA_VERSION,
        "protocol_id": protocol_id,
        "label_map": dict(label_map),
        "benign_id": 0,
        "n_tasks": len(tasks),
        "days": [str(t.get("day", f"t{i}")) for i, t in enumerate(tasks)],
        "task_sizes": [
            {"train": int(len(t["y_train"])), "test": int(len(t["y_test"]))} for t in tasks
        ],
        "feature_cols": list(feature_cols),
        "feature_units": feature_units,
        "split": dict(split_def),
        "scaler": dict(scaler_info),
        "imputation": dict(imputation),
        "sources": list(sources),
        "row_ids": row_id_kind,
        "npz_sha256": sha256_file(out_path),
        "builder_commit": source_commit(),
    }
    if extra:
        for key, value in extra.items():
            if key in sidecar and sidecar[key] != value:
                raise ValueError(f"extra metadata conflicts with {key}")
            sidecar[key] = value
    fd, tmp_name = tempfile.mkstemp(dir=str(out_path.parent), prefix=".taskmeta.", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(sidecar, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, out_path.with_suffix(".json"))
    finally:
        Path(tmp_name).unlink(missing_ok=True)
    return sidecar


def is_v2(path: Path) -> bool:
    try:
        with np.load(path, allow_pickle=False) as z:
            return "format" in z and str(z["format"]) == FORMAT_TAG
    except Exception:
        return False


def read_v2(path: Path) -> tuple[list[dict], dict[str, int]]:
    meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    if meta.get("schema_version") != SCHEMA_VERSION or meta.get("npz_sha256") != sha256_file(path):
        raise ValueError(f"{path} sidecar version or NPZ hash mismatch")
    if not meta.get("protocol_id") or not meta.get("sources") or not meta.get("split"):
        raise ValueError(f"{path} missing protocol/source/split provenance")
    with np.load(path, allow_pickle=False) as z:
        if str(z["format"]) != FORMAT_TAG:
            raise ValueError(f"{path} is not a {FORMAT_TAG} artifact")
        n = int(z["n_tasks"])
        keys = [str(k) for k in z["label_map_keys"].tolist()]
        vals = [int(v) for v in z["label_map_vals"].tolist()]
        label_map = dict(zip(keys, vals))
        benign_name = "Benign" if "Benign" in label_map else "Normal"
        assert_label_map(label_map, benign_name)
        if label_map != meta.get("label_map") or meta.get("benign_id") != 0:
            raise ValueError(f"{path} label map differs from sidecar")
        features = meta.get("feature_cols") or []
        if len(features) != len(set(features)) or set(features) != set(meta.get("feature_units") or {}):
            raise ValueError(f"{path} feature schema invalid")
        tasks = []
        for i in range(n):
            tasks.append(
                {
                    "day": str(z[f"t{i}_day"]),
                    "labels": [str(x) for x in z[f"t{i}_labels"].tolist()],
                    "X_train": np.asarray(z[f"t{i}_X_train"], dtype=np.float32),
                    "y_train": np.asarray(z[f"t{i}_y_train"], dtype=np.int64),
                    "X_test": np.asarray(z[f"t{i}_X_test"], dtype=np.float32),
                    "y_test": np.asarray(z[f"t{i}_y_test"], dtype=np.int64),
                    "id_train": np.asarray(z[f"t{i}_id_train"], dtype=np.int64),
                    "id_test": np.asarray(z[f"t{i}_id_test"], dtype=np.int64),
                }
            )
    if len(tasks) != meta.get("n_tasks"):
        raise ValueError(f"{path} task count differs from sidecar")
    for i, task in enumerate(tasks):
        _validate_task(task, i, len(features), set(label_map.values()))
    _validate_row_ids(tasks, meta["sources"])
    return tasks, label_map


def legacy_allowlist() -> dict[str, str]:
    """Checked-in filename -> sha256 for the audited legacy bytes."""
    manifest = Path(__file__).with_name("legacy_task_hashes.json")
    if not manifest.exists():
        return {}
    try:
        return json.loads(manifest.read_text(encoding="utf-8"))
    except Exception:
        return {}
