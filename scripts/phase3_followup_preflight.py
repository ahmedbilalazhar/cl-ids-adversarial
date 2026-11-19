"""Read-only readiness audit for Phase 3 follow-up studies.

Does not load feature/label arrays and never opens final-test records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = ROOT / "data/processed"
    unsw = read_json(data / "tasks_unsw.json")
    iot = read_json(data / "tasks_iot.json")
    common = sorted(set(unsw["feature_cols"]) & set(iot["feature_cols"]))
    prep_dir = data / "phase3-reference74-v1"
    prep = read_json(prep_dir / "preparation-report.json")
    train = read_json(prep_dir / "train/manifest.json")
    dev = read_json(prep_dir / "development/manifest.json")
    phase3_protocol = read_json(ROOT / "configs/phase3/cpu-v3.json")
    reference_protocol = read_json(ROOT / "configs/phase3/reference74-v1.json")
    evaluator_source = (ROOT / "src/phase3_v2/evaluate.py").read_text(encoding="utf-8")
    external_result = ROOT / "results/phase3-followup/external-discovery-summary-v2.json"
    discovery_result = ROOT / "results/phase3-followup/discovery-development-sensitivity-v2.json"
    assignment_result = ROOT / "results/phase3-followup/discovery-development-assignment-v1.json"
    assignment_summary = ROOT / "results/phase3-followup/discovery-development-assignment-summary-v1.json"
    replicate_summary = ROOT / "results/phase3-followup/discovery-development-replicates-summary-v1.json"
    compatibility_audit = ROOT / "results/phase3-followup/external-full-method-compatibility-v1.json"
    compatibility = read_json(compatibility_audit) if compatibility_audit.is_file() else {}
    extension_protocol_path = ROOT / "configs/phase3/external-method-extension-v1.json"
    extension_protocol = read_json(extension_protocol_path) if extension_protocol_path.is_file() else {}
    external_method_summary_path = ROOT / "results/phase3-followup/external-method-training-pilot-summary-v1.json"
    external_method_summary = read_json(external_method_summary_path) if external_method_summary_path.is_file() else {}
    support_audit_path = ROOT / "results/phase3-followup/external-training-support-audit-v1.json"
    id_audit_path = ROOT / "results/phase3-followup/external-id-isolation-audit-v1.json"
    support_audit = read_json(support_audit_path) if support_audit_path.is_file() else {}
    id_audit = read_json(id_audit_path) if id_audit_path.is_file() else {}
    result = {
        "scope": "read-only preflight; no feature or label arrays loaded",
        "external_replication": {
            "status": "discovery_submodule_replicated_full_method_protocol_required"
            if external_result.is_file() else "protocol_required",
            "datasets": ["UNSW-NB15", "CICIoT2023"],
            "features": {"unsw": len(unsw["feature_cols"]), "iot": len(iot["feature_cols"]), "shared_names": len(common)},
            "result_summary_present": external_result.is_file(),
            "full_method_compatibility_audit_present": compatibility_audit.is_file(),
            "full_method_status": compatibility.get("status", "not_audited"),
            "full_method_blocker_count": len(compatibility.get("blockers", [])),
            "prospective_extension_status": extension_protocol.get("status", "not_drafted"),
            "train_label_support_audit_present": support_audit_path.is_file(),
            "source_support_feasible_by_dataset": {
                item["dataset"]: item["feasible_for_source_to_benign_pilot"]
                for item in support_audit.get("datasets", [])
            },
            "task_id_audit_present": id_audit_path.is_file(),
            "train_and_test_task_ids_disjoint_by_dataset": {
                item["dataset"]: item["train_task_ids_disjoint"] and item["test_task_ids_disjoint"]
                for item in id_audit.get("datasets", [])
            },
            "train_only_method_pilot_summary_present": external_method_summary_path.is_file(),
            "train_only_method_pilot_status": external_method_summary.get("status", "not_run"),
            "train_only_method_pilot_completed_arms": external_method_summary.get("completed_arms", 0),
            "train_only_method_pilot_test_scoring_performed": external_method_summary.get("test_metrics_computed"),
            "note": "The full-method adapter has a one-seed train-only simulated-client pilot; no held-out test metrics exist and the protocol remains an external benchmark extension.",
        },
        "cross_dataset_transfer": {
            "status": "blocked_pending_semantic_feature_bridge",
            "shared_feature_names": common,
            "note": "Both source schemas mark units undocumented; feature-name overlap alone would not prove equivalence.",
        },
        "unlabeled_discovery": {
            "status": "development_pilot_sensitivity_assignment_ablation_and_three_partitions_complete"
            if discovery_result.is_file() else "development_protocol_required",
            "development_manifest_present": (prep_dir / "development/manifest.json").is_file(),
            "development_sensitivity_result_present": discovery_result.is_file(),
            "assignment_ablation_result_present": assignment_result.is_file(),
            "assignment_ablation_three_partition_summary_present": assignment_summary.is_file(),
            "partition_replicate_summary_present": replicate_summary.is_file(),
            "note": "Three component partitions, threshold/cap sensitivity, and one assignment-rule ablation are recorded; all remain exploratory.",
        },
        "final_test": {
            "status": "sealed_not_ready" if (
                prep.get("test_rows_exported", 0) == 0
                or not phase3_protocol.get("dispatchable_gpu_grid", False)
                or not phase3_protocol.get("final_test_evaluation_authorized", False)
            ) else "requires_separate_package_audit",
            "reported_test_rows_exported": prep.get("test_rows_exported"),
            "train_manifest_test_rows": train.get("final_test_feature_rows_exported"),
            "development_manifest_test_rows": dev.get("final_test_rows_exported"),
            "test_package_directory_present": (prep_dir / "final_test").is_dir(),
            "dispatchable_gpu_grid": phase3_protocol.get("dispatchable_gpu_grid"),
            "final_test_evaluation_authorized": phase3_protocol.get("final_test_evaluation_authorized"),
            "sealed_final_seed_count": len(phase3_protocol.get("final_seeds_sealed", [])),
            "reference_protocol_settings_status": reference_protocol.get("settings_status"),
            "reference_protocol_remaining_gates": reference_protocol.get("remaining_grid_gates", []),
            "existing_evaluator_scope": "development_only" if (
                "manifest['role'] != 'development_only'" in evaluator_source
                and "Only the pinned development bank is accepted" in evaluator_source
            ) else "needs_source_review",
            "blockers": [
                "No final-test features or labels are exported; no isolated final_test package exists.",
                "Final-test evaluation is explicitly unauthorized and the GPU grid is not dispatchable.",
                "The reference74 configuration is an untuned implementation reference, not a selected final setting.",
                "The available evaluator accepts only the pinned development-only manifest; a separate final evaluator is absent.",
                "Protocol-listed scientific, scope, runtime, and analysis gates remain unresolved.",
            ],
            "note": "Metadata and evaluator source only; no final-test package, arrays, or rows were opened.",
        },
    }
    rendered = json.dumps(result, indent=2) + "\n"
    print(rendered, end="")
    if args.output:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
