"""Run the remaining qualified CPU checks sequentially after one active grid."""
from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path

from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v3.development import workflow_lock
from src.phase3_v3.protocol import code_identity

BASE = ROOT/'results/phase3-cpu-v3'
STEPS = (
    ('poison-methods', 'scripts.accept_phase3_v3_poison', (), BASE/'poison-acceptance.json', ('passed',)),
    ('timing', 'scripts.remeasure_phase3_v3', (), BASE/'cost-correction/selection.json', ('complete',)),
    ('matched-diagnostic', 'scripts.match_phase3_v3_diagnostic', (), BASE/'matched-diagnostic/index.json', ('complete', 'diagnostic_failures_retained')),
    ('controls', 'scripts.verify_phase3_v3_controls', (), BASE/'controls/acceptance.json', ('passed',)),
    ('recovery', 'scripts.recover_phase3_v3', (), BASE/'recovery/acceptance.json', ('passed',)),
    ('profiles', 'scripts.profile_phase3_v3', (), BASE/'profiling/jobs.json', ('passed',)),
    ('count-audit', 'scripts.audit_phase3_endpoints', (), ROOT/'results/phase3-endpoint-audit-v1/audit.json', ('passed',)),
    ('report', 'scripts.report_phase3_v3', (), BASE/'completion.json', ('CPU_v3_implemented_verified_and_profiled', 'CPU_v3_diagnostic_failures_retained')),
    ('source-bundle', 'scripts.package_phase3_cpu', ('--output', 'results/phase3-source-bundle-v1/CPU-delivery'),
     ROOT/'results/phase3-source-bundle-v1/CPU-delivery/acceptance.json', ('passed',)),
)


def timestamp():
    return datetime.now(UTC).isoformat()


@contextmanager
def temporary_awake():
    if os.name != 'nt':
        raise OSError('This execution wrapper is qualified for the current Windows host')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.SetThreadExecutionState.argtypes = [wintypes.DWORD]
    kernel.SetThreadExecutionState.restype = wintypes.DWORD
    if not kernel.SetThreadExecutionState(0x80000001):
        raise OSError(ctypes.get_last_error(), 'Temporary system idle request failed')
    try:
        yield
    finally:
        kernel.SetThreadExecutionState(0x80000000)


def wait_for_grid(pid, maximum_seconds):
    # Keep the opened process handle: PID reuse cannot accidentally select a new job.
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        if (BASE/'development/completion.json').exists():
            return
        raise OSError(ctypes.get_last_error(), 'Named grid unavailable without a completion record')
    deadline = time.monotonic()+maximum_seconds
    try:
        while time.monotonic() < deadline:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                raise OSError(ctypes.get_last_error(), 'Cannot inspect named grid')
            if code.value != 259:
                if code.value != 0:
                    raise ChildProcessError(f'Grid process exited {code.value}; no post-grid model job started')
                return
            time.sleep(5)
        raise TimeoutError('Grid still active at bounded wait expiry; no post-grid model job started')
    finally:
        kernel.CloseHandle(handle)


def source_files():
    paths = sorted(set((ROOT/'scripts').glob('*phase3*.py')) | set((ROOT/'tests').glob('test_phase3*.py')))
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--grid-pid', type=int, required=True)
    p.add_argument('--maximum-grid-wait-seconds', type=int, default=21600)
    p.add_argument('--output', type=Path, default=BASE/'post-grid')
    p.add_argument('--resume', action='store_true')
    args = p.parse_args()
    if args.grid_pid <= 0 or args.maximum_grid_wait_seconds <= 0:
        raise ValueError('Positive explicit grid PID and bounded wait required')
    with workflow_lock(args.output), temporary_awake():
        if args.output.exists() and not args.resume:
            raise FileExistsError(args.output)
        args.output.mkdir(parents=True, exist_ok=True)
        identity = code_identity()
        if identity != '38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c':
            raise ValueError('Frozen v3 scientific source changed')
        manifest = source_files()
        plan_path = args.output/'procedure.json'
        plan = {'code_identity': identity, 'source_files': manifest,
                'steps': [{'name': s[0], 'module': s[1], 'arguments': list(s[2]), 'evidence': str(s[3]), 'allowed_status': list(s[4])} for s in STEPS]}
        if plan_path.exists():
            if read_json(plan_path) != plan:
                raise ValueError('Post-grid source/procedure changed; retain previous output and use a new destination')
        else:
            write_json(plan_path, plan)
        status = {'status': 'waiting_for_grid', 'grid_pid': args.grid_pid, 'started_utc': timestamp(), 'completed_steps': [],
                  'temporary_idle_request_scope': 'This controller thread only; released on exit, no persistent power-policy changes'}
        write_json(args.output/'status.json', status)
        print({'status': 'waiting_for_grid', 'pid': args.grid_pid}, flush=True)
        try:
            wait_for_grid(args.grid_pid, args.maximum_grid_wait_seconds)
            complete = read_json(BASE/'development/completion.json')
            if complete['status'] not in ('clean_feasible_development_complete', 'clean_gate_failed_final_grid_blocked'):
                raise ValueError('Declared grid incomplete')
            for index, (name, module, arguments, target, expected) in enumerate(STEPS, 1):
                if code_identity() != identity or source_files() != manifest:
                    raise ValueError('Scientific or delivery source changed during execution')
                receipt = args.output/f'{index:02d}-{name}.json'
                if receipt.exists():
                    prior = read_json(receipt)
                    if prior['status'] != 'passed' or prior['evidence_sha256'] != digest(target):
                        raise ValueError('Completed step receipt changed or failed; no automatic retry')
                    status['completed_steps'].append(name)
                    continue
                log = args.output/f'{index:02d}-{name}.log'
                if log.exists():
                    raise FileExistsError('Unreceipted prior step log retained; investigate before a new attempt')
                status.update({'status': 'running_step', 'active_step': name, 'updated_utc': timestamp()})
                write_json(args.output/'status.json', status)
                print({'status': 'running_step', 'step': name}, flush=True)
                started = time.perf_counter()
                with log.open('x', encoding='utf-8') as stream:
                    child = subprocess.run([sys.executable, '-m', module, *arguments], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False)
                passed = child.returncode == 0 and target.exists() and read_json(target)['status'] in expected
                record = {'status': 'passed' if passed else 'failed', 'module': module, 'exit_code': child.returncode,
                          'ended_utc': timestamp(), 'elapsed_seconds': time.perf_counter()-started, 'log_sha256': digest(log),
                          'evidence': str(target), 'evidence_sha256': digest(target) if target.exists() else None}
                write_json(receipt, record)
                if not passed:
                    raise ChildProcessError(f'Post-grid step failed: {name}; see preserved log {log}')
                status['completed_steps'].append(name)
            status.update({'status': 'passed', 'ended_utc': timestamp(), 'active_step': None})
            write_json(args.output/'status.json', status)
            print({'status': 'passed', 'completed_steps': status['completed_steps']}, flush=True)
        except BaseException as exc:
            status.update({'status': 'failed', 'ended_utc': timestamp(), 'exception': type(exc).__name__, 'message': str(exc)})
            write_json(args.output/'status.json', status)
            raise


if __name__ == '__main__':
    main()
