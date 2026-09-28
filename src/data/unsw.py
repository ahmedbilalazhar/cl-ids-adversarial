"""UNSW-NB15 task builder (Phase-4 step 20, dataset #2).

Provenance: HuggingFace mirror Mireu-Lab/UNSW-NB15 (train.csv/test.csv).
WARNING (verified 2026-09-26): the mirror SWAPPED the canonical names —
their test.csv (175,341 rows) IS the canonical training set and train.csv
(82,332 rows) IS the canonical test set (distributions match Moustafa &
Slay 2015). This script uses the 175k pool for TRAIN and the 82k pool for
TEST, i.e. the canonical split is preserved, never re-split.

Protocol mirrors the CICIDS primary: 4 sequential tasks, Normal present in
every task (disjoint id-ordered slices, CII spirit), frozen T0-fit scaler,
one-hot proto/service/state (categories from train pool; unseen test
categories -> all-zero, disclosed), id rank as flow_order proxy.
Output schema == tasks.npz (X_train/y_train/X_test/y_test/labels +
label_map + feature_cols) so run_experiment/fedavg run unchanged.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

TASKS = [
    ["Normal", "Generic"],
    ["Normal", "Exploits", "Fuzzers"],
    ["Normal", "DoS", "Reconnaissance"],
    ["Normal", "Analysis", "Backdoor", "Shellcode", "Worms"],
]
CAT_COLS = ["proto", "service", "state"]
LABEL = "attack_cat"


def load_pools(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    # NOTE the mirror swap: 175k file = canonical train pool.
    tr = pd.read_csv(raw_dir / "test.csv", low_memory=False)
    te = pd.read_csv(raw_dir / "train.csv", low_memory=False)
    assert len(tr) == 175341 and len(te) == 82332, (len(tr), len(te))
    return tr, te


def encode(df_tr: pd.DataFrame, df_te: pd.DataFrame):
    df_tr = df_tr.copy()
    df_te = df_te.copy()
    for c in CAT_COLS:
        df_tr[c] = df_tr[c].fillna("-").astype(str)
        df_te[c] = df_te[c].fillna("-").astype(str)
    cat_maps = {}
    onehot = []
    for c in CAT_COLS:
        cats = sorted(df_tr[c].unique().tolist())
        cat_maps[c] = cats
        for df in (df_tr, df_te):
            for v in cats:
                col = f"{c}__{v}"
                df[col] = (df[c] == v).astype(np.float32)
                if df is df_tr:
                    onehot.append(col)
    num_cols = [
        c
        for c in df_tr.columns
        if c not in CAT_COLS + [LABEL, "label", "id"] + onehot
        and pd.api.types.is_numeric_dtype(df_tr[c])
    ]
    # Median imputation with T0-train medians is applied by the caller;
    # here just report NaN prevalence for the log.
    nanrep = {c: float(df_tr[c].isna().mean()) for c in num_cols if df_tr[c].isna().any()}
    feat = [f"{c}__{v}" for c in CAT_COLS for v in cat_maps[c]] + num_cols
    return df_tr, df_te, feat, num_cols, nanrep, cat_maps


def build(raw_dir: Path, seed: int = 42):
    df_tr, df_te = load_pools(raw_dir)
    df_tr, df_te, feat, num_cols, nanrep, cat_maps = encode(df_tr, df_te)
    print("NaN prevalence (train pool):", {k: round(v, 4) for k, v in nanrep.items()})
    # NOTE: the union MUST be parenthesized before subtracting the benign
    # label. `|` binds looser than `-`, so an unparenthesized
    # `A | B - {"Normal"}` keeps "Normal" from A and silently duplicates it
    # at position 0 AND its sorted position — the old code overwrote
    # Normal's id (benign was 7, not 0) via dict-dedup.
    all_cats = (set(df_tr[LABEL].unique()) | set(df_te[LABEL].unique())) - {"Normal"}
    labels = ["Normal"] + sorted(all_cats)
    assert len(labels) == len(set(labels)), f"duplicate class names: {labels}"
    label_map = {label: i for i, label in enumerate(labels)}
    assert label_map["Normal"] == 0, label_map
    assert sorted(label_map.values()) == list(range(len(label_map)))
    # Disjoint Normal slices across tasks (id order), CII spirit.
    n_tr = df_tr[df_tr[LABEL] == "Normal"].sort_values("id")
    n_te = df_te[df_te[LABEL] == "Normal"].sort_values("id")
    n_slices_tr = np.array_split(n_tr.index.to_numpy(), 4)
    n_slices_te = np.array_split(n_te.index.to_numpy(), 4)

    tasks = []
    for ti, cats in enumerate(TASKS):
        tr_parts = [df_tr.loc[n_slices_tr[ti]]]
        te_parts = [df_te.loc[n_slices_te[ti]]]
        for cat in cats:
            if cat == "Normal":
                continue
            tr_parts.append(df_tr[df_tr[LABEL] == cat].sort_values("id"))
            te_parts.append(df_te[df_te[LABEL] == cat].sort_values("id") if cat in set(df_te[LABEL]) else df_te.iloc[0:0])
        # Source row ids BEFORE concat resets the index: csv-positional ids
        # within each pool file (stable provenance for the v2 schema).
        ids_tr = np.concatenate([p.index.to_numpy(dtype=np.int64) for p in tr_parts])
        ids_te = np.concatenate([p.index.to_numpy(dtype=np.int64) for p in te_parts])
        tr_df = pd.concat(tr_parts, ignore_index=True)
        te_df = pd.concat(te_parts, ignore_index=True)
        y_tr = tr_df[LABEL].map(label_map).to_numpy(dtype=np.int64)
        y_te = te_df[LABEL].map(label_map).to_numpy(dtype=np.int64)
        X_tr = tr_df[feat].to_numpy(dtype=np.float64)
        X_te = te_df[feat].to_numpy(dtype=np.float64)
        tasks.append(
            {"X_train": X_tr, "y_train": y_tr, "X_test": X_te, "y_test": y_te,
             "id_train": ids_tr, "id_test": ids_te,
             "labels": sorted(set(tr_df[LABEL]) | set(te_df[LABEL]))}
        )
        print(f"T{ti} {cats}: train={len(y_tr)} test={len(y_te)}")
    return tasks, label_map, feat, num_cols


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=Path("data/raw_unsw"))
    ap.add_argument("--out", type=Path, default=Path("data/processed/tasks_unsw.npz"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    from src.paths import resolve_repo_path

    args.raw = resolve_repo_path(args.raw)
    args.out = resolve_repo_path(args.out)
    tasks, label_map, feat, num_cols = build(args.raw, args.seed)[:4]
    # Frozen scaler on T0 train; median imputation with T0 medians.
    med = {}
    t0 = pd.DataFrame(tasks[0]["X_train"], columns=feat).replace([np.inf, -np.inf], np.nan)
    for c in num_cols:
        med[c] = float(t0[c].median())
    sc = StandardScaler()
    sc.fit(t0[num_cols].fillna(pd.Series(med)).to_numpy(dtype=np.float64))
    for t in tasks:
        dtr = pd.DataFrame(t["X_train"], columns=feat).replace([np.inf, -np.inf], np.nan)
        dte = pd.DataFrame(t["X_test"], columns=feat).replace([np.inf, -np.inf], np.nan)
        dtr[num_cols] = dtr[num_cols].fillna(pd.Series(med))
        dte[num_cols] = dte[num_cols].fillna(pd.Series(med))
        t["X_train"] = np.hstack(
            [dtr[[c for c in feat if c not in num_cols]].to_numpy(dtype=np.float32),
             sc.transform(dtr[num_cols].to_numpy(dtype=np.float64)).astype(np.float32)]
        )
        t["X_test"] = np.hstack(
            [dte[[c for c in feat if c not in num_cols]].to_numpy(dtype=np.float32),
             sc.transform(dte[num_cols].to_numpy(dtype=np.float64)).astype(np.float32)]
        )
        assert np.isfinite(t["X_train"]).all() and np.isfinite(t["X_test"]).all()
    from src.data.task_schema import assert_label_map, sha256_file, units_for, write_taskset

    assert_label_map(dict(label_map), "Normal")
    tr_csv, te_csv = args.raw / "test.csv", args.raw / "train.csv"  # mirror swap
    feat_out = [c for c in feat if c not in num_cols] + num_cols
    sidecar = write_taskset(
        args.out, tasks, dict(label_map),
        feature_cols=feat_out,
        feature_units=units_for(feat_out),
        protocol_id="unsw-standard-v2",
        split_def={"name": "unsw-4task-cii", "seed": args.seed,
                   "note": "Normal sliced disjointly (id order) across 4 tasks; attacks by id order"},
        scaler_info={"kind": "T0-only", "fitted_on": "T0 train (strictly future-blind)",
                     "mean": [float(v) for v in sc.mean_.tolist()],
                     "scale": [float(v) for v in sc.scale_.tolist()]},
        imputation={"method": "T0-train medians", "medians": {k: float(v) for k, v in med.items()}},
        sources=[{"file": str(tr_csv), "sha256": sha256_file(tr_csv), "role": "canonical-train-pool-175341"},
                 {"file": str(te_csv), "sha256": sha256_file(te_csv), "role": "canonical-test-pool-82332"}],
        row_id_kind="UNSW csv positional index (0-based within each pool file)",
        extra={"n_tasks": 4},
    )
    print("in_dim:", len(feat_out), "| label_map:", label_map)
    print("saved", args.out, sidecar["npz_sha256"][:16])


if __name__ == "__main__":
    main()
