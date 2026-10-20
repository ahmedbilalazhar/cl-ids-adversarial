"""Audit task labels, source-row identity, and duplicate-content exposure.

Distinct source rows can have identical measured features. Different train
and test source pools may also both use positional row ID zero. Keep these
cases separate: a feature match is not proof of shared source-row identity.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.content import feature_row_keys
from src.data.sequence import load_tasks


def _norm_features(x: np.ndarray) -> np.ndarray:
    """Feature rows as void scalars with -0.0 normalized away."""
    return feature_row_keys(x)


def _content_rows(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Feature+label rows as void scalars with -0.0 normalized away."""
    arr = np.ascontiguousarray(
        np.column_stack((np.asarray(x, dtype=np.float32), y)), dtype=np.float64
    )
    arr[:, :-1][arr[:, :-1] == 0] = 0.0
    width = arr.dtype.itemsize * arr.shape[1]
    return arr.view(f"V{width}").reshape(-1)


def content_overlap_count(Xtr, ytr, Xte, yte) -> int:
    """Count test records with an exact feature-and-label match in train."""
    if len(Xte) == 0 or len(Xtr) == 0:
        return 0
    return int(np.isin(_content_rows(Xte, yte), _content_rows(Xtr, ytr)).sum())


def cross_split_overlaps(tasks: list[dict]) -> tuple[int, int]:
    """Pooled train-vs-test matching across ALL tasks.

    Returns (feature_overlap, content_overlap): test rows matching any train
    row on features alone, and on features+label. Per-task counting misses
    leakage across task boundaries and hides feature matches under conflicting
    labels; these pooled counts do not.
    """
    tr_x = [np.asarray(t["X_train"]) for t in tasks if len(t["X_train"])]
    te_x = [np.asarray(t["X_test"]) for t in tasks if len(t["X_test"])]
    if not tr_x or not te_x:
        return 0, 0
    ftr = np.concatenate([_norm_features(a) for a in tr_x])
    fte = np.concatenate([_norm_features(a) for a in te_x])
    feature_overlap = int(np.isin(fte, ftr).sum())
    cte = np.concatenate([
        _content_rows(a, b)
        for a, b in zip(te_x, [np.asarray(t["y_test"]) for t in tasks if len(t["X_test"])])])
    ctr = np.concatenate([
        _content_rows(a, b)
        for a, b in zip(tr_x, [np.asarray(t["y_train"]) for t in tasks if len(t["X_train"])])])
    content_overlap = int(np.isin(cte, ctr).sum())
    return feature_overlap, content_overlap


def source_overlap_count(train_ids: np.ndarray, test_ids: np.ndarray) -> int:
    return int(np.intersect1d(train_ids, test_ids).size)


def audit_file(path: Path) -> dict:
    tasks, label_map = load_tasks(path)
    try:
        meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        meta = {}
    has_ids = all("id_train" in t and "id_test" in t for t in tasks)
    same_pool = len(meta.get("sources", [])) == 1 if has_ids else False
    per_task = []
    train_ids = []
    test_ids = []
    for i, task in enumerate(tasks):
        tr_labels = {int(v) for v in np.unique(task["y_train"])}
        te_labels = {int(v) for v in np.unique(task["y_test"])}
        source_overlap = None
        if has_ids:
            tr_ids = np.asarray(task["id_train"], dtype=np.int64)
            te_ids = np.asarray(task["id_test"], dtype=np.int64)
            train_ids.append(tr_ids)
            test_ids.append(te_ids)
            source_overlap = source_overlap_count(tr_ids, te_ids) if same_pool else 0
        content_overlap = content_overlap_count(
            task["X_train"], task["y_train"], task["X_test"], task["y_test"]
        )
        per_task.append({
            "task": i, "train": len(task["y_train"]), "test": len(task["y_test"]),
            "content_overlap": content_overlap, "source_overlap": source_overlap,
            "outside_map": sorted((tr_labels | te_labels) - set(label_map.values())),
        })
    cross_train = cross_test = cross_split = None
    if has_ids:
        all_train = np.concatenate(train_ids)
        all_test = np.concatenate(test_ids)
        cross_train = len(all_train) - len(np.unique(all_train))
        cross_test = len(all_test) - len(np.unique(all_test))
        cross_split = source_overlap_count(all_train, all_test) if same_pool else 0
    cross_feature, cross_content = cross_split_overlaps(tasks)
    return {
        "file": path.name, "n_tasks": len(tasks), "n_classes": len(label_map),
        "benign_id": label_map.get("Benign", label_map.get("Normal")),
        "schema": meta.get("schema_version", "legacy"),
        "protocol": meta.get("protocol_id", "legacy-undocumented"),
        "has_ids": has_ids, "pool_scope": "shared" if same_pool else (
            "separate train/test" if has_ids else "unknown"),
        "cross_train_reuse": cross_train, "cross_test_reuse": cross_test,
        "cross_split_source_overlap": cross_split, "tasks": per_task,
        "cross_split_feature_overlap": cross_feature,
        "cross_split_content_overlap": cross_content,
        "expects_feature_disjoint": meta.get("split", {}).get("post_scale_test_match_basis")
        == "float32-features",
    }


