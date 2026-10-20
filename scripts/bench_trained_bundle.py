"""Trained-bundle benchmark on real dims (exploratory, single host).

Trains a small MLP on duplicate-disjoint T0 train rows, exports a versioned
inference bundle, and measures batch-1 latency, throughput, and peak RSS on
this CPU host. Outputs go to results/diagnostics (exploratory only): the
accuracy is a T0 train->test sanity metric, NOT a continual-learning claim,
and latency is host-specific, NOT edge validation.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import inference
from src.data.sequence import load_tasks
from src.models import build_model


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="data/processed/tasks_chrono_dedup.npz")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", type=Path, default=Path("results/diagnostics"))
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    tasks, label_map = load_tasks(ROOT / args.tasks)
    task = tasks[0]
    in_dim = task["X_train"].shape[1]
    n_classes = int(max(label_map.values())) + 1
    feature_cols = [f"f{i}" for i in range(in_dim)]

    model = build_model({"arch": "mlp", "hidden": [128, 64]}, in_dim, n_classes)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    model.train()
    Xtr = torch.from_numpy(task["X_train"])
    ytr = torch.from_numpy(task["y_train"])
    for _ in range(args.epochs):
        perm = torch.randperm(len(Xtr))
        for i in range(0, len(Xtr), args.batch_size):
            idx = perm[i:i + args.batch_size]
            opt.zero_grad()
            loss = torch.nn.functional.cross_entropy(model(Xtr[idx]), ytr[idx])
            loss.backward()
            opt.step()

    # Inputs are already in model space (pre-scaled artifact): the bundle
    # carries identity preprocessing, disclosed in protocol_id.
    zeros = {c: 0.0 for c in feature_cols}
    meta, state = inference.export_bundle(
        model, feature_cols=feature_cols, label_map={k: int(v) for k, v in label_map.items()},
        scaler_mean=[0.0] * in_dim, scaler_scale=[1.0] * in_dim, medians=zeros,
        protocol_id="cicids-T0-finetune-identity-prescaled",
        train_config=f"T0 train rows, {args.epochs} epochs, seed {args.seed}")
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / "trained_mlp_bundle.pt"
    file_sha = inference.save_bundle(bundle_path, meta, state)
    meta2, state2 = inference.load_bundle(bundle_path, expected_file_sha256=file_sha)
    model2 = build_model({"arch": "mlp", "hidden": [128, 64]}, in_dim, n_classes)
    model2.load_state_dict(state2)

    out = inference.predict_batch(meta2, model2, task["X_test"][:2000],
                                  abstain_min_confidence=0.9)
    test_pred = inference.predict_batch(meta2, model2, task["X_test"])
    sanity_acc = float((test_pred["labels"] == task["y_test"]).mean())

    latencies = []
    x1 = task["X_test"][:1]
    model2.eval()
    with torch.no_grad():
        for _ in range(20):
            model2(torch.from_numpy(x1))
        for _ in range(200):
            t0 = time.perf_counter()
            model2(torch.from_numpy(x1))
            latencies.append((time.perf_counter() - t0) * 1000.0)
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p99 = latencies[int(len(latencies) * 0.99) - 1]
    xb = torch.from_numpy(task["X_test"][:256])
    with torch.no_grad():
        t0 = time.perf_counter()
        for _ in range(20):
            model2(xb)
        throughput = 256 * 20 / (time.perf_counter() - t0)
    try:
        import psutil

        proc = psutil.Process()
        rss_before = proc.memory_info().rss
        with torch.no_grad():
            for _ in range(10):
                model2(torch.from_numpy(task["X_test"][:4096]))
        rss_delta_mb = round((proc.memory_info().rss - rss_before) / 1e6, 2)
    except ImportError:
        rss_delta_mb = None

    record = {
        "status": "exploratory single-host benchmark; not a CL claim or edge validation",
        "protocol_id": meta2["protocol_id"],
        "bundle": str(bundle_path),
        "bundle_file_sha256": file_sha,
        "in_dim": in_dim, "n_classes": n_classes,
        "params": sum(p.numel() for p in model2.parameters()),
        "t0_test_sanity_acc": round(sanity_acc, 4),
        "abstained_at_0_9": out["n_abstained"],
        "batch1_latency_ms_p50": round(p50, 4),
        "batch1_latency_ms_p99": round(p99, 4),
        "batch256_throughput_sps": round(throughput, 1),
        "rss_delta_mb": rss_delta_mb,
        "predict_latency_ms_per_sample": round(out["latency_ms_per_sample"], 4),
    }
    record_path = out_dir / "trained_bundle_bench.json"
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
