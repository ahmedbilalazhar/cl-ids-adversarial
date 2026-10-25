"""Immutable validated stage cache; deterministic mappings computed only once."""
from __future__ import annotations

import numpy as np

from src.phase3_v2.data import StageInput, load_stage, verify_train


def map_targets(labels, slots):
    """Vectorized exact integer mapping for the fixed 16-class source registry."""
    lookup = np.full(16, -1, dtype=np.int64)
    if len(set(slots)) != len(slots) or any(type(code) is not int or not 0 <= code < 16 for code in slots):
        raise ValueError('Invalid source registry')
    for slot, code in enumerate(slots):
        lookup[code] = slot
    result = lookup[labels]
    if np.any(result < 0):
        raise KeyError(int(labels[np.flatnonzero(result < 0)[0]]))
    return result


class CachedStage(StageInput):
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, '_targets', {})

    def targets(self, slots):
        key = tuple(slots)
        if key not in self._targets:
            value = map_targets(self.y, slots)
            value.setflags(write=False)
            self._targets[key] = value
        # Preserve the frozen API's fresh writable target array without exposing
        # the cache to tensor alias mutation. The expensive Python mapping is
        # still computed only once.
        return self._targets[key].copy()


class StageCache:
    def __init__(self, loader, integrity_check=None):
        self.loader, self.values = loader, {}
        self.loads = 0
        self._integrity_check = integrity_check

    @classmethod
    def package(cls, path, settings, manifest):
        # Full hashes and isolation checks precede all numerical execution.
        verify_train(path, settings, manifest)
        return cls(lambda stage: load_stage(path, stage), lambda: verify_train(path, settings, manifest))

    def verify_integrity(self):
        if self._integrity_check is not None:
            self._integrity_check()

    def __call__(self, stage):
        if stage not in self.values:
            source = self.loader(stage)
            self.values[stage] = CachedStage(source.stage, source.x, source.y, source.ids, source.owner)
            self.loads += 1
        return self.values[stage]


class DeviceCache:
    """Only a stage's feature tensor and supplied targets enter device memory."""
    def __init__(self, device):
        import torch
        self.device = torch.device(device)
        self.key, self.x, self.targets = None, None, {}

    def get(self, data, slots):
        import torch
        if self.key is not data:
            self.key = data
            self.x = torch.from_numpy(np.array(data.x, copy=True)).to(self.device)
            self.targets = {}
        key = tuple(slots)
        if key not in self.targets:
            self.targets[key] = torch.from_numpy(data.targets(slots)).to(self.device)
        return self.x, self.targets[key]
