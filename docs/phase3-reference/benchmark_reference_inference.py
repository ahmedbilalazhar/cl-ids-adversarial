"""Measure descriptive CPU inference latency on the locked dev bank/checkpoints."""
from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.phase3.common import digest, load_state, read_json, reference_protocol
from src.phase3.model import ReferenceMLP
from src.phase3.reference import model_identity, runtime

PROTOCOL = ROOT / "configs/phase3/reference74-v1.json"
RUN = ROOT / "results/phase3-reference74-v1/reference"
DEV = ROOT / "data/processed/phase3-reference74-v1/development"
OUT = ROOT / "docs/phase3-reference/evidence/inference-latency"
WARMUPS = 10
CALLS = 100
BATCHES = (1, 256)


def percentile(values, q):
    return float(np.quantile(np.asarray(values, dtype=np.float64), q, method="linear"))


def main():
    config = reference_protocol(PROTOCOL)
    environment = runtime(config)
    run = read_json(RUN / "run.json")
    manifest = read_json(DEV / "manifest.json")
    if run["status"] != "complete_reference" or manifest["role"] != "development_only":
        raise RuntimeError("A completed reference and development-only bank are required")
    data = np.load(DEV / "x.npy", mmap_mode="r", allow_pickle=False)
    if data.ndim != 2 or data.shape[1] != 74 or data.shape[0] < max(BATCHES):
        raise RuntimeError("Development input shape differs from the adopted profile")
    checkpoints = [item for item in run["checkpoints"] if item["stage_end"]]
    if len(checkpoints) != 4:
        raise RuntimeError("Expected exactly four stage-final checkpoints")
    OUT.mkdir(parents=True, exist_ok=True)
    observations = []
    model_rows = []
    torch.set_num_threads(1)
    for checkpoint in checkpoints:
        path = RUN / checkpoint["file"]
        if digest(path) != checkpoint["file_sha256"]:
            raise RuntimeError(f"Checkpoint identity changed: {path.name}")
        metadata, arrays = load_state(path)
        slots = metadata["slots"]
        model = ReferenceMLP(len(slots), config["seed"])
        model.load_state_dict({key[6:]: torch.from_numpy(value) for key, value in arrays.items() if key.startswith("model.")})
        model.eval()
        identity = model_identity(model, slots)
        model_rows.append({"stage": checkpoint["stage"], "file": checkpoint["file"],
                           "checkpoint_sha256": checkpoint["file_sha256"], "model_identity": identity,
                           "checkpoint_bytes": path.stat().st_size, "active_head_width": len(slots)})
        for batch_size in BATCHES:
            sample = torch.from_numpy(np.array(data[:batch_size], dtype=np.float32, copy=True))
            with torch.inference_mode():
                for _ in range(WARMUPS):
                    output = model(sample)
                if not torch.isfinite(output).all():
                    raise FloatingPointError("Non-finite benchmark output")
                seconds = []
                for _ in range(CALLS):
                    start = time.perf_counter_ns()
                    output = model(sample)
                    seconds.append((time.perf_counter_ns() - start) / 1e9)
            for trial, value in enumerate(seconds, start=1):
                observations.append({"stage": checkpoint["stage"], "batch_size": batch_size,
                                     "trial": trial, "seconds": value, "model_identity": identity})
    with (OUT / "inference-latency-observations.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(observations[0]))
        writer.writeheader()
        writer.writerows(observations)
    groups = []
    for stage in range(1, 5):
        for batch in BATCHES:
            values = [item["seconds"] for item in observations if item["stage"] == stage and item["batch_size"] == batch]
            groups.append({"stage": stage, "batch_size": batch, "calls": len(values), "warmups": WARMUPS,
                           "median_seconds_per_batch": statistics.median(values),
                           "p95_seconds_per_batch": percentile(values, .95),
                           "mean_seconds_per_batch": statistics.fmean(values),
                           "sample_sd_seconds_per_batch": statistics.stdev(values),
                           "median_seconds_per_record": statistics.median(values) / batch})
    result = {"schema": "phase3-reference-inference-latency-v1", "status": "development_only_descriptive_latency",
              "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "protocol_sha256": digest(PROTOCOL), "run_manifest_sha256": digest(RUN / "run.json"),
              "development_manifest_sha256": digest(DEV / "manifest.json"), "runtime": environment,
              "device": "CPU", "timing_scope": "evaluation-mode forward pass only; excludes preprocessing, loading, network and serialization",
              "batch_sizes": list(BATCHES), "warmups_per_checkpoint_batch": WARMUPS,
              "measured_calls_per_checkpoint_batch": CALLS, "checkpoints": model_rows,
              "summary": groups, "final_test_accessed": False,
              "limitations": ["One CPU, one thread and one model checkpoint per stage; no device/generalization uncertainty.",
                              "No process RSS, allocation, serialized communication, network delay or energy was measured."]}
    (OUT / "inference-latency-summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": groups,
                      "outputs": [str(OUT / "inference-latency-summary.json"), str(OUT / "inference-latency-observations.csv")]}, indent=2))


if __name__ == "__main__":
    main()
