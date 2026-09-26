from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
import torch
import yaml
from torch.utils.data import DataLoader

from src.attacks.backdoor import inject_backdoor
from src.attacks.flip import label_flip
from src.attacks.novelty import anchor_novelty_poison, novelty_poison_stream
from src.cl.derpp import DERpp
from src.cl.er import ExperienceReplay
from src.cl.ewc import EWC
from src.cl.finetune import FineTune
from src.cl.lwf import LwF
from src.data.sequence import load_tasks, fit_scaler_on_train, build_tasks, load_feature_cols
from src.defenses.consistency import knn_consistency_filter
from src.defenses.purification import small_loss_filter
from src.discovery.pipeline import evaluate_discovery, fit_threshold, recon_scores
from src.metrics import asr_backdoor, average_accuracy, backward_transfer, forgetting, forward_transfer, summarize
from src.models.mlp import Autoencoder, TabularMLP
from src.cl.base import set_seed, to_loader


METHODS = {
    "finetune": FineTune,
    "ewc": EWC,
    "lwf": LwF,
    "er": ExperienceReplay,
    "derpp": DERpp,
    "joint": FineTune,
}


def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_or_build_tasks(cfg: dict):
    data_cfg = cfg.get("data", {})
    scenario = data_cfg.get("scenario", "cii")
    tasks_path = Path(data_cfg.get("tasks", "data/processed/tasks.npz"))
    seed = cfg.get("seed", 42)

    if tasks_path.exists():
        tasks, label_map = load_tasks(tasks_path)
        if scenario == "ci":
            tasks = filter_ci(tasks, label_map)
        return tasks, label_map

    clean_path = Path(data_cfg.get("clean", "data/processed/cicids2017_clean.parquet"))
    if not clean_path.exists():
        raise FileNotFoundError(
            f"Neither {tasks_path} nor {clean_path} found. "
            "Run src.data.clean and src.data.sequence first, or use scripts/smoke_test.py for synthetic data."
        )
    import pandas as pd

    df = pd.read_parquet(clean_path) if clean_path.suffix == ".parquet" else pd.read_csv(clean_path)
    tasks, label_map = build_tasks(df, scenario=scenario, seed=seed)
    tasks = fit_scaler_on_train(tasks)
    return tasks, label_map


def filter_ci(tasks, label_map):
    seen: list[str] = []
    out = []
    for t in tasks:
        for lab in t["labels"]:
            if lab not in seen:
                seen.append(lab)
        allowed = [label_map[x] for x in seen if x in label_map]
        tr = np.isin(t["y_train"], allowed)
        te = np.isin(t["y_test"], allowed)
        nt = dict(t)
        nt["y_train"] = t["y_train"][tr]
        nt["X_train"] = t["X_train"][tr]
        nt["y_test"] = t["y_test"][te]
        nt["X_test"] = t["X_test"][te]
        out.append(nt)
    return out


def train_autoencoder(X: np.ndarray, in_dim: int, device: str, seed: int, epochs: int = 5) -> Autoencoder:
    set_seed(seed)
    ae = Autoencoder(in_dim).to(device)
    opt = torch.optim.Adam(ae.parameters(), lr=1e-3)
    x = torch.from_numpy(X).float().to(device)
    ae.train()
    for _ in range(epochs):
        opt.zero_grad()
        loss = torch.mean((ae(x) - x) ** 2)
        loss.backward()
        opt.step()
    ae.eval()
    return ae


