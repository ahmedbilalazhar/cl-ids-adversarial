"""Training CLI — thin entry point (``python -m src.run_experiment``).

Orchestration lives in :mod:`src.runner`, persistence in
:mod:`src.reporting`. All public names are re-exported here so existing
imports (``scripts/run_grid.py``, ``src/federated/fedavg.py``) keep working.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from src.methods import METHODS
from src.paths import RESULTS_DIR, find_config, runs_dir
from src.reporting import append_table, rebuild_table, save_results
from src.runner import run
from src.tasks import filter_ci, load_or_build_tasks

__all__ = [
    "METHODS",
    "append_table",
    "filter_ci",
    "load_or_build_tasks",
    "rebuild_table",
    "run",
    "save_results",
]


def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, help="config YAML path or bare config name")
    ap.add_argument("--rebuild-table", action="store_true")
    args = ap.parse_args()
    if args.rebuild_table:
        rebuild_table(RESULTS_DIR)
        return
    if not args.config:
        ap.error("--config required unless --rebuild-table")
    cfg_path = args.config
    if not cfg_path.exists() and cfg_path.suffix not in (".yaml", ".yml"):
        cfg_path = find_config(str(cfg_path))
    cfg = load_config(cfg_path)
    result = run(cfg)
    save_results(result, cfg, runs_dir())
    append_table(result, cfg, RESULTS_DIR)


if __name__ == "__main__":
    main()
