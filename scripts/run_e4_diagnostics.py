"""Sequential, resumable three-arm E4 diagnostics with per-seed logs."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml

from src.reporting import check_artifact

CONFIGS = (
    "e4_novelty_nopois_c",
    "e4_novelty_anchor_c",
    "e4_novelty_label_control_c",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--results-dir", type=Path, default=Path("results/diagnostics"))
    args = parser.parse_args()
    if os.environ.get("CL_THREADS") != "2":
        raise ValueError("set CL_THREADS=2 before comparing these diagnostic seeds")
    results_dir = args.results_dir.resolve()
    logs = results_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        for name in CONFIGS:
            config_path = Path("configs/novelty") / f"{name}.yaml"
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            cfg["seed"] = seed
            command = [
                sys.executable, "-m", "src.run_experiment", "--config", str(config_path),
                "--seed", str(seed), "--results-dir", str(results_dir), "--resume",
            ]
            log_path = logs / f"{name}_seed{seed}.log"
            with log_path.open("w", encoding="utf-8") as log:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
            if result.returncode:
                raise RuntimeError(f"{name} seed {seed} failed; see {log_path}")
            state = check_artifact(results_dir / "runs", name, seed, cfg)
            if not state["complete"] or state.get("provenance_level") != "code-hashed":
                raise RuntimeError(f"{name} seed {seed}: {state}; see {log_path}")
            print(f"validated {name} seed {seed} ({state['provenance_level']})", flush=True)


if __name__ == "__main__":
    main()
