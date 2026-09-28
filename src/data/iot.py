"""CICIoT2023 task builder (dataset #3, v2 schema).

Provenance: HuggingFace mirror lacg030175/CIC-IoT-2023-full, random/
train+test parquets (30.8M + 7.7M rows). The pools never load fully into
memory: pass 1 counts labels; pass 2 takes exact, seeded uniform samples
without replacement per fine Label and per benign quarter, in 100k-row
batches. Peak transient footprint is one batch plus the capped sample.
Full-scale rerun on free-tier GPU is logged as follow-up, not as a blocker.

Tasks mirror the UNSW 4-task shape: T0 Benign+DDoS; T1 +DoS; T2 +Mirai+Recon;
T3 +Spoofing+Web-based+BruteForce. Benign quarters assigned by running
positional counter in file order (CII spirit). T0-fit scaler (strictly
future-blind). Output: taskset-v2 (pickle-free .npz + extended JSON sidecar).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

TASKS = [
    ["Benign", "DDoS"],
    ["Benign", "DoS"],
    ["Benign", "Mirai", "Recon"],
    ["Benign", "Spoofing", "Web-based", "BruteForce"],
]
TRAIN_CAP = 3000  # per fine Label (DDoS alone has 12 variants)
TEST_CAP = 1000
ROW_ID_COL = "_source_row_id"


BATCH = 100_000  # streaming batch: ~100k rows transient, never full pools
BENIGN_TRAIN_CAP = 8000
BENIGN_TEST_CAP = 4000


def _seed_for(*parts: str) -> int:
    import hashlib

    h = hashlib.md5("|".join(parts).encode(), usedforsecurity=False).hexdigest()
    return int(h[:8], 16)


def _pool_counts(pool_path: Path) -> tuple[dict, int, int]:
    """Pass 1 (streaming): per-(attack_class, Label) counts + benign total."""
    import pyarrow.parquet as pq

    counts: dict[tuple[str, str], int] = {}
    benign = 0
    total = 0
    pf = pq.ParquetFile(pool_path)
    for batch in pf.iter_batches(batch_size=BATCH, columns=["attack_class", "Label"]):
        df = batch.to_pandas()
        df["attack_class"] = df["attack_class"].astype(str)
        df["Label"] = df["Label"].astype(str)
        total += len(df)
        benign += int((df["attack_class"] == "Benign").sum())
        for (a, lab), g in df.groupby(["attack_class", "Label"]):
            counts[(str(a), str(lab))] = counts.get((str(a), str(lab)), 0) + len(g)
    return counts, benign, total


def _pool_sample(
    pool_path: Path, feat: list[str], seed: int, train: bool,
) -> tuple[dict, list, dict]:
    """Pass 2: collect only preselected within-group row ranks."""
    import pyarrow.parquet as pq

    cap = TRAIN_CAP if train else TEST_CAP
    bcap = BENIGN_TRAIN_CAP if train else BENIGN_TEST_CAP
    tag = "train" if train else "test"
    counts, benign_total, total = _pool_counts(pool_path)
    selected = {
        key: np.sort(np.random.RandomState(_seed_for(tag, *key, str(seed))).choice(
            n, size=min(cap, n), replace=False))
        for key, n in counts.items() if key[0] != "Benign"
    }
    benign_selected = []
    for q in range(4):
        lo = (q * benign_total + 3) // 4
        hi = ((q + 1) * benign_total + 3) // 4
        choice = np.random.RandomState(_seed_for(tag, "benign", str(q), str(seed))).choice(
            hi - lo, size=min(bcap, hi - lo), replace=False)
        benign_selected.append(np.sort(choice + lo))
    selected_benign = np.sort(np.concatenate(benign_selected))
    parts: dict[tuple[str, str], list[pd.DataFrame]] = {key: [] for key in selected}
    benign_parts: list[list[pd.DataFrame]] = [[] for _ in range(4)]
    seen: dict[tuple[str, str], int] = {}
    benign_seen = 0
    pos = 0
    cols = feat + ["attack_class", "Label", ROW_ID_COL]
    pf = pq.ParquetFile(pool_path)
    for batch in pf.iter_batches(batch_size=BATCH, columns=cols[:-1]):
        df = batch.to_pandas()
        df["attack_class"] = df["attack_class"].astype(str)
        df["Label"] = df["Label"].astype(str)
        df[ROW_ID_COL] = np.arange(pos, pos + len(df), dtype=np.int64)
        ben_mask = df["attack_class"] == "Benign"
        ben = df.loc[ben_mask]
        lo = np.searchsorted(selected_benign, benign_seen)
        hi = np.searchsorted(selected_benign, benign_seen + len(ben))
        if hi > lo:
            chosen = ben.iloc[selected_benign[lo:hi] - benign_seen]
            # The quarter is based on benign rank, which can differ from pool
            # row position when attacks are interleaved.
            ranks = selected_benign[lo:hi]
            quarter = np.minimum(3, (4 * ranks) // max(1, benign_total))
            for q in range(4):
                sub = chosen.iloc[np.flatnonzero(quarter == q)]
                if len(sub):
                    benign_parts[q].append(sub)
        benign_seen += len(ben)
        for key, group in df.loc[~ben_mask].groupby(["attack_class", "Label"], sort=False):
            start = seen.get(key, 0)
            target = selected.get(key)
            if target is None:
                raise ValueError(f"uncounted IoT label group: {key}")
            first = np.searchsorted(target, start)
            last = np.searchsorted(target, start + len(group))
            if last > first:
                parts[key].append(group.iloc[target[first:last] - start])
            seen[key] = start + len(group)
        pos += len(df)
    if pos != total or benign_seen != benign_total or seen != {
        key: count for key, count in counts.items() if key[0] != "Benign"
    }:
        raise ValueError("IoT pool changed between counting and sampling passes")
    atk_frames = {key: pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=cols)
                  for key, chunks in parts.items()}
    b_frames = [pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=cols)
                for chunks in benign_parts]
    for frame in [*atk_frames.values(), *b_frames]:
        for col in feat:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    stats = {"pool_rows": pos, "benign_rows": benign_seen, "attack_groups": len(atk_frames)}
    return atk_frames, b_frames, stats


def build(raw_dir: Path, seed: int = 42):
    import pyarrow.parquet as pq

    schema_names = pq.ParquetFile(raw_dir / "train.parquet").schema.names
    feat = [c for c in schema_names if c not in ("Label", "attack_class", "label")]
    tr_atk, tr_ben, tr_stats = _pool_sample(raw_dir / "train.parquet", feat, seed, True)
    te_atk, te_ben, te_stats = _pool_sample(raw_dir / "test.parquet", feat, seed, False)
    print(f"train pool: {tr_stats} | test pool: {te_stats}")
    all_cats = ({a for (a, _) in tr_atk} | {a for (a, _) in te_atk}) - {"Benign"}
    labels = ["Benign"] + sorted(all_cats)
    assert len(labels) == len(set(labels)), f"duplicate class names: {labels}"
    label_map = {label: i for i, label in enumerate(labels)}
    assert label_map["Benign"] == 0, label_map
    assert sorted(label_map.values()) == list(range(len(label_map)))
    tasks = []
    for ti, cats in enumerate(TASKS):
        tr_parts = [tr_ben[ti]]
        te_parts = [te_ben[ti]]
        for cat in cats:
            if cat == "Benign":
                continue
            tr_parts.append(pd.concat(
                [f for (a, _), f in tr_atk.items() if a == cat] or [tr_ben[ti].iloc[0:0]],
                ignore_index=True))
            te_parts.append(pd.concat(
                [f for (a, _), f in te_atk.items() if a == cat] or [te_ben[ti].iloc[0:0]],
                ignore_index=True))
        tr_df = pd.concat(tr_parts, ignore_index=True)
        te_df = pd.concat(te_parts, ignore_index=True)
        y_tr = tr_df["attack_class"].map(label_map).to_numpy(dtype=np.int64)
        y_te = te_df["attack_class"].map(label_map).to_numpy(dtype=np.int64)
        tasks.append({"X_train": tr_df[feat].to_numpy(dtype=np.float64),
                      "y_train": y_tr,
                      "X_test": te_df[feat].to_numpy(dtype=np.float64),
                      "y_test": y_te,
                      "id_train": tr_df[ROW_ID_COL].to_numpy(dtype=np.int64),
                      "id_test": te_df[ROW_ID_COL].to_numpy(dtype=np.int64),
                      "labels": sorted(set(tr_df["attack_class"]) | set(te_df["attack_class"]))})
        print(f"T{ti} {cats}: train={len(y_tr)} test={len(y_te)}")
    return tasks, label_map, feat


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=Path("data/raw_iot"))
    ap.add_argument("--out", type=Path, default=Path("data/processed/tasks_iot.npz"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    from src.paths import resolve_repo_path

    args.raw = resolve_repo_path(args.raw)
    args.out = resolve_repo_path(args.out)
    tasks, label_map, feat = build(args.raw, args.seed)
    # inf -> NaN BEFORE medians: rate-like columns can carry +/-inf, and a
    # median over inf is inf (fillna would no-op and the finite assert fails).
    t0raw = pd.DataFrame(tasks[0]["X_train"], columns=feat).replace([np.inf, -np.inf], np.nan)
    med = t0raw.median()
    sc = StandardScaler()
    sc.fit(t0raw.fillna(med).to_numpy(dtype=np.float64))
    for t in tasks:
        for k in ("X_train", "X_test"):
            d = pd.DataFrame(t[k], columns=feat).replace([np.inf, -np.inf], np.nan).fillna(med)
            t[k] = sc.transform(d.to_numpy(dtype=np.float64)).astype(np.float32)
        assert np.isfinite(t["X_train"]).all() and np.isfinite(t["X_test"]).all()
    from src.data.task_schema import assert_label_map, sha256_file, units_for, write_taskset

    assert_label_map(dict(label_map), "Benign")
    med_d = {c: float(med[c]) for c in feat}
    sidecar = write_taskset(
        args.out, tasks, dict(label_map),
        feature_cols=list(feat),
        feature_units=units_for(list(feat)),
        protocol_id="iot-capped-v2",
        split_def={"name": "iot-4task-cii-capped", "seed": args.seed,
                   "caps": {"train_per_label": TRAIN_CAP, "test_per_label": TEST_CAP,
                            "benign_per_task": BENIGN_TRAIN_CAP,
                            "benign_test_per_task": BENIGN_TEST_CAP},
                   "method": "two-pass exact seeded uniform sampling without replacement; "
                             "benign quarters by within-benign rank"},
        scaler_info={"kind": "T0-only", "fitted_on": "T0 train (strictly future-blind)",
                     "mean": [float(v) for v in sc.mean_.tolist()],
                     "scale": [float(v) for v in sc.scale_.tolist()]},
        imputation={"method": "T0-train medians (inf recoded to NaN first)", "medians": med_d},
        sources=[{"file": str(args.raw / "train.parquet"), "sha256": sha256_file(args.raw / "train.parquet")},
                 {"file": str(args.raw / "test.parquet"), "sha256": sha256_file(args.raw / "test.parquet")}],
        row_id_kind=("0-based row positions within the train/test parquet pool; "
                     "pool identity is supplied by the split and source checksums"),
    )
    print("in_dim:", len(feat), "| label_map:", label_map)
    print("saved", args.out, sidecar["npz_sha256"][:16])


if __name__ == "__main__":
    main()
