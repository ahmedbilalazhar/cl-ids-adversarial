from __future__ import annotations

import copy
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from src.attacks.backdoor import DEFAULT_TRIGGER, inject_backdoor
from src.attacks.flip import label_flip
from src.cl.base import set_seed, to_loader
from src.data.sequence import load_feature_cols
from src.defenses.consistency import knn_consistency_filter
from src.defenses.purification import small_loss_filter
from src.federated.partition import dirichlet_partition
from src.metrics import summarize
from src.models.mlp import TabularMLP
from src.run_experiment import METHODS, load_or_build_tasks


def _predict(model: torch.nn.Module, X: np.ndarray, device: str) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        logits = model(torch.from_numpy(X).to(device))
        return logits.argmax(dim=1).cpu().numpy()


def _poison_shard(
    X: np.ndarray,
    y: np.ndarray,
    attack: dict,
    label_map: dict,
    feature_names: list[str],
    seed: int,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Apply the UNCHANGED single-node attack to one client's shard.

    Mirrors src/run_experiment.py apply_attack (label_flip/backdoor branches).
    Returns (X, y, meta) with meta['poisoned'] mask and fraction.
    """
    name = (attack or {}).get("type")
    meta = {"poisoned": np.zeros(len(y), dtype=bool), "fraction": 0.0}
    if name is None:
        return X, y, meta
    budget = float(attack.get("budget", 0.0))
    if name == "label_flip":
        mode = attack.get("mode", "random")
        src_name = attack.get("source_class")
        src = label_map.get(src_name) if src_name else None
        tgt = int(attack.get("target_class", label_map.get("Benign", 0)))
        y2, flipped = label_flip(y, budget=budget, mode=mode, source_class=src, target_class=tgt, seed=seed)
        meta = {"poisoned": flipped, "fraction": float(flipped.mean()) if len(y) else 0.0}
        return X, y2, meta
    if name == "backdoor":
        atk_name = attack.get("attack_class", "PortScan")
        atk = label_map.get(atk_name)
        if atk is None:
            atk = int(max(y[y > 0])) if (y > 0).any() else 0
        tgt = int(attack.get("target_class", label_map.get("Benign", 0)))
        X2, y2, trig = inject_backdoor(
            X, y, budget=budget, feature_names=feature_names, attack_class=atk, target_label=tgt, seed=seed
        )
        meta = {"poisoned": trig, "fraction": float(trig.mean()) if len(y) else 0.0}
        return X2, y2, meta
    raise ValueError(f"Federated wrapper supports label_flip/backdoor, got: {name}")


def _fedavg(state_dicts: list[dict], weights: list[float]) -> dict:
    total = float(sum(weights))
    out = {}
    for k in state_dicts[0]:
        out[k] = sum(sd[k] * (w / total) for sd, w in zip(state_dicts, weights))
    return out


def run_federated(cfg: dict) -> dict:
    """One federated continual run. Config extends single-node schema with:

    fed: {n_clients (default 5), malicious_id (default last), alpha (0.5),
          local_epochs (default = epochs_per_task)}
    attack: same schema as single-node; applied ONLY to the malicious
      client's shard at `budget` fraction of that shard.
    """
    seed = int(cfg.get("seed", 42))
    set_seed(seed)
    device = cfg.get("device", "cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"
    fed = cfg.get("fed") or {}
    n_clients = int(fed.get("n_clients", 5))
    mal_id = int(fed.get("malicious_id", n_clients - 1))
    alpha = float(fed.get("alpha", 0.5))
    local_epochs = int(fed.get("local_epochs", cfg.get("epochs_per_task", 3)))
    batch_size = int(cfg.get("batch_size", 256))
    attack = cfg.get("attack") or {}
    budget = float(attack.get("budget", 0.0))
    defense = cfg.get("defense") or {}  # same schema as single-node run_experiment

    tasks, label_map = load_or_build_tasks(cfg)
    in_dim = tasks[0]["X_train"].shape[1]
    feature_names = cfg.get("feature_names")
    if not feature_names:
        tasks_path = Path(cfg.get("data", {}).get("tasks", "data/processed/tasks.npz"))
        feature_names = load_feature_cols(tasks_path)
    if not feature_names:
        feature_names = [f"f{i}" for i in range(in_dim)]
    n_classes = int(max(label_map.values())) + 1

    method_name = cfg.get("cl_method", "er")
    method_cls = METHODS[method_name]
    method_kwargs = {k: cfg[k] for k in ("buffer_size", "ewc_lambda", "alpha", "beta", "temperature", "lr") if k in cfg}
    method_kwargs.setdefault("lr", float(cfg.get("lr", 1e-3)))

    server = TabularMLP(in_dim, n_classes, hidden=cfg.get("hidden", [128, 64]))
    server.to(device)
    # Persistent per-client CL state (buffers, Fisher, LwF snapshots) across tasks.
    clients = []
    for _ in range(n_clients):
        m = method_cls(copy.deepcopy(server), device=device, **dict(method_kwargs))
        clients.append(m)

    t0 = time.time()
    R = np.zeros((len(tasks), len(tasks)))
    asr_rows = []
    poison_frac_rows = []

    for t in range(len(tasks)):
        X_pool = tasks[t]["X_train"]
        y_pool = tasks[t]["y_train"]
        shards = dirichlet_partition(y_pool, n_clients=n_clients, alpha=alpha, seed=seed + 1000 + t)
        assert sum(len(s) for s in shards) == len(y_pool)
        # Broadcast current global weights to all clients.
        global_sd = server.state_dict()
        for m in clients:
            m.model.load_state_dict(copy.deepcopy(global_sd), strict=True)

        sds, ws = [], []
        for k in range(n_clients):
            idx = shards[k]
            Xk, yk = X_pool[idx].copy(), y_pool[idx].copy()
            frac = 0.0
            if len(yk) == 0:
                # Dirichlet skew can leave a client with zero samples on small
                # tasks. It sits out the round: contributes its (broadcast)
                # weights at aggregation weight 0. No data is moved between
                # clients, so the non-IID construction is preserved.
                m = clients[k]
                m.model.load_state_dict(copy.deepcopy(global_sd), strict=True)
                sds.append({kk: vv.detach().cpu().clone() for kk, vv in m.model.state_dict().items()})
                ws.append(0.0)
                poison_frac_rows.append({"task": t, "client": k, "poison_fraction": 0.0, "n": 0})
                continue
            if k == mal_id and budget > 0 and len(yk):
                Xk, yk, meta = _poison_shard(Xk, yk, attack, label_map, feature_names, seed=seed + t)
                frac = meta["fraction"]
            poison_frac_rows.append({"task": t, "client": k, "poison_fraction": frac, "n": len(yk)})
            m = clients[k]
            # Per-client pre-training defense filter (mirrors single-node
            # run_experiment: applied to the shard AFTER poisoning, using the
            # client's carried-over model, before before_task/train_task).
            if defense.get("type") == "small_loss" and len(yk):
                keep = small_loss_filter(
                    m.model, Xk, yk, keep_ratio=float(defense.get("keep_ratio", 0.75)), device=device
                )
                Xk, yk = Xk[keep], yk[keep]
            elif defense.get("type") == "knn_consistency" and len(yk):
                keep = knn_consistency_filter(
                    Xk, yk, k=int(defense.get("k", 10)), keep_ratio=float(defense.get("keep_ratio", 0.75))
                )
                Xk, yk = Xk[keep], yk[keep]
            if len(yk) == 0:
                m.model.load_state_dict(copy.deepcopy(global_sd), strict=True)
                sds.append({kk: vv.detach().cpu().clone() for kk, vv in m.model.state_dict().items()})
                ws.append(0.0)
                continue
            loader = to_loader(Xk, yk, batch_size=batch_size, shuffle=True)
            class_bound = int(max(n_classes, int(yk.max()) + 1)) if len(yk) else n_classes
            m.before_task(t, loader, class_bound=class_bound)
            m.train_task(loader, epochs=local_epochs)
            m.after_task(t, loader)
            sds.append({kk: vv.detach().cpu().clone() for kk, vv in m.model.state_dict().items()})
            ws.append(float(len(yk)))

        agg = _fedavg([{k: v.to(device) for k, v in sd.items()} for sd in sds], ws)
        server.load_state_dict(agg, strict=True)
        # EWC anchor ~= global solution after broadcast (Fisher stays local).
        for m in clients:
            if hasattr(m, "anchor") and m.anchor:
                m.anchor = {n: p.detach().clone() for n, p in m.model.named_parameters() if p.requires_grad}
                m.model.load_state_dict(copy.deepcopy(agg), strict=True)

        for j in range(t + 1):
            pred = _predict(server, tasks[j]["X_test"], device)
            R[t, j] = float(np.mean(pred == tasks[j]["y_test"]))

        # ASR on the GLOBAL model (same definitions as single-node).
        asr = 0.0
        atk_type = attack.get("type")
        if atk_type == "backdoor":
            X_te = tasks[t]["X_test"].copy()
            y_te = tasks[t]["y_test"]
            trg = attack.get("trigger") or DEFAULT_TRIGGER
            cols = [feature_names.index(f) for f, _ in zip(trg["features"], trg["values"]) if f in feature_names]
            vals = [float(v) for f, v in zip(trg["features"], trg["values"]) if f in feature_names]
            atk = label_map.get(attack.get("attack_class", "PortScan"), int(max(label_map.values())))
            tgt = int(attack.get("target_class", label_map.get("Benign", 0)))
            cand = np.where(y_te == atk)[0]
            if len(cand) == 0:
                cand = np.arange(len(y_te))
            if cols and len(cand):
                for i in cand:
                    for c, v in zip(cols, vals):
                        X_te[i, c] = v
                asr = float(np.mean(_predict(server, X_te, device)[cand] == tgt))
        elif atk_type == "label_flip" and attack.get("mode") == "targeted":
            src_name = attack.get("source_class")
            tgt = int(attack.get("target_class", label_map.get("Benign", 0)))
            if src_name and src_name in label_map:
                mask = tasks[t]["y_test"] == label_map[src_name]
                if mask.any():
                    asr = float(np.mean(_predict(server, tasks[t]["X_test"], device)[mask] == tgt))
        asr_rows.append({"task": t, "asr": asr})

    summary = summarize(R)
    summary["asr_mean"] = float(np.mean([r["asr"] for r in asr_rows])) if asr_rows else None
    summary["wall_sec"] = time.time() - t0
    summary["cl_method"] = method_name
    summary["attack"] = attack.get("type")
    summary["seed"] = seed
    summary["scenario"] = cfg.get("data", {}).get("scenario", "cii")
    summary["fed"] = {"n_clients": n_clients, "malicious_id": mal_id, "alpha": alpha, "local_epochs": local_epochs}
    mal_frac = [r["poison_fraction"] for r in poison_frac_rows if r["client"] == mal_id]
    summary["malicious_shard_poison_mean"] = float(np.mean(mal_frac)) if mal_frac else 0.0
    return {"R": R, "summary": summary, "asr_rows": asr_rows, "poison_frac_rows": poison_frac_rows}