def main() -> None:
    files = sorted((ROOT / "data" / "processed").glob("tasks*.npz"))
    report = [audit_file(path) for path in files]
    failures = []
    lines = [
        "# Task-artifact audit", "",
        ("Generated by `python scripts/audit_tasks.py`. Counts are for task artifacts, "
         "not raw-flow packet equivalence."), "",
        ("| Artifact | Tasks | Benign ID | ID scope | Same-source train/test IDs | "
         "Pooled feature-only test matches | Pooled feature+label test matches |"),
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for item in report:
        content = item["cross_split_content_overlap"]
        features = item["cross_split_feature_overlap"]
        source = item["cross_split_source_overlap"]
        if source is None:
            source_str = "not verifiable"
        elif item["has_ids"] and item["pool_scope"] != "shared":
            # Separate positional-ID pools (e.g. UNSW/IoT train vs test
            # files) are not comparable row-wise: 0 here would wrongly read
            # as "verified disjoint". Content matches are the real signal.
            source_str = "n/a (separate pools)"
        else:
            source_str = str(source)
        lines.append(
            f"| `{item['file']}` | {item['n_tasks']} | {item['benign_id']} | "
            f"{item['pool_scope']} | {source_str} | {features} | {content} |"
        )
        if item["benign_id"] != 0:
            failures.append(f"{item['file']}: benign ID is not zero")
        if item["expects_feature_disjoint"] and features:
            failures.append(f"{item['file']}: declared feature-disjoint artifact has {features} test matches")
        if source is not None and source != 0:
            failures.append(f"{item['file']}: {source} source rows cross train/test")
        if item["cross_train_reuse"] not in (None, 0):
            failures.append(f"{item['file']}: train source IDs reused across tasks")
        if item["cross_test_reuse"] not in (None, 0):
            failures.append(f"{item['file']}: test source IDs reused across tasks")
        for task in item["tasks"]:
            if task["outside_map"]:
                failures.append(f"{item['file']} t{task['task']}: unmapped labels")
    lines += ["", ("The summary pools all training tasks and all test tasks, compares "
                   "features at the model's float32 precision, and normalizes signed "
                   "zeros. Each matching test row is counted once. Conflicting labels "
                   "do not remove a feature-only match."), "",
              "## Per-task content matches", "",
              ("Exact matches are counted in the post-preprocessing feature space and "
               "require the same class label within the same task. They are a memorization-risk indicator, "
               "not proof of shared source-row identity."), ""]
    for item in report:
        lines.append(f"### `{item['file']}` ({item['protocol']})")
        for task in item["tasks"]:
            overlap = task["source_overlap"]
            if overlap is not None and item["has_ids"] and item["pool_scope"] != "shared":
                overlap = "n/a (separate pools)"
            elif overlap is None:
                overlap = "unverifiable"
            lines.append(
                f"- T{task['task']}: train {task['train']}, test {task['test']}, "
                f"exact test matches {task['content_overlap']}, "
                f"same-source row overlap {overlap}"
            )
        if item["has_ids"]:
            lines.append(
                f"- Across tasks: train ID reuse {item['cross_train_reuse']}, "
                f"test ID reuse {item['cross_test_reuse']}."
            )
        lines.append(
            f"- Cross-split pooled matching (all tasks): "
            f"{item['cross_split_feature_overlap']} test rows match a train row "
            f"on features, of which {item['cross_split_content_overlap']} also "
            f"agree on the label."
        )
        lines.append("")
    lines += [
        "## Interpretation", "",
        ("- Legacy CICIDS artifacts have no row IDs. Source-level split and "
         "cross-task disjointness cannot be certified from them. Their results remain "
         "executed, not manifest-validated; rebuild v2 artifacts before claims."),
        ("- UNSW and IoT v2 train/test row IDs are positions within different source "
         "files. The separate-pool source split is disjoint by construction, while "
         "duplicate content across those files still poses a memorization risk."),
        ("- CICIDS Friday has substantial exact train/test content overlap in its "
         "legacy tasks. Do not interpret its current test accuracy as independent "
         "generalization without a duplicate-disjoint sensitivity analysis."),
        ("- The duplicate-disjoint CICIDS arm removes repeated raw feature+label "
         "rows globally, then excludes any remaining post-scaling test match "
         "on FEATURES (labels ignored, signed zeros normalized) against all "
         "training tasks. It is a distinct protocol, not a repair "
         "of historical scores. See `docs/cicids_cross_file_audit.md` for "
         "original-CSV cross-file content fingerprints."),
        ("- Pooled cross-split counts complement per-task matching: per-task "
         "counts miss test rows that match a *different* task's train rows, "
         "and feature+label counting hides feature matches under conflicting "
         "labels. The feature-only count is the conservative memorization "
         "indicator; identical features do not establish common raw-flow identity."),
        ("- `flow_order` is a within-file, per-class capture-order proxy. It does "
         "not define a globally chronological deployment stream."),
    ]
    out = ROOT / "docs" / "task_audit.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}; hard failures: {len(failures)}")
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
