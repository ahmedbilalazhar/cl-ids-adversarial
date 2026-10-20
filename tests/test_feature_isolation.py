"""Leakage must be checked independently of labels and task boundaries."""
import json

import numpy as np
import pytest

from scripts import audit_tasks
from src.data.sequence import exclude_test_content_matches


def _task(train, train_label, test, test_label, index):
    return {
        "X_train": np.asarray([train], dtype=np.float32),
        "y_train": np.array([train_label], dtype=np.int64),
        "X_test": np.asarray([test], dtype=np.float32),
        "y_test": np.array([test_label], dtype=np.int64),
        "id_train": np.array([index * 2], dtype=np.int64),
        "id_test": np.array([index * 2 + 1], dtype=np.int64),
    }


def test_conflicting_labels_and_signed_zero_do_not_hide_feature_overlap():
    tasks = [_task([-0.0, 1.0], 0, [0.0, 1.0], 1, 0)]
    assert exclude_test_content_matches(tasks) == 1
    assert len(tasks[0]["id_test"]) == 0


def test_feature_keys_use_model_precision_without_mutating_inputs():
    from src.data.content import feature_row_keys

    original = np.array([[-0.0, 1.0 + 1e-10]], dtype=np.float64)
    expected = np.array([[0.0, 1.0]], dtype=np.float32)
    np.testing.assert_array_equal(feature_row_keys(original), feature_row_keys(expected))
    assert np.signbit(original[0, 0])
    assert original[0, 1] != 1.0


def test_label_agreement_audit_uses_the_same_model_precision():
    train = np.array([[-0.0, 1.0 + 1e-10]], dtype=np.float64)
    test = np.array([[0.0, 1.0]], dtype=np.float32)
    assert audit_tasks.content_overlap_count(train, np.array([1]), test, np.array([1])) == 1
    assert np.signbit(train[0, 0])


def _audit(tmp_path, monkeypatch, tasks):
    path = tmp_path / "tasks.npz"
    path.with_suffix(".json").write_text(json.dumps({"sources": [{"file": "synthetic"}]}))
    monkeypatch.setattr(audit_tasks, "load_tasks", lambda path: (tasks, {"Benign": 0, "A": 1}))
    return audit_tasks.audit_file(path)


def test_audit_distinguishes_feature_overlap_from_label_agreement(tmp_path, monkeypatch):
    tasks = [_task([1.0], 0, [2.0], 0, 0), _task([3.0], 1, [1.0], 1, 1)]
    result = _audit(tmp_path, monkeypatch, tasks)
    assert result["cross_split_feature_overlap"] == 1
    assert result["cross_split_content_overlap"] == 0


def test_audit_counts_content_matches_across_different_tasks(tmp_path, monkeypatch):
    tasks = [_task([1.0], 0, [2.0], 0, 0), _task([3.0], 1, [1.0], 0, 1)]
    result = _audit(tmp_path, monkeypatch, tasks)
    assert sum(t["content_overlap"] for t in result["tasks"]) == 0
    assert result["cross_split_content_overlap"] == 1
    assert result["cross_split_feature_overlap"] == 1


def test_versioned_feature_exclusion_preserves_parent_and_protocol(tmp_path):
    from scripts.exclude_task_feature_overlap import exclude_overlap
    from src.data.sequence import load_tasks
    from src.data.task_schema import sha256_file, write_taskset

    source, successor = tmp_path / "tasks.npz", tmp_path / "tasks_features.npz"
    tasks = [_task([1.0, -0.0], 0, [1.0, 0.0], 1, 0)]
    original = write_taskset(
        source, tasks, {"Benign": 0, "A": 1}, feature_cols=["f0", "f1"],
        protocol_id="synthetic-offline-init", split_def={"seed": 42},
        scaler_info={"kind": "offline-init", "fitted_on": "T0+T1 train"},
        imputation={"method": "none"}, sources=[{"sha256": "0" * 64}],
        row_id_kind="shared source positions", extra={"custom_metadata": 123},
    )
    before = (sha256_file(source), sha256_file(source.with_suffix(".json")))
    result = exclude_overlap(source, successor)
    assert before == (sha256_file(source), sha256_file(source.with_suffix(".json")))
    assert result["scaler"] == original["scaler"]
    lineage = result["feature_exclusion_lineage"]
    assert lineage["removed_test_rows"] == 1
    assert lineage["removed_test_ids_by_task"] == [[1]]
    assert lineage["parent_extra_metadata"] == {"custom_metadata": 123}
    repaired, _ = load_tasks(successor)
    assert len(repaired[0]["X_test"]) == 0
    np.testing.assert_array_equal(repaired[0]["X_train"], tasks[0]["X_train"])
    assert audit_tasks.audit_file(successor)["cross_split_feature_overlap"] == 0
    with pytest.raises(FileExistsError):
        exclude_overlap(source, successor)
    with pytest.raises(ValueError, match="distinct successor"):
        exclude_overlap(source, source)


def test_audit_rejects_a_false_feature_disjoint_declaration(tmp_path, monkeypatch):
    tasks = [_task([1.0], 0, [1.0], 1, 0)]
    result = _audit(tmp_path, monkeypatch, tasks)
    result["expects_feature_disjoint"] = True
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "data" / "processed" / "tasks.npz").touch()
    (tmp_path / "docs").mkdir()
    monkeypatch.setattr(audit_tasks, "ROOT", tmp_path)
    monkeypatch.setattr(audit_tasks, "audit_file", lambda path: result)
    with pytest.raises(SystemExit) as error:
        audit_tasks.main()
    assert error.value.code == 1
    report = (tmp_path / "docs" / "task_audit.md").read_text(encoding="utf-8")
    assert "Pooled feature-only test matches" in report
