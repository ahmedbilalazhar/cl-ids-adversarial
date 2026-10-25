"""Record observed resources and operator-declared session bounds before training."""
import argparse
import math
import shutil
from pathlib import Path

from src.phase3.common import write_json
from .runtime import configure, safe_output
from .selection import selected_settings, SELECTION_SHA256


def inspect(device, output, session_seconds, minimum_free_bytes):
    if (type(session_seconds) not in (int, float) or not math.isfinite(session_seconds)
            or session_seconds <= 0 or type(minimum_free_bytes) is not int or minimum_free_bytes <= 0):
        raise ValueError('Positive session and storage requirements must be declared')
    runtime = configure(device)
    output = safe_output(output)
    output.mkdir(parents=True, exist_ok=True)
    disk = shutil.disk_usage(output)
    if disk.free < minimum_free_bytes:
        raise RuntimeError('Insufficient free space for declared storage requirement')
    memory = None
    if Path('/proc/meminfo').is_file():
        memory = {k: int(v.split()[0])*1024 for k, v in
                  (line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
                  if k in ('MemTotal', 'MemAvailable')}
    for learner in ('FT', 'EI', 'DR'):
        selected_settings(learner)
    return {'schema': 'kaggle-preflight-v1', 'runtime': runtime,
            'selection_sha256': SELECTION_SHA256, 'memory_bytes': memory,
            'free_disk_bytes': disk.free, 'minimum_free_bytes': minimum_free_bytes,
            'declared_session_seconds': session_seconds,
            'session_limit_verified_by_provider': False,
            'sklearn': {'required': False, 'reason': 'Count metrics and exact analysis do not use sklearn',
                        'installed_version': runtime['packages'].get('scikit-learn')},
            'durability_qualified': False, 'final_dispatchable': False,
            'scope': 'Resource observation, not a storage durability or provider quota guarantee'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--session-seconds', type=float, required=True)
    parser.add_argument('--minimum-free-bytes', type=int, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = inspect(args.device, args.output.parent, args.session_seconds, args.minimum_free_bytes)
    write_json(args.output, result)


if __name__ == '__main__':
    main()
