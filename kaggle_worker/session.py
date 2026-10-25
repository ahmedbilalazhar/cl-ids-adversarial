"""Standard-library notebook scheduling, command receipts and consistent exports."""
from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import signal
import subprocess
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path


def positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError('Positive finite '+name+' required')


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save_receipt(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


@dataclass(frozen=True)
class SessionBudget:
    seconds: float
    export_reserve: float
    started: float
    clock: object = time.monotonic

    def __post_init__(self):
        positive(self.seconds, 'session budget')
        positive(self.export_reserve, 'export reservation')
        if (self.export_reserve >= self.seconds or type(self.started) not in (int, float)
                or not math.isfinite(self.started) or not callable(self.clock)):
            raise ValueError('Invalid session clock or reservation')

    def available(self):
        now = self.clock()
        if type(now) not in (int, float) or not math.isfinite(now) or now < self.started:
            raise ValueError('Session clock regressed or is invalid')
        return max(0., self.seconds-(now-self.started)-self.export_reserve)

    def job_seconds(self, minimum):
        positive(minimum, 'minimum job bound')
        available = self.available()
        return available if available > minimum else 0.


@contextlib.contextmanager
def file_lock(path):
    """Shared worker/export OS lock; released by the kernel after process exit."""
    with Path(path).open('a+b') as handle:
        if os.name == 'nt':
            import msvcrt
            handle.seek(0)
            if not handle.read(1):
                handle.write(b'0')
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            if os.name == 'nt':
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


class CommandFailed(RuntimeError):
    def __init__(self, receipt):
        self.receipt = receipt
        super().__init__(receipt['module']+': '+receipt['outcome']+'; inspect the retained command log')


def stop_process(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def run_logged(command, module, output, cwd, env, timeout):
    """One immutable attempt, including launch/timeout failures; no shell command."""
    positive(timeout, 'command timeout')
    if type(command) is not list or not command or any(type(v) is not str for v in command):
        raise ValueError('Explicit command argument list required')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        prefix = output/f'command-{index:04d}'
        reservation = prefix.with_suffix('.reservation')
        if prefix.with_suffix('.json').exists() or prefix.with_suffix('.log').exists():
            index += 1
            continue
        try:
            with reservation.open('x'):
                pass
            break
        except FileExistsError:
            index += 1
    log, receipt_path = prefix.with_suffix('.log'), prefix.with_suffix('.json')
    began, process, exception = time.perf_counter(), None, None
    outcome, returncode = 'launch_failed', None
    try:
        with log.open('x', encoding='utf-8') as stream:
            try:
                process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                           stdout=stream, stderr=subprocess.STDOUT,
                                           start_new_session=os.name != 'nt',
                                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
                returncode = process.wait(timeout=timeout)
                outcome = 'succeeded' if returncode == 0 else 'failed'
            except BaseException as exc:
                exception = exc
                if process is not None:
                    stop_process(process)
                    returncode = process.returncode
                outcome = 'timed_out' if isinstance(exc, subprocess.TimeoutExpired) else (
                    'interrupted' if isinstance(exc, KeyboardInterrupt) else 'launch_failed')
                stream.write('\nRetained command failure: '+type(exc).__name__+'\n')
    finally:
        receipt = {'schema': 'kaggle-command-attempt-v2', 'module': module, 'argv': command,
                   'outcome': outcome, 'returncode': returncode,
                   'subprocess_wall_seconds': time.perf_counter()-began,
                   'timeout_seconds': timeout, 'log_sha256': sha256(log),
                   'exception': None if exception is None else type(exception).__name__,
                   'scope': 'Complete subprocess wall time, including interpreter startup and all work of the named module',
                   'final_dispatchable': False}
        save_receipt(receipt_path, receipt)
    if isinstance(exception, KeyboardInterrupt):
        raise exception
    if outcome != 'succeeded':
        raise CommandFailed(receipt) from exception
    return receipt


def inventory(root):
    files = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('Export source contains an escaping or symbolic path')
        if path.is_file():
            name = path.relative_to(root).as_posix()
            if any(character in name for character in ('\\', ':', '\x00')):
                raise ValueError('Export filename is not portable')
            # OS mutex bytes are not trajectory state; Windows prevents reading
            # their locked byte through another handle while the lock is held.
            if path.name == 'worker.lock':
                continue
            files[name] = path
    return files


def export_outputs(output, destination):
    """Consistent, immutable export; a complete adjacent receipt marks success."""
    output, destination = Path(output).resolve(), Path(destination).resolve()
    if not output.is_dir() or destination.is_relative_to(output):
        raise ValueError('Export destination must be outside the existing output tree')
    destination.mkdir(parents=True, exist_ok=True)
    inventory(output)  # Reject links before opening any worker lock.
    started = time.perf_counter()
    with contextlib.ExitStack() as locks:
        for job in sorted(output.rglob('job.json')):
            locks.enter_context(file_lock(job.parent/'worker.lock'))
        files = inventory(output)
        index = 1
        while True:
            archive = destination/f'phase3-qualification-output-{index:04d}.zip'
            if archive.with_suffix('.json').exists():
                index += 1
                continue
            try:
                stream = archive.open('xb')
                break
            except FileExistsError:
                index += 1
        receipt_path = archive.with_suffix('.json')
        try:
            hashes, total = {}, 0
            with stream, zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as container:
                for name, path in files.items():
                    hasher = hashlib.sha256()
                    with path.open('rb') as source, container.open(name, 'w') as target:
                        while block := source.read(8*1024**2):
                            target.write(block)
                            hasher.update(block)
                            total += len(block)
                    hashes[name] = hasher.hexdigest()
            if set(inventory(output)) != set(files) or any(sha256(files[name]) != sha for name, sha in hashes.items()):
                raise ValueError('Output changed while exporting; preserve this attempt and retry')
            result = {'schema': 'kaggle-output-export-v2', 'status': 'complete_export',
                      'archive': archive.name, 'archive_sha256': sha256(archive),
                      'files': hashes, 'uncompressed_bytes': total,
                      'excluded_runtime_files': [p.relative_to(output).as_posix() for p in sorted(output.rglob('worker.lock'))],
                      'export_seconds': time.perf_counter()-started,
                      'provider_durability_qualified': False, 'final_dispatchable': False}
            save_receipt(receipt_path, result)
            return result
        except BaseException as exc:
            if not stream.closed:
                stream.close()
            save_receipt(receipt_path, {'schema': 'kaggle-output-export-v2', 'status': 'failed_export_retained',
                         'archive': archive.name, 'exception': type(exc).__name__, 'message': str(exc),
                         'final_dispatchable': False})
            raise
