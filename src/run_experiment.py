"""Training CLI — thin entry point (``python -m src.run_experiment``).

Orchestration lives in :mod:`src.runner`, persistence in
:mod:`src.reporting`. All public names are re-exported here so existing
imports (``scripts/run_grid.py``, ``src/federated/fedavg.py``) keep working.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from src.config_validation import validate_config
from src.methods import METHODS
from src.paths import RESULTS_DIR, find_config, resolve_repo_path
from src.reporting import (
    append_table,
    assert_seed_writable,
    check_artifact,
    rebuild_table,
    save_results,
    source_tree_hash,
)
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


def execute_config(cfg: dict, out_dir: Path, *, resume: bool = False) -> dict | None:
    """Run through the runner declared by the config, then commit one seed."""
    validate_config(cfg)
    name = str(cfg["name"])
    seed = int(cfg.get("seed", 42))
    state = check_artifact(out_dir, name, seed, cfg)
    if state["complete"]:
        if resume:
            print(f"SKIP {name} seed {seed}: validated manifest")
            return None
        raise FileExistsError(f"completed seed already exists: {name}/{seed}; use --resume")
    assert_seed_writable(out_dir, name, seed, cfg)
    code_hash = source_tree_hash()
    if cfg.get("fed"):
        from src.federated.fedavg import run_federated

        result = run_federated(cfg)
    else:
        result = run(cfg)
    save_results(result, cfg, out_dir, expected_code_hash=code_hash)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, help="config YAML path or bare config name")
    ap.add_argument("--rebuild-table", action="store_true")
    ap.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--seed", type=int, help="override the config seed")
    ap.add_argument("--resume", action="store_true", help="skip manifest-validated seeds")
    args = ap.parse_args()
    results_dir = resolve_repo_path(args.results_dir)
    if args.rebuild_table:
        rebuild_table(results_dir)
        return
    if not args.config:
        ap.error("--config required unless --rebuild-table")
    cfg_path = args.config
    if not cfg_path.exists() and cfg_path.suffix not in (".yaml", ".yml"):
        cfg_path = find_config(str(cfg_path))
    cfg = load_config(cfg_path)
    if args.seed is not None:
        cfg["seed"] = args.seed
    execute_config(cfg, results_dir / "runs", resume=args.resume)


if __name__ == "__main__":
    main()
