"""Phase-B task-builder invariants: disjoint Monday-benign draws, determinism."""
import numpy as np
import pandas as pd

from src.data.sequence import build_tasks


def _frame() -> pd.DataFrame:
    rng = np.random.RandomState(0)
    return pd.DataFrame({
        "Label": ["Benign"] * 60 + ["Benign"] * 20 + ["FTP-Patator"] * 20,
        "day": ["monday"] * 60 + ["tuesday"] * 40,
        "flow_order": list(range(60)) + list(range(40)),
        "f": rng.randn(100),
    })


def _all_ids(tasks) -> set[int]:
    out: set[int] = set()
    for t in tasks:
        out |= set(t["id_train"].tolist()) | set(t["id_test"].tolist())
    return out


def test_monday_benign_never_reused_across_tasks():
    # Regression: same-seed sampling of the shared Monday pool once handed
    # identical benign rows to every task when Monday was not first (reverse
    # order), contaminating cross-task train/test splits.
    for order in ("default", "alt", "reverse"):
        tasks, _ = build_tasks(_frame(), scenario="cii", benign_per_task=10,
                               seed=42, order=order, split="chrono")
        assert len(tasks) == 2
        first = set(tasks[0]["id_train"]) | set(tasks[0]["id_test"])
        second = set(tasks[1]["id_train"]) | set(tasks[1]["id_test"])
        assert not (first & second), f"{order}: {sorted(first & second)}"


def test_task_build_is_deterministic():
    first, _ = build_tasks(_frame(), scenario="cii", benign_per_task=10,
                           seed=42, order="reverse", split="chrono")
    second, _ = build_tasks(_frame(), scenario="cii", benign_per_task=10,
                            seed=42, order="reverse", split="chrono")
    assert _all_ids(first) == _all_ids(second)


def test_empty_day_skipped_not_crashed():
    df = _frame().iloc[:0].copy()
    tasks, _ = build_tasks(df, scenario="cii", seed=42, order="default", split="chrono")
    assert tasks == []


def test_ci_scenario_rejects_benign_after_t0(tmp_path):
    import pytest

    from src.data.task_schema import write_taskset
    from src.tasks import load_or_build_tasks

    def _write(path, task_ids):
        id_to_name = {0: "Benign", 1: "Attack"}
        tasks = []
        for t, ids in enumerate(task_ids):
            y = np.array(ids, dtype=np.int64)
            tasks.append({"day": f"t{t}",
                          "labels": sorted({id_to_name[v] for v in ids}),
                          "X_train": np.zeros((len(y), 2), dtype=np.float32),
                          "y_train": y,
                          "X_test": np.zeros((len(y), 2), dtype=np.float32),
                          "y_test": y.copy(),
                          "id_train": np.arange(len(y), dtype=np.int64) + t * 1000,
                          "id_test": np.arange(len(y), dtype=np.int64) + 10_000_000 + t * 1000})
        write_taskset(path, tasks, {"Benign": 0, "Attack": 1},
                      feature_cols=["f0", "f1"], protocol_id="synthetic-v2",
                      split_def={"name": "fixed", "seed": 0},
                      scaler_info={"kind": "identity", "fitted_on": "none"},
                      imputation={"method": "none"},
                      sources=[{"identity": "synthetic",
                                "sha256": hashlib.sha256(b"ci-guard").hexdigest()}],
                      row_id_kind="synthetic")

    import hashlib

    good = tmp_path / "ci_true.npz"
    _write(good, [[0, 0], [1, 1]])
    tasks, _ = load_or_build_tasks({"data": {"scenario": "ci", "tasks": str(good)}})
    assert len(tasks) == 2

    bad = tmp_path / "ci_false.npz"
    _write(bad, [[0, 0], [0, 1, 1]])
    with pytest.raises(ValueError, match="benign absent after T0"):
        load_or_build_tasks({"data": {"scenario": "ci", "tasks": str(bad)}})


def test_cleaner_rejects_string_metadata_instead_of_wiping():
    import pandas as pd
    import pytest

    from src.data.clean import _clean_frame

    base = {"Destination Port": [80, 443], "Fwd Packet Length Max": [10, 20],
            "Label": ["BENIGN", "DDoS"]}
    out, _ = _clean_frame(pd.DataFrame(base), "monday")
    assert len(out) == 2  # numeric metadata passes through, then dropped
    assert "Destination Port" not in out.columns
    hostile = dict(base, **{"Flow ID": ["a", "b"], "Source IP": ["1.1.1.1", "2.2.2.2"]})
    with pytest.raises(ValueError, match="non-numeric"):
        _clean_frame(pd.DataFrame(hostile), "monday")
    empty = pd.DataFrame({"Fwd Packet Length Max": [float("nan")],
                          "Label": ["BENIGN"]})
    with pytest.raises(ValueError, match="emptied"):
        _clean_frame(empty, "monday")


def test_pool_sample_consolidation_preserves_content(tmp_path, monkeypatch):
    import pandas as pd

    from src.data import iot

    classes = (["Benign"] * 20 + ["DDoS", "DoS"] * 12)
    frame = pd.DataFrame({
        "f0": np.arange(len(classes), dtype=np.float64),
        "f1": np.arange(len(classes), dtype=np.float64) * 3.0,
        "attack_class": classes,
        "Label": classes,
    })
    pool = tmp_path / "train.parquet"
    frame.to_parquet(pool, index=False)
    monkeypatch.setattr(iot, "BATCH", 7)
    monkeypatch.setattr(iot, "TRAIN_CAP", 100)
    monkeypatch.setattr(iot, "BENIGN_TRAIN_CAP", 100)
    monkeypatch.setattr(iot, "CONSOLIDATE_EVERY", 1)
    atk1, ben1, _ = iot._pool_sample(pool, ["f0", "f1"], 4, True)
    monkeypatch.setattr(iot, "CONSOLIDATE_EVERY", 10 ** 9)
    atk2, ben2, _ = iot._pool_sample(pool, ["f0", "f1"], 4, True)
    assert set(atk1) == set(atk2)
    for key in atk1:
        pd.testing.assert_frame_equal(atk1[key], atk2[key])
    for f1, f2 in zip(ben1, ben2):
        pd.testing.assert_frame_equal(f1, f2)
