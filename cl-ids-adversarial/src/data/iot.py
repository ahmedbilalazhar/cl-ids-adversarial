"""CICIoT2023 task builder (Phase-4 step 20, dataset #3).

Provenance: HuggingFace mirror lacg030175/CIC-IoT-2023-full, random/
train+test parquets (40 numeric flow features + Label/attack_class/label).
Scale control (disclosed): the full files are ~8M+ rows; replication uses a
seed-fixed stratified subsample (train cap 3k/Label, test cap 1k/Label,
positional order = capture-order proxy) to keep CPU grids tractable and to
match the CICIDS scale (ours ~180k rows vs IoT-full ~15M).
Full-scale rerun on free-tier GPU is logged as follow-up, not as a blocker.

Tasks mirror the UNSW 4-task shape: T0 Benign+DDoS; T1 +DoS; T2 +Mirai+Recon;
T3 +Spoofing+Web-based+BruteForce. Benign split into disjoint positional
quarters across tasks (CII spirit). Frozen T0-fit scaler. Output schema ==
tasks.npz.
"""
from __future__ import annotations

import argparse
import json
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


def capped(g: pd.DataFrame, cap: int, seed: int) -> pd.DataFrame:
    if len(g) <= cap:
        return g
    return g.sample(n=cap, random_state=seed)


def build(raw_dir: Path, seed: int = 42):
    tr = pd.read_parquet(raw_dir / "train.parquet")
    te = pd.read_parquet(raw_dir / "test.parquet")
    feat = [c for c in tr.columns if c not in ("Label", "attack_class", "label")]
    for c in feat:  # numeric coercion, median handled at scaler stage
        tr[c] = pd.to_numeric(tr[c], errors="coerce")
        te[c] = pd.to_numeric(te[c], errors="coerce")
    labels = ["Benign"] + sorted(set(tr["attack_class"]) | set(te["attack_class"]) - {"Benign"})
    label_map = {l: i for i, l in enumerate(labels)}
    ben_tr = tr[tr["attack_class"] == "Benign"]
    ben_te = te[te["attack_class"] == "Benign"]
    btr = np.array_split(ben_tr.index.to_numpy(), 4)
    bte = np.array_split(ben_te.index.to_numpy(), 4)
    BENIGN_PER_TASK = 8000  # matches CICIDS benign_per_task=5000 scale
    tasks = []
    for ti, cats in enumerate(TASKS):
        tr_parts = [capped(tr.loc[btr[ti]], BENIGN_PER_TASK, seed)]
        te_parts = [capped(te.loc[bte[ti]], BENIGN_PER_TASK // 2, seed)]
        for cat in cats:
            if cat == "Benign":
                continue
            gtr = tr[tr["attack_class"] == cat]
            gte = te[te["attack_class"] == cat]
            # Stratify by fine Label within class so rare variants survive.
            tr_parts += [capped(g, TRAIN_CAP, seed) for _, g in gtr.groupby("Label")]
            te_parts += [capped(g, TEST_CAP, seed) for _, g in gte.groupby("Label")]
        tr_df = pd.concat(tr_parts, ignore_index=True)
        te_df = pd.concat(te_parts, ignore_index=True)
        y_tr = tr_df["attack_class"].map(label_map).to_numpy(dtype=np.int64)
        y_te = te_df["attack_class"].map(label_map).to_numpy(dtype=np.int64)
        tasks.append({"X_train": tr_df[feat].to_numpy(dtype=np.float64),
                      "y_train": y_tr,
                      "X_test": te_df[feat].to_numpy(dtype=np.float64),
                      "y_test": y_te,
                      "labels": sorted(set(tr_df["attack_class"]) | set(te_df["attack_class"]))})
        print(f"T{ti} {cats}: train={len(y_tr)} test={len(y_te)}")
    return tasks, label_map, feat


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=Path("data/raw_iot"))
    ap.add_argument("--out", type=Path, default=Path("data/processed/tasks_iot.npz"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    tasks, label_map, feat = build(args.raw, args.seed)
    med = pd.DataFrame(tasks[0]["X_train"], columns=feat).median()
    sc = StandardScaler()
    sc.fit(pd.DataFrame(tasks[0]["X_train"], columns=feat).fillna(med).to_numpy(dtype=np.float64))
    for t in tasks:
        for k in ("X_train", "X_test"):
            d = pd.DataFrame(t[k], columns=feat).fillna(med)
            t[k] = sc.transform(d.to_numpy(dtype=np.float64)).astype(np.float32)
        assert np.isfinite(t["X_train"]).all() and np.isfinite(t["X_test"]).all()
    payload = {"label_map": label_map, "tasks": [
        {"X_train": t["X_train"], "y_train": t["y_train"], "X_test": t["X_test"],
         "y_test": t["y_test"], "labels": t["labels"]} for t in tasks]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, payload_obj=np.array(payload, dtype=object), allow_pickle=True)
    args.out.with_suffix(".json").write_text(
        json.dumps({"label_map": label_map, "n_tasks": 4, "feature_cols": feat,
                    "caps": {"train_per_label": TRAIN_CAP, "test_per_label": TEST_CAP,
                             "benign_per_task": 8000, "benign_test_per_task": 4000}}))
    print("in_dim:", len(feat), "| label_map:", label_map)
    print("saved", args.out)


if __name__ == "__main__":
    main()
