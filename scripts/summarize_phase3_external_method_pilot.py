"""Build a hash-checked inventory of the external train-only method pilot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results/phase3-followup/external-method-training-pilot-v1"
OUT = ROOT / "results/phase3-followup/external-method-training-pilot-summary-v1.json"
PROTOCOL = ROOT / "configs/phase3/external-method-extension-v1.json"
RUNNER = ROOT / "scripts/run_phase3_external_method_trainpilot.py"
SOURCES = [RUNNER, ROOT / "src/phase3_external/model.py",
           ROOT / "src/phase3_v2/learning.py", ROOT / "src/phase3/reference.py",
           ROOT / "src/phase3/common.py"]
EXPECTED = {
    (dataset, seed, learner, admission, condition)
    for dataset in ("UNSW-NB15", "CICIoT2023")
    for seed in (101, 202, 303)
    for learner, admission in (("FT", "NONE"), ("EI", "NONE"), ("DR", "NONE"), ("DR", "DC"))
    for condition in ("clean", "poisoned")
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    summary_path = OUT_DIR / "summary.json"
    execution = json.loads(summary_path.read_text(encoding="utf-8"))
    if execution.get("status") != "completed_train_only_pilot_no_test_metrics":
        raise ValueError("Pilot execution summary is incomplete")
    if execution.get("external_test_arrays_accessed") is not False or execution.get("cicids_final_test_accessed") is not False or execution.get("test_metrics_computed") is not False:
        raise ValueError("Pilot execution summary violates the no-test boundary")
    arms = []
    observed = set()
    for run_path in sorted(OUT_DIR.rglob("run.json")):
        run = json.loads(run_path.read_text(encoding="utf-8"))
        key = (run["dataset"], run["seed"], run["learner"], run["admission"], run["condition"])
        if key in observed:
            raise ValueError(f"Duplicate pilot arm: {key}")
        observed.add(key)
        if run.get("seed") not in {101, 202, 303} or len(run.get("stages", [])) != 4:
            raise ValueError(f"Unexpected seed/task count in {run_path}")
        if run.get("external_test_arrays_accessed") is not False or run.get("cicids_final_test_accessed") is not False or run.get("test_metrics_computed") is not False:
            raise ValueError(f"Test boundary violation in {run_path}")
        if digest(PROTOCOL) != run["protocol_sha256"]:
            raise ValueError("Protocol changed after the train-only pilot")
        stem = "unsw" if run["dataset"] == "UNSW-NB15" else "iot"
        dataset_meta = ROOT / f"data/processed/tasks_{stem}.json"
        dataset_npz = ROOT / f"data/processed/tasks_{stem}.npz"
        meta = json.loads(dataset_meta.read_text(encoding="utf-8"))
        if digest(dataset_npz) != run["dataset_artifact_sha256"] or meta["npz_sha256"] != run["dataset_artifact_sha256"]:
            raise ValueError(f"Dataset artifact changed after training: {run['dataset']}")
        input_dir = ROOT / "results/phase3-followup/external-method-inputs-v2" / stem / f"seed-{run['seed']}"
        input_manifest = input_dir / "manifest.json"
        input_artifact = input_dir / "train-ownership-poison-mask.npz"
        if digest(input_manifest) != run["training_input_manifest_sha256"] or digest(input_artifact) != run["training_input_artifact_sha256"]:
            raise ValueError(f"Synthetic training input changed after training: {key}")
        for checkpoint in run["stage_checkpoints"]:
            path = run_path.parent / f"stage-{checkpoint['stage']}-model.npz"
            if digest(path) != checkpoint["file_sha256"]:
                raise ValueError(f"Checkpoint hash mismatch: {path}")
        poison_rows = sum(stage["poisoned_rows"] for stage in run["stages"])
        source_rows = sum(stage["clean_source_rows"] for stage in run["stages"])
        arms.append({"dataset": run["dataset"], "learner": run["learner"],
                     "admission": run["admission"], "condition": run["condition"],
                     "seed": run["seed"], "tasks": len(run["stages"]),
                     "training_rows_across_tasks": sum(stage["train_rows"] for stage in run["stages"]),
                     "task1_source_rows_on_attacker": source_rows if run["condition"] == "poisoned" else None,
                     "task1_poisoned_rows": poison_rows,
                     "elapsed_seconds": run["elapsed_seconds"],
                     "final_model_sha256": run["stages"][-1]["model_sha256"],
                     "run_json_sha256": digest(run_path),
                     "checkpoint_files_sha256": [x["file_sha256"] for x in run["stage_checkpoints"]],
                     "external_test_arrays_accessed": False,
                     "test_metrics_computed": False,
                     "run_file": run_path.relative_to(ROOT).as_posix()})
    if observed != EXPECTED:
        raise ValueError(f"Pilot arm inventory mismatch; missing={EXPECTED-observed}, extra={observed-EXPECTED}")
    intervention = []
    for dataset in ("UNSW-NB15", "CICIoT2023"):
        for seed in (101, 202, 303):
            paired = [r for r in arms if r["dataset"] == dataset and r["seed"] == seed
                      and r["condition"] == "poisoned"]
            if len(paired) != 4 or len({(r["task1_source_rows_on_attacker"], r["task1_poisoned_rows"]) for r in paired}) != 1:
                raise ValueError(f"Paired method arms disagree on one intervention mask: {dataset}/{seed}")
            source, poisoned = paired[0]["task1_source_rows_on_attacker"], paired[0]["task1_poisoned_rows"]
            if poisoned * 2 not in {source, source - 1}:
                raise ValueError(f"Intervention is not a deterministic half-dose: {dataset}/{seed}")
            intervention.append({"dataset": dataset, "seed": seed,
                                 "attacker_task1_source_rows": source,
                                 "relabeled_source_rows": poisoned,
                                 "realized_dose": [poisoned, source]})
    output = {
        "schema": "phase3-external-method-training-pilot-inventory-v1",
        "status": "complete_train_only_execution_test_scoring_gated",
        "study_type": "one-seed simulated-client benchmark extension; not a faithful external replication",
        "completed_arms": len(arms),
        "task_stage_checkpoints": sum(x["tasks"] for x in arms),
        "datasets": ["UNSW-NB15", "CICIoT2023"],
        "methods": ["FT", "EI", "DR", "DR+DC"],
        "seeds": [101, 202, 303],
        "intervention_by_dataset_seed": intervention,
        "total_successful_arm_runtime_seconds": sum(x["elapsed_seconds"] for x in arms),
        "runtime": execution["runtime"],
        "protocol_sha256": digest(PROTOCOL),
        "source_sha256_at_inventory_time": {p.relative_to(ROOT).as_posix(): digest(p) for p in SOURCES},
        "source_hash_timing_note": "Runner orchestration gained resumable-arm handling after the first batch; train_client, model architecture, datasets, and completed arm-level protocol settings were unchanged. Runner hash is therefore the post-resume source hash, not a claim that all orchestration bytes were identical for every arm.",
        "arms": arms,
        "feature_arrays_accessed": True,
        "training_arrays_only": True,
        "external_test_arrays_accessed": False,
        "cicids_final_test_accessed": False,
        "test_metrics_computed": False,
        "result_interpretation": "Execution and numerical-path evidence only. Single seed, synthetic client ownership, and no held-out evaluation; no effectiveness or generalization conclusion is supported.",
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUT.relative_to(ROOT).as_posix(), "completed_arms": len(arms),
                      "stage_checkpoints": output["task_stage_checkpoints"],
                      "runtime_seconds": round(output["total_successful_arm_runtime_seconds"], 2),
                      "test_metrics_computed": False}, indent=2))


if __name__ == "__main__":
    main()
