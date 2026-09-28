"""Lightweight regression tests — no dataset or GPU required."""
import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import average_accuracy, backward_transfer, forgetting, summarize


def test_metrics_on_identity_matrix():
    R = np.eye(3)
    assert average_accuracy(R) == 1 / 3
    s = summarize(R)
    assert set(s) == {"acc", "bwt", "fwt", "forgetting"}
    assert forgetting(R) >= 0.0


def test_bwt_zero_without_forgetting():
    R = np.ones((3, 3))
    assert backward_transfer(R) == 0.0


def test_configs_parse():
    cfgs = sorted((ROOT / "configs").rglob("*.yaml"))
    assert len(cfgs) == 214, f"211 audited configs plus T0, dedup, and E4 label control, got {len(cfgs)}"
    from scripts.groups import GROUPS
    from src.config_validation import validate_config

    grouped = {n for g in GROUPS.values() for n in g}
    for path in cfgs:  # all files, not just the first 20
        with open(path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        assert isinstance(cfg, dict), path.name
        assert isinstance(cfg.get("name"), str), path.name
        assert cfg.get("cl_method") in {"finetune", "ewc", "lwf", "er", "derpp", "joint"}, path.name
        assert isinstance((cfg.get("data") or {}).get("tasks"), str), path.name
        validate_config(cfg)
    # every grid entry resolves to exactly one config file
    from src.paths import find_config

    for key in grouped:
        assert find_config(key).exists(), key


def test_layout_contract():
    for d in ["src", "configs", "scripts", "docs", "data", "results", "notebooks", "tests"]:
        assert (ROOT / d).is_dir(), f"missing top-level dir: {d}"
    assert (ROOT / "README.md").exists()
    assert (ROOT / "pyproject.toml").exists()
    # Phase-A index docs — every major folder must be self-describing
    for doc in ["configs/README.md", "scripts/README.md", "docs/README.md", "data/README.md",
                "results/README.md", "docs/papers/README.md", "reports/README.md"]:
        assert (ROOT / doc).exists(), f"missing index doc: {doc}"


def test_entrypoint_and_notebook_regressions():
    env = dict(os.environ, CL_THREADS="1")
    status_import = subprocess.run(
        [sys.executable, "-c", "import scripts.grid_status"], cwd=ROOT,
        env=env, check=True, capture_output=True, text=True,
    )
    assert not status_import.stdout.strip()
    e5 = subprocess.run(
        [sys.executable, "scripts/e5_evasion.py", "--help"], cwd=ROOT,
        env=env, check=True, capture_output=True, text=True,
    )
    assert "--benign_sample" in e5.stdout
    notebook = json.loads((ROOT / "notebooks/architecture_colab.ipynb").read_text(encoding="utf-8"))
    cells = "".join("".join(cell.get("source", [])) for cell in notebook["cells"])
    assert 'Path("configs/arch").glob("ar_*.yaml")' in cells
    assert "architecture_colab_bundle_v2.zip" in cells
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "lint:\n\tpython -m ruff check src scripts tests" in makefile.replace("\r\n", "\n")
    assert "|| true" not in makefile


def _synthetic_tasks_file(path: Path) -> None:
    from src.data.task_schema import write_taskset

    rng = np.random.RandomState(0)
    n_feat = 8
    tasks = []
    for t, labels in enumerate([[0], [0, 1]]):
        if t == 0:
            y = np.zeros(60, dtype=np.int64)
            X = rng.randn(60, n_feat).astype(np.float32) * 0.5
        else:
            y = np.array([0] * 30 + [1] * 30, dtype=np.int64)
            X = rng.randn(60, n_feat).astype(np.float32)
            X[y == 1] += 2.0
        idx = rng.permutation(len(y))
        X, y = X[idx], y[idx]
        split = 42
        tasks.append({"day": f"syn_{t}", "labels": [str(v) for v in np.unique(y)],
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


def test_synthetic_end_to_end_single_and_federated(tmp_path):
    """Tiny e2e: both CLIs persist validated artifacts; interrupted writes never
    count as complete; resume works; tables rebuild; wrong-runner federated
    output is rejected."""

    from src.reporting import (
        check_artifact, config_hash, is_complete, save_results, sha256_file, source_tree_hash,
    )

    tmp = tmp_path
    out = tmp / "runs"
    out.mkdir(parents=True)
    task_file = tmp / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)

    base = {"device": "cpu", "epochs_per_task": 1, "batch_size": 16, "lr": 1e-3,
            "data": {"scenario": "cii", "tasks": str(task_file)},
            "feature_names": [f"f{i}" for i in range(8)]}
    single_cfg = dict(base, name="synth_single", seed=7, cl_method="finetune")
    fed_cfg = dict(base, name="synth_fed", seed=7, cl_method="finetune",
                   fed={"n_clients": 2, "malicious_id": 1, "alpha": 0.5, "local_epochs": 1})

    single_config = tmp / "single.yaml"
    fed_config = tmp / "fed.yaml"
    single_config.write_text(yaml.safe_dump(single_cfg), encoding="utf-8")
    fed_config.write_text(yaml.safe_dump(fed_cfg), encoding="utf-8")
    env = dict(os.environ, CL_THREADS="1")

    def cli(path: Path, *args: str) -> str:
        proc = subprocess.run(
            [sys.executable, "-m", "src.run_experiment", "--config", str(path),
             "--results-dir", str(tmp), "--resume", *args],
            cwd=ROOT, env=env, check=True, capture_output=True, text=True,
        )
        return proc.stdout

    cli(single_config)
    m1 = json.loads((out / "synth_single_manifest_seed7.json").read_text(encoding="utf-8"))
    assert m1["runner"] == "single-node" and m1["seed"] == 7
    assert m1["task_metadata_hash"] == sha256_file(task_file.with_suffix(".json"))
    assert is_complete(out, "synth_single", 7, single_cfg)

    cli(fed_config)
    r2 = json.loads((out / "synth_fed_summary_seed7.json").read_text(encoding="utf-8"))
    assert isinstance(r2.get("fed"), dict)
    assert is_complete(out, "synth_fed", 7, fed_cfg)
    assert "SKIP synth_fed seed 7" in cli(fed_config)

    # A crash after the pending marker and one output must not complete seed 8.
    seed8_cfg = dict(fed_cfg, seed=8)
    marker = {"name": "synth_fed", "seed": 8, "config_hash": config_hash(seed8_cfg),
              "task_file_hash": sha256_file(task_file),
              "task_metadata_hash": sha256_file(task_file.with_suffix(".json")),
              "source_tree_hash": source_tree_hash()}
    (out / "synth_fed_pending_seed8.json").write_text(json.dumps(marker), encoding="utf-8")
    (out / "synth_fed_summary_seed8.json").write_text("{truncated", encoding="utf-8")
    assert not is_complete(out, "synth_fed", 8, seed8_cfg)
    cli(fed_config, "--seed", "8")
    assert is_complete(out, "synth_fed", 8, seed8_cfg)

    subprocess.run([sys.executable, "-m", "src.run_experiment", "--rebuild-table",
                    "--results-dir", str(tmp)], cwd=ROOT, env=env, check=True, capture_output=True)
    with open(tmp / "baseline_table.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert {(r["name"], r["seed"]) for r in rows} == {
        ("synth_single", "7"), ("synth_fed", "7"), ("synth_fed", "8")}
    subprocess.run([sys.executable, "scripts/stats_summary.py", "--results-dir", str(tmp)],
                   cwd=ROOT, env=env, check=True, capture_output=True)
    with open(tmp / "stats_summary.csv", encoding="utf-8", newline="") as f:
        assert {r["name"] for r in csv.DictReader(f)} == {"synth_single", "synth_fed"}
    with open(tmp / "baseline_table.csv", encoding="utf-8", newline="") as f:
        rows2 = list(csv.DictReader(f))
    assert rows == rows2

    meta_path = task_file.with_suffix(".json")
    original_meta = meta_path.read_bytes()
    meta_path.write_text('{"schema_version": 2, "protocol_id": "tampered"}', encoding="utf-8")
    assert not check_artifact(out, "synth_single", 7, single_cfg)["complete"]
    meta_path.write_bytes(original_meta)
    assert check_artifact(out, "synth_single", 7, single_cfg)["complete"]

    # A single-node payload cannot be committed under a federated config.
    wrong = {"R": np.eye(2), "summary": json.loads(
        (out / "synth_single_summary_seed7.json").read_text(encoding="utf-8"))}
    try:
        save_results(wrong, dict(fed_cfg), out)
    except ValueError:
        pass
    else:
        raise AssertionError("federated summary from wrong runner was not rejected")
    assert check_artifact(out, "synth_fed", 7, fed_cfg)["complete"]


def test_reporting_rejects_unmanifested_federated_without_fed():
    from src.reporting import validate_summary
    try:
        validate_summary({"acc": 0.5, "bwt": 0.0, "fwt": 0.0, "forgetting": 0.0,
                          "seed": 1, "cl_method": "finetune", "scenario": "cii"},
                         {"seed": 1, "fed": {"n_clients": 5}})
    except ValueError:
        pass
    else:
        raise AssertionError("missing fed field was not rejected")


def test_backdoor_cli_persists_eligible_endpoint_single_and_federated(tmp_path):
    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    attack = {"type": "backdoor", "attack_class": "Attack", "target_class": 0,
              "budget": 0.5, "trigger": {"features": ["f0"], "values": [3.0]}}
    base = {"seed": 7, "device": "cpu", "cl_method": "finetune",
            "epochs_per_task": 1, "batch_size": 16, "lr": 1e-3,
            "data": {"scenario": "cii", "tasks": str(task_file)}, "attack": attack}
    env = dict(os.environ, CL_THREADS="1")
    for name, fed in (("backdoor_single", None),
                      ("backdoor_fed", {"n_clients": 2, "malicious_id": 1,
                                        "alpha": 0.5, "local_epochs": 1})):
        cfg = dict(base, name=name)
        if fed:
            cfg["fed"] = fed
        config_path = tmp_path / f"{name}.yaml"
        config_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
        subprocess.run(
            [sys.executable, "-m", "src.run_experiment", "--config", str(config_path),
             "--results-dir", str(tmp_path), "--resume"],
            cwd=ROOT, env=env, check=True, capture_output=True, text=True,
        )
        summary = json.loads((tmp_path / "runs" / f"{name}_summary_seed7.json").read_text(encoding="utf-8"))
        assert summary["asr_rows"][0]["asr"] is None
        assert summary["asr_rows"][0]["eligible"] == 0
        assert summary["asr_eligible"] > 0
        assert summary["asr_successes"] <= summary["asr_eligible"]
        if fed:
            assert "poison_rows" in summary


def test_pending_only_seed_preserves_provenance(tmp_path):
    from src.reporting import config_hash, save_results, sha256_file

    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    cfg = {"name": "pending_probe", "seed": 3, "cl_method": "finetune",
           "lr": 0.001, "data": {"scenario": "cii", "tasks": str(task_file)}}
    marker = {"name": cfg["name"], "seed": cfg["seed"],
              "config_hash": config_hash(cfg), "task_file_hash": sha256_file(task_file),
              "task_metadata_hash": sha256_file(task_file.with_suffix(".json"))}
    pending = tmp_path / "pending_probe_pending_seed3.json"
    pending.write_text(json.dumps(marker), encoding="utf-8")
    changed = dict(cfg, lr=0.002)
    result = {"R": np.eye(2), "summary": {"acc": 0.5, "bwt": 0.0,
              "fwt": 0.0, "forgetting": 0.0, "seed": 3,
              "cl_method": "finetune", "scenario": "cii"}}
    try:
        save_results(result, changed, tmp_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("pending-only seed from another config was overwritten")
    assert json.loads(pending.read_text(encoding="utf-8")) == marker
    assert not (tmp_path / "pending_probe_manifest_seed3.json").exists()


def test_manifest_rejects_matrix_seed_config_runner_and_hash_mismatch(tmp_path):
    from src.reporting import check_artifact, save_results, sha256_file

    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    cfg = {"name": "integrity_probe", "seed": 3, "cl_method": "finetune",
           "lr": 0.001, "data": {"scenario": "cii", "tasks": str(task_file)}}
    result = {"R": np.eye(2), "summary": {"acc": 0.5, "bwt": 0.0,
              "fwt": 0.0, "forgetting": 0.0, "seed": 3,
              "cl_method": "finetune", "scenario": "cii"}}
    save_results(result, cfg, tmp_path)
    r_path = tmp_path / "integrity_probe_R_seed3.csv"
    s_path = tmp_path / "integrity_probe_summary_seed3.json"
    m_path = tmp_path / "integrity_probe_manifest_seed3.json"
    original_r, original_s, original_m = r_path.read_bytes(), s_path.read_bytes(), m_path.read_bytes()
    assert check_artifact(tmp_path, cfg["name"], 3, cfg)["complete"]

    r_path.write_text("not,a,matrix\n", encoding="utf-8")
    assert not check_artifact(tmp_path, cfg["name"], 3, cfg)["complete"]
    r_path.write_bytes(original_r)
    summary = json.loads(original_s)
    summary["seed"] = 4
    s_path.write_text(json.dumps(summary), encoding="utf-8")
    manifest = json.loads(original_m)
    manifest["summary_sha256"] = sha256_file(s_path)
    m_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert "seed" in check_artifact(tmp_path, cfg["name"], 3, cfg)["reason"]
    s_path.write_bytes(original_s)
    m_path.write_bytes(original_m)
    assert not check_artifact(tmp_path, cfg["name"], 3, dict(cfg, lr=0.002))["complete"]
    manifest["runner"] = "federated"
    m_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert not check_artifact(tmp_path, cfg["name"], 3, cfg)["complete"]
    m_path.write_bytes(original_m)
    manifest["task_file_hash"] = "0" * 64
    m_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert not check_artifact(tmp_path, cfg["name"], 3, cfg)["complete"]


def test_manifest_rejects_runtime_source_mismatch(tmp_path):
    from src.reporting import check_artifact, save_results

    task_file = tmp_path / "tasks_synth.npz"
    _synthetic_tasks_file(task_file)
    cfg = {"name": "code_probe", "seed": 3, "cl_method": "finetune",
           "data": {"scenario": "cii", "tasks": str(task_file)}}
    result = {"R": np.eye(2), "summary": {"acc": 0.5, "bwt": 0.0,
              "fwt": None, "forgetting": 0.0, "seed": 3,
              "cl_method": "finetune", "scenario": "cii"}}
    try:
        save_results(result, cfg, tmp_path, expected_code_hash="0" * 64)
    except RuntimeError:
        pass
    else:
        raise AssertionError("changed runtime source was committed")
    assert not (tmp_path / "code_probe_manifest_seed3.json").exists()
    save_results(result, cfg, tmp_path)
    manifest_path = tmp_path / "code_probe_manifest_seed3.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == 3
    assert check_artifact(tmp_path, "code_probe", 3, cfg)["provenance_level"] == "code-hashed"
    manifest["source_tree_hash"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert "source tree hash" in check_artifact(tmp_path, "code_probe", 3, cfg)["reason"]


def test_iot_sampling_preserves_source_rows_and_spaced_feature_names(tmp_path, monkeypatch):
    import pandas as pd

    from src.data import iot

    classes = (["Benign"] * 16 + ["DDoS", "DoS", "Mirai", "Recon",
                                   "Spoofing", "Web-based", "BruteForce"] * 3)
    frame = pd.DataFrame({
        "Protocol Type": np.arange(len(classes), dtype=np.float32) + 100,
        "Rate": np.arange(len(classes), dtype=np.float32) * 2,
        "attack_class": classes,
        "Label": classes,
    })
    frame.to_parquet(tmp_path / "train.parquet", index=False)
    frame.to_parquet(tmp_path / "test.parquet", index=False)
    monkeypatch.setattr(iot, "BATCH", 4)
    monkeypatch.setattr(iot, "TRAIN_CAP", 2)
    monkeypatch.setattr(iot, "TEST_CAP", 2)
    monkeypatch.setattr(iot, "BENIGN_TRAIN_CAP", 2)
    monkeypatch.setattr(iot, "BENIGN_TEST_CAP", 2)
    tasks, label_map, features = iot.build(tmp_path, seed=4)
    assert label_map["Benign"] == 0
    assert features[0] == "Protocol Type"
    for task in tasks:
        ids = task["id_train"]
        assert len(ids) == len(np.unique(ids))
        np.testing.assert_array_equal(task["X_train"][:, 0], frame.iloc[ids]["Protocol Type"])


def test_cicids_content_dedup_keeps_first_source_row():
    import pandas as pd

    from src.data.sequence import build_tasks

    frame = pd.DataFrame({
        "Label": ["Benign"] * 8,
        "day": ["monday"] * 8,
        "flow_order": np.arange(8),
        "f": [1, 1, 2, 3, 4, 5, 6, 7],
    })
    tasks, _ = build_tasks(frame, split="chrono", dedup_content=True)
    assert len(tasks) == 1
    ids = np.r_[tasks[0]["id_train"], tasks[0]["id_test"]]
    assert len(ids) == 7 and 0 in ids and 1 not in ids
    assert not np.intersect1d(tasks[0]["id_train"], tasks[0]["id_test"]).size


def test_post_scale_content_exclusion_checks_all_train_tasks():
    from src.data.sequence import exclude_test_content_matches

    tasks = [
        {"X_train": np.array([[1.0]], dtype=np.float32),
         "y_train": np.array([0]), "X_test": np.array([[2.0]], dtype=np.float32),
         "y_test": np.array([0]), "id_test": np.array([1])},
        {"X_train": np.array([[3.0]], dtype=np.float32),
         "y_train": np.array([1]), "X_test": np.array([[1.0], [4.0]], dtype=np.float32),
         "y_test": np.array([0, 1]), "id_test": np.array([2, 3])},
    ]
    assert exclude_test_content_matches(tasks) == 1
    np.testing.assert_array_equal(tasks[1]["id_test"], [3])


def test_v2_source_ids_are_scoped_to_source_pool():
    from src.data.task_schema import _validate_row_ids

    task = {"id_train": np.array([0]), "id_test": np.array([0])}
    try:
        _validate_row_ids([task], [{"role": "shared"}])
    except ValueError:
        pass
    else:
        raise AssertionError("single-source train/test row overlap was accepted")
    _validate_row_ids([task], [{"role": "train"}, {"role": "test"}])
