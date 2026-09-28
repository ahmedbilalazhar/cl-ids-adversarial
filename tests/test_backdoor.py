"""Backdoor mechanism and endpoint checks on tiny synthetic arrays."""
import json

import numpy as np
import pytest

from src.attacks.backdoor import backdoor_outcome, scaled_trigger
from src.config_validation import validate_config
from src.data.task_schema import sha256_file
from src.federated.fedavg import _poison_shard
from src.runner import apply_attack


def test_scaled_trigger_requires_verified_features_and_scaler(tmp_path):
    task_file = tmp_path / "tasks.npz"
    task_file.write_bytes(b"synthetic task bytes")
    meta = {"schema_version": 2, "npz_sha256": sha256_file(task_file),
            "feature_cols": ["a", "b"],
            "scaler": {"kind": "t0-only", "mean": [10.0, 20.0], "scale": [2.0, 4.0]}}
    task_file.with_suffix(".json").write_text(json.dumps(meta), encoding="utf-8")
    raw = {"features": ["b", "a"], "values": [28.0, 14.0]}
    assert scaled_trigger(raw, ["a", "b"], task_file)["values"] == [2.0, 2.0]
    with pytest.raises(ValueError, match="absent"):
        scaled_trigger({"features": ["missing"], "values": [1.0]}, ["a", "b"], task_file)
    with pytest.raises(ValueError, match="order"):
        scaled_trigger(raw, ["b", "a"], task_file)
    meta["npz_sha256"] = "0" * 64
    task_file.with_suffix(".json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ValueError, match="verified"):
        scaled_trigger(raw, ["a", "b"], task_file)


def test_single_and_federated_poison_use_same_configured_trigger():
    X = np.zeros((10, 2), dtype=np.float32)
    y = np.array([0, 0, 1, 1, 1, 1, 1, 1, 1, 1])
    trigger = {"features": ["b"], "values": [3.5]}
    attack = {"type": "backdoor", "attack_class": "Attack", "target_class": 0,
              "budget": 0.5, "trigger": {"features": ["b"], "values": [28.0]}}
    cfg = {"attack": attack, "seed": 1}
    task = {"X_train": X, "y_train": y}
    X_single, y_single, single_meta = apply_attack(
        cfg, task, 0, ["a", "b"], None, "cpu", {"Benign": 0, "Attack": 1}, 2,
        trigger=trigger,
    )
    X_fed, y_fed, fed_meta = _poison_shard(
        X, y, attack, {"Benign": 0, "Attack": 1}, ["a", "b"], seed=1,
        trigger=trigger,
    )
    np.testing.assert_array_equal(X_single, X_fed)
    np.testing.assert_array_equal(y_single, y_fed)
    np.testing.assert_array_equal(single_meta["triggered"], fed_meta["poisoned"])
    assert np.all(X_single[single_meta["triggered"], 1] == 3.5)
    assert np.all(y_single[single_meta["triggered"]] == 0)


def test_asr_denominator_and_absent_attack_class():
    X = np.array([[0.0], [0.0], [0.0]], dtype=np.float32)
    y = np.array([1, 1, 0])
    def predictor(x):
        return (x[:, 0] < 1).astype(np.int64)
    trigger = {"features": ["a"], "values": [2.0]}
    result = backdoor_outcome(predictor, X, y, ["a"], 1, 0, trigger)
    assert result == {"asr": 1.0, "eligible": 2, "successes": 2,
                      "clean_target_errors": 0, "clean_target_error_rate": 0.0}
    absent = backdoor_outcome(predictor, X, y, ["a"], 2, 0, trigger)
    assert absent["asr"] is None and absent["eligible"] == 0


def test_config_preflight_rejects_wrong_runner_krum_and_budget():
    cfg = {"name": "probe", "cl_method": "finetune", "device": "cpu",
           "data": {"tasks": "data/processed/tasks_chrono_dedup.npz", "scenario": "cii"}}
    validate_config(cfg, expected_runner="single-node")
    with pytest.raises(ValueError, match="runner"):
        validate_config(cfg, expected_runner="federated")
    fed_cfg = {**cfg, "fed": {"n_clients": 5, "malicious_ids": [3, 4],
                             "aggregator": "krum"}}
    with pytest.raises(ValueError, match="Krum"):
        validate_config(fed_cfg)
    bad_budget = {**cfg, "attack": {"type": "label_flip", "budget": 1.5}}
    with pytest.raises(ValueError, match="budget"):
        validate_config(bad_budget)
    bad_target = {**cfg, "attack": {"type": "label_flip", "budget": 0.1,
                                   "source_class": "unknown", "target_class": "Benign"}}
    with pytest.raises(KeyError, match="source"):
        validate_config(bad_target)
