"""Minimal local inference contract for a trained IDS bundle (Phase G).

Scope: load a versioned bundle (fitted preprocessing + label map + model
weights with integrity hashes), validate inputs fail-closed, predict with an
explicit abstain policy, and report health metrics. This is CPU-local
inference only: no federation, privacy, or edge-suitability claim follows.

Bundle file layout (torch.save): {"meta": {...}, "state": state_dict}.
"""
from __future__ import annotations

import hashlib
import io
import json
import time
from pathlib import Path

import numpy as np
import torch

SCHEMA_VERSION = 1
INTERFACE_VERSION = 1
DEFAULT_MAX_BATCH = 4096  # memory bound for one predict call on CPU


def _tensor_bytes_hash(state: dict) -> str:
    h = hashlib.sha256()
    for key in sorted(state):
        t = state[key].detach().cpu()
        h.update(key.encode())
        h.update(str(tuple(t.shape)).encode() + b"\0")
        h.update(str(t.dtype).encode() + b"\0")
        h.update(np.ascontiguousarray(t.numpy()).tobytes())
    return h.hexdigest()


def export_bundle(model: torch.nn.Module, *, feature_cols: list[str],
                  label_map: dict[str, int], scaler_mean: list[float],
                  scaler_scale: list[float], medians: dict[str, float],
                  protocol_id: str, train_config: str) -> tuple[dict, dict]:
    """Package fitted preprocessing + weights. Returns (meta, state_dict)."""
    if len(set(feature_cols)) != len(feature_cols) or not feature_cols:
        raise ValueError("feature_cols must be unique and nonempty")
    if sorted(label_map.values()) != list(range(len(label_map))):
        raise ValueError("label_map ids must be contiguous from 0")
    mean = np.asarray(scaler_mean, dtype=np.float64)
    scale = np.asarray(scaler_scale, dtype=np.float64)
    if mean.shape != (len(feature_cols),) or scale.shape != mean.shape:
        raise ValueError("scaler mean/scale must match feature count")
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(scale)) or bool((scale <= 0).any()):
        raise ValueError("scaler parameters must be finite with positive scale")
    if set(medians) != set(feature_cols) or not all(np.isfinite(v) for v in medians.values()):
        raise ValueError("medians must cover every feature with finite values")
    state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    meta = {
        "schema_version": SCHEMA_VERSION, "min_interface_version": 1,
        "protocol_id": protocol_id, "train_config": train_config,
        "feature_cols": list(feature_cols),
        "label_map": {str(k): int(v) for k, v in label_map.items()},
        "scaler_mean": [float(v) for v in mean],
        "scaler_scale": [float(v) for v in scale],
        "medians": {str(k): float(v) for k, v in medians.items()},
        "model_sha256": _tensor_bytes_hash(state),
        "torch_version": torch.__version__,
    }
    return meta, state


