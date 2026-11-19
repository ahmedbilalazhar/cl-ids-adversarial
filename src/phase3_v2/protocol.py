"""Small explicit configuration and scientific identity boundaries."""
from __future__ import annotations

import platform
from dataclasses import asdict, dataclass

import numpy as np
import torch

from src.phase3.common import ROOT, digest, identity, read_json

PROTOCOL = ROOT / 'configs/phase3/cpu-v2.json'


@dataclass(frozen=True)
class Settings:
    learner: str = 'DR'
    admission: str = 'NONE'
    seed: int = 101
    rounds: int = 3
    epochs: int = 1
    learning_rate: float = .001
    lambda_E: float = 10.
    lambda_y: float = 1.
    lambda_z: float = .5
    dose: tuple[int, int] = (0, 1)

    def validate(self):
        if self.learner not in {'FT', 'EI', 'DR'} or self.admission not in {'NONE', 'DG', 'DM', 'DC', 'DQ'}:
            raise ValueError('Unsupported learner/admission')
        if self.learner != 'DR' and self.admission != 'NONE':
            raise ValueError('Admission controls use DR settings')
        if self.seed not in {101, 102, 103} or (self.rounds, self.epochs) not in {(1, 3), (3, 1)}:
            raise ValueError('Only declared development seeds and synchronization budgets are executable')
        if self.dose not in {(0, 1), (1, 10), (3, 10), (1, 2)}:
            raise ValueError('Undeclared dose')
        if any(not np.isfinite(v) or v < 0 for v in (self.learning_rate, self.lambda_E, self.lambda_y, self.lambda_z)) or self.learning_rate == 0:
            raise ValueError('Invalid coefficients')
        return self

    def scientific(self):
        # Unused settings do not split identities of exact pilot/tuning aliases.
        data = asdict(self)
        if self.learner != 'EI':
            data.pop('lambda_E')
        if self.learner != 'DR':
            data.pop('lambda_y')
            data.pop('lambda_z')
        return data


def code_files():
    files = list((ROOT / 'src/phase3_v2').glob('*.py')) + list((ROOT / 'src/phase3').glob('*.py'))
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(files)}


def code_identity():
    return identity(code_files())


def configure_runtime():
    contract = read_json(PROTOCOL)
    if platform.python_version() != contract['runtime']['python'] or torch.__version__ != contract['runtime']['torch'] or np.__version__ != contract['runtime']['numpy']:
        raise RuntimeError('CPU runtime does not match v2 lock')
    torch.set_num_threads(1)
    # Multiple simulator calls in one acceptance process share one configured runtime.
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_float32_matmul_precision('highest')
    torch.set_default_dtype(torch.float32)
    return {'python': platform.python_version(), 'torch': torch.__version__, 'numpy': np.__version__,
            'platform': platform.platform(), 'processor': platform.processor(),
            'torch_build': torch.__config__.show(), 'device': 'cpu', 'threads': 1,
            'interop_threads': 1, 'deterministic_algorithms': True, 'amp': False, 'dtype': 'float32'}
