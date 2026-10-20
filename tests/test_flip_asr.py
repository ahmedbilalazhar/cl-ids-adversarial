"""Label-flip ASR eval consistency: score the class actually flipped."""
import hashlib
from pathlib import Path

import numpy as np

from src.runner import run


def _write_tasks(path: Path, trains: list[np.ndarray], tests: list[np.ndarray]) -> None:
    from src.data.task_schema import write_taskset

    rng = np.random.RandomState(0)
    n_feat = 4
    tasks = []
    for t, (y_tr, y_te) in enumerate(zip(trains, tests)):
        X_tr = rng.randn(len(y_tr), n_feat).astype(np.float32) + y_tr[:, None] * 3.0
        X_te = rng.randn(len(y_te), n_feat).astype(np.float32) + y_te[:, None] * 3.0
        tasks.append({"day": f"syn_{t}", "labels": ["0", "1", "2"],
                      "X_train": X_tr, "y_train": y_tr.astype(np.int64),
                      "X_test": X_te, "y_test": y_te.astype(np.int64),
                      "id_train": np.arange(len(y_tr), dtype=np.int64) + t * 1000,
                      "id_test": np.arange(len(y_te), dtype=np.int64) + 10_000_000 + t * 1000})
    write_taskset(
        path, tasks, {"Benign": 0, "Attack": 1, "Other": 2},
        feature_cols=[f"f{i}" for i in range(n_feat)],
        protocol_id="synthetic-v2", split_def={"name": "fixed", "seed": 0},
        scaler_info={"kind": "identity", "fitted_on": "none"},
        imputation={"method": "none"},
        sources=[{"identity": "seeded synthetic generator",
                  "sha256": hashlib.sha256(b"flip-probe").hexdigest()}],
        row_id_kind="synthetic global row index",
    )


def _cfg(path: Path, attack: dict) -> dict:
    return {"name": "flip-probe", "seed": 7, "device": "cpu", "cl_method": "finetune",
            "epochs_per_task": 1, "batch_size": 16, "lr": 1e-3,
            "data": {"scenario": "cii", "tasks": str(path)},
            "feature_names": [f"f{i}" for i in range(4)], "attack": attack}


def test_persistent_asr_scores_train_time_source(tmp_path):
    # Train majority (class 1) differs from test majority (class 2). The flip
    # poisons class 1; eval must score class 1, not the test majority.
    y_tr = np.array([0] * 5 + [1] * 30 + [2] * 5)
    y_te = np.array([0] * 2 + [1] * 3 + [2] * 15)
    path = tmp_path / "tasks_flip.npz"
    _write_tasks(path, [y_tr, y_tr], [y_te, y_te])
    attack = {"type": "label_flip", "mode": "persistent", "target_class": 0, "budget": 0.5}
    result = run(_cfg(path, attack))
    for row in result["asr_rows"]:
        assert row["source_class"] == 1, row
    assert result["summary"]["poison_rows"][0]["source_class"] == 1


def test_numeric_source_class_is_scored_not_silently_na(tmp_path):
    y_tr = np.array([0] * 10 + [1] * 20 + [2] * 10)
    y_te = np.array([0] * 5 + [1] * 10 + [2] * 5)
    path = tmp_path / "tasks_flipnum.npz"
    _write_tasks(path, [y_tr, y_tr], [y_te, y_te])
    attack = {"type": "label_flip", "mode": "targeted", "source_class": 1,
              "target_class": 0, "budget": 0.5}
    result = run(_cfg(path, attack))
    for row in result["asr_rows"]:
        assert row["source_class"] == 1, row
        assert row["asr"] is not None, row


def test_single_node_rerun_is_bit_identical(tmp_path):
    y_tr = np.array([0] * 10 + [1] * 20 + [2] * 10)
    y_te = np.array([0] * 5 + [1] * 10 + [2] * 5)
    path = tmp_path / "tasks_rerun.npz"
    _write_tasks(path, [y_tr, y_tr], [y_te, y_te])
    attack = {"type": "label_flip", "mode": "targeted", "source_class": "Attack",
              "target_class": 0, "budget": 0.5}
    cfg = _cfg(path, attack)
    first, second = run(cfg), run(cfg)
    np.testing.assert_array_equal(first["R"], second["R"])
    assert {k: v for k, v in first["summary"].items() if k != "wall_sec"} == \
        {k: v for k, v in second["summary"].items() if k != "wall_sec"}


def test_buffer_target_persists_validated_artifact(tmp_path):
    from src.reporting import check_artifact, save_results

    y_tr = np.array([0] * 10 + [1] * 20 + [2] * 10)
    y_te = np.array([0] * 5 + [1] * 10 + [2] * 5)
    path = tmp_path / "tasks_buf.npz"
    _write_tasks(path, [y_tr, y_tr], [y_te, y_te])
    attack = {"type": "label_flip", "target": "buffer", "mode": "targeted",
              "source_class": "Attack", "target_class": 0,
              "budget": 0.0, "buffer_budget": 1.0}
    cfg = dict(_cfg(path, attack), name="buf-probe", cl_method="er",
               buffer_size=64)
    out = tmp_path / "runs"
    out.mkdir()
    result = run(cfg)
    buf_rows = [r for r in result["summary"]["poison_rows"] if r["target"] == "buffer"]
    assert buf_rows, result["summary"]["poison_rows"]
    assert all(r["eligible"] >= 0 and r["changed"] >= 0 for r in buf_rows)
    save_results(result, cfg, out)
    state = check_artifact(out, "buf-probe", 7, cfg)
    assert state["complete"], state