def apply_attack(cfg: dict, task, task_idx: int, feature_names: list[str], ae, device: str, label_map: dict, in_dim: int):
    attack = cfg.get("attack") or {}
    name = attack.get("type")
    X = task["X_train"].copy()
    y = task["y_train"].copy()
    triggered = np.zeros(len(y), dtype=bool)
    asr_meta = {"target_label": 0, "triggered": triggered}

    if name is None:
        return X, y, asr_meta

    budget = float(attack.get("budget", 0.0))
    seed = int(cfg.get("seed", 42)) + task_idx

    if name == "label_flip":
        mode = attack.get("mode", "random")
        src_name = attack.get("source_class")
        src = label_map.get(src_name) if src_name else None
        tgt = int(attack.get("target_class", label_map.get("Benign", 0)))
        y, flipped = label_flip(y, budget=budget, mode=mode, source_class=src, target_class=tgt, seed=seed)
        asr_meta["triggered"] = flipped
        asr_meta["target_label"] = tgt

    elif name == "backdoor":
        atk_name = attack.get("attack_class", "PortScan")
        atk = label_map.get(atk_name)
        if atk is None:
            atk = int(max(y[y > 0])) if (y > 0).any() else 0
        tgt = int(attack.get("target_class", label_map.get("Benign", 0)))
        X, y, triggered = inject_backdoor(
            X, y, budget=budget, feature_names=feature_names, attack_class=atk, target_label=tgt, seed=seed
        )
        asr_meta["triggered"] = triggered
        asr_meta["target_label"] = tgt

    elif name == "novelty":
        if ae is None:
            ae = train_autoencoder(X, in_dim=in_dim, device=device, seed=seed)
        unknown_label = attack.get("unknown_label")
        if unknown_label is None:
            unknown_label = int(np.max(list(label_map.values())) + 1)
        eps = float(attack.get("eps", 0.5))
        steps = int(attack.get("steps", 5))
        thr_q = float(attack.get("threshold_quantile", 0.95))
        thr = asr_meta.get("threshold")
        if thr is None:
            thr = fit_threshold(recon_scores(ae, X, device=device), quantile=thr_q)
        mode = attack.get("mode", "maxrecon")
        if mode == "anchor":
            X, y, poisoned = anchor_novelty_poison(
                ae,
                X,
                y,
                budget=budget,
                unknown_label=int(unknown_label),
                threshold=float(thr),
                noise=float(attack.get("anchor_noise", 0.05)),
                seed=seed,
                device=device,
            )
        else:
            X, y, poisoned = novelty_poison_stream(
                ae,
                X,
                y,
                budget=budget,
                unknown_label=int(unknown_label),
                threshold=float(thr),
                eps=eps,
                steps=steps,
                seed=seed,
                device=device,
            )
        asr_meta["triggered"] = poisoned
        asr_meta["target_label"] = int(unknown_label)
        asr_meta["threshold"] = float(thr)
        asr_meta["ae"] = ae
        asr_meta["X_poisoned"] = X
        asr_meta["y_poisoned"] = y

    else:
        raise ValueError(f"Unknown attack type: {name}")

    return X, y, asr_meta


def evaluate(model_method, tasks, upto: int) -> np.ndarray:
    row = np.zeros(upto + 1)
    for j in range(upto + 1):
        pred = model_method.predict(tasks[j]["X_test"])
        row[j] = float(np.mean(pred == tasks[j]["y_test"]))
    return row


def poison_buffer(method, attack: dict, label_map: dict, seed: int) -> None:
    if not isinstance(method, (ExperienceReplay, DERpp)) or not getattr(method, "buffer_y", None):
        return
    budget = float(attack.get("buffer_budget", attack.get("budget", 0.0)))
    if budget <= 0:
        return
    rng = np.random.RandomState(seed)
    y = np.asarray(method.buffer_y, dtype=np.int64)
    y, flipped = label_flip(
        y,
        budget=budget,
        mode=attack.get("mode", "random"),
        source_class=label_map.get(attack.get("source_class")) if attack.get("source_class") else None,
        target_class=int(attack.get("target_class", label_map.get("Benign", 0))),
        seed=seed,
    )
    method.buffer_y = [int(v) for v in y]
    if isinstance(method, DERpp) and method.buffer_logits:
        for i in np.where(flipped)[0]:
            if i < len(method.buffer_logits):
                li = method.buffer_logits[i].copy()
                tgt = int(attack.get("target_class", label_map.get("Benign", 0)))
                if tgt < len(li):
                    li[:] = 0.0
                    li[tgt] = 1.0
                    method.buffer_logits[i] = li


