"""Post hoc detector sensitivity audit; never select a primary threshold here."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import yaml

from src.discovery.pipeline import fit_threshold, recon_scores
from src.runner import train_autoencoder
from src.tasks import load_or_build_tasks

QUANTILES = (0.50, 0.75, 0.90, 0.95, 0.99)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/novelty/e4_novelty_nopois_c.yaml"))
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("results/diagnostics/e4_threshold_sensitivity.json"))
    args = parser.parse_args()
    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    cfg["seed"] = args.seed
    tasks, _ = load_or_build_tasks(cfg)
    rows = []
    for task_id, task in enumerate(tasks):
        X_train, y_train = task["X_train"], task["y_train"]
        benign = np.flatnonzero(y_train == 0)
        shuffled = np.random.RandomState(args.seed + task_id).permutation(benign)
        n_cal = max(1, len(shuffled) // 5)
        ae = train_autoencoder(
            X_train[shuffled[n_cal:]], X_train.shape[1], "cpu", args.seed + task_id,
        )
        calibration = recon_scores(ae, X_train[shuffled[:n_cal]])
        test_scores = recon_scores(ae, task["X_test"])
        y_test = task["y_test"]
        attack = y_test != 0
        benign_test = ~attack
        for quantile in QUANTILES:
            threshold = fit_threshold(calibration, quantile)
            flagged = test_scores >= threshold
            rows.append({
                "task": task_id, "quantile": quantile, "threshold": threshold,
                "n_attack_test": int(attack.sum()),
                "n_benign_test": int(benign_test.sum()),
                "attack_flagged_rate": float(flagged[attack].mean()) if attack.any() else None,
                "benign_false_alert_rate": float(flagged[benign_test].mean()) if benign_test.any() else None,
            })
    output = {
        "status": "post hoc descriptive threshold sensitivity; primary 0.95 threshold unchanged",
        "config": str(args.config), "seed": args.seed, "rows": rows,
        "warning": "Do not choose a new headline threshold using held-out outcomes from this audit.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
