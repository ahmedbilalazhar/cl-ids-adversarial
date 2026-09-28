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


def _chrono_split_per_class(
    X: np.ndarray, y: np.ndarray, order: np.ndarray, test_size: float, day: str,
    ids: np.ndarray | None = None,
) -> tuple:
    """Time-ordered train/test split, stratified by class.

    Within each class, flows are ordered by ``flow_order`` (capture-order
    proxy); the FIRST (1-test_size) fraction trains, the LAST test_size
    fraction tests. The ordering is PER CLASS, not a globally chronological
    deployment stream: different classes interleave arbitrarily in capture
    time, and this function must not be described as reproducing a global
    stream order. Guarantees: train is strictly earlier than test within
    every class; every class with >=2 flows gets >=1 test flow. Singleton
    classes go to train only (disclosed in the build log).
    When ``ids`` (source row ids aligned with X/y) is given, the selected
    ids are returned alongside as (X_tr, X_te, y_tr, y_te, ids_tr, ids_te).
    """
    tr_parts, te_parts = [], []
    for lab in np.unique(y):
        idx = np.where(y == lab)[0]
        idx = idx[np.argsort(order[idx], kind="stable")]
        n = len(idx)
        if n == 1:
            print(f"  [chrono] {day}: singleton class id={lab} -> train only (no test sample)")
            tr_parts.append(idx)
            continue
        n_te = max(1, int(round(n * test_size)))
        n_te = min(n_te, n - 1)  # keep >=1 train sample
        tr_parts.append(idx[: n - n_te])
        te_parts.append(idx[n - n_te :])
    tr = np.concatenate(tr_parts)
    te = np.concatenate(te_parts) if te_parts else np.zeros(0, dtype=np.int64)
    if ids is None:
        return X[tr], X[te], y[tr], y[te]
    ids = np.asarray(ids)
    return X[tr], X[te], y[tr], y[te], ids[tr], ids[te]


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
    split: str = "random",
    dedup_content: bool = False,
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
    # The cleaner assigns flow_order separately in each CSV. Keep its ordering
    # role, but use the parquet row position as a globally unique source ID.
    df = df.copy()
    df["_source_row_id"] = np.arange(len(df), dtype=np.int64)
    feature_cols = [c for c in df.columns if c not in ("Label", "day", "flow_order", "_source_row_id")]
    if dedup_content:
        before = len(df)
        df = df.drop_duplicates(subset=feature_cols + ["Label"], keep="first")
        print(f"[dedup-content] removed {before - len(df)} repeated feature+label rows globally")
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
        task_order = (
            task_df["flow_order"].to_numpy(dtype=np.int64)
            if "flow_order" in task_df.columns
            else np.arange(len(task_df))
        )
        ids_all = task_df["_source_row_id"].to_numpy(dtype=np.int64)

        if len(np.unique(y)) < 2 and day != "monday":
            continue

        if split == "chrono":
            X_tr, X_te, y_tr, y_te, ids_tr, ids_te = _chrono_split_per_class(
                X, y, task_order, test_size=test_size, day=day, ids=ids_all
            )
        else:
            strat = y if len(np.unique(y)) > 1 else None
            try:
                X_tr, X_te, y_tr, y_te, ids_tr, ids_te = train_test_split(
                    X, y, ids_all, test_size=test_size, random_state=seed, stratify=strat
                )
            except ValueError:
                X_tr, X_te, y_tr, y_te, ids_tr, ids_te = train_test_split(
                    X, y, ids_all, test_size=test_size, random_state=seed)

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
            ids_tr, ids_te = ids_tr[mask_tr], ids_te[mask_te]

        tasks.append(
            {
                "day": day,
                "X_train": X_tr,
                "y_train": y_tr.astype(np.int64),
                "X_test": X_te,
                "y_test": y_te.astype(np.int64),
                "id_train": np.asarray(ids_tr, dtype=np.int64),
                "id_test": np.asarray(ids_te, dtype=np.int64),
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


def fit_scaler_offline_init(tasks: list[dict], n_fit: int = 2) -> list[dict]:
    """Fit ONE StandardScaler on the first ``n_fit`` tasks' TRAIN data and
    apply it to every task's train and test splits.

    ACCURATE CHARACTERIZATION (Phase-2 correction): this is an
    OFFLINE-INITIALIZATION protocol, not strictly future-blind at T0. The
    scaler is fit on T0+T1 training data BEFORE T0 training starts, so T0's
    training already uses statistics from T1 rows (same-distribution
    initialization data, but not future-blind). It excludes all TEST rows and
    all rows from tasks beyond the fit window. Prefer this name;
    ``fit_scaler_frozen`` is a behavior-identical alias kept so existing
    configs and results keep their meaning.
    """
    sc = StandardScaler()
    X_fit = np.concatenate([t["X_train"] for t in tasks[:n_fit]], axis=0)
    sc.fit(X_fit)
    for t in tasks:
        t["X_train"] = sc.transform(t["X_train"]).astype(np.float32)
        t["X_test"] = sc.transform(t["X_test"]).astype(np.float32)
        t["scaler"] = sc
        t["scaler_fitted_on"] = (
            "T0 train (future-blind)" if n_fit == 1 else f"T0..T{n_fit - 1} train (offline init)"
        )
    return tasks


def fit_scaler_frozen(tasks: list[dict], n_fit: int = 2) -> list[dict]:
    """Behavior-identical alias of :func:`fit_scaler_offline_init` (kept so
    existing configs, manifests, and results keep their meaning)."""
    return fit_scaler_offline_init(tasks, n_fit=n_fit)


def fit_scaler_t0_only(tasks: list[dict]) -> list[dict]:
    """Sensitivity arm: fit the single scaler on T0 TRAIN only (strictly
    future-blind — no T1 row touches the statistics), apply to all tasks.
    Compare against the T0+T1 offline-init protocol to quantify how much the
    initialization window matters."""
    return fit_scaler_offline_init(tasks, n_fit=1)


def exclude_test_content_matches(tasks: list[dict]) -> int:
    """Remove test records matching any train record at model precision.

    This is used only by the explicit duplicate-disjoint sensitivity arm.
    The source-row split remains unchanged; the exclusion operates on the
    final float32 feature representation seen by the model.
    """
    def rows(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        arr = np.ascontiguousarray(np.column_stack((x, y)), dtype=np.float64)
        return arr.view(f"V{arr.dtype.itemsize * arr.shape[1]}").reshape(-1)

    train_rows = np.concatenate([rows(t["X_train"], t["y_train"]) for t in tasks])
    removed = 0
    for task in tasks:
        keep = ~np.isin(rows(task["X_test"], task["y_test"]), train_rows)
        removed += int((~keep).sum())
        for key in ("X_test", "y_test", "id_test"):
            task[key] = task[key][keep]
    return removed


def _scaler_info(tasks: list[dict], kind: str) -> dict:
    if kind == "per-task":
        return {
            "kind": kind,
            "per_task": [
                {"task": i, "fitted_on": f"T{i} train", "mean": t["scaler"].mean_.tolist(),
                 "scale": t["scaler"].scale_.tolist()}
                for i, t in enumerate(tasks)
            ],
        }
    sc = None
    fitted_on = ""
    for t in tasks:
        if isinstance(t.get("scaler"), StandardScaler):
            sc = t["scaler"]
            fitted_on = str(t.get("scaler_fitted_on", ""))
            break
    if sc is None:
        return {"kind": kind, "fitted_on": fitted_on or "unknown", "mean": [], "scale": []}
    return {
        "kind": kind,
        "fitted_on": fitted_on or kind,
        "mean": [float(v) for v in np.asarray(sc.mean_).tolist()],
        "scale": [float(v) for v in np.asarray(sc.scale_).tolist()],
    }


def save_tasks(
    tasks: list[dict],
    label_map: dict[str, int],
    out_path: Path,
    feature_cols: list[str] | None = None,
    *,
    protocol_id: str = "cicids-random-pertask",
    split_def: dict | None = None,
    scaler_kind: str = "per-task",
    sources: list[dict] | None = None,
    extra: dict | None = None,
) -> dict:
    """Write a v2 task artifact (pickle-free .npz + extended JSON sidecar).

    Existing checked-in legacy files are NOT rewritten here; they load via
    the authenticated-legacy path in :func:`load_tasks` until regenerated.
    """
    from src.data.task_schema import assert_label_map, units_for, write_taskset

    assert_label_map(dict(label_map), BENIGN)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar = write_taskset(
        out_path,
        tasks,
        dict(label_map),
        feature_cols=list(feature_cols or []),
        feature_units=units_for(list(feature_cols or [])),
        protocol_id=protocol_id,
        split_def=split_def or {},
        scaler_info=_scaler_info(tasks, scaler_kind),
        imputation={"method": "none (clean parquet is finite; asserted at build)"},
        sources=sources or [],
        row_id_kind=(
            "0-based row positions in cleaned parquet; flow_order is used only "
            "as a per-class ordering proxy, not a global deployment stream"
        ),
        extra=extra,
    )
    out_path.parent.joinpath("feature_cols.json").write_text(
        json.dumps(list(feature_cols or []), indent=2), encoding="utf-8")
    return sidecar


def load_tasks(path: Path) -> tuple[list[dict], dict[str, int]]:
    from src.data.task_schema import is_v2, legacy_allowlist, read_v2, sha256_file

    if is_v2(path):
        return read_v2(path)
    # Controlled migration path: legacy pickle payloads load ONLY when their
    # exact bytes match the checked-in allowlist (audited baseline).
    allow = legacy_allowlist()
    digest = sha256_file(path)
    if allow.get(path.name) != digest:
        raise ValueError(
            f"{path} is a legacy (pickle) task artifact whose sha256 is not in "
            f"src/data/legacy_task_hashes.json. Regenerate it with the v2 "
            f"builders instead of loading unauthenticated pickles."
        )
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
    ap.add_argument(
        "--dedup-content", action="store_true",
        help="sensitivity arm: keep the first global feature+label occurrence before splitting",
    )
    ap.add_argument(
        "--split",
        choices=["random", "chrono"],
        default="random",
        help="random: stratified train_test_split (status quo secondary); "
        "chrono: per-class time-ordered split by flow_order (primary).",
    )
    ap.add_argument(
        "--scaler",
        choices=["pertask", "frozen", "t0"],
        default="pertask",
        help="pertask: fit one StandardScaler per task train split (legacy secondary); "
        "frozen: ONE scaler fit on T0+T1 train BEFORE T0 training (offline "
        "initialization, NOT strictly future-blind at T0); "
        "t0: sensitivity arm, scaler fit on T0 train only (strictly future-blind).",
    )
    args = ap.parse_args()
    from src.paths import resolve_repo_path

    args.processed = resolve_repo_path(args.processed)
    args.out = resolve_repo_path(args.out)

    if args.processed.suffix == ".parquet":
        df = pd.read_parquet(args.processed)
    else:
        df = pd.read_csv(args.processed)

    tasks, label_map = build_tasks(
        df, scenario=args.scenario, benign_per_task=args.benign_per_task, seed=args.seed, order=args.order,
        split=args.split, dedup_content=args.dedup_content,
    )
    if args.scaler == "frozen":
        tasks = fit_scaler_offline_init(tasks)
        scaler_kind = "offline-init-T0T1"
    elif args.scaler == "t0":
        tasks = fit_scaler_t0_only(tasks)
        scaler_kind = "t0-only"
    else:
        tasks = fit_scaler_on_train(tasks)
        scaler_kind = "per-task"
    if args.dedup_content:
        removed = exclude_test_content_matches(tasks)
        print(f"[dedup-content] excluded {removed} post-scaling test matches against all train tasks")
    feature_cols = [c for c in df.columns if c not in ("Label", "day", "flow_order")]
    from src.data.task_schema import sha256_file as _sha

    save_tasks(
        tasks, label_map, args.out, feature_cols=feature_cols,
        protocol_id=(f"cicids-{args.split}-{scaler_kind}-{args.scenario}-{args.order}"
                     + ("-dedup-content" if args.dedup_content else "")),
        split_def={"name": args.split, "test_size": 0.3, "seed": args.seed,
                   "order": args.order, "scenario": args.scenario,
                   "dedup_content": args.dedup_content,
                   "post_scale_test_exclusion": args.dedup_content,
                   "note": "chrono ordering is per-class by flow_order, not a global stream"},
        scaler_kind=scaler_kind,
        sources=[{"file": str(args.processed), "sha256": _sha(args.processed)}],
    )

    for i, t in enumerate(tasks):
        print(f"T{i} {t['day']}: train={len(t['y_train'])} test={len(t['y_test'])} labels={t['labels']}")
    print(f"label_map={label_map}")


if __name__ == "__main__":
    main()
