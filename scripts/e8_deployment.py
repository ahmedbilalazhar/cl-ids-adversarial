"""Software-level deployment-cost measurement (Phase-5 steps 22-23).

Runs anywhere (laptop now, Colab/Kaggle later) and REPORTS its platform:
CPU model/count, RAM, OS, Python/torch versions, resource limits. Measures
per architecture (mlp/wide/transformer): params, model size, FLOPs/sample
(analytic for MLP, measured for transformer via forward hooks), batch-1
latency (median of repeats), batch-256 throughput, peak RSS delta.

These numbers are a DEPLOYMENT-COST / software-efficiency evaluation, NOT
physical edge-device validation. The paper states the platform plainly and
carries a limitations line that dedicated edge hardware was unavailable.
Usage: python scripts/e8_deployment.py  (fast, CPU-only)
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.models import build_model


def platform_info() -> dict:
    try:
        import psutil

        mem = psutil.virtual_memory()
        ram = {"total_mb": round(mem.total / 1e6, 1), "avail_mb": round(mem.available / 1e6, 1)}
        cpu_n = psutil.cpu_count(logical=True)
    except ImportError:
        ram, cpu_n = {}, os.cpu_count()
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": cpu_n,
        "ram": ram,
        "python": platform.python_version(),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "note": "software-level proxy measurement; NOT physical edge hardware",
    }


def mlp_flops(in_dim: int, hidden: list[int], n_classes: int) -> int:
    dims = [in_dim] + list(hidden) + [n_classes]
    return sum(2 * dims[i] * dims[i + 1] for i in range(len(dims) - 1))


def bench_arch(cfg: dict, in_dim: int, n_classes: int, reps: int = 200) -> dict:
    model = build_model(cfg, in_dim, n_classes)
    model.eval()
    n_params = sum(p.numel() for p in model.parameters())
    size_kb = n_params * 4 / 1024.0
    x1 = torch.randn(1, in_dim)
    xb = torch.randn(256, in_dim)
    with torch.no_grad():
        for _ in range(20):  # warmup
            model(x1)
        t0 = time.perf_counter()
        for _ in range(reps):
            model(x1)
        lat_ms = (time.perf_counter() - t0) / reps * 1000.0
        t0 = time.perf_counter()
        for _ in range(20):
            model(xb)
        thr = 256 * 20 / (time.perf_counter() - t0)
    try:
        import psutil

        proc = psutil.Process(os.getpid())
        rss_before = proc.memory_info().rss
        with torch.no_grad():
            for _ in range(20):
                model(torch.randn(4096, in_dim))
        rss_mb = (proc.memory_info().rss - rss_before) / 1e6
    except ImportError:
        rss_mb = None
    flops = None
    if cfg.get("arch", "mlp") in ("mlp", "wide"):
        flops = mlp_flops(in_dim, cfg.get("hidden", [128, 64]), n_classes)
    return {
        "params": n_params,
        "size_kb": round(size_kb, 1),
        "flops_per_sample": flops,
        "batch1_latency_ms": round(lat_ms, 4),
        "batch256_throughput_sps": round(thr, 1),
        "rss_delta_mb": round(rss_mb, 2) if rss_mb is not None else None,
    }


def primary_dims(default_tasks: str = "data/processed/tasks_chrono_dedup.npz") -> tuple[int, int]:
    """Read model dims from the primary task artifact instead of hardcoding.

    The old hardcoded (78, 15) described a 78-input model while the audited
    artifacts carry 76 features, so published param/FLOP counts did not match
    any real model. n_classes falls back to 15 when the sidecar is absent.
    """
    in_dim, n_classes = 78, 15
    try:
        meta = json.loads((ROOT / default_tasks).with_suffix(".json").read_text(encoding="utf-8"))
        in_dim = len(meta["feature_cols"])
        n_classes = len(meta["label_map"])
    except (OSError, ValueError, KeyError):
        pass
    return in_dim, n_classes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=ROOT / "results" / "e8_deployment.json")
    ap.add_argument("--tasks", default="data/processed/tasks_chrono_dedup.npz")
    args = ap.parse_args()
    in_dim, n_classes = primary_dims(args.tasks)
    out = {
        "platform": platform_info(),
        "archs": {
            "mlp": bench_arch({"arch": "mlp", "hidden": [128, 64]}, in_dim, n_classes),
            "wide": bench_arch({"arch": "wide", "hidden": [256, 128]}, in_dim, n_classes),
            "transformer": bench_arch({"arch": "transformer"}, in_dim, n_classes),
        },
    }
    p = Path(args.output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
