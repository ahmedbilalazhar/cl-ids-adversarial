"""Strict identities, atomic writes and versioned random streams."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_PROTOCOL_SHA256 = "a8fc9dc310716d104a1df24f4eef24885af46481d8c6d6c25c6d2a302388127a"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def reference_protocol(path):
    if digest(path) != REFERENCE_PROTOCOL_SHA256:
        raise ValueError("This reference executable requires the immutable reference74-v1 protocol; changes need a new version")
    return read_json(path)


def identity(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


def read_json(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError(f"Duplicate JSON key: {k}")
            result[k] = v
        return result
    def invalid(value):
        raise ValueError(f"Invalid JSON number: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique, parse_constant=invalid)


def rng(namespace, seed, *scope):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([1, namespace, seed, *scope])))


def torch_seed(namespace, seed, *scope):
    return int(rng(namespace, seed, *scope).integers(0, 2**63, dtype=np.int64))


def encode_rng(generator):
    state = generator.bit_generator.state.copy()
    state["state"] = {k: str(v) for k, v in state["state"].items()}
    return state


def decode_rng(state):
    if state["bit_generator"] != "PCG64":
        raise ValueError("Only the adopted PCG64 stream is accepted")
    state = {**state, "state": {k: int(v) for k, v in state["state"].items()}}
    generator = np.random.Generator(np.random.PCG64())
    generator.bit_generator.state = state
    return generator


def array_identity(array):
    a = np.ascontiguousarray(array)
    h = hashlib.sha256(canonical({"dtype": a.dtype.str, "shape": a.shape}).encode())
    h.update(a.tobytes())
    return h.hexdigest()


def save_state(path, metadata, arrays):
    """One pickle-free transaction, valid only at a completed broadcast boundary."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as f:
        np.savez(f, metadata=np.array(canonical(metadata)), **arrays)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


def load_state(path):
    with np.load(path, allow_pickle=False) as state:
        metadata = json.loads(str(state["metadata"]))
        arrays = {k: state[k].copy() for k in state.files if k != "metadata"}
    return metadata, arrays


def state_identity(metadata, arrays):
    return identity({"metadata": metadata,
                     "arrays": {k: array_identity(v) for k, v in sorted(arrays.items())}})
