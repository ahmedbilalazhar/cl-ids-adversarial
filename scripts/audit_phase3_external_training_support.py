"""Train-label-only support audit for prospective external intervention design.

Loads only per-task training label vectors from UNSW/CICIoT artifacts. Does not
load external test arrays, feature arrays, or any CICIDS final-test material.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
OUTPUT = ROOT / "results/phase3-followup/external-training-support-audit-v1.json"
MIN_SOURCE_ROWS = 50


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def audit(dataset: str, stem: str, benign_name: str) -> dict:
    metadata_path = DATA / f"tasks_{stem}.json"
    archive_path = DATA / f"tasks_{stem}.npz"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if sha256(archive_path) != metadata["npz_sha256"]:
        raise ValueError(f"{dataset}: task artifact hash differs from metadata")
    if metadata["label_map"].get(benign_name) != metadata.get("benign_id"):
        raise ValueError(f"{dataset}: benign name/id mismatch")
    label_names = {int(v): str(k) for k, v in metadata["label_map"].items()}
    benign_id = int(metadata["benign_id"])
    counts: list[dict[int, int]] = []
    # Access only t*_y_train keys. In particular, no t*_X_* or t*_y_test key is requested.
    with np.load(archive_path, allow_pickle=False) as package:
        for task in range(int(metadata["n_tasks"])):
            key = f"t{task}_y_train"
            if key not in package.files:
                raise KeyError(f"{dataset}: missing {key}")
            y = np.asarray(package[key])
            if y.ndim != 1 or not np.issubdtype(y.dtype, np.integer):
                raise ValueError(f"{dataset}: invalid training labels in {key}")
            values, frequencies = np.unique(y.astype(np.int64, copy=False), return_counts=True)
            current = {int(v): int(n) for v, n in zip(values, frequencies)}
            if not set(current).issubset(label_names):
                raise ValueError(f"{dataset}: unknown label ID in {key}")
            counts.append(current)

    # Prospective selection rule: among attack labels absent at T0 and first
    # present at T1, choose highest T1 train support; break ties by label ID.
    t0, t1 = counts[0], counts[1]
    candidates = [
        label_id for label_id, n in t1.items()
        if label_id != benign_id and n >= MIN_SOURCE_ROWS and t0.get(label_id, 0) == 0
    ]
    candidates.sort(key=lambda label_id: (-t1[label_id], label_id))
    selected = candidates[0] if candidates else None
    return {
        "dataset": dataset,
        "protocol_id": metadata["protocol_id"],
        "metadata_sha256": sha256(metadata_path),
        "task_artifact_sha256": sha256(archive_path),
        "task_train_rows_from_sidecar": [int(x["train"]) for x in metadata["task_sizes"]],
        "observed_train_label_counts": [
            {label_names[k]: v for k, v in sorted(row.items())} for row in counts
        ],
        "candidate_new_attack_labels_t1": [
            {"label_id": k, "label": label_names[k], "t1_train_rows": t1[k]}
            for k in candidates
        ],
        "selected_source_label": None if selected is None else label_names[selected],
        "selected_source_label_id": selected,
        "selected_source_t1_train_rows": None if selected is None else t1[selected],
        "t1_benign_train_rows": t1.get(benign_id, 0),
        "selection_rule": f"Largest task-1 train support among non-benign labels absent from task 0; minimum {MIN_SOURCE_ROWS}; ties by ascending label ID.",
        "feasible_for_source_to_benign_pilot": selected is not None and t1.get(benign_id, 0) >= MIN_SOURCE_ROWS,
    }


def main() -> None:
    reports = [
        audit("UNSW-NB15", "unsw", "Normal"),
        audit("CICIoT2023", "iot", "Benign"),
    ]
    result = {
        "schema": "phase3-external-training-support-audit-v1",
        "scope": "training-label support only; no external test labels/features or CICIDS final-test data loaded",
        "test_arrays_accessed": False,
        "cicids_final_test_accessed": False,
        "minimum_source_rows": MIN_SOURCE_ROWS,
        "datasets": reports,
        "interpretation_limit": "Support feasibility does not resolve missing persistent ownership, component/session grouping, external task alignment, or full-method comparability. Any simulated-client study is an independent benchmark extension, not a faithful replication.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "datasets": [
        {"dataset": r["dataset"], "selected_source_label": r["selected_source_label"],
         "source_rows": r["selected_source_t1_train_rows"],
         "feasible": r["feasible_for_source_to_benign_pilot"]}
        for r in reports
    ], "test_arrays_accessed": False, "cicids_final_test_accessed": False}, indent=2))


if __name__ == "__main__":
    main()
