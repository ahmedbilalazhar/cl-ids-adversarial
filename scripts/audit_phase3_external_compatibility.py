"""Read-only compatibility audit for a full-method external replication."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/phase3-followup/external-full-method-compatibility-v1.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    reference = json.loads((ROOT / "configs/phase3/reference74-v1.json").read_text(encoding="utf-8"))
    feature_count = int(reference["data"]["inputs"])
    model_text = (ROOT / "src/phase3/model.py").read_text(encoding="utf-8")
    data_text = (ROOT / "src/phase3_v2/data.py").read_text(encoding="utf-8")
    model_match = re.search(r"nn\.Linear\((\d+),\s*128\)", model_text)
    data_match = re.search(r"\(n,\s*(\d+)\)", data_text)
    if not model_match or not data_match or int(model_match.group(1)) != feature_count or int(data_match.group(1)) != feature_count:
        raise ValueError("Expected locked reference input dimension could not be verified")
    external = {}
    for name in ("unsw", "iot"):
        meta_path = ROOT / f"data/processed/tasks_{name}.json"
        task_path = ROOT / f"data/processed/tasks_{name}.npz"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if sha256(task_path) != meta["npz_sha256"]:
            raise ValueError(f"Task-artifact SHA-256 mismatch: {name}")
        with zipfile.ZipFile(task_path) as archive:
            array_names = archive.namelist()
        external[name] = {
            "protocol_id": meta["protocol_id"],
            "feature_count": len(meta["feature_cols"]),
            "feature_names": meta["feature_cols"],
            "known_feature_units": sum("unknown" not in str(v).lower() for v in meta["feature_units"].values()),
            "label_map": meta["label_map"],
            "task_sizes": meta["task_sizes"],
            "split": meta["split"],
            "row_id_kind": meta["row_ids"],
            "owner_arrays_present": any("owner" in n.lower() for n in array_names),
            "component_or_session_fields_documented": any(k in meta for k in ("component_ids", "session_ids", "groups")),
            "task_artifact_sha256": meta["npz_sha256"],
            "metadata_sha256": sha256(meta_path),
        }

    common_external = sorted(set(external["unsw"]["feature_names"]) & set(external["iot"]["feature_names"]))
    ref_taxonomy = reference["taxonomy"]["source_code_order"]
    blockers = [
        "Reference model and StageInput contracts are fixed to 74 ordered CICIDS features; external inputs have 194 and 39 features.",
        "External task artifacts have no owner arrays, while the reference requires five persistent client owners.",
        "External sidecars contain source-row identifiers but no component/session group field corresponding to the reference's session/content graph split.",
        "The external label taxonomies and task class schedules differ; there is no predeclared semantic map to the adopted CICIDS taxonomy.",
        "The adopted protocol's native feature units are undocumented, preventing a defensible common semantic projection for transfer.",
    ]
    result = {
        "schema": "phase3-external-full-method-compatibility-v1",
        "status": "full_method_external_replication_requires_versioned_protocol_amendment",
        "final_test_accessed": False,
        "reference_contract": {
            "protocol_sha256": hashlib.sha256((ROOT / "configs/phase3/reference74-v1.json").read_bytes()).hexdigest(),
            "feature_count_config": feature_count,
            "model_input_count_source": int(model_match.group(1)),
            "stage_input_count_source": int(data_match.group(1)),
            "taxonomy": ref_taxonomy,
            "client_count": 5,
            "grouping": reference["data"]["graph"],
            "ownership": reference["data"]["ownership"],
        },
        "external_datasets": external,
        "shared_external_feature_names": common_external,
        "feature_transfer_status": "blocked_no_common_named_fields_and_units_undocumented",
        "independent_discovery_submodule_status": "completed_three_seed_exploratory_refits",
        "full_method_external_status": "not_faithful_without_amendment",
        "blockers": blockers,
        "safe_next_step": "Either define and preregister a new external estimand, taxonomy, feature contract, ownership/group split, and intervention schedule, or retain external evidence as discovery-submodule-only.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "blockers": len(blockers),
                      "output": str(OUTPUT), "final_test_accessed": False}, indent=2))


if __name__ == "__main__":
    main()
