"""Check external task row-ID reuse without loading features or labels."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
OUTPUT = ROOT / "results/phase3-followup/external-id-isolation-audit-v1.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_dataset(dataset: str, stem: str) -> dict:
    meta_path = DATA / f"tasks_{stem}.json"
    archive_path = DATA / f"tasks_{stem}.npz"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if sha256(archive_path) != meta["npz_sha256"]:
        raise ValueError(f"{dataset}: task artifact hash differs from sidecar")
    pools = {"train": {}, "test": {}}
    total_counts = {"train": 0, "test": 0}
    with np.load(archive_path, allow_pickle=False) as package:
        for task in range(int(meta["n_tasks"])):
            for role in ("train", "test"):
                key = f"t{task}_id_{role}"
                if key not in package.files:
                    raise KeyError(f"{dataset}: missing {key}")
                ids = np.asarray(package[key])
                if ids.ndim != 1 or not np.issubdtype(ids.dtype, np.integer):
                    raise ValueError(f"{dataset}: invalid ID vector in {key}")
                ints = [int(v) for v in ids]
                if len(ints) != len(set(ints)):
                    raise ValueError(f"{dataset}: duplicate IDs within {key}")
                pools[role][task] = set(ints)
                total_counts[role] += len(ints)

    collisions = {role: [] for role in pools}
    for role, task_sets in pools.items():
        for left in range(len(task_sets)):
            for right in range(left + 1, len(task_sets)):
                overlap = task_sets[left] & task_sets[right]
                if overlap:
                    collisions[role].append({
                        "task_pair": [left, right],
                        "overlap_count": len(overlap),
                        "sample_ids_sha256": hashlib.sha256(
                            np.asarray(sorted(overlap), dtype=np.int64).tobytes()
                        ).hexdigest(),
                    })
    return {
        "dataset": dataset,
        "protocol_id": meta["protocol_id"],
        "metadata_sha256": sha256(meta_path),
        "task_artifact_sha256": sha256(archive_path),
        "task_counts": {role: [len(pools[role][t]) for t in range(int(meta["n_tasks"]))] for role in pools},
        "unique_rows_within_pool": total_counts,
        "cross_task_id_collisions": collisions,
        "train_task_ids_disjoint": not collisions["train"],
        "test_task_ids_disjoint": not collisions["test"],
        "train_test_id_comparison": "not performed: row IDs are positional within separate provider pools and need not share a namespace",
    }


def main() -> None:
    datasets = [check_dataset("UNSW-NB15", "unsw"), check_dataset("CICIoT2023", "iot")]
    result = {
        "schema": "phase3-external-id-isolation-audit-v1",
        "scope": "identifier arrays only; no feature or label arrays loaded",
        "feature_arrays_accessed": False,
        "label_arrays_accessed": False,
        "cicids_final_test_accessed": False,
        "datasets": datasets,
        "interpretation_limit": "Disjoint positional IDs establish task assignment uniqueness only. They do not establish component, session, host, campaign, or train/test duplicate-flow isolation.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "datasets": [
        {"dataset": x["dataset"], "train_disjoint": x["train_task_ids_disjoint"],
         "test_disjoint": x["test_task_ids_disjoint"], "collisions": x["cross_task_id_collisions"]}
        for x in datasets
    ], "features_accessed": False, "labels_accessed": False,
       "cicids_final_test_accessed": False}, indent=2))


if __name__ == "__main__":
    main()
