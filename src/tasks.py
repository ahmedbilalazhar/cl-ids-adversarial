"""Task-sequence loading with repo-root-relative path resolution."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from src.data.sequence import build_tasks, fit_scaler_on_train, load_tasks
from src.paths import resolve_repo_path as _resolve_repo_path


def load_or_build_tasks(cfg: dict):
    data_cfg = cfg.get("data", {})
    scenario = data_cfg.get("scenario", "cii")
    tasks_path = _resolve_repo_path(Path(data_cfg.get("tasks", "data/processed/tasks.npz")))
    seed = cfg.get("seed", 42)

    if tasks_path.exists():
        tasks, label_map = load_tasks(tasks_path)
        if scenario == "ci":
            tasks = filter_ci(tasks, label_map)
        return tasks, label_map

    clean_path = _resolve_repo_path(Path(data_cfg.get("clean", "data/processed/cicids2017_clean.parquet")))
    if not clean_path.exists():
        raise FileNotFoundError(
            f"Neither {tasks_path} nor {clean_path} found. "
            "Run src.data.clean and src.data.sequence first, or use scripts/smoke_test.py for synthetic data."
        )
    import pandas as pd

    df = pd.read_parquet(clean_path) if clean_path.suffix == ".parquet" else pd.read_csv(clean_path)
    tasks, label_map = build_tasks(df, scenario=scenario, seed=seed)
    tasks = fit_scaler_on_train(tasks)
    return tasks, label_map


def filter_ci(tasks, label_map):
    seen: list[str] = []
    out = []
    for t in tasks:
        for lab in t["labels"]:
            if lab not in seen:
                seen.append(lab)
        allowed = [label_map[x] for x in seen if x in label_map]
        tr = np.isin(t["y_train"], allowed)
        te = np.isin(t["y_test"], allowed)
        nt = dict(t)
        nt["y_train"] = t["y_train"][tr]
        nt["X_train"] = t["X_train"][tr]
        nt["y_test"] = t["y_test"][te]
        nt["X_test"] = t["X_test"][te]
        if "id_train" in t:
            nt["id_train"] = t["id_train"][tr]
            nt["id_test"] = t["id_test"][te]
        out.append(nt)
    return out
