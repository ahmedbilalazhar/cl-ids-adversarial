from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DAY_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday"]

ORDERS = {
    "default": DAY_ORDER,
    "alt": ["monday", "friday", "wednesday", "tuesday", "thursday"],
    "reverse": list(reversed(DAY_ORDER)),
}

ATTACKS_BY_DAY = {
    "monday": [],
    "tuesday": ["FTP-Patator", "SSH-Patator"],
    "wednesday": ["DoS Slowloris", "DoS Slowhttptest", "DoS Hulk", "DoS GoldenEye", "Heartbleed"],
    "thursday": ["Web Attack Brute Force", "Web Attack XSS", "Web Attack Sql Injection", "Infiltration"],
    "friday": ["Bot", "PortScan", "DDoS"],
}

BENIGN = "Benign"


def build_label_map() -> dict[str, int]:
    label_map = {BENIGN: 0}
    nxt = 1
    for day in DAY_ORDER:
        for lab in ATTACKS_BY_DAY[day]:
            if lab not in label_map:
                label_map[lab] = nxt
                nxt += 1
    return label_map


def build_tasks(
    df: pd.DataFrame,
    scenario: str = "cii",
    test_size: float = 0.3,
    benign_per_task: int = 5000,
    seed: int = 42,
    order: str = "default",
) -> tuple[list[dict], dict[str, int]]:
    label_map = build_label_map()
    # Phase 0 fix: repair mojibake Web-Attack labels already baked into the
    # checked-in parquet (see clean.py fix). Without this, Thursday's 3 Web
    # Attack families (1470+21+652 flows) silently match nothing in
    # ATTACKS_BY_DAY and are dropped from every task sequence built so far.
    if "Label" in df.columns:
        df = df.copy()

        def _repair(x: str) -> str:
            if x in label_map:
                return x
            low = str(x).lower()
            if "brute force" in low:
                return "Web Attack Brute Force"
            if "xss" in low:
                return "Web Attack XSS"
            if "sql injection" in low:
                return "Web Attack Sql Injection"
            return x

        df["Label"] = df["Label"].map(_repair)
    feature_cols = [c for c in df.columns if c not in ("Label", "day")]
    rng = np.random.RandomState(seed)
    day_order = ORDERS.get(order, DAY_ORDER)

    tasks = []
    seen_labels: list[str] = []

    for day in day_order:
        day_df = df[df["day"] == day]
        attacks = ATTACKS_BY_DAY[day]
        present_attacks = [a for a in attacks if a in set(day_df["Label"].unique())]

        parts = []
        if scenario == "cii" or day == "monday":
            ben = day_df[day_df["Label"] == BENIGN]
            if len(ben) > benign_per_task:
                ben = ben.sample(n=benign_per_task, random_state=seed)
            parts.append(ben)
            if scenario == "ci" and day != "monday":
                pass
        elif scenario == "ci" and day == "monday":
            ben = day_df[day_df["Label"] == BENIGN]
            if len(ben) > benign_per_task:
                ben = ben.sample(n=benign_per_task, random_state=seed)
            parts.append(ben)

        if scenario == "cii" and day != "monday":
            if BENIGN not in seen_labels:
                mon = df[(df["day"] == "monday") & (df["Label"] == BENIGN)]
                if len(mon) > benign_per_task:
                    mon = mon.sample(n=benign_per_task, random_state=seed)
                parts.append(mon)

        for a in present_attacks:
            parts.append(day_df[day_df["Label"] == a])

        if not parts:
            continue

        task_df = pd.concat(parts, ignore_index=True)
        y = task_df["Label"].map(label_map).to_numpy()
        X = task_df[feature_cols].to_numpy(dtype=np.float64)

        if len(np.unique(y)) < 2 and day != "monday":
            continue

        strat = y if len(np.unique(y)) > 1 else None
        try:
            X_tr, X_te, y_tr, y_te = train_test_split(
                X, y, test_size=test_size, random_state=seed, stratify=strat
            )
        except ValueError:
            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=seed)

        if scenario == "ci" and day == "monday":
            seen_labels = [BENIGN]
        else:
            for a in present_attacks:
                if a not in seen_labels:
                    seen_labels.append(a)
            if BENIGN not in seen_labels and scenario == "cii":
                seen_labels.insert(0, BENIGN)

        if scenario == "ci":
            allowed = [label_map[x] for x in seen_labels if x in label_map]
            mask_tr = np.isin(y_tr, allowed)
            mask_te = np.isin(y_te, allowed)
            X_tr, y_tr = X_tr[mask_tr], y_tr[mask_tr]
            X_te, y_te = X_te[mask_te], y_te[mask_te]

        tasks.append(
            {
                "day": day,
                "X_train": X_tr,
                "y_train": y_tr.astype(np.int64),
                "X_test": X_te,
                "y_test": y_te.astype(np.int64),
                "labels": sorted(set(task_df["Label"].tolist())),
            }
        )

    return tasks, label_map


