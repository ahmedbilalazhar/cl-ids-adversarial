"""Per-family reconstruction-score audit for E4 tasks (post hoc, exploratory).

Retrains the task autoencoder with the exact runner/audit scheme (benign
80/20 AE-fit/calibration split seeded by seed+task) and reports per-family
score medians plus one-vs-benign AUCs. Answers which T1 family inverts, not
whether to change the q0.95 primary threshold (it must not).

Usage: python scripts/audit_family_scores.py [--seeds 1 2 3]
  [--output results/diagnostics/e4_t1_family.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.discovery.pipeline import recon_scores
from src.runner import train_autoencoder
from src.tasks import load_or_build_tasks


def family_medians(y: np.ndarray, scores: np.ndarray, id_to_name: dict[int, str]) -> dict[str, dict]:
    """Median score + count per class id present in y."""
    out = {}
    for class_id in sorted(set(np.unique(y).tolist())):
        mask = y == class_id
        out[str(class_id)] = {"name": id_to_name.get(int(class_id), str(int(class_id))),
                              "n": int(mask.sum()),
                              "median": float(np.median(scores[mask]))}
    return out


def one_vs_benign_auc(y: np.ndarray, scores: np.ndarray, family_id: int, benign_id: int = 0) -> float | None:
    """AUC of family-vs-benign score ranking; None when either side is empty."""
    mask = (y == family_id) | (y == benign_id)
    if not mask.any():
        return None
    sub_y, sub_s = y[mask], scores[mask]
    if (sub_y == family_id).sum() == 0 or (sub_y == benign_id).sum() == 0:
        return None
    return float(roc_auc_score((sub_y == family_id).astype(int), sub_s))


def task_family_audit(ae, X_test: np.ndarray, y_test: np.ndarray,
                      id_to_name: dict[int, str]) -> dict:
    scores = recon_scores(ae, X_test)
    families = family_medians(y_test, scores, id_to_name)
    aucs = {}
    for class_id in sorted(set(np.unique(y_test).tolist())):
        if int(class_id) == 0:
            continue
        aucs[str(class_id)] = one_vs_benign_auc(y_test, scores, int(class_id))
    return {"families": families, "one_vs_benign_auc": aucs}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/novelty/e4_novelty_nopois_c.yaml"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--output", type=Path,
                        default=Path("results/diagnostics/e4_family_scores.json"))
    args = parser.parse_args()
    base = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    label_map = json.loads(
        (ROOT / base["data"]["tasks"]).with_suffix(".json").read_text(encoding="utf-8")
    )["label_map"]
    id_to_name = {int(v): str(k) for k, v in label_map.items()}
    seeds_out = []
    for seed in args.seeds:
        cfg = dict(base, seed=seed)
        tasks, _ = load_or_build_tasks(cfg)
        per_task = []
        for task_id, task in enumerate(tasks):
            X_train, y_train = task["X_train"], task["y_train"]
            benign = np.flatnonzero(y_train == 0)
            shuffled = np.random.RandomState(seed + task_id).permutation(benign)
            n_cal = max(1, len(shuffled) // 5)
            ae = train_autoencoder(X_train[shuffled[n_cal:]], X_train.shape[1],
                                   "cpu", seed + task_id)
            entry = {"task": task_id, "day": task.get("day", f"t{task_id}")}
            entry.update(task_family_audit(ae, task["X_test"], task["y_test"], id_to_name))
            per_task.append(entry)
        seeds_out.append({"seed": seed, "tasks": per_task})
    output = {
        "status": "post hoc per-family score audit; primary q0.95 threshold unchanged",
        "config": str(args.config),
        "warning": "Exploratory only: no detector selection, no poisoning effect.",
        "seeds": seeds_out,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    for entry in seeds_out:
        t1 = entry["tasks"][1]
        fams = {v["name"]: v["median"] for v in t1["families"].values()}
        print(f"seed {entry['seed']} T1 medians: {fams} auc: {t1['one_vs_benign_auc']}")


if __name__ == "__main__":
    main()
