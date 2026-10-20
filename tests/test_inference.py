"""Phase-G inference contract: bundle roundtrip, strict schema, abstention."""
import numpy as np
import pandas as pd
import pytest
import torch

from src import inference
from src.models import build_model


def _trained() -> tuple[dict, dict, torch.nn.Module]:
    rng = np.random.RandomState(0)
    X = np.vstack([rng.randn(30, 4), rng.randn(30, 4) + 3.0]).astype(np.float64)
    y = np.array([0] * 30 + [1] * 30)
    cols = [f"f{i}" for i in range(4)]
    df = pd.DataFrame(X, columns=cols)
    medians = {c: float(df[c].median()) for c in cols}
    mean = df.mean().to_numpy()
    scale = df.std().to_numpy() + 0.5
    Xs = ((X - mean) / scale).astype(np.float32)
    model = build_model({"arch": "mlp", "hidden": [16, 8]}, 4, 2)
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)
    model.train()
    for _ in range(5):
        opt.zero_grad()
        loss = torch.nn.functional.cross_entropy(
            model(torch.from_numpy(Xs)), torch.from_numpy(y))
        loss.backward()
        opt.step()
    meta, state = inference.export_bundle(
        model, feature_cols=cols, label_map={"Benign": 0, "Attack": 1},
        scaler_mean=list(mean), scaler_scale=list(scale), medians=medians,
        protocol_id="synthetic-v1", train_config="synthetic")
    return meta, state, model


def test_bundle_roundtrip_preserves_predictions(tmp_path):
    meta, state, model = _trained()
    path = tmp_path / "bundle.pt"
    file_sha = inference.save_bundle(path, meta, state)
    meta2, state2 = inference.load_bundle(path, expected_file_sha256=file_sha)
    assert meta2["model_sha256"] == meta["model_sha256"]
    model2 = build_model({"arch": "mlp", "hidden": [16, 8]}, 4, 2)
    model2.load_state_dict(state2)
    rng = np.random.RandomState(1)
    df = pd.DataFrame(rng.randn(10, 4), columns=[f"f{i}" for i in range(4)])
    a = inference.predict_batch(meta, model, df)
    b = inference.predict_batch(meta2, model2, df)
    assert (a["labels"] == b["labels"]).all()
    assert a["n"] == 10 and a["n_abstained"] == 0 and a["n_imputed_cells"] == 0
    assert a["latency_ms_per_sample"] > 0


def test_schema_failures_are_loud(tmp_path):
    meta, _, model = _trained()
    df = pd.DataFrame(np.zeros((5, 4)), columns=[f"f{i}" for i in range(4)])
    with pytest.raises(ValueError, match="missing=.*f3"):
        inference.predict_batch(meta, model, df.drop(columns=["f3"]))
    with pytest.raises(ValueError, match="extra="):
        inference.predict_batch(meta, model, df.assign(zzz=1.0))
    with pytest.raises(ValueError, match="width"):
        inference.predict_batch(meta, model, np.zeros((5, 3)))
    with pytest.raises(ValueError, match="empty"):
        inference.predict_batch(meta, model, df.iloc[0:0])
    with pytest.raises(ValueError, match="max_batch"):
        inference.predict_batch(meta, model, df, max_batch=2)


def test_imputation_counted_and_abstention_consistent():
    meta, _, model = _trained()
    df = pd.DataFrame(np.zeros((6, 4)), columns=[f"f{i}" for i in range(4)])
    df.iloc[0, 0] = np.nan
    df.iloc[1, 2] = np.inf
    out = inference.predict_batch(meta, model, df, abstain_min_confidence=0.7)
    assert out["n_imputed_cells"] == 2
    assert (out["abstained"] == (out["confidence"] < 0.7)).all()
    assert out["n_abstained"] == int(out["abstained"].sum())
    assert set(out["names"]) <= {"Benign", "Attack", "ABSTAIN"}


def test_integrity_and_version_gates(tmp_path):
    meta, state, model = _trained()
    path = tmp_path / "bundle.pt"
    inference.save_bundle(path, meta, state)
    with pytest.raises(ValueError, match="file hash"):
        inference.load_bundle(path, expected_file_sha256="0" * 64)
    raw = bytearray(path.read_bytes())
    raw[len(raw) // 2] ^= 0xFF  # flip a byte mid-file (tensor payload region)
    path.write_bytes(bytes(raw))
    # Either the file no longer parses or the weight gate fires; both are
    # fail-closed ValueErrors.
    with pytest.raises(ValueError, match="unreadable or corrupt|mismatch"):
        inference.load_bundle(path)
    forged = dict(meta, model_sha256="0" * 64)
    with pytest.raises(ValueError, match="weight hash"):
        _load_raw(forged, state)
    bad = dict(meta, schema_version=999)
    with pytest.raises(ValueError, match="schema"):
        _load_raw(bad, state)
    with pytest.raises(ValueError, match="positive scale"):
        inference.export_bundle(model, feature_cols=["a"], label_map={"B": 0},
                                scaler_mean=[0.0], scaler_scale=[0.0],
                                medians={"a": 0.0}, protocol_id="x",
                                train_config="x")


def _load_raw(meta: dict, state: dict):
    import io as _io
    import tempfile
    from pathlib import Path as _P

    buf = _io.BytesIO()
    torch.save({"meta": meta, "state": state}, buf)
    p = _P(tempfile.mkdtemp()) / "b.pt"
    p.write_bytes(buf.getvalue())
    return inference.load_bundle(p)


def test_versioned_registry_and_rollback(tmp_path):
    from src.inference import list_bundles, rollback, save_versioned_bundle

    meta, state, _ = _trained()
    assert list_bundles(tmp_path, "mlp") == []
    first = save_versioned_bundle(tmp_path, "mlp", meta, state)
    assert first.name == "mlp_v1.pt"
    meta2 = dict(meta, protocol_id="synthetic-v2")
    second = save_versioned_bundle(tmp_path, "mlp", meta2, state)
    assert second.name == "mlp_v2.pt"
    entries = list_bundles(tmp_path, "mlp")
    assert [e["version"] for e in entries] == [2, 1]
    assert entries[1]["protocol_id"] == "synthetic-v1"
    back = rollback(tmp_path, "mlp", 1)
    assert back == first
    loaded, _ = inference.load_bundle(back)
    assert loaded["protocol_id"] == "synthetic-v1"
    with pytest.raises(ValueError, match="no bundle"):
        rollback(tmp_path, "mlp", 9)
    with pytest.raises(ValueError, match="no bundle"):
        rollback(tmp_path, "other", 1)
    first.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="hash mismatch"):
        rollback(tmp_path, "mlp", 1)
