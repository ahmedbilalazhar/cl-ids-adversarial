"""Sequential multi-group driver (robust launcher; survives shell loss).

Runs each group via scripts/run_grid.py semantics in-process, appending to a
per-group log; skip-if-exists means a re-run resumes. Used to chain long
grids unattended (free-tier/Laptop): `python scripts/run_groups.py c_f2 c_f4`.

THREADING (mandatory when running >1 worker on one machine): each worker is
capped via CL_THREADS (default 2) BEFORE numpy/torch import. Running 5
workers with default 8-thread pools thrashes 8 cores — measured 4.3 h for a
single federated run vs ~100 s capped. Example (4 workers x 2 threads on 8
logical cores):
    $env:CL_THREADS=2; python scripts/run_groups.py c_f2 c_f4
    $env:CL_THREADS=2; python scripts/run_groups.py bz f2r
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    groups = sys.argv[1:]
    if not groups:
        print("usage: run_groups.py <group> [<group> ...]")
        raise SystemExit(2)
    threads = os.environ.get("CL_THREADS", "2")
    env = dict(os.environ)
    for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[var] = threads
    env["CL_THREADS"] = threads
    log = ROOT / "results" / "run_groups.log"
    print(f"CL_THREADS={threads} groups={groups}", flush=True)
    for g in groups:
        t0 = time.time()
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"\n=== {g} start {time.strftime('%H:%M:%S')} threads={threads} ===\n")
            f.flush()
            proc = subprocess.run(
                [sys.executable, "scripts/run_grid.py", g],
                cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, text=True, env=env,
            )
            f.write(f"=== {g} exit={proc.returncode} {(time.time()-t0)/60:.1f} min ===\n")
            f.flush()
        print(f"{g}: exit={proc.returncode} {(time.time()-t0)/60:.1f} min", flush=True)
        if proc.returncode:
            raise SystemExit(f"Stopping group queue after {g} failed with exit={proc.returncode}")


if __name__ == "__main__":
    main()
