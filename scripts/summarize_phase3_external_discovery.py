"""Aggregate registered external discovery runs without pooling datasets or flows."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = [ROOT / "results/phase3-followup/external-discovery-v2.json"]


def mean_sd(values):
    return {"mean": statistics.mean(values), "sd_across_seeds": statistics.stdev(values) if len(values) > 1 else None}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=Path("results/phase3-followup/external-discovery-summary-v2.json"))
    args = ap.parse_args()
    parts = [json.loads(p.read_text(encoding="utf-8")) for p in INPUTS]
    config_hashes = {p["config_sha256"] for p in parts}
    if len(config_hashes) != 1:
        raise ValueError("External run configs differ")
    rows = [row for part in parts for row in part["rows"]]
    seeds = sorted({row["seed"] for row in rows})
    if seeds != [1, 42, 101]:
        raise ValueError(f"Expected all registered seeds [1, 42, 101], found {seeds}")
    summary = {}
    for dataset in sorted({row["dataset"] for row in rows}):
        dr = [row for row in rows if row["dataset"] == dataset]
        tasks = sorted({row["task"] for row in dr})
        by_seed, by_task = {}, {}
        for task in tasks:
            tr = [row for row in dr if row["task"] == task]
            if {row["seed"] for row in tr} != set(seeds):
                raise ValueError(f"Missing seed for {dataset} task {task}")
            by_task[str(task)] = {
                "attack_flagged_rate": mean_sd([row["metrics"]["attack_flagged_rate"] for row in tr]),
                "benign_false_alert_rate": mean_sd([row["metrics"]["benign_false_alert_rate"] for row in tr]),
                "cluster_assignment_ari": mean_sd([row["metrics"]["cluster_assignment_ari"] for row in tr]),
                "n_external_holdout": tr[0]["n_external_holdout"],
                "n_attack_holdout": tr[0]["metrics"]["n_attack_test"],
                "n_benign_holdout": tr[0]["metrics"]["n_benign_test"],
            }
        for seed in seeds:
            sr = [row for row in dr if row["seed"] == seed]
            by_seed[str(seed)] = {
                "equal_task_attack_flagged_rate": statistics.mean(row["metrics"]["attack_flagged_rate"] for row in sr),
                "equal_task_benign_false_alert_rate": statistics.mean(row["metrics"]["benign_false_alert_rate"] for row in sr),
                "equal_task_cluster_assignment_ari": statistics.mean(row["metrics"]["cluster_assignment_ari"] for row in sr),
            }
        summary[dataset] = {
            "aggregation": "equal weight over four tasks; means and SD across three model/calibration seeds",
            "tasks": by_task,
            "equal_task_metrics": {
                key: mean_sd([v[key] for v in by_seed.values()])
                for key in ("equal_task_attack_flagged_rate", "equal_task_benign_false_alert_rate", "equal_task_cluster_assignment_ari")
            },
            "per_seed": by_seed,
        }
    result = {"schema": "phase3-external-discovery-summary-v1", "status": "exploratory_independent_dataset_replication",
              "config_sha256": next(iter(config_hashes)), "seeds": seeds, "datasets": summary,
              "pooling": "No cross-dataset pooling; no duplicate flow pooling across seeds.",
              "limitations": parts[0]["limitations"]}
    out = args.output if args.output.is_absolute() else ROOT / args.output
    if out.exists():
        raise FileExistsError(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    for name, data in summary.items():
        m = data["equal_task_metrics"]
        print(name, "attack", m["equal_task_attack_flagged_rate"],
              "benign_FAR", m["equal_task_benign_false_alert_rate"],
              "ARI", m["equal_task_cluster_assignment_ari"])
    print(out)


if __name__ == "__main__":
    main()
