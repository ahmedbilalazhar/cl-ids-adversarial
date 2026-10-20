"""Phase-D federated controls: per-client accounting and empty-submission handling."""
import hashlib
from pathlib import Path

import numpy as np
import pytest
import torch

from src.federated import fedavg
from src.federated.fedavg import _buffer_report, _class_counts, run_federated
from src.federated.partition import stable_partition
from src.federated.robust import DynamicTrust


def _synthetic_tasks_file(path: Path) -> None:
    from src.data.task_schema import write_taskset

    rng = np.random.RandomState(0)
    n_feat = 8
    tasks = []
    for t in range(2):
        y = np.array([0] * 30 + [1] * 30, dtype=np.int64)
        X = rng.randn(60, n_feat).astype(np.float32)
        X[y == 1] += 2.0
        idx = rng.permutation(len(y))
        X, y = X[idx], y[idx]
        split = 42
        tasks.append({"day": f"syn_{t}", "labels": ["0", "1"],
                      "X_train": X[:split], "y_train": y[:split],
                      "X_test": X[split:], "y_test": y[split:],
                      "id_train": idx[:split].astype(np.int64) + t * 100,
                      "id_test": idx[split:].astype(np.int64) + t * 100})
    write_taskset(
        path, tasks, {"Benign": 0, "Attack": 1},
        feature_cols=[f"f{i}" for i in range(n_feat)],
        protocol_id="synthetic-v2", split_def={"name": "fixed", "seed": 0},
        scaler_info={"kind": "identity", "fitted_on": "none"},
        imputation={"method": "none"},
        sources=[{"identity": "seeded synthetic generator",
                  "sha256": hashlib.sha256(b"".join(t["X_train"].tobytes() for t in tasks)).hexdigest()}],
        row_id_kind="synthetic global row index",
    )


def _fed_cfg(task_file: Path, **fed) -> dict:
    return {"name": "synth_fedctrl", "seed": 7, "device": "cpu", "cl_method": "finetune",
            "epochs_per_task": 1, "batch_size": 16, "lr": 1e-3,
            "data": {"scenario": "cii", "tasks": str(task_file)},
            "feature_names": [f"f{i}" for i in range(8)],
            "fed": {"n_clients": 3, "malicious_id": 2, "alpha": 0.5,
                    "local_epochs": 1, **fed}}


def test_per_client_records_are_internally_consistent(tmp_path):
    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    result = run_federated(_fed_cfg(task_file))
    rows = result["summary"]["poison_rows"]
    assert len(rows) == 2 * 3  # tasks x clients
    required = {"pre_defense_n", "post_defense_n", "class_counts_pre", "class_counts_post",
                "participated", "optimizer_steps", "buffer_n", "buffer_class_counts",
                "buffer_bytes_est", "comm_bytes"}
    for row in rows:
        assert required <= set(row), row
        assert row["pre_defense_n"] == row["n"]
        assert row["post_defense_n"] == row["n"]  # no defense configured
        assert row["participated"] == (row["post_defense_n"] > 0)
        assert sum(row["class_counts_pre"].values()) == row["pre_defense_n"]
        assert sum(row["class_counts_post"].values()) == row["post_defense_n"]
        assert row["comm_bytes"] > 0
        if row["participated"]:
            assert row["optimizer_steps"] == 1 * ((row["post_defense_n"] + 15) // 16)
        else:
            assert row["optimizer_steps"] == 0
    assert result["summary"]["fed_exclusions"] == []
    assert result["summary"]["fed"]["excluded_inactive_clients"] == []
    rate = result["summary"]["fed_participation_rate"]
    assert 0.0 < rate <= 1.0
    assert result["summary"]["comm_bytes_total"] == sum(r["comm_bytes"] for r in rows)


def test_empty_shards_excluded_from_unweighted_aggregates(tmp_path, monkeypatch):
    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)

    def rigged_partition(y, n_clients=5, alpha=0.5, seed=42):
        n = len(y)
        # Client 4 gets nothing; the rest split evenly.
        parts = np.array_split(np.arange(n), n_clients - 1)
        return [p.astype(np.int64) for p in parts] + [np.zeros(0, dtype=np.int64)]

    monkeypatch.setattr(fedavg, "dirichlet_partition", rigged_partition)
    for aggregator in ("median",):
        cfg = _fed_cfg(task_file, aggregator=aggregator)
        cfg["fed"]["n_clients"] = 5
        result = run_federated(cfg)
        assert np.isfinite(result["R"]).all()
        assert result["summary"]["fed"]["excluded_inactive_clients"] == [4]
        tasks_seen = {r["task"] for r in result["summary"]["fed_exclusions"]}
        assert tasks_seen == {0, 1}
        assert result["summary"]["fed_participation_rate"] == 0.8
    # Four actual submissions cannot satisfy Krum with f=1, even if the
    # configured federation contains five clients. Never silently clamp f.
    cfg = _fed_cfg(task_file, aggregator="krum")
    cfg["fed"]["n_clients"] = 5
    with pytest.raises(ValueError, match="Krum requires"):
        run_federated(cfg)


