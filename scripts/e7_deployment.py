from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cl.base import set_seed, to_loader
from src.cl.derpp import DERpp
from src.cl.er import ExperienceReplay
from src.cl.ewc import EWC
from src.cl.finetune import FineTune
from src.cl.lwf import LwF
from src.data.sequence import load_tasks
from src.models.mlp import TabularMLP


def peak_rss_mb() -> float:
    try:
        import psutil

        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:
        return float("nan")


def count_params(model: torch.nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def approx_flops(model, in_dim: int) -> int:
    macs = 0
    prev = in_dim
    for m in model.backbone:
        if isinstance(m, torch.nn.Linear):
            macs += prev * m.out_features
            prev = m.out_features
    if hasattr(model, "classifier"):
        macs += prev * model.classifier.out_features
    return int(macs * 2)


def bench(model, X, device: str, n: int = 50, warmup: int = 10) -> float:
    model.eval()
    x = torch.from_numpy(X[:1]).to(device)
    with torch.no_grad():
        for _ in range(warmup):
            model(x)
        if device == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n):
            model(x)
        if device == "cuda":
            torch.cuda.synchronize()
        dt = (time.perf_counter() - t0) / n
    return dt * 1000.0


def main():
    set_seed(42)
    tasks_path = ROOT / "data" / "processed" / "tasks.npz"
    if not tasks_path.exists():
        print("tasks.npz missing; run sequence builder first")
        sys.exit(1)
    tasks, label_map = load_tasks(tasks_path)
    in_dim = tasks[0]["X_train"].shape[1]
    n_classes = int(max(label_map.values())) + 1
    device = "cpu"

    rows = []
    for name, cls, kw in [
        ("finetune", FineTune, {}),
        ("ewc", EWC, {"ewc_lambda": 100.0}),
        ("lwf", LwF, {}),
        ("er", ExperienceReplay, {"buffer_size": 500}),
        ("derpp", DERpp, {"buffer_size": 500}),
        ("joint", FineTune, {}),
    ]:
        set_seed(42)
        model = TabularMLP(in_dim, n_classes, hidden=[128, 64]).to(device)
        method = cls(model, lr=1e-3, device=device, **kw)
        if name == "joint":
            X_all = np.concatenate([t["X_train"] for t in tasks], axis=0)
            y_all = np.concatenate([t["y_train"] for t in tasks], axis=0)
            loader = to_loader(X_all, y_all, batch_size=256)
            method.before_task(0, loader, class_bound=n_classes)
            method.train_task(loader, epochs=1)
        else:
            for t in tasks:
                loader = to_loader(t["X_train"], t["y_train"], batch_size=256)
                bound = int(max(n_classes, t["y_train"].max() + 1))
                method.before_task(0, loader, class_bound=bound)
                method.train_task(loader, epochs=1)
                method.after_task(0, loader)
                break
        rss = peak_rss_mb()
        lat = bench(method.model, tasks[0]["X_test"], device)
        params = count_params(method.model)
        flops = approx_flops(method.model, in_dim)
        rows.append(
            {
                "method": name,
                "params": params,
                "approx_flops_per_sample": flops,
                "infer_latency_ms_batch1": round(lat, 4),
                "peak_rss_mb": round(rss, 1),
                "device": device,
            }
        )
        print(rows[-1])

    out = ROOT / "results" / "e7_deployment.csv"
    out.parent.mkdir(exist_ok=True)
    import csv

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (ROOT / "results" / "e7_deployment.json").write_text(json.dumps(rows, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
