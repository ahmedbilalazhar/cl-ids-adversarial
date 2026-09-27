"""Byzantine update attacks on the federated aggregation step (Phase-3 step 13).

All attacks operate on SUBMITTED client updates (state_dicts) AFTER local
training, mirroring an adversary that controls the client's upload path.
Data-level poisoning (label_flip/backdoor on the shard) is separate and
combinable — see src/federated/fedavg.py _poison_shard.

Conventions: sd = client's trained state_dict (tensors on any device),
global_sd = broadcast model at round start. Helpers convert to DELTAS
(d = sd - global); aggregation rules consume deltas.
"""
from __future__ import annotations

import numpy as np
import torch


def to_deltas(sd: dict, global_sd: dict) -> dict:
    return {k: (sd[k].float() - global_sd[k].float()).cpu() for k in sd}


def from_deltas(delta: dict, global_sd: dict, device: str = "cpu") -> dict:
    return {k: (global_sd[k].float().to("cpu") + delta[k]).to(device) for k in delta}


def flatten(delta: dict) -> tuple[np.ndarray, list[tuple[str, tuple]]]:
    """Flatten a delta dict to 1-D numpy + layout for unflattening."""
    parts, layout = [], []
    for k in sorted(delta):
        v = np.asarray(delta[k], dtype=np.float64).ravel()
        layout.append((k, delta[k].shape))
        parts.append(v)
    return np.concatenate(parts), layout


def unflatten(vec: np.ndarray, layout: list[tuple[str, tuple]]) -> dict:
    out, pos = {}, 0
    for k, shape in layout:
        n = int(np.prod(shape))
        out[k] = torch.from_numpy(vec[pos : pos + n].reshape(shape).astype(np.float32))
        pos += n
    return out


def sign_flip_delta(delta: dict, scale: float = 1.0) -> dict:
    """Negate the client's update (sign-flip): submit -scale * delta."""
    return {k: (-scale * v.float()).cpu() for k, v in delta.items()}


def model_replacement_delta(delta: dict, boost: float) -> dict:
    """Bagdasaryan-style replacement: scale delta by boost (approx N/eta)."""
    return {(k): (boost * v.float()).cpu() for k, v in delta.items()}


def little_is_enough(
    benign_deltas: list[dict], z: float = 1.5, direction: str = "neg"
) -> dict:
    """Baruch et al. 'A Little Is Enough': craft ONE malicious delta from the
    benign population as mean(d) -/+ z * std(d) coordinate-wise (state_dict
    tensors preserved structurally). Caller replicates it to each malicious
    client. NOTE: white-box w.r.t. benign updates (strong adversary) —
    disclosed, conservative for the DEFENSE (hardest to filter)."""
    flats = []
    layout = None
    for d in benign_deltas:
        v, layout = flatten(d)
        flats.append(v)
    M = np.stack(flats, axis=0)
    mu = M.mean(axis=0)
    sd = M.std(axis=0)
    sgn = -1.0 if direction == "neg" else 1.0
    crafted = mu + sgn * z * sd
    return unflatten(crafted, layout)