def save_bundle(path: Path, meta: dict, state: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        torch.save({"meta": meta, "state": state}, f)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bundle(path: Path, *, expected_file_sha256: str | None = None) -> tuple[dict, dict]:
    """Load and verify. Fails closed on version, schema, or hash mismatch."""
    raw = Path(path).read_bytes()
    if expected_file_sha256 is not None and hashlib.sha256(raw).hexdigest() != expected_file_sha256:
        raise ValueError("bundle file hash mismatch: refusing to load")
    try:
        payload = torch.load(io.BytesIO(raw), map_location="cpu", weights_only=False)
    except Exception as e:
        raise ValueError(f"bundle unreadable or corrupt ({type(e).__name__})") from e
    meta, state = payload["meta"], payload["state"]
    if meta.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported bundle schema: {meta.get('schema_version')}")
    if int(meta.get("min_interface_version", 1)) > INTERFACE_VERSION:
        raise ValueError("bundle needs a newer inference interface")
    if _tensor_bytes_hash(state) != meta.get("model_sha256"):
        raise ValueError("model weight hash mismatch: refusing to load")
    return meta, state


def validate_frame(data, meta: dict, *, max_batch: int = DEFAULT_MAX_BATCH) -> np.ndarray:
    """Strict schema validation + training-consistent imputation.

    Accepts a DataFrame (named columns) or an ndarray (positional, must match
    bundle order exactly). Missing/extra columns, width mismatch, batch
    overflow, and empty input raise. NaN/inf are median-imputed and counted.
    Returns float32 model-space array (scaled).
    """
    cols = meta["feature_cols"]
    if isinstance(data, np.ndarray):
        if data.ndim != 2 or data.shape[1] != len(cols):
            raise ValueError(f"expected width {len(cols)}, got shape {data.shape}")
        arr = np.asarray(data, dtype=np.float64)
    else:
        have = list(data.columns)
        missing = [c for c in cols if c not in have]
        extra = [c for c in have if c not in cols]
        if missing or extra:
            raise ValueError(f"schema mismatch: missing={missing} extra={extra}")
        arr = np.column_stack([np.asarray(data[c], dtype=np.float64) for c in cols])
    if len(arr) == 0:
        raise ValueError("empty batch")
    if len(arr) > max_batch:
        raise ValueError(f"batch {len(arr)} exceeds max_batch {max_batch}")
    bad = ~np.isfinite(arr)
    n_bad = int(bad.sum())
    if n_bad:
        medians = np.array([meta["medians"][c] for c in cols], dtype=np.float64)
        arr = np.where(bad, medians[None, :], arr)
    mean = np.array(meta["scaler_mean"], dtype=np.float64)
    scale = np.array(meta["scaler_scale"], dtype=np.float64)
    out = ((arr - mean[None, :]) / scale[None, :]).astype(np.float32)
    if not np.all(np.isfinite(out)):
        raise ValueError("non-finite values after preprocessing")
    return out, n_bad  # model-space array + imputed-cell count


def predict(meta: dict, model: torch.nn.Module, X: np.ndarray, *,
            device: str = "cpu", abstain_min_confidence: float | None = None,
            max_batch: int = DEFAULT_MAX_BATCH) -> dict:
    """Predict label ids with optional abstention. Never silently drops rows."""
    if abstain_min_confidence is not None and not 0.0 < abstain_min_confidence <= 1.0:
        raise ValueError("abstain_min_confidence must be in (0, 1]")
    model = model.to(device)
    model.eval()
    t0 = time.perf_counter()
    prob_blocks = []
    with torch.no_grad():
        for i in range(0, len(X), max_batch):
            logits = model(torch.from_numpy(X[i:i + max_batch]).to(device))
            prob_blocks.append(torch.softmax(logits, dim=1).cpu().numpy())
    probs = np.concatenate(prob_blocks, axis=0)
    latency_ms = (time.perf_counter() - t0) / max(1, len(X)) * 1000.0
    conf = probs.max(axis=1)
    ids = probs.argmax(axis=1).astype(np.int64)
    abstained = np.zeros(len(X), dtype=bool)
    if abstain_min_confidence is not None:
        abstained = conf < abstain_min_confidence
        ids = np.where(abstained, -1, ids)
    names = {v: k for k, v in meta["label_map"].items()}
    return {"labels": ids, "names": [names.get(int(v), "ABSTAIN") for v in ids],
            "confidence": conf.astype(float), "abstained": abstained,
            "n": len(X), "n_abstained": int(abstained.sum()),
            "latency_ms_per_sample": float(latency_ms)}


def predict_batch(meta: dict, model: torch.nn.Module, data, *,
                  device: str = "cpu", abstain_min_confidence: float | None = None,
                  max_batch: int = DEFAULT_MAX_BATCH) -> dict:
    """Full contract in one call: validate, impute, scale, predict, report."""
    X, n_imputed = validate_frame(data, meta, max_batch=max_batch)
    out = predict(meta, model, X, device=device,
                  abstain_min_confidence=abstain_min_confidence,
                  max_batch=max_batch)
    out["n_imputed_cells"] = n_imputed
    return out


def _registry_path(directory: Path) -> Path:
    return Path(directory) / "bundle_registry.json"


def _read_registry(directory: Path) -> dict:
    path = _registry_path(directory)
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("bundle registry is corrupt")
    return data


def save_versioned_bundle(directory: Path, stem: str, meta: dict, state: dict) -> Path:
    """Save as ``{stem}_v{n}.pt`` with a hash-chained registry entry.

    Versions increase monotonically; existing bundles are never overwritten.
    Returns the new bundle path.
    """
    from datetime import UTC, datetime

    directory = Path(directory)
    registry = _read_registry(directory)
    entries = registry.get(stem, [])
    version = (max((e["version"] for e in entries), default=0)) + 1
    path = directory / f"{stem}_v{version}.pt"
    if path.exists():
        raise FileExistsError(f"refusing to overwrite bundle: {path}")
    file_sha = save_bundle(path, meta, state)
    entries.append({"version": version, "file": path.name, "sha256": file_sha,
                    "protocol_id": meta.get("protocol_id"),
                    "created_utc": datetime.now(UTC).isoformat()})
    registry[stem] = entries
    _registry_path(directory).write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return path


def list_bundles(directory: Path, stem: str) -> list[dict]:
    """Newest-first bundle records; empty list when nothing was ever saved."""
    entries = _read_registry(directory).get(stem, [])
    return sorted(entries, key=lambda e: e["version"], reverse=True)


def rollback(directory: Path, stem: str, target_version: int) -> Path:
    """Return the verified path of a prior bundle version (fail-closed).

    Verifies the file hash against the registry before returning; loading
    and health-checking the returned bundle is the caller's next step.
    """
    directory = Path(directory)
    for entry in _read_registry(directory).get(stem, []):
        if entry["version"] == target_version:
            path = directory / entry["file"]
            if not path.is_file():
                raise FileNotFoundError(f"registered bundle missing: {path}")
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            if h.hexdigest() != entry["sha256"]:
                raise ValueError(f"registered bundle hash mismatch: {path}")
            return path
    raise ValueError(f"no bundle {stem!r} at version {target_version}")
