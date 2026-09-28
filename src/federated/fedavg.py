from __future__ import annotations

import copy
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from src.attacks.backdoor import backdoor_outcome, inject_backdoor, scaled_trigger
from src.attacks.byzantine import (
    from_deltas,
    little_is_enough,
    model_replacement_delta,
    sign_flip_delta,
    to_deltas,
)
from src.attacks.flip import label_flip, majority_attack_class, resolve_attack_target, resolve_class_id
from src.cl.base import set_seed, to_loader
from src.data.sequence import load_feature_cols
from src.defenses.consistency import knn_consistency_filter
from src.defenses.purification import small_loss_filter
from src.federated.partition import dirichlet_partition
from src.federated.robust import (
    DynamicTrust,
    fedavg_deltas,
    krum_deltas,
    median_deltas,
    multi_krum_deltas,
    trimmed_mean_deltas,
)
from src.metrics import summarize
from src.methods import METHODS
from src.models import build_model
from src.paths import resolve_repo_path
from src.tasks import load_or_build_tasks


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
    model=None,
    device: str = "cpu",
    trigger=None,
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
        src = resolve_class_id(src_name, label_map, role="source") if src_name is not None else None
        tgt = resolve_attack_target(attack, label_map)
        if src is None and mode in {"persistent", "adaptive", "knn_adaptive"}:
            source = majority_attack_class(y, tgt)
        elif mode == "random":
            source = None
        else:
            source = src
        eligible = int((y == source).sum()) if source is not None else (
            len(y) if len(np.unique(y)) > 1 else 0
        )
        if mode == "adaptive":
            # White-box vs the malicious client's carried-over model.
            from src.attacks.flip import adaptive_loss_preserving_flip

            if model is None:
                raise ValueError("adaptive flip needs the carried-over model")
            y2, flipped = adaptive_loss_preserving_flip(
                model, X, y, budget=budget, source_class=src,
                target_class=tgt, seed=seed, device=device,
            )
        elif mode == "knn_adaptive":
            from src.attacks.flip import knn_preserving_flip

            y2, flipped = knn_preserving_flip(
                X, y, budget=budget, source_class=src, target_class=tgt,
                k=int(attack.get("knn_k", 10)), seed=seed,
            )
        else:
            y2, flipped = label_flip(y, budget=budget, mode=mode, source_class=src, target_class=tgt, seed=seed)
        meta = {"poisoned": flipped, "fraction": float(flipped.mean()) if len(y) else 0.0,
                "eligible": eligible, "changed": int(flipped.sum()),
                "labels_changed": int(np.sum(y2 != y)), "source_class": source}
        return X, y2, meta
    if name == "backdoor":
        atk_name = attack.get("attack_class", "PortScan")
        atk = label_map.get(atk_name)
        if atk is None:
            raise ValueError(f"backdoor attack class absent from label map: {atk_name}")
        tgt = resolve_attack_target(attack, label_map)
        X2, y2, trig = inject_backdoor(
            X, y, budget=budget, feature_names=feature_names, attack_class=atk,
            target_label=tgt, trigger=trigger, seed=seed
        )
        meta = {"poisoned": trig, "fraction": float(trig.mean()) if len(y) else 0.0,
                "eligible": int(np.sum((y == atk) & (y != tgt))), "changed": int(trig.sum()),
                "labels_changed": int(np.sum(y2 != y))}
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

    fed: {n_clients (default 5), malicious_id (default last),
          malicious_ids (default [malicious_id]; fraction sweep),
          alpha (0.5), local_epochs (default = epochs_per_task),
          aggregator (fedavg|trimmed_mean|median|krum|multi_krum|dynamic_trust),
          trim_ratio (0.2), n_mal (assumed #malicious for krum)}
    attack: same schema as single-node; applied ONLY to malicious clients'
      shards at `budget` fraction of each shard. PLUS optional
      attack.update_attack {method: sign_flip|lie|model_replacement, ...}
      applied to malicious clients' SUBMITTED updates (combinable).
    """
    seed = int(cfg.get("seed", 42))
    set_seed(seed)
    device = cfg.get("device", "cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"
    fed = cfg.get("fed") or {}
    n_clients = int(fed.get("n_clients", 5))
    mal_id = int(fed.get("malicious_id", n_clients - 1))
    mal_ids = list(fed.get("malicious_ids", [mal_id]))
    aggregator = str(fed.get("aggregator", "fedavg"))
    trim_ratio = float(fed.get("trim_ratio", 0.2))
    n_mal = int(fed.get("n_mal", len(mal_ids)))
    alpha = float(fed.get("alpha", 0.5))
    local_epochs = int(fed.get("local_epochs", cfg.get("epochs_per_task", 3)))
    batch_size = int(cfg.get("batch_size", 256))
    attack = cfg.get("attack") or {}
    budget = float(attack.get("budget", 0.0))
    up_attack = attack.get("update_attack") or {}
    up_method = up_attack.get("method")
    defense = cfg.get("defense") or {}  # same schema as single-node run_experiment
    trust = DynamicTrust(n_clients=n_clients) if aggregator == "dynamic_trust" else None

    tasks, label_map = load_or_build_tasks(cfg)
    in_dim = tasks[0]["X_train"].shape[1]
    feature_names = cfg.get("feature_names")
    if not feature_names:
        tasks_path = resolve_repo_path(Path(cfg.get("data", {}).get("tasks", "data/processed/tasks.npz")))
        feature_names = load_feature_cols(tasks_path)
    if not feature_names:
        feature_names = [f"f{i}" for i in range(in_dim)]
    trigger = None
    if attack.get("type") == "backdoor":
        tasks_path = resolve_repo_path(Path(cfg.get("data", {}).get("tasks", "data/processed/tasks.npz")))
        trigger = scaled_trigger(attack.get("trigger"), feature_names, tasks_path)
    n_classes = int(max(label_map.values())) + 1

    method_name = cfg.get("cl_method", "er")
    method_cls = METHODS[method_name]
    method_kwargs = {k: cfg[k] for k in ("buffer_size", "ewc_lambda", "alpha", "beta", "temperature", "lr") if k in cfg}
    method_kwargs.setdefault("lr", float(cfg.get("lr", 1e-3)))

    from src.models import build_model

    server = build_model(cfg, in_dim, n_classes)
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
            eligible = changed = 0
            if len(yk) == 0:
                # Dirichlet skew can leave a client with zero samples on small
                # tasks. It sits out the round: contributes its (broadcast)
                # weights at aggregation weight 0. No data is moved between
                # clients, so the non-IID construction is preserved.
                m = clients[k]
                m.model.load_state_dict(copy.deepcopy(global_sd), strict=True)
                sds.append({kk: vv.detach().cpu().clone() for kk, vv in m.model.state_dict().items()})
                ws.append(0.0)
                poison_frac_rows.append({"task": t, "client": k, "poison_fraction": 0.0,
                                         "n": 0, "eligible": 0, "changed": 0,
                                         "labels_changed": 0, "configured_shard_budget": budget,
                                         "retained_after_defense": 0})
                continue
            if k in mal_ids and budget > 0 and len(yk):
                Xk, yk, meta = _poison_shard(
                    Xk, yk, attack, label_map, feature_names, seed=seed + t,
                    model=clients[k].model, device=device, trigger=trigger,
                )
                frac = meta["fraction"]
                eligible = meta.get("eligible", 0)
                changed = meta.get("changed", int(meta["poisoned"].sum()))
            poison_frac_rows.append({"task": t, "client": k, "poison_fraction": frac,
                                     "n": len(yk), "eligible": eligible, "changed": changed,
                                     "labels_changed": meta.get("labels_changed", 0) if k in mal_ids and budget > 0 else 0,
                                     "configured_shard_budget": budget if k in mal_ids else 0.0,
                                     "source_class": meta.get("source_class") if k in mal_ids and budget > 0 else None,
                                     "retained_after_defense": changed})
            m = clients[k]
            # Per-client pre-training defense filter (mirrors single-node
            # run_experiment: applied to the shard AFTER poisoning, using the
            # client's carried-over model, before before_task/train_task).
            if defense.get("type") == "small_loss" and len(yk):
                keep = small_loss_filter(
                    m.model, Xk, yk, keep_ratio=float(defense.get("keep_ratio", 0.75)), device=device
                )
                Xk, yk = Xk[keep], yk[keep]
                if k in mal_ids and budget > 0:
                    poison_frac_rows[-1]["retained_after_defense"] = int((meta["poisoned"] & keep).sum())
            elif defense.get("type") == "knn_consistency" and len(yk):
                keep = knn_consistency_filter(
                    Xk, yk, k=int(defense.get("k", 10)), keep_ratio=float(defense.get("keep_ratio", 0.75))
                )
                Xk, yk = Xk[keep], yk[keep]
                if k in mal_ids and budget > 0:
                    poison_frac_rows[-1]["retained_after_defense"] = int((meta["poisoned"] & keep).sum())
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

        if aggregator == "fedavg" and not up_method:
            # Locked path: bit-identical weighted model averaging (all F2/F4
            # results). Robust rules and update-attacks use the delta path.
            agg = _fedavg([{k: v.to(device) for k, v in sd.items()} for sd in sds], ws)
        else:
            # Update-level Byzantine attack: substitute malicious submissions.
            if up_method in ("sign_flip", "model_replacement"):
                for k in mal_ids:
                    d = to_deltas(
                        {kk: vv.to("cpu") for kk, vv in sds[k].items()},
                        {kk: vv.to("cpu") for kk, vv in global_sd.items()},
                    )
                    if up_method == "sign_flip":
                        d = sign_flip_delta(d, scale=float(up_attack.get("scale", 1.0)))
                    else:
                        d = model_replacement_delta(d, boost=float(up_attack.get("boost", 5.0)))
                    sds[k] = from_deltas(d, {kk: vv.to("cpu") for kk, vv in global_sd.items()})
            elif up_method == "lie":
                ben = [
                    to_deltas(
                        {kk: vv.to("cpu") for kk, vv in sds[k].items()},
                        {kk: vv.to("cpu") for kk, vv in global_sd.items()},
                    )
                    for k in range(n_clients)
                    if k not in mal_ids
                ]
                crafted = little_is_enough(
                    ben, z=float(up_attack.get("z", 1.5)),
                    direction=str(up_attack.get("direction", "neg")),
                )
                for k in mal_ids:
                    sds[k] = from_deltas(
                        crafted, {kk: vv.to("cpu") for kk, vv in global_sd.items()}
                    )
            elif up_method is not None:
                raise ValueError(f"Unknown update_attack method: {up_method}")
            deltas = [
                to_deltas(
                    {kk: vv.to("cpu") for kk, vv in sd.items()},
                    {kk: vv.to("cpu") for kk, vv in global_sd.items()},
                )
                for sd in sds
            ]
            if aggregator in ("fedavg",):
                agg_d = fedavg_deltas(deltas, ws)
            elif aggregator == "trimmed_mean":
                agg_d = trimmed_mean_deltas(deltas, trim_ratio=trim_ratio)
            elif aggregator == "median":
                agg_d = median_deltas(deltas)
            elif aggregator == "krum":
                agg_d = krum_deltas(deltas, n_mal=n_mal)
            elif aggregator == "multi_krum":
                agg_d = multi_krum_deltas(deltas, n_mal=n_mal)
            elif aggregator == "dynamic_trust":
                agg_d = trust(deltas, ws)
            else:
                raise ValueError(f"Unknown aggregator: {aggregator}")
            agg = {
                k: (global_sd[k].float().to(device) + agg_d[k].to(device))
                for k in agg_d
            }
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
        asr = None
        atk_type = attack.get("type")
        if atk_type == "backdoor":
            outcome = backdoor_outcome(
                lambda x: _predict(server, x, device), tasks[t]["X_test"],
                tasks[t]["y_test"], feature_names,
                label_map.get(attack.get("attack_class", "PortScan")),
                resolve_attack_target(attack, label_map), trigger,
            )
            asr_rows.append({"task": t, **outcome})
        elif atk_type == "label_flip" and attack.get("mode") in ("targeted", "persistent", "adaptive", "knn_adaptive"):
            src_name = attack.get("source_class")
            tgt = resolve_attack_target(attack, label_map)
            if attack.get("mode") == "persistent":
                from src.attacks.flip import majority_attack_class

                src = majority_attack_class(tasks[t]["y_test"], tgt)
                mask = tasks[t]["y_test"] == src if src is not None else np.zeros(len(tasks[t]["y_test"]), dtype=bool)
                if mask.any():
                    asr = float(np.mean(_predict(server, tasks[t]["X_test"], device)[mask] == tgt))
            elif src_name and src_name in label_map:
                mask = tasks[t]["y_test"] == label_map[src_name]
                if mask.any():
                    asr = float(np.mean(_predict(server, tasks[t]["X_test"], device)[mask] == tgt))
        if atk_type != "backdoor":
            asr_rows.append({"task": t, "asr": asr})

    summary = summarize(R)
    if attack.get("type") == "backdoor":
        eligible = sum(r["eligible"] for r in asr_rows)
        summary["asr_mean"] = sum(r["successes"] for r in asr_rows) / eligible if eligible else None
        summary["asr_eligible"] = eligible
        summary["asr_successes"] = sum(r["successes"] for r in asr_rows)
        summary["asr_rows"] = asr_rows
        summary["poison_rows"] = poison_frac_rows
    else:
        asr_values = [r["asr"] for r in asr_rows if r["asr"] is not None]
        summary["asr_mean"] = float(np.mean(asr_values)) if asr_values else None
    summary["wall_sec"] = time.time() - t0
    summary["cl_method"] = method_name
    atk_label = attack.get("type")
    if up_method:
        atk_label = f"{atk_label}+byz_{up_method}" if atk_label else f"byz_{up_method}"
    summary["attack"] = atk_label
    summary["seed"] = seed
    summary["scenario"] = cfg.get("data", {}).get("scenario", "cii")
    summary["runtime_device"] = device
    summary["fed"] = {
        "n_clients": n_clients, "malicious_id": mal_id, "malicious_ids": mal_ids,
        "alpha": alpha, "local_epochs": local_epochs, "aggregator": aggregator,
        "update_attack": up_method,
    }
    mal_frac = [r["poison_fraction"] for r in poison_frac_rows if r["client"] in mal_ids]
    summary["malicious_shard_poison_mean"] = float(np.mean(mal_frac)) if mal_frac else 0.0
    summary["poison_rows"] = poison_frac_rows
    summary["poison_changed_total"] = sum(r["changed"] for r in poison_frac_rows)
    summary["poison_eligible_total"] = sum(r["eligible"] for r in poison_frac_rows)
    n_train_total = sum(r["n"] for r in poison_frac_rows)
    summary["poison_realized_global_dose"] = summary["poison_changed_total"] / n_train_total if n_train_total else None
    return {"R": R, "summary": summary, "asr_rows": asr_rows, "poison_frac_rows": poison_frac_rows}