def test_dynamic_trust_index_mapping_keeps_per_client_state():
    trust = DynamicTrust(n_clients=3)
    d0 = {"w": torch.tensor([1.0, 0.0])}
    d2 = {"w": torch.tensor([1.0, 1.0])}
    before = trust.trust.copy()
    out = trust([d0, d2], index=[0, 2])
    assert trust.trust.shape == (3,)
    assert trust.trust[1] == before[1]  # inactive client untouched
    assert trust.trust[0] != before[0] and trust.trust[2] != before[2]
    assert np.isfinite(out["w"].numpy()).all()


def test_helpers_on_empty_inputs():
    assert _class_counts(np.zeros(0, dtype=np.int64)) == {}

    class NoBuffer:
        pass

    assert _buffer_report(NoBuffer(), 8, 2) == {
        "buffer_n": 0, "buffer_class_counts": {}, "buffer_bytes_est": 0}


def test_aggregate_updates_degenerate_keeps_global():
    from src.federated.fedavg import _aggregate_updates

    torch.manual_seed(0)
    global_sd = {"w": torch.randn(4)}
    sds = [{"w": torch.randn(4)} for _ in range(3)]
    ws = [0.0, 0.0, 0.0]
    agg, excluded = _aggregate_updates(
        sds, ws, global_sd, [], aggregator="median", trim_ratio=0.2,
        n_mal=1, up_method=None, up_attack={}, mal_ids=[2], trust=None,
        device="cpu")
    assert excluded == [0, 1, 2]
    torch.testing.assert_close(agg["w"], global_sd["w"])


def test_aggregate_updates_excludes_inactive_only_for_unweighted():
    from src.federated.fedavg import _aggregate_updates
    from src.federated.robust import DynamicTrust

    torch.manual_seed(0)
    global_sd = {"w": torch.zeros(4)}
    active = {"w": torch.tensor([1.0, 1.0, 1.0, 1.0])}
    idle = {"w": torch.zeros(4)}  # broadcast copy: zero delta
    sds = [dict(active), dict(active), dict(idle)]
    ws = [10.0, 10.0, 0.0]
    # Median over actives only: zero-delta vote must not drag the result.
    agg, excluded = _aggregate_updates(
        [dict(s) for s in sds], ws, global_sd, [0, 1], aggregator="median",
        trim_ratio=0.2, n_mal=1, up_method=None, up_attack={}, mal_ids=[2],
        trust=None, device="cpu")
    assert excluded == [2]
    torch.testing.assert_close(agg["w"], torch.tensor([1.0, 1.0, 1.0, 1.0]))
    # Locked FedAvg path records no exclusions (weights already neutralize).
    agg, excluded = _aggregate_updates(
        [dict(s) for s in sds], ws, global_sd, [0, 1], aggregator="fedavg",
        trim_ratio=0.2, n_mal=1, up_method=None, up_attack={}, mal_ids=[2],
        trust=None, device="cpu")
    assert excluded == []
    torch.testing.assert_close(agg["w"], torch.tensor([1.0, 1.0, 1.0, 1.0]))
    # DynamicTrust keeps per-client state across exclusions.
    trust = DynamicTrust(n_clients=3)
    agg, excluded = _aggregate_updates(
        [dict(s) for s in sds], ws, global_sd, [0, 2], aggregator="dynamic_trust",
        trim_ratio=0.2, n_mal=1, up_method=None, up_attack={}, mal_ids=[1],
        trust=trust, device="cpu")
    assert excluded == [1]
    assert trust.trust.shape == (3,)
    assert np.isfinite(agg["w"].numpy()).all()


def test_stable_partition_covers_once_deterministically():
    ids = np.arange(1000, dtype=np.int64)
    first = stable_partition(ids, n_clients=5)
    second = stable_partition(ids, n_clients=5)
    assert len(first) == 5
    for a, b in zip(first, second):
        np.testing.assert_array_equal(a, b)
    seen = np.sort(np.concatenate(first))
    np.testing.assert_array_equal(seen, ids)  # exact coverage, no overlap
    sizes = [len(s) for s in first]
    # Hash assignment scatters multinomially: all clients served, spread
    # within 25% of n at this size (verified 180-233 of mean 200).
    assert all(s > 0 for s in sizes)
    assert max(sizes) - min(sizes) <= 0.25 * len(ids)
    with pytest.raises(ValueError, match="n_clients"):
        stable_partition(ids, n_clients=1)


