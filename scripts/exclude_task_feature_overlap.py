"""Create a versioned feature-disjoint successor without rewriting its parent.

This changes only test membership, not the parent's scaler or ordering protocol.
Usage: python scripts/exclude_task_feature_overlap.py --source INPUT.npz --out OUTPUT.npz
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.sequence import exclude_test_content_matches, load_tasks
from src.data.task_schema import is_v2, sha256_file, write_taskset


def exclude_overlap(source: Path, out: Path) -> dict:
    if source.resolve() == out.resolve():
        raise ValueError("a distinct successor path is required")
    if out.exists() or out.with_suffix(".json").exists():
        raise FileExistsError(f"successor already exists: {out}")
    if not is_v2(source):
        raise ValueError("the parent must be a validated v2 artifact with provenance")
    tasks, label_map = load_tasks(source)
    meta = json.loads(source.with_suffix(".json").read_text(encoding="utf-8"))
    previous_ids = [task["id_test"].copy() for task in tasks]
    removed = exclude_test_content_matches(tasks)
    removed_ids = [np.setdiff1d(ids, task["id_test"]).tolist()
                   for ids, task in zip(previous_ids, tasks)]
    split = dict(meta["split"])
    split.update(post_scale_test_exclusion=True, post_scale_test_match_basis="float32-features")
    return write_taskset(
        out, tasks, label_map, feature_cols=meta["feature_cols"],
        feature_units=meta["feature_units"],
        protocol_id=meta["protocol_id"] + "-feature-disjoint-f32",
        split_def=split, scaler_info=meta["scaler"], imputation=meta["imputation"],
        sources=meta["sources"], row_id_kind=meta["row_ids"],
        extra={"feature_exclusion_lineage": {
            "parent_file": source.name, "parent_npz_sha256": sha256_file(source),
            "parent_metadata_sha256": sha256_file(source.with_suffix(".json")),
            "removed_test_rows": removed, "removed_test_ids_by_task": removed_ids,
            "scope": "all training tasks versus all test tasks; labels ignored",
            "parent_extra_metadata": {key: value for key, value in meta.items() if key not in {
                "schema_version", "protocol_id", "label_map", "benign_id", "n_tasks",
                "days", "task_sizes", "feature_cols", "feature_units", "split", "scaler",
                "imputation", "sources", "row_ids", "npz_sha256", "builder_commit",
            }},
        }},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    meta = exclude_overlap(args.source, args.out)
    print(f"wrote {args.out}; removed {meta['feature_exclusion_lineage']['removed_test_rows']} test rows")


if __name__ == "__main__":
    main()
