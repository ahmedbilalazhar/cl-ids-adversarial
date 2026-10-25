"""Read-only supplied-label stage inputs; no evaluator annotations are imported."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.phase3.common import ROOT, digest, read_json

from .protocol import PROTOCOL, Settings

BASE_TRAIN = 'cabcf3c266d85b29cfd0c60943d90c6d128d9a78d6dcae2922f1b117acfa692b'
BASE_DEV = '2d8e209d17777b8ac5b2cc7f32dfb90fd5c358a671b79dcc3715b8368e57f081'
TRAIN_FILES = {f'E{s}/{k}.npy' for s in range(1, 5) for k in ('x', 'y', 'ids', 'owner')}


@dataclass(frozen=True)
class StageInput:
    stage: int
    x: np.ndarray
    y: np.ndarray
    ids: np.ndarray
    owner: np.ndarray

    def __post_init__(self):
        n = len(self.y)
        specifications = [(self.x, np.dtype('<f4'), (n, 74)), (self.y, np.dtype('<i8'), (n,)),
                          (self.ids, np.dtype('<u8'), (n,)), (self.owner, np.dtype('i1'), (n,))]
        if self.stage not in range(1, 5) or any(a.dtype != dtype or a.shape != shape for a, dtype, shape in specifications):
            raise ValueError('Stage shape/dtype mismatch')
        if not np.isfinite(self.x).all() or np.any(self.y < 0) or np.any(self.y >= 16) or np.any(self.owner < 0) or np.any(self.owner >= 5):
            raise ValueError('Invalid stage values')
        if len(np.unique(self.ids)) != n or (n > 1 and not np.all(self.ids[1:] > self.ids[:-1])):
            raise ValueError('IDs must be distinct canonical increasing uint64')
        for a, _, _ in specifications:
            a.setflags(write=False)

    def targets(self, slots):
        mapping = {code: slot for slot, code in enumerate(slots)}
        return np.array([mapping[int(y)] for y in self.y], dtype=np.int64)


def verify_files(folder: Path, expected: dict, allowed: set):
    if set(expected) != allowed:
        raise ValueError('Package file schema mismatch')
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    if actual != allowed | {'manifest.json'}:
        raise ValueError('Unexpected or missing package files')
    for name, sha in expected.items():
        if digest(folder / name) != sha:
            raise ValueError('Package hash mismatch: ' + name)


def verify_train(folder: Path, settings: Settings, expected_manifest: str):
    if digest(folder / 'manifest.json') != expected_manifest:
        raise ValueError('Expected training manifest identity differs')
    m = read_json(folder / 'manifest.json')
    if m['schema'] != 'phase3-train-v2' or m['base_train_manifest_sha256'] != BASE_TRAIN or m['protocol_sha256'] != digest(PROTOCOL):
        raise ValueError('Incompatible training lineage')
    if m['seed'] != settings.seed or tuple(m['dose']) != settings.dose:
        raise ValueError('Settings and supplied-label package differ')
    verify_files(folder, m['files'], TRAIN_FILES)
    # x and IDs must be the original calibrated train-only arrays, at every dose.
    fixed = read_json(ROOT / 'docs/phase3-reference/evidence/preparation-rebuild.json')['files']
    for s in range(1, 5):
        for k in ('x', 'ids'):
            name = f'E{s}/{k}.npy'
            if m['files'][name] != fixed['train/' + name]:
                raise ValueError('Feature/ID bank differs from adopted train-only inventory')
    stages = [load_stage(folder, s) for s in range(1, 5)]
    ids = np.concatenate([s.ids for s in stages])
    if len(np.unique(ids)) != len(ids):
        raise ValueError('Fresh IDs reused across stages')
    return m


def load_stage(folder: Path, stage: int):
    arrays = [np.load(folder / f'E{stage}/{k}.npy', allow_pickle=False, mmap_mode='r') for k in ('x', 'y', 'ids', 'owner')]
    return StageInput(stage, *arrays)