def test_stable_partition_follows_shared_ids():
    rng = np.random.RandomState(0)
    pool_a = np.sort(rng.choice(5000, size=500, replace=False))
    pool_b = np.sort(rng.choice(5000, size=500, replace=False))
    shared = np.intersect1d(pool_a, pool_b)
    assert len(shared) > 0
    assign: dict[int, set[int]] = {}
    for pool in (pool_a, pool_b):
        for k, shard in enumerate(stable_partition(pool, n_clients=4)):
            for i in shard:
                assign.setdefault(int(pool[i]), set()).add(k)
    assert all(len(v) == 1 for v in assign.values())


def test_stable_partition_run_end_to_end(tmp_path):
    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    result = run_federated(_fed_cfg(task_file, partition="stable"))
    assert result["summary"]["fed"]["partition"] == "stable"
    assert np.isfinite(result["R"]).all()
    rows = result["summary"]["poison_rows"]
    assert len(rows) == 2 * 3
    assert all(r["participated"] for r in rows)


def test_invalid_partition_rejected():
    from src.config_validation import validate_config

    cfg = {"name": "probe", "cl_method": "finetune", "device": "cpu",
           "data": {"tasks": "data/processed/tasks_chrono_dedup.npz", "scenario": "cii"},
           "fed": {"n_clients": 5, "partition": "bogus"}}
    with pytest.raises(ValueError, match="partition"):
        validate_config(cfg)


def _summary_key(summary: dict) -> dict:
    return {k: v for k, v in summary.items() if k != "wall_sec"}


def test_federated_rerun_is_bit_identical(tmp_path):
    # Reproducibility contract: same code + seed + threads => identical
    # outputs in one process (decision #52 covers cross-setting limits).
    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    first = run_federated(_fed_cfg(task_file))
    second = run_federated(_fed_cfg(task_file))
    np.testing.assert_array_equal(first["R"], second["R"])
    assert _summary_key(first["summary"]) == _summary_key(second["summary"])


def test_federated_ewc_exercises_anchor_sync(tmp_path):
    # Covers the post-aggregation anchor-reset lines with a real EWC run:
    # anchor tracks each client's local solution, Fisher stays local.
    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    cfg = _fed_cfg(task_file, aggregator="median")
    cfg["cl_method"] = "ewc"
    result = run_federated(cfg)
    assert np.isfinite(result["R"]).all()
    assert result["summary"]["cl_method"] == "ewc"
    # Inactive clients are excluded from the unweighted median; the record
    # must agree with per-client participation flags.
    rows = result["summary"]["poison_rows"]
    assert result["summary"]["fed"]["excluded_inactive_clients"] == sorted(
        {r["client"] for r in rows if not r["participated"]})


def test_multi_round_scales_matched_work(tmp_path):
    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    one = run_federated(_fed_cfg(task_file))
    two = run_federated(_fed_cfg(task_file, rounds=2))
    assert two["summary"]["fed"]["rounds"] == 2
    assert one["summary"]["fed"]["rounds"] == 1
    assert np.isfinite(two["R"]).all()
    r1 = two["summary"]["fed_round_rows"]
    assert len(r1) == 2 * 3 * 2  # tasks x clients x rounds
    assert {r["round"] for r in r1} == {0, 1}
    steps_1 = sum(r["optimizer_steps"] for r in one["summary"]["poison_rows"])
    steps_2 = sum(r["optimizer_steps"] for r in two["summary"]["poison_rows"])
    assert steps_2 == 2 * steps_1
    # Communication is per submission and submissions are same-sized:
    # totals match the round-row sums and repeat across rounds.
    assert two["summary"]["comm_bytes_total"] == sum(r["comm_bytes"] for r in r1)
    by_tc: dict[tuple[int, int], list[int]] = {}
    for r in r1:
        by_tc.setdefault((r["task"], r["client"]), []).append(r["comm_bytes"])
    assert all(len(set(v)) == 1 and v[0] > 0 for v in by_tc.values())
    # Dose is task-level: identical counts in both arms.
    for key in ("poison_changed_total", "poison_eligible_total"):
        assert two["summary"][key] == one["summary"][key]


def test_invalid_rounds_rejected(tmp_path):
    from src.config_validation import validate_config

    base = {"name": "probe", "cl_method": "finetune", "device": "cpu",
            "data": {"tasks": "data/processed/tasks_chrono_dedup.npz", "scenario": "cii"},
            "fed": {"n_clients": 5}}
    for bad in (0, -1, "2", True):
        with pytest.raises(ValueError, match="rounds"):
            validate_config({**base, "fed": {**base["fed"], "rounds": bad}})
    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    with pytest.raises(ValueError, match="rounds"):
        run_federated(_fed_cfg(task_file, rounds=0))
