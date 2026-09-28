"""Single-node experiment runner (training loop + attack application)."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch

from src.attacks.backdoor import backdoor_outcome, inject_backdoor, scaled_trigger
from src.attacks.flip import (
    label_flip,
    majority_attack_class,
    resolve_attack_target,
    resolve_class_id,
)
from src.attacks.novelty import anchor_novelty_poison, novelty_poison_stream
from src.cl.base import limit_threads, set_seed, to_loader
from src.cl.derpp import DERpp
from src.cl.er import ExperienceReplay
from src.data.sequence import load_feature_cols
from src.defenses.consistency import knn_consistency_filter
from src.defenses.purification import small_loss_filter
from src.discovery.pipeline import (
    evaluate_discovery,
    fit_discovery,
    fit_threshold,
    provisional_labels,
    recon_scores,
)
from src.methods import METHODS
from src.metrics import summarize
from src.models.mlp import Autoencoder
from src.paths import resolve_repo_path
from src.tasks import load_or_build_tasks

limit_threads()


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


def apply_attack(cfg: dict, task, task_idx: int, feature_names: list[str], ae, device: str, label_map: dict, in_dim: int, model=None, trigger=None, discovery_threshold=None):
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
        src = resolve_class_id(src_name, label_map, role="source") if src_name is not None else None
        tgt = resolve_attack_target(attack, label_map)
        if mode == "adaptive":
            # Phase-3 step 15: white-box vs the carried-over (defended) model.
            from src.attacks.flip import adaptive_loss_preserving_flip

            if model is None:
                raise ValueError("adaptive flip needs the carried-over model")
            y, flipped = adaptive_loss_preserving_flip(
                model, X, y, budget=budget, source_class=src,
                target_class=tgt, seed=seed, device=device,
            )
        elif mode == "knn_adaptive":
            # Phase-3 step 15: tailored vs kNN-consistency filtering.
            from src.attacks.flip import knn_preserving_flip

            y, flipped = knn_preserving_flip(
                X, y, budget=budget, source_class=src, target_class=tgt,
                k=int(attack.get("knn_k", 10)), seed=seed,
            )
        else:
            y, flipped = label_flip(y, budget=budget, mode=mode, source_class=src, target_class=tgt, seed=seed)
        asr_meta["triggered"] = flipped
        asr_meta["target_label"] = tgt

    elif name == "backdoor":
        atk_name = attack.get("attack_class", "PortScan")
        atk = label_map.get(atk_name)
        if atk is None:
            raise ValueError(f"backdoor attack class absent from label map: {atk_name}")
        tgt = resolve_attack_target(attack, label_map)
        X, y, triggered = inject_backdoor(
            X, y, budget=budget, feature_names=feature_names, attack_class=atk,
            target_label=tgt, trigger=trigger, seed=seed
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
        thr = discovery_threshold
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


def attack_dose_row(
    attack: dict, original_y: np.ndarray, changed_mask: np.ndarray,
    label_map: dict, *, task: int, retained_mask: np.ndarray | None = None,
    target: str = "stream", labels_changed: int | None = None,
) -> dict:
    """Report actual candidates, changes, and post-filter retention."""
    kind = attack.get("type")
    budget = float(attack.get("buffer_budget", attack.get("budget", 0.0))) if target == "buffer" else float(attack.get("budget", 0.0))
    source_class = None
    if kind == "label_flip":
        mode = attack.get("mode", "random")
        target_label = resolve_attack_target(attack, label_map)
        named = attack.get("source_class")
        if named is not None and mode != "random":
            source_class = resolve_class_id(named, label_map, role="source")
        elif mode in {"persistent", "adaptive", "knn_adaptive"}:
            source_class = majority_attack_class(original_y, target_label)
        eligible = int((original_y == source_class).sum()) if source_class is not None else (
            len(original_y) if len(np.unique(original_y)) > 1 else 0
        )
    elif kind == "backdoor":
        source_class = int(label_map[attack.get("attack_class", "PortScan")])
        target_label = resolve_attack_target(attack, label_map)
        eligible = int(((original_y == source_class) & (original_y != target_label)).sum())
    elif kind == "novelty":
        mode = attack.get("mode", "maxrecon")
        eligible = int((original_y == 0).sum()) if mode == "anchor" and (original_y != 0).any() else len(original_y)
    else:
        eligible = 0
    changed_mask = np.asarray(changed_mask, dtype=bool)
    if len(changed_mask) != len(original_y):
        raise ValueError("attack dose mask length mismatch")
    if retained_mask is None:
        retained_mask = np.ones(len(original_y), dtype=bool)
    changed = int(changed_mask.sum())
    retained = int((changed_mask & retained_mask).sum())
    n = len(original_y)
    return {
        "task": task, "target": target, "attack": kind,
        "mode": attack.get("mode"), "source_class": source_class,
        "attacker_knowledge": "carried_model" if attack.get("mode") == "adaptive" else "configured_input",
        "configured_budget": budget, "n": n, "eligible": eligible,
        "changed": changed, "retained_after_defense": retained,
        "attacker_labels_changed": labels_changed if labels_changed is not None else changed,
        "realized_shard_dose": changed / n if n else None,
        "realized_global_dose": changed / n if n else None,
    }


def poison_buffer(method, attack: dict, label_map: dict, seed: int) -> None:
    if not isinstance(method, (ExperienceReplay, DERpp)) or not getattr(method, "buffer_y", None):
        return
    budget = float(attack.get("buffer_budget", attack.get("budget", 0.0)))
    if budget <= 0:
        return
    y = np.asarray(method.buffer_y, dtype=np.int64)
    src_name = attack.get("source_class")
    src = resolve_class_id(src_name, label_map, role="source") if src_name is not None else None
    y, flipped = label_flip(
        y,
        budget=budget,
        mode=attack.get("mode", "random"),
        source_class=src,
        target_class=resolve_attack_target(attack, label_map),
        seed=seed,
    )
    method.buffer_y = [int(v) for v in y]
    if isinstance(method, DERpp) and method.buffer_logits:
        for i in np.where(flipped)[0]:
            if i < len(method.buffer_logits):
                li = method.buffer_logits[i].copy()
                tgt = resolve_attack_target(attack, label_map)
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
        tasks_path = resolve_repo_path(Path(cfg.get("data", {}).get("tasks", "data/processed/tasks.npz")))
        feature_names = load_feature_cols(tasks_path)
    if not feature_names:
        feature_names = [f"f{i}" for i in range(in_dim)]
    atk = cfg.get("attack") or {}
    atk_type = atk.get("type")
    trigger = None
    if atk_type == "backdoor":
        tasks_path = resolve_repo_path(Path(cfg.get("data", {}).get("tasks", "data/processed/tasks.npz")))
        trigger = scaled_trigger(atk.get("trigger"), feature_names, tasks_path)
    n_classes = int(max(label_map.values())) + 1 + int((cfg.get("attack") or {}).get("type") == "novelty")

    # Phase-2 head-strategy ablation: grow_head=true starts the classifier at
    # T0 width and lets BaseCLMethod._maybe_expand grow it per task (Paper-1
    # §4.1 / plan "growing head" protocol). Default False = pre-sized fixed
    # head (Paper-2 §3.2.1 protocol). Single-node only.
    from src.models import build_model

    grow_head = bool(cfg.get("grow_head", False))
    if grow_head:
        n_init = int(tasks[0]["y_train"].max()) + 1
        model = build_model(cfg, in_dim, n_init)
    else:
        model = build_model(cfg, in_dim, n_classes)
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
    poison_rows = []
    next_provisional_class = int(max(label_map.values())) + 1
    t0 = time.time()
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
        summary["asr_mean"] = None
        summary["wall_sec"] = time.time() - t0
        summary["cl_method"] = method_name
        summary["attack"] = atk_type
        summary["seed"] = seed
        summary["scenario"] = cfg.get("data", {}).get("scenario", "cii")
        summary["runtime_device"] = device
        return {"R": R, "summary": summary, "asr_rows": asr_rows}

    for t in range(len(tasks)):
        X_tr = tasks[t]["X_train"]
        y_tr = tasks[t]["y_train"]
        ae = None
        discovery_threshold = None
        if atk_type == "novelty":
            benign_index = np.flatnonzero(y_tr == 0)
            if len(benign_index) < 2:
                raise ValueError("novelty discovery requires separate benign AE and calibration flows")
            shuffled = np.random.RandomState(seed + t).permutation(benign_index)
            n_calibration = max(1, len(shuffled) // 5)
            ae = train_autoencoder(X_tr[shuffled[n_calibration:]], in_dim=in_dim, device=device, seed=seed + t)
            discovery_threshold = fit_threshold(
                recon_scores(ae, X_tr[shuffled[:n_calibration]], device=device),
                quantile=float(atk.get("threshold_quantile", 0.95)),
            )

        if attack_target == "stream":
            X_tr, y_tr, asr_meta = apply_attack(
                cfg, tasks[t], t, feature_names, ae, device, label_map, in_dim,
                model=method.model, trigger=trigger, discovery_threshold=discovery_threshold,
            )
        else:
            asr_meta = {"target_label": resolve_attack_target(atk, label_map), "triggered": np.zeros(len(y_tr), dtype=bool)}
        attack_label_changes = int(np.sum(y_tr != tasks[t]["y_train"]))

        fitted_discovery = None
        cluster_class_map = {}
        if atk_type == "novelty":
            fitted_discovery = fit_discovery(
                ae, discovery_threshold, X_tr, asr_meta["triggered"],
                device=device, min_cluster_size=int(atk.get("min_cluster_size", 15)),
                max_cluster_candidates=int(atk.get("max_cluster_candidates", 4000)),
                seed=seed + t,
            )
            if atk.get("training_mode", "discovery") == "direct_label_poison":
                # Explicit control: train on attacker-supplied labels, with no
                # cluster label entering the classifier. Remap the config's
                # sentinel unknown ID to a contiguous model output ID.
                y_tr = y_tr.copy()
                y_tr[y_tr == int(asr_meta["target_label"])] = int(max(label_map.values())) + 1
            else:
                # Discovery arm: attack-supplied unknown labels are ignored.
                # Only training-cluster membership can relabel the stream.
                y_tr, cluster_class_map = provisional_labels(
                    tasks[t]["y_train"], fitted_discovery, next_provisional_class,
                )
                next_provisional_class += len(cluster_class_map)
            if len(y_tr) and int(y_tr.max()) >= next_provisional_class:
                next_provisional_class = int(y_tr.max()) + 1

        keep = np.ones(len(y_tr), dtype=bool)
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
        if atk_type is not None and attack_target == "stream":
            poison_rows.append(attack_dose_row(
                atk, tasks[t]["y_train"], asr_meta["triggered"], label_map,
                task=t, retained_mask=keep, labels_changed=attack_label_changes,
            ))

        class_bound = int(max(n_classes, y_tr.max() + 1))
        if grow_head:
            # Running seen-width: expand_head only ever grows, old rows copied.
            class_bound = int(max(int(y_tr.max()) + 1, 1))
        loader = to_loader(X_tr, y_tr, batch_size=batch_size, shuffle=True)
        method.before_task(t, loader, class_bound=class_bound)
        method.train_task(loader, epochs=epochs)
        method.after_task(t, loader)
        if attack_target == "buffer" and atk_type == "label_flip":
            before_buffer = np.asarray(method.buffer_y, dtype=np.int64).copy()
            poison_buffer(method, atk, label_map, seed=seed + t)
            after_buffer = np.asarray(method.buffer_y, dtype=np.int64)
            poison_rows.append(attack_dose_row(
                atk, before_buffer, before_buffer != after_buffer, label_map,
                task=t, target="buffer",
            ))

        R[t, : t + 1] = evaluate(method, tasks, t)

        asr = None
        if atk_type == "backdoor":
            outcome = backdoor_outcome(
                method.predict, tasks[t]["X_test"], tasks[t]["y_test"], feature_names,
                label_map.get(atk.get("attack_class", "PortScan")),
                resolve_attack_target(atk, label_map), trigger,
            )
            attack_class = label_map[atk.get("attack_class", "PortScan")]
            target_label = resolve_attack_target(atk, label_map)
            outcome["train_eligible"] = int(np.sum(
                (tasks[t]["y_train"] == attack_class) & (tasks[t]["y_train"] != target_label)
            ))
            outcome["train_poisoned"] = int(np.sum(asr_meta["triggered"]))
            n_train = len(tasks[t]["y_train"])
            outcome["train_realized_dose"] = outcome["train_poisoned"] / n_train if n_train else None
            asr_rows.append({"task": t, **outcome})
        elif atk_type == "label_flip":
            y_te = tasks[t]["y_test"]
            pred = method.predict(tasks[t]["X_test"])
            if attack_target == "buffer":
                src_name = atk.get("source_class")
                tgt = resolve_attack_target(atk, label_map)
                if src_name and src_name in label_map:
                    mask = y_te == label_map[src_name]
                    asr = float(np.mean(pred[mask] == tgt)) if mask.any() else None
            else:
                src_name = atk.get("source_class")
                tgt = resolve_attack_target(atk, label_map)
                if atk.get("mode") == "persistent":
                    # Resolve the same per-task majority class the attack used.
                    from src.attacks.flip import majority_attack_class

                    src = majority_attack_class(y_te, tgt)
                    mask = y_te == src if src is not None else np.zeros(len(y_te), dtype=bool)
                    asr = float(np.mean(pred[mask] == tgt)) if mask.any() else None
                elif src_name and src_name in label_map and atk.get("mode") in ("targeted", "adaptive", "knn_adaptive"):
                    mask = y_te == label_map[src_name]
                    asr = float(np.mean(pred[mask] == tgt)) if mask.any() else None
        elif atk_type == "novelty":
            # There is no single attack-success target across provisional
            # clusters. Discovery endpoints below carry their own denominators.
            asr = None
        if atk_type != "backdoor":
            asr_rows.append({"task": t, "asr": asr})

        if atk_type == "novelty" and fitted_discovery is not None:
            disc = evaluate_discovery(
                ae=ae,
                threshold=discovery_threshold,
                fitted=fitted_discovery,
                X_test=tasks[t]["X_test"],
                y_test=tasks[t]["y_test"],
                device=device,
            )
            disc["task"] = t
            disc["training_mode"] = atk.get("training_mode", "discovery")
            disc["cluster_class_map"] = {str(k): int(v) for k, v in cluster_class_map.items()}
            disc["cluster_poison_fraction"] = {str(k): v for k, v in fitted_discovery["poison_fraction"].items()}
            disc["n_train_poisoned"] = int(np.sum(asr_meta["triggered"]))
            disc["n_train_relabelled_by_discovery"] = int(np.sum(fitted_discovery["train_labels"] >= 0)) if cluster_class_map else 0
            disc["n_ae_fit"] = len(shuffled) - n_calibration
            disc["n_ae_calibration"] = n_calibration
            disc["n_cluster_fit_candidates"] = fitted_discovery["n_fit_candidates"]
            disc["n_novel_train_candidates"] = fitted_discovery["n_novel_candidates"]
            y_test = tasks[t]["y_test"]
            predictions = method.predict(tasks[t]["X_test"])
            family_rows = []
            for class_name, class_id in label_map.items():
                family = y_test == class_id
                if family.any():
                    correct = int((predictions[family] == class_id).sum())
                    family_rows.append({
                        "class": class_name, "label": int(class_id),
                        "n": int(family.sum()), "correct": correct,
                        "recall": correct / int(family.sum()),
                    })
            disc["downstream_family_rows"] = family_rows
            benign_test = y_test == 0
            disc["downstream_benign_false_positive_rate"] = (
                float((predictions[benign_test] != 0).mean()) if benign_test.any() else None
            )
            discovery_rows.append(disc)

    summary = summarize(R)
    if atk_type == "backdoor":
        eligible = sum(r["eligible"] for r in asr_rows)
        summary["asr_mean"] = sum(r["successes"] for r in asr_rows) / eligible if eligible else None
        summary["asr_eligible"] = eligible
        summary["asr_successes"] = sum(r["successes"] for r in asr_rows)
        summary["asr_rows"] = asr_rows
    else:
        asr_values = [r["asr"] for r in asr_rows if r["asr"] is not None]
        summary["asr_mean"] = float(np.mean(asr_values)) if asr_values else None
    summary["wall_sec"] = time.time() - t0
    summary["cl_method"] = method_name
    summary["attack"] = (cfg.get("attack") or {}).get("type")
    summary["seed"] = seed
    summary["scenario"] = cfg.get("data", {}).get("scenario", "cii")
    summary["runtime_device"] = device
    if poison_rows:
        summary["poison_rows"] = poison_rows
        summary["poison_changed_total"] = sum(row["changed"] for row in poison_rows)
        summary["poison_eligible_total"] = sum(row["eligible"] for row in poison_rows)
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
            ("benign_false_alert_rate", discovery_rows),
            ("attack_flagged_rate", attack_rows),
            ("cluster_assignment_purity", discovery_rows),
            ("cluster_assignment_ari", discovery_rows),
            ("downstream_benign_false_positive_rate", discovery_rows),
        )
        for key, rows in mean_specs:
            vals = [float(r[key]) for r in rows if r.get(key) is not None]
            if vals:
                summary[f"{key}_mean"] = float(np.mean(vals))
    return {"R": R, "summary": summary, "asr_rows": asr_rows, "discovery_rows": discovery_rows}
