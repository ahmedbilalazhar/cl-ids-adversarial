"""Small-case exact-vs-capped HDBSCAN sensitivity for the E4 training path."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import yaml
from sklearn.metrics import adjusted_rand_score

from src.discovery.pipeline import fit_discovery, fit_threshold, recon_scores
from src.runner import train_autoencoder
from src.tasks import load_or_build_tasks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/novelty/e4_novelty_nopois_c.yaml"))
    parser.add_argument("--task", type=int, default=2)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--reference-size", type=int, default=1500)
    parser.add_argument("--cap", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path("results/diagnostics/e4_cluster_cap_sensitivity.json"))
    args = parser.parse_args()
    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    cfg["seed"] = args.seed
    tasks, _ = load_or_build_tasks(cfg)
    task = tasks[args.task]
    X, y = task["X_train"], task["y_train"]
    benign = np.flatnonzero(y == 0)
    if len(benign) < 2:
        raise ValueError("separate benign fitting and calibration rows are required")
    shuffled = np.random.RandomState(args.seed + args.task).permutation(benign)
    n_cal = max(1, len(shuffled) // 5)
    started = time.monotonic()
    ae = train_autoencoder(X[shuffled[n_cal:]], X.shape[1], "cpu", args.seed + args.task)
    threshold = fit_threshold(recon_scores(ae, X[shuffled[:n_cal]]))
    candidate = np.flatnonzero(recon_scores(ae, X) >= threshold)
    if len(candidate) < args.reference_size or args.cap >= args.reference_size:
        raise ValueError("need more novel candidates than the reference size, and cap < reference size")
    reference = np.sort(np.random.RandomState(args.seed + 10_000).choice(
        candidate, size=args.reference_size, replace=False,
    ))
    X_ref = X[reference]
    poison = np.zeros(len(X_ref), dtype=bool)
    exact = fit_discovery(
        ae, threshold, X_ref, poison, min_cluster_size=15,
        max_cluster_candidates=args.reference_size, seed=args.seed,
    )
    capped = fit_discovery(
        ae, threshold, X_ref, poison, min_cluster_size=15,
        max_cluster_candidates=args.cap, seed=args.seed,
    )
    exact_labels = exact["train_labels"]
    capped_labels = capped["train_labels"]
    result = {
        "config": str(args.config), "seed": args.seed, "task": args.task,
        "n_full_train": len(X), "n_full_novel": len(candidate),
        "reference_size": args.reference_size, "cap": args.cap,
        "exact_clusters": len(exact["centers"]), "capped_clusters": len(capped["centers"]),
        "exact_assigned_fraction": float((exact_labels >= 0).mean()),
        "capped_assigned_fraction": float((capped_labels >= 0).mean()),
        "adjusted_rand_index": float(adjusted_rand_score(exact_labels, capped_labels)),
        "wall_sec": round(time.monotonic() - started, 3),
        "note": "Seeded training-candidate subset only; this does not validate the full 4000-candidate cap or a poisoning effect.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
