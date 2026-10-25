"""Hash-locked Linux environments with an offline verified reuse path."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

UV_VERSION = '0.12.18'
PYTHON_VERSION = '3.12.14'


def fingerprint(python):
    script = ("import json,platform; from importlib.metadata import distributions; "
              "print(json.dumps({'python':platform.python_version(), 'packages':"
              "dict(sorted((d.metadata['Name'].lower().replace('_','-'),d.version) "
              "for d in distributions() if d.metadata['Name']))},sort_keys=True))")
    return json.loads(subprocess.check_output([str(python), '-c', script], text=True))


def bootstrap(device, output, working_root=Path('/kaggle/working')):
    if device not in ('cpu', 'cuda'):
        raise ValueError('Unsupported environment profile')
    if sys.platform != 'linux' or platform.machine() != 'x86_64' or not working_root.is_dir():
        raise RuntimeError('Bootstrap requires a Kaggle Linux x86_64 notebook')
    output, working_root = output.resolve(), working_root.resolve()
    if not output.is_relative_to(working_root) or output == working_root:
        raise ValueError('Use a dedicated environment directory under the saved working root')
    lock = Path(__file__).resolve().parent/'locks'/f'{device}.txt'
    expected = {'profile': device, 'python': PYTHON_VERSION, 'uv': UV_VERSION,
                'lock_sha256': hashlib.sha256(lock.read_bytes()).hexdigest()}
    python, receipt = output/'bin/python', output/'.phase3-environment.json'
    if receipt.exists():
        old = json.loads(receipt.read_text(encoding='utf-8'))
        if old.get('contract') != expected:
            raise ValueError('Existing environment has another lock; preserve it and choose a fresh directory')
        if python.is_file() and fingerprint(python) == old.get('installed'):
            print('Verified existing locked environment; no install or network operation needed')
            return python
        raise ValueError('Installed environment drifted; preserve it and choose a fresh directory')
    try:
        available = version('uv')
    except PackageNotFoundError:
        available = None
    if available != UV_VERSION:
        subprocess.run([sys.executable, '-m', 'pip', 'install', f'uv=={UV_VERSION}'], check=True)
    tool = [sys.executable, '-m', 'uv']
    subprocess.run(tool+['python', 'install', PYTHON_VERSION], check=True)
    if not python.exists():
        subprocess.run(tool+['venv', '--python', PYTHON_VERSION, str(output)], check=True)
    subprocess.run(tool+['pip', 'sync', '--python', str(python), '--require-hashes',
                         '--only-binary', ':all:', str(lock)], check=True)
    installed = fingerprint(python)
    if installed['python'] != PYTHON_VERSION:
        raise ValueError('Unexpected interpreter after bootstrap')
    record = {'contract': expected, 'installed': installed, 'status': 'locked_environment_installed'}
    temporary = receipt.with_suffix('.json.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        stream.write(json.dumps(record, indent=2, sort_keys=True)+'\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, receipt)
    print(python)
    return python


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
    parser.add_argument('--output', type=Path, default=Path('/kaggle/working/phase3-env-v2'))
    args = parser.parse_args()
    os.environ.setdefault('UV_CACHE_DIR', '/kaggle/working/.uv-cache')
    bootstrap(args.device, args.output)


if __name__ == '__main__':
    main()
