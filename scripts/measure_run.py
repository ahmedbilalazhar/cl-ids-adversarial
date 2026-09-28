"""Measure a single command's wall time and sampled process-tree peak RSS.

Example: python scripts/measure_run.py --output results/diagnostics/e4_resource.json -- python -m src.run_experiment ...
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import psutil


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("command required after --")
    started = time.monotonic()
    process = subprocess.Popen(command)
    parent = psutil.Process(process.pid)
    peak = 0
    try:
        while process.poll() is None:
            try:
                processes = [parent, *parent.children(recursive=True)]
                rss = sum(p.memory_info().rss for p in processes if p.is_running())
                peak = max(peak, rss)
            except psutil.Error:
                pass
            time.sleep(0.2)
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        raise
    elapsed = time.monotonic() - started
    result = {
        "command": command, "exit_code": process.returncode,
        "wall_sec": round(elapsed, 3), "sampled_peak_rss_mb": round(peak / 2**20, 2),
        "sample_interval_sec": 0.2, "host": platform.node(),
        "cpu": platform.processor(), "logical_cpus": psutil.cpu_count(logical=True),
        "system_ram_gb": round(psutil.virtual_memory().total / 2**30, 2),
        "created_utc": datetime.now(UTC).isoformat(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return process.returncode


if __name__ == "__main__":
    sys.exit(main())
