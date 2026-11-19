"""Independently summarize observed wall time and checkpoint bytes for the adopted 74-feature runs.

No models are trained. Every result JSON is checked against the completion
manifest, and exact duplicate copies are collapsed before summarization.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "results/phase3-followup-ablation"
AUDIT_PATH = ROOT / "results/phase3-rigorous-audit-v1/followup-independent-audit.json"
OUTPUT = ROOT / "submissions/phase3-audited-report"
EXPECTED_ORIGINAL_SHA256 = "c219925799b2fe3b1d73e4203e25d1f94987b6c401f0288290f5f0bb67a2311f"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def quantiles(values: list[float]) -> dict:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot summarize an empty group")
    return {
        "n": len(ordered),
        "min": ordered[0],
        "median": statistics.median(ordered),
        "p90_nearest_rank": ordered[math.ceil(0.9 * len(ordered)) - 1],
        "max": ordered[-1],
    }


def experiment_key(run: dict) -> tuple:
    settings = run["settings"]
    dose = run["attack"]["dose"]
    return (
        settings["block"], settings["learner"], settings.get("admission", "NONE"),
        int(settings["seed"]), tuple(dose), float(settings["q"]),
        float(settings["lambda_y"]), float(settings["lambda_z"]),
    )


def main() -> None:
    completion = json.loads((RUN_ROOT / "completion-followup.json").read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    if audit["status"] != "passed" or audit["completion_inventory_hashes_valid"] is not True:
        raise RuntimeError("Independent follow-up audit is not passing")
    result_records = {
        rel: expected_hash for rel, expected_hash in completion["files"].items()
        if rel.replace("\\", "/").endswith("/result.json")
    }
    if len(result_records) != audit["completion_inventory_result_files"]:
        raise RuntimeError("Result-path count differs from the independent audit")

    unique: dict[tuple, dict] = {}
    seen_hashes: dict[str, tuple] = {}
    for rel, expected_hash in sorted(result_records.items()):
        path = RUN_ROOT / rel
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            raise RuntimeError(f"Completion-manifest hash mismatch: {rel}")
        run = json.loads(path.read_text(encoding="utf-8"))
        key = experiment_key(run)
        elapsed = float(run["elapsed_seconds"])
        if not math.isfinite(elapsed) or elapsed <= 0:
            raise RuntimeError(f"Invalid elapsed_seconds in {rel}")
        prior = unique.get(key)
        if prior is not None:
            if prior["sha256"] != actual_hash:
                raise RuntimeError(f"Conflicting duplicate result for experiment key {key}")
            prior["copies"] += 1
            continue
        row = {
            "path": rel.replace("\\", "/"), "sha256": actual_hash,
            "block": run["settings"]["block"], "learner": run["settings"]["learner"],
            "admission": run["settings"].get("admission", "NONE"),
            "seed": int(run["settings"]["seed"]),
            "dose": "/".join(map(str, run["attack"]["dose"])),
            "q": float(run["settings"]["q"]),
            "elapsed_seconds": elapsed,
            "compressed_four_stage_checkpoint_bytes": sum(
                int(value) for value in run["serialized_stage_weight_bytes"].values()
            ),
            "copies": 1,
        }
        unique[key] = row
        seen_hashes[actual_hash] = key

    expected_unique = int(audit["unique_full_runs"])
    if len(unique) != expected_unique:
        raise RuntimeError(f"Unique result count {len(unique)} != audited count {expected_unique}")
    exact_duplicate_copies = len(result_records) - len(unique)
    if exact_duplicate_copies != audit["duplicate_cross_directory_copies"]:
        raise RuntimeError("Exact-copy count differs from the independent audit")
    rows = sorted(unique.values(), key=lambda row: (row["block"], row["learner"], row["admission"], row["seed"], row["dose"]))

    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["block"], []).append(row)
    summary = {
        "schema": "phase3-adopted-observed-costs-v1",
        "scope": "adopted 74-feature development trajectories only",
        "unique_result_trajectories": len(rows),
        "result_json_files_in_completion_manifest": len(result_records),
        "exact_duplicate_result_copies_collapsed": exact_duplicate_copies,
        "independent_audit_status": audit["status"],
        "completion_manifest_elapsed_seconds_for_408_run_block": completion["elapsed_seconds"],
        "blocks": {
            block: {
                "unique_trajectories": len(group),
                "elapsed_seconds": quantiles([r["elapsed_seconds"] for r in group]),
                "compressed_four_stage_checkpoint_bytes": quantiles([
                    r["compressed_four_stage_checkpoint_bytes"] for r in group
                ]),
                "settings": sorted({
                    f"{r['learner']}/{r['admission']}" for r in group
                }),
            }
            for block, group in sorted(groups.items())
        },
        "interpretation": (
            "Per-run elapsed_seconds are observed runner wall time, not training-only time; "
            "they may include scoring, checkpoint serialization and orchestration. "
            "Compressed four-stage NPZ sizes are stored artifact sizes, not transmitted "
            "message sizes. The completion manifest's 32,655.01 seconds covers its "
            "408-run follow-up execution count and is reported separately from the "
            "417 unique result inventory, which also includes nine clean confirmations."
        ),
        "not_measured": [
            "training/admission/replay/Fisher/aggregation/evaluation wall time by component",
            "process peak RSS and complete allocated client state",
            "serialized upload/download framing, labels, registry and protocol metadata",
            "network delay, edge device runtime, and energy",
        ],
        "source_completion_manifest_sha256": sha256(RUN_ROOT / "completion-followup.json"),
        "source_independent_audit_sha256": sha256(AUDIT_PATH),
        "frozen_original_submission_sha256": EXPECTED_ORIGINAL_SHA256,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT / "observed-run-costs.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path = OUTPUT / "observed-run-costs-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    order = ["clean-confirmation", "core", "matched-random", "replay-loss", "quota"]
    present = [block for block in order if block in groups]
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    data = [[r["elapsed_seconds"] for r in groups[block]] for block in present]
    ax.boxplot(data, tick_labels=[f"{b}\n(n={len(groups[b])})" for b in present],
               showfliers=True, whis=(10, 90), patch_artist=True,
               boxprops={"facecolor": "#d9e8f3", "edgecolor": "#20639b"},
               medianprops={"color": "#c64a4a", "linewidth": 1.5},
               whiskerprops={"color": "#20639b"}, capprops={"color": "#20639b"},
               flierprops={"marker": ".", "markersize": 3, "alpha": 0.5})
    ax.set_yscale("log")
    ax.set_ylabel("Observed wall time per trajectory (seconds; log scale)")
    ax.set_title("Adopted 74-feature development runs: observed elapsed time")
    ax.grid(axis="y", which="both", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT / "figures/observed-run-time.pdf")
    plt.close(fig)
    print(json.dumps({"summary": str(json_path), "csv": str(csv_path),
                      "figure": str(OUTPUT / "figures/observed-run-time.pdf"),
                      "unique_trajectories": len(rows),
                      "duplicate_result_copies": exact_duplicate_copies,
                      "blocks": summary["blocks"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