def fit_scaler_on_train(tasks: list[dict]) -> list[dict]:
    for t in tasks:
        sc = StandardScaler()
        t["X_train"] = sc.fit_transform(t["X_train"]).astype(np.float32)
        t["X_test"] = sc.transform(t["X_test"]).astype(np.float32)
        t["scaler"] = sc
    return tasks


def save_tasks(
    tasks: list[dict],
    label_map: dict[str, int],
    out_path: Path,
    feature_cols: list[str] | None = None,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict = {"label_map": label_map, "tasks": []}
    if feature_cols is not None:
        payload["feature_cols"] = list(feature_cols)
    for t in tasks:
        payload["tasks"].append(
            {
                "day": t["day"],
                "labels": t["labels"],
                "X_train": t["X_train"],
                "y_train": t["y_train"],
                "X_test": t["X_test"],
                "y_test": t["y_test"],
            }
        )
    np.savez_compressed(out_path, payload_obj=np.array(payload, dtype=object), allow_pickle=True)
    meta = {"label_map": label_map, "days": [t["day"] for t in tasks], "n_tasks": len(tasks)}
    if feature_cols is not None:
        meta["feature_cols"] = list(feature_cols)
        out_path.parent.joinpath("feature_cols.json").write_text(json.dumps(list(feature_cols), indent=2))
    out_path.with_suffix(".json").write_text(json.dumps(meta, indent=2))


def load_tasks(path: Path) -> tuple[list[dict], dict[str, int]]:
    data = np.load(path, allow_pickle=True)["payload_obj"].item()
    tasks = data["tasks"]
    for t in tasks:
        t["X_train"] = np.asarray(t["X_train"], dtype=np.float32)
        t["y_train"] = np.asarray(t["y_train"], dtype=np.int64)
        t["X_test"] = np.asarray(t["X_test"], dtype=np.float32)
        t["y_test"] = np.asarray(t["y_test"], dtype=np.int64)
    return tasks, data["label_map"]


def load_feature_cols(path: Path) -> list[str] | None:
    meta_path = path.with_suffix(".json")
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if "feature_cols" in meta:
            return meta["feature_cols"]
    sidecar = path.parent / "feature_cols.json"
    if sidecar.exists():
        return json.loads(sidecar.read_text())
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", type=Path, default=Path("data/processed/cicids2017_clean.parquet"))
    ap.add_argument("--out", type=Path, default=Path("data/processed/tasks.npz"))
    ap.add_argument("--scenario", choices=["cii", "ci"], default="cii")
    ap.add_argument("--order", choices=list(ORDERS.keys()), default="default")
    ap.add_argument("--benign-per-task", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if args.processed.suffix == ".parquet":
        df = pd.read_parquet(args.processed)
    else:
        df = pd.read_csv(args.processed)

    tasks, label_map = build_tasks(
        df, scenario=args.scenario, benign_per_task=args.benign_per_task, seed=args.seed, order=args.order
    )
    tasks = fit_scaler_on_train(tasks)
    feature_cols = [c for c in df.columns if c not in ("Label", "day")]
    save_tasks(tasks, label_map, args.out, feature_cols=feature_cols)

    for i, t in enumerate(tasks):
        print(f"T{i} {t['day']}: train={len(t['y_train'])} test={len(t['y_test'])} labels={t['labels']}")
    print(f"label_map={label_map}")


if __name__ == "__main__":
    main()
