"""Pinned candidate runtime, separate from the frozen Windows CPU execution."""
from __future__ import annotations

import os
import platform
import subprocess
from importlib.metadata import distributions
from pathlib import Path

os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')

import numpy as np
import torch

from src.phase3.common import ROOT, digest, identity
from src.phase3_v3.protocol import code_identity

FROZEN = '38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c'
FROZEN_FILES = {
    'configs/phase3/cpu-v2.json': 'd6ec54eb3ea1845177e6df159ae975a9c267200081e03a591fd17c6b81ef085e',
    'configs/phase3/cpu-v3.json': '3943ddfbc04aa8a3b42e2a59118e5c5f666476b2a2c0ab186f445b773cc69ce4',
    'configs/phase3/reference74-v1.json': 'a8fc9dc310716d104a1df24f4eef24885af46481d8c6d6c25c6d2a302388127a',
    'configs/phase3/taxonomy-v1.json': '410b7e3b5709cc58c637496c08fc20200de20911b68a044edd4d420731394561',
    'docs/phase3-cpu-v2/decisions-2026-10-24.md': '5f333429d3d71f7101d152b87ba9bce251c4cd7632307bc71c2d98fc3e033986',
    'docs/phase3-cpu-v3/decisions-2026-10-24.md': '966cea6e0b290bbd3a3bb1bf1fda2185a2b71d2cc5c3ce822ecf414656d09cbd',
}


def verify_frozen_bindings():
    if code_identity() != FROZEN:
        raise ValueError('Frozen numerical source changed')
    actual = {name: digest(ROOT/name) for name in FROZEN_FILES}
    if actual != FROZEN_FILES:
        raise ValueError('Frozen protocol, taxonomy or decision bytes changed; a new scientific revision is required')
    return actual


def source_files():
    paths = set((ROOT/'kaggle_worker').glob('*.py')) | set((ROOT/'kaggle_worker/locks').glob('*'))
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(paths) if path.is_file()}


def configure(device='cpu'):
    verify_frozen_bindings()
    if platform.python_version() != '3.12.14' or np.__version__ != '2.3.5':
        raise RuntimeError('Use Python 3.12.14 and NumPy 2.3.5 in the isolated notebook environment')
    if str(torch.__version__) not in ('2.7.0+cpu', '2.7.0+cu126'):
        raise RuntimeError('Candidate requires torch 2.7.0+cpu or 2.7.0+cu126')
    target = torch.device(device)
    if target.type not in ('cpu', 'cuda'):
        raise ValueError('Only CPU or CUDA candidates supported')
    torch.set_num_threads(1)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_default_dtype(torch.float32)
    torch.set_float32_matmul_precision('highest')
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    gpu = None
    if target.type == 'cuda':
        if not torch.cuda.is_available() or str(torch.__version__) != '2.7.0+cu126':
            raise RuntimeError('An actual CUDA worker and pinned CUDA build are required')
        if os.environ.get('CUBLAS_WORKSPACE_CONFIG') != ':4096:8' or os.environ.get('TORCH_ALLOW_TF32_CUBLAS_OVERRIDE') == '1':
            raise RuntimeError('Incompatible CUDA precision/determinism environment')
        torch.cuda.set_device(target)
        props = torch.cuda.get_device_properties(target)
        try:
            driver = subprocess.check_output(
                ['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'], text=True).strip().splitlines()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError('Cannot record NVIDIA driver') from exc
        gpu = {'name': props.name, 'capability': list(torch.cuda.get_device_capability(target)),
               'memory_bytes': props.total_memory, 'driver_versions': driver}
    processor = platform.processor()
    if not processor and Path('/proc/cpuinfo').is_file():
        processor = next((line.split(':', 1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines()
                          if line.startswith('model name')), 'unavailable')
    return {'schema': 'kaggle-qualification-runtime-v1', 'python': platform.python_version(),
            'torch': str(torch.__version__), 'numpy': np.__version__, 'cuda': torch.version.cuda,
            'cudnn': torch.backends.cudnn.version(), 'torch_build': torch.__config__.show(),
            'system': platform.system(), 'machine': platform.machine(), 'processor': processor,
            'CPU_capability': torch.backends.cpu.get_cpu_capability(),
            'device_type': target.type, 'gpu': gpu, 'threads': 1, 'interop_threads': 1,
            'dtype': 'float32', 'amp': False, 'tf32': False, 'deterministic_algorithms': True,
            'cublas_workspace': os.environ.get('CUBLAS_WORKSPACE_CONFIG'),
            'packages': dict(sorted((dist.metadata['Name'].lower(), dist.version) for dist in distributions()
                                    if dist.metadata['Name'])),
            'worker_source_identity': identity(source_files()), 'frozen_code_identity': FROZEN}


def synchronize(device):
    if torch.device(device).type == 'cuda':
        torch.cuda.synchronize(device)


def resources(device):
    peak_rss = None
    if platform.system() == 'Linux':
        import resource
        peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    cuda = torch.device(device).type == 'cuda'
    return {'process_peak_RSS_bytes': peak_rss,
            'cuda_peak_allocated_bytes': torch.cuda.max_memory_allocated(device) if cuda else None,
            'cuda_peak_reserved_bytes': torch.cuda.max_memory_reserved(device) if cuda else None,
            'scope': 'Linux process high-water RSS; PyTorch CUDA allocator only, not total GPU occupancy'}


def safe_output(path):
    """Notebook results must live on the saved working volume."""
    path = Path(path).resolve()
    if Path('/kaggle').exists() and not path.is_relative_to(Path('/kaggle/working')):
        raise ValueError('Notebook output must be under /kaggle/working')
    return path
