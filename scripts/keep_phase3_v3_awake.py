"""Temporary Windows idle-sleep inhibition tied to one known worker process."""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import time
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pid', type=int, required=True)
    p.add_argument('--max-seconds', type=int, default=21600)
    p.add_argument('--status', type=Path, required=True)
    args = p.parse_args()
    if os.name != 'nt' or args.pid <= 0 or args.max_seconds <= 0:
        raise ValueError('A live Windows worker PID and positive bounded duration are required')
    if args.status.exists() or args.status.with_suffix('.completed.json').exists():
        raise FileExistsError(args.status)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.SetThreadExecutionState.argtypes = [wintypes.DWORD]
    kernel.SetThreadExecutionState.restype = wintypes.DWORD
    handle = kernel.OpenProcess(0x1000, False, args.pid)
    if not handle:
        raise OSError(ctypes.get_last_error(), 'Cannot open the named worker process')
    request = {'schema': 'phase3-temporary-idle-guard-v1', 'target_pid': args.pid,
               'started_utc': datetime.now(UTC).isoformat(), 'maximum_seconds': args.max_seconds,
               'scope': 'ES_SYSTEM_REQUIRED on this helper thread only; display may turn off; no persistent power-policy edit; manual sleep still possible'}
    deadline = time.monotonic()+args.max_seconds
    reason = 'worker_ended'
    try:
        if not kernel.SetThreadExecutionState(0x80000001):
            raise OSError(ctypes.get_last_error(), 'Temporary idle-sleep request failed')
        args.status.parent.mkdir(parents=True, exist_ok=True)
        args.status.write_text(json.dumps(request, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'status': 'temporary_idle_guard_active', 'target_pid': args.pid}), flush=True)
        while time.monotonic() < deadline:
            exit_code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)) or exit_code.value != 259:
                break
            time.sleep(5)
        else:
            reason = 'bounded_duration_expired'
    finally:
        kernel.SetThreadExecutionState(0x80000000)
        kernel.CloseHandle(handle)
    args.status.with_suffix('.completed.json').write_text(json.dumps({**request, 'ended_utc': datetime.now(UTC).isoformat(),
               'status': reason, 'temporary_request_released': True}, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