def run(cfg: dict) -> dict:
    seed = int(cfg.get("seed", 42))
    set_seed(seed)
    device = cfg.get("device", "cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    tasks, label_map = load_or_build_tasks(cfg)
    in_dim = tasks[0]["X_train"].shape[1]
    feature_names = cfg.get("feature_names")
    if not feature_names:
        tasks_path = Path(cfg.get("data", {}).get("tasks", "data/processed/tasks.npz"))
        feature_names = load_feature_cols(tasks_path)
    if not feature_names:
        feature_names = [f"f{i}" for i in range(in_dim)]
    n_classes = int(max(label_map.values())) + 1 + int((cfg.get("attack") or {}).get("type") == "novelty")

    # Phase-2 head-strategy ablation: grow_head=true starts the classifier at
    # T0 width and lets BaseCLMethod._maybe_expand grow it per task (Paper-1
    # §4.1 / plan "growing head" protocol). Default False = pre-sized fixed
    # head (Paper-2 §3.2.1 protocol). Single-node only.
    grow_head = bool(cfg.get("grow_head", False))
    if grow_head:
        n_init = int(tasks[0]["y_train"].max()) + 1
        model = TabularMLP(in_dim, n_init, hidden=cfg.get("hidden", [128, 64]))
    else:
        model = TabularMLP(in_dim, n_classes, hidden=cfg.get("hidden", [128, 64]))
    method_name = cfg.get("cl_method", "er")
    method_cls = METHODS[method_name]
    method_kwargs = {
        k: cfg[k]
        for k in ("buffer_size", "ewc_lambda", "alpha", "temperature", "lr")
        if k in cfg
    }
    method_kwargs.setdefault("lr", float(cfg.get("lr", 1e-3)))
    method = method_cls(model, device=device, **method_kwargs)

    epochs = int(cfg.get("epochs_per_task", 3))
    batch_size = int(cfg.get("batch_size", 256))
    defense = cfg.get("defense") or {}

    R = np.zeros((len(tasks), len(tasks)))
    asr_rows = []
    discovery_rows = []
    t0 = time.time()
    atk = cfg.get("attack") or {}
    atk_type = atk.get("type")
    attack_target = atk.get("target", "stream")

    if method_name == "joint":
        X_all = np.concatenate([t["X_train"] for t in tasks], axis=0)
        y_all = np.concatenate([t["y_train"] for t in tasks], axis=0)
        loader_all = to_loader(X_all, y_all, batch_size=batch_size, shuffle=True)
        bound = int(max(n_classes, int(y_all.max()) + 1))
        method.before_task(0, loader_all, class_bound=bound)
        method.train_task(loader_all, epochs=epochs)
        method.after_task(0, loader_all)
        row = np.array(
            [float(np.mean(method.predict(tasks[j]["X_test"]) == tasks[j]["y_test"])) for j in range(len(tasks))]
        )
        for j in range(len(tasks)):
            R[j, : j + 1] = row[: j + 1]
        summary = summarize(R)
        summary["asr_mean"] = 0.0
        summary["wall_sec"] = time.time() - t0
        summary["cl_method"] = method_name
        summary["attack"] = atk_type
        summary["seed"] = seed
        summary["scenario"] = cfg.get("data", {}).get("scenario", "cii")
        return {"R": R, "summary": summary, "asr_rows": asr_rows}

    for t in range(len(tasks)):
        X_tr = tasks[t]["X_train"]
        y_tr = tasks[t]["y_train"]
        ae = None
        if atk_type == "novelty":
            X_ae = X_tr[y_tr == 0] if (y_tr == 0).any() else X_tr
            if len(X_ae) < 64:
                X_ae = X_tr
            ae = train_autoencoder(X_ae, in_dim=in_dim, device=device, seed=seed + t)

        if attack_target == "stream":
            X_tr, y_tr, asr_meta = apply_attack(cfg, tasks[t], t, feature_names, ae, device, label_map, in_dim)
        else:
            asr_meta = {"target_label": int(atk.get("target_class", label_map.get("Benign", 0))), "triggered": np.zeros(len(y_tr), dtype=bool)}

        if defense.get("type") == "small_loss":
            keep = small_loss_filter(
                method.model, X_tr, y_tr, keep_ratio=float(defense.get("keep_ratio", 0.75)), device=device
            )
            X_tr, y_tr = X_tr[keep], y_tr[keep]
        elif defense.get("type") == "knn_consistency":
            keep = knn_consistency_filter(
                X_tr, y_tr, k=int(defense.get("k", 10)), keep_ratio=float(defense.get("keep_ratio", 0.75))
            )
            X_tr, y_tr = X_tr[keep], y_tr[keep]

        class_bound = int(max(n_classes, y_tr.max() + 1))
        if grow_head:
            # Running seen-width: expand_head only ever grows, old rows copied.
            class_bound = int(max(int(y_tr.max()) + 1, 1))
        loader = to_loader(X_tr, y_tr, batch_size=batch_size, shuffle=True)
        method.before_task(t, loader, class_bound=class_bound)
        method.train_task(loader, epochs=epochs)
        method.after_task(t, loader)
        if attack_target == "buffer" and atk_type == "label_flip":
            poison_buffer(method, atk, label_map, seed=seed + t)

        R[t, : t + 1] = evaluate(method, tasks, t)

        asr = 0.0
        if atk_type == "backdoor":
            X_te = tasks[t]["X_test"].copy()
            y_te = tasks[t]["y_test"]
            cols, vals = [], []
            from src.attacks.backdoor import DEFAULT_TRIGGER

            trg = (cfg.get("attack") or {}).get("trigger") or DEFAULT_TRIGGER
            for fname, fval in zip(trg["features"], trg["values"]):
                if fname in feature_names:
                    cols.append(feature_names.index(fname))
                    vals.append(float(fval))
            atk_name = (cfg.get("attack") or {}).get("attack_class", "PortScan")
            atk = label_map.get(atk_name)
            if atk is None:
                atk = int(max(label_map.values()))
            tgt = int((cfg.get("attack") or {}).get("target_class", label_map.get("Benign", 0)))
            cand = np.where(y_te == atk)[0]
            if len(cand) == 0:
                cand = np.arange(len(y_te))
            if cols and len(cand):
                for i in cand:
                    for c, v in zip(cols, vals):
                        X_te[i, c] = v
                pred = method.predict(X_te)
                asr = float(np.mean(pred[cand] == tgt))
            else:
                asr = 0.0
        elif atk_type == "label_flip":
            y_te = tasks[t]["y_test"]
            pred = method.predict(tasks[t]["X_test"])
            if attack_target == "buffer":
                src_name = atk.get("source_class")
                tgt = int(atk.get("target_class", label_map.get("Benign", 0)))
                if src_name and src_name in label_map:
                    mask = y_te == label_map[src_name]
                    asr = float(np.mean(pred[mask] == tgt)) if mask.any() else 0.0
            else:
                src_name = atk.get("source_class")
                tgt = int(atk.get("target_class", label_map.get("Benign", 0)))
                if src_name and src_name in label_map and atk.get("mode") == "targeted":
                    mask = y_te == label_map[src_name]
                    asr = float(np.mean(pred[mask] == tgt)) if mask.any() else 0.0
        elif atk_type == "novelty":
            y_te = tasks[t]["y_test"]
            pred = method.predict(tasks[t]["X_test"])
            attack_labels = [
                label_map[a]
                for a in (
                    "FTP-Patator",
                    "SSH-Patator",
                    "DoS Slowloris",
                    "DoS Slowhttptest",
                    "DoS Hulk",
                    "DoS GoldenEye",
                    "Heartbleed",
                    "Web Attack Brute Force",
                    "Web Attack XSS",
                    "Web Attack Sql Injection",
                    "Infiltration",
                    "Bot",
                    "PortScan",
                    "DDoS",
                )
                if a in label_map
            ]
            known = np.isin(y_te, attack_labels + [0])
            if known.any():
                asr = float(np.mean(pred[known] == int(asr_meta["target_label"])))
        asr_rows.append({"task": t, "asr": asr})

        if atk_type == "novelty" and asr_meta.get("ae") is not None:
            disc = evaluate_discovery(
                ae=asr_meta["ae"],
                threshold=float(asr_meta.get("threshold", 0.0)),
                X_tr=asr_meta.get("X_poisoned", tasks[t]["X_train"]),
                y_tr=asr_meta.get("y_poisoned", tasks[t]["y_train"]),
                poison_mask=asr_meta.get("triggered", np.zeros(len(tasks[t]["y_train"]), dtype=bool)),
                X_te=tasks[t]["X_test"],
                y_te=tasks[t]["y_test"],
                device=device,
                min_cluster_size=int((cfg.get("attack") or {}).get("min_cluster_size", 15)),
            )
            disc["task"] = t
            discovery_rows.append(disc)

    summary = summarize(R)
    summary["asr_mean"] = float(np.mean([r["asr"] for r in asr_rows])) if asr_rows else None
    summary["wall_sec"] = time.time() - t0
    summary["cl_method"] = method_name
    summary["attack"] = (cfg.get("attack") or {}).get("type")
    summary["seed"] = seed
    summary["scenario"] = cfg.get("data", {}).get("scenario", "cii")
    if discovery_rows:
        summary["discovery_rows"] = discovery_rows
        attack_rows = [r for r in discovery_rows if int(r.get("n_attack_test", 0)) > 0]
        mean_specs = (
            ("discovery_miss_rate", discovery_rows),
            ("fictitious_absorption", discovery_rows),
            ("poison_novel_rate", discovery_rows),
            ("noise_rate_attack", attack_rows),
            ("absorbed_attack_rate", attack_rows),
            ("clustered_attack_rate", attack_rows),
            ("test_novel_rate", discovery_rows),
            ("n_clusters", discovery_rows),
            ("n_fictitious", discovery_rows),
        )
        for key, rows in mean_specs:
            vals = [float(r[key]) for r in rows if key in r]
            if vals:
                summary[f"{key}_mean"] = float(np.mean(vals))
    return {"R": R, "summary": summary, "asr_rows": asr_rows, "discovery_rows": discovery_rows}


def save_results(result: dict, cfg: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    name = cfg.get("name", "experiment")
    seed = cfg.get("seed", 42)
    R = result["R"]
    with open(out_dir / f"{name}_R_seed{seed}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for row in R:
            w.writerow([f"{v:.6f}" for v in row])
    (out_dir / f"{name}_summary_seed{seed}.json").write_text(json.dumps(result["summary"], indent=2))
    print(json.dumps(result["summary"], indent=2))
    print("R matrix:\n", np.array2string(R, precision=3))


def append_table(result: dict, cfg: dict, out_dir: Path) -> None:
    table = out_dir / "baseline_table.csv"
    header = "name,method,attack,scenario,acc,bwt,fwt,forgetting,asr_mean,seed\n"
    if not table.exists():
        table.write_text(header, encoding="utf-8")
    s = result["summary"]
    atk = s.get("attack")
    if cfg.get("defense"):
        atk = f"{atk}+defense" if atk else "defense"
    row = (
        f"{cfg.get('name')},{s.get('cl_method')},{atk or ''},"
        f"{cfg.get('data', {}).get('scenario')},"
        f"{s['acc']:.6f},{s['bwt']:.6f},{s['fwt']:.6f},{s['forgetting']:.6f},"
        f"{s.get('asr_mean')},{seed if (seed := cfg.get('seed', 42)) else ''}\n"
    )
    with open(table, "a", encoding="utf-8") as f:
        f.write(row)


def rebuild_table(out_dir: Path) -> None:
    rows = []
    for p in sorted(out_dir.glob("*_summary_seed*.json")):
        s = json.loads(p.read_text())
        name = p.name.replace("_summary_seed", "|").replace(".json", "")
        if "|" in name:
            base, seed = name.rsplit("|", 1)
        else:
            base, seed = name, str(s.get("seed", ""))
        atk = s.get("attack")
        # Defense label: resolve via config (names like f4_fed_* carry defense
        # in the config, not in the filename). Mirrors Gate-D config lookup.
        defended = "defense" in base
        if not defended:
            try:
                import yaml as _yaml

                _root = Path(__file__).resolve().parents[1]
                _cfg = _yaml.safe_load((_root / f"configs/{base}.yaml").read_text(encoding="utf-8")) or {}
                defended = bool(_cfg.get("defense"))
            except Exception:
                defended = False
        if defended:
            atk = f"{atk}+defense" if atk else "defense"
        rows.append(
            {
                "name": base,
                "method": s.get("cl_method"),
                "attack": atk or "",
                "scenario": s.get("scenario") or "",
                "acc": f"{s['acc']:.6f}",
                "bwt": f"{s['bwt']:.6f}",
                "fwt": f"{s['fwt']:.6f}",
                "forgetting": f"{s['forgetting']:.6f}",
                "asr_mean": s.get("asr_mean"),
                "seed": s.get("seed", seed),
            }
        )
    fields = ["name", "method", "attack", "scenario", "acc", "bwt", "fwt", "forgetting", "asr_mean", "seed"]
    with open(out_dir / "baseline_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Rebuilt baseline_table.csv with {len(rows)} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path)
    ap.add_argument("--rebuild-table", action="store_true")
    args = ap.parse_args()
    out_dir = Path("results")
    if args.rebuild_table:
        rebuild_table(out_dir)
        return
    if not args.config:
        ap.error("--config required unless --rebuild-table")
    cfg = load_config(args.config)
    result = run(cfg)
    save_results(result, cfg, out_dir)
    append_table(result, cfg, out_dir)


if __name__ == "__main__":
    main()
