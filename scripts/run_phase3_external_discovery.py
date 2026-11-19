"""Independent external replication of the label-free discovery submodule."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from src.data.sequence import load_tasks
from src.discovery.pipeline import evaluate_discovery, fit_discovery_unlabeled, fit_threshold, recon_scores
from src.models.mlp import Autoencoder

CONFIG = ROOT / "configs/phase3/external-discovery-replication-v1.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/phase3-followup/external-discovery-v1.json"))
    parser.add_argument("--seeds", type=int, nargs="+", help="Optional subset of preregistered seeds")
    args = parser.parse_args()
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    seeds = args.seeds or cfg["seeds"]
    if any(seed not in cfg["seeds"] for seed in seeds):
        parser.error(f"Seeds must come from the frozen list {cfg['seeds']}")
    torch.set_num_threads(1)
    rows = []
    dataset_provenance = {}
    for dataset, entry in cfg["datasets"].items():
        task_path = ROOT / entry["task_artifact"]
        meta_path = ROOT / entry["metadata"]
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if sha256(task_path) != meta["npz_sha256"]:
            raise ValueError(f"Task artifact hash mismatch for {dataset}")
        tasks, label_map = load_tasks(task_path)
        benign = int(label_map[entry["benign_label"]])
        if benign != int(meta["benign_id"]):
            raise ValueError(f"Benign label ID mismatch for {dataset}")
        dataset_provenance[dataset] = {
            "task_artifact_sha256": sha256(task_path), "metadata_sha256": sha256(meta_path),
            "protocol_id": meta["protocol_id"], "feature_count": len(meta["feature_cols"]),
            "label_map": label_map, "split": meta["split"], "feature_units": meta["feature_units"],
        }
        for seed in seeds:
            for task_id, task in enumerate(tasks):
                x_train = np.asarray(task["X_train"], dtype=np.float32)
                y_train = np.asarray(task["y_train"], dtype=np.int64)
                benign_rows = np.flatnonzero(y_train == benign)
                if len(benign_rows) < 2:
                    raise ValueError(f"Insufficient benign train rows: {dataset} task {task_id}")
                shuffled = np.random.RandomState(seed + task_id).permutation(benign_rows)
                n_cal = max(1, int(len(shuffled) * cfg["benign_training_calibration_fraction"]))
                fit_rows, cal_rows = shuffled[n_cal:], shuffled[:n_cal]
                torch.manual_seed(seed + task_id)
                model = Autoencoder(x_train.shape[1])
                optimizer = torch.optim.Adam(model.parameters(), lr=cfg["autoencoder"]["learning_rate"])
                batch = int(cfg["autoencoder"]["batch_size"])
                fit_order = np.random.RandomState(seed + 1000 + task_id).permutation(fit_rows)
                model.train()
                for _ in range(int(cfg["autoencoder"]["epochs"])):
                    for start in range(0, len(fit_order), batch):
                        xb = torch.from_numpy(x_train[fit_order[start:start + batch]].copy())
                        optimizer.zero_grad(set_to_none=True)
                        loss = torch.mean((model(xb) - xb) ** 2)
                        loss.backward()
                        optimizer.step()
                model.eval()
                threshold = fit_threshold(
                    recon_scores(model, x_train[cal_rows]), float(cfg["threshold_quantile"]),
                )
                cluster_rows = np.ones(len(x_train), dtype=bool)
                cluster_rows[cal_rows] = False
                fitted = fit_discovery_unlabeled(
                    model, threshold, x_train[cluster_rows],
                    min_cluster_size=int(cfg["clustering"]["min_cluster_size"]),
                    max_cluster_candidates=int(cfg["clustering"]["max_fit_candidates"]),
                    seed=seed + task_id,
                )
                y_test = np.asarray(task["y_test"], dtype=np.int64)
                x_test = np.asarray(task["X_test"], dtype=np.float32)
                metrics = evaluate_discovery(model, threshold, fitted, x_test, y_test, benign_label=benign)
                # The shared evaluator's historical “test” fields refer here to each
                # external dataset's supplied held-out task split, never CIC final test.
                rows.append({"dataset": dataset, "seed": seed, "task": task_id,
                             "n_train": len(x_train), "n_benign_fit": len(fit_rows),
                             "n_benign_calibration": len(cal_rows), "n_cluster_fit": int(cluster_rows.sum()),
                             "n_external_holdout": len(y_test),
                             "threshold": threshold, "metrics": metrics})
                print(json.dumps({"dataset": dataset, "seed": seed, "task": task_id,
                                  "attack_flagged_rate": metrics["attack_flagged_rate"],
                                  "benign_false_alert_rate": metrics["benign_false_alert_rate"]}), flush=True)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "phase3-external-discovery-result-v1", "status": "exploratory_independent_dataset_replication",
        "config": cfg, "config_sha256": sha256(CONFIG), "datasets": dataset_provenance,
        "rows": rows, "final_cic_test_accessed": False,
        "limitations": ["Independent refits only; no model or weights transfer across datasets.",
                        "This reproduces only the unsupervised discovery submodule, not the full poisoning/continual-learning claim.",
                        "Source task split conventions differ; component/session disjointness is not established by these metadata.",
                        "All feature units are undocumented; do not compare thresholds or raw scores across datasets."],
    }
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output), "rows": len(rows)}))


if __name__ == "__main__":
    main()
