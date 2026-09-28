"""Cheap, import-safe preflight for experiment configurations."""
from __future__ import annotations

import json
from pathlib import Path

from src.attacks.flip import resolve_class_id
from src.methods import METHODS
from src.paths import resolve_repo_path

AGGREGATORS = {"fedavg", "trimmed_mean", "median", "krum", "multi_krum", "dynamic_trust"}
ATTACK_TYPES = {"label_flip", "backdoor", "novelty"}
FLIP_MODES = {"random", "targeted", "persistent", "adaptive", "knn_adaptive"}
UPDATE_ATTACKS = {"sign_flip", "lie", "model_replacement"}


def validate_config(cfg: dict, *, expected_runner: str | None = None) -> None:
    """Reject mismatched runner, invalid attack/federation, and absent inputs."""
    if not isinstance(cfg, dict):
        raise TypeError("config must be a mapping")
    name = cfg.get("name")
    if not isinstance(name, str) or not name or any(c in name for c in "/\\:"):
        raise ValueError("config needs a safe nonempty name")
    if cfg.get("cl_method") not in METHODS:
        raise ValueError(f"{name}: unknown CL method")
    if "fed" in cfg and cfg["fed"] is not None and not isinstance(cfg["fed"], dict):
        raise TypeError(f"{name}: fed must be a mapping")
    if isinstance(cfg.get("fed"), dict) and not cfg["fed"]:
        raise ValueError(f"{name}: fed settings cannot be empty")
    runner = "federated" if cfg.get("fed") else "single-node"
    if expected_runner is not None and runner != expected_runner:
        raise ValueError(f"{name}: expected {expected_runner} runner, got {runner}")
    data = cfg.get("data") or {}
    task_name = data.get("tasks")
    if not isinstance(task_name, str) or not task_name:
        raise ValueError(f"{name}: task artifact path required")
    task_path = resolve_repo_path(Path(task_name))
    if not task_path.is_file():
        raise ValueError(f"{name}: task artifact missing: {task_path}")
    meta_path = task_path.with_suffix(".json")
    if not meta_path.is_file():
        raise ValueError(f"{name}: task metadata missing: {meta_path}")
    label_map = json.loads(meta_path.read_text(encoding="utf-8")).get("label_map")
    if not isinstance(label_map, dict) or not label_map:
        raise ValueError(f"{name}: task label map missing")
    if data.get("scenario", "cii") not in {"cii", "ci"}:
        raise ValueError(f"{name}: unsupported scenario")
    if cfg.get("device", "cpu") not in {"cpu", "cuda"}:
        raise ValueError(f"{name}: unsupported device")

    attack = cfg.get("attack") or {}
    kind = attack.get("type")
    if kind is not None and kind not in ATTACK_TYPES:
        raise ValueError(f"{name}: unknown attack type {kind}")
    budget = attack.get("budget", 0)
    if kind is not None and (
        isinstance(budget, bool) or not isinstance(budget, (int, float)) or not 0 <= budget <= 1
    ):
        raise ValueError(f"{name}: attack budget must be between 0 and 1")
    if kind == "label_flip" and attack.get("mode", "random") not in FLIP_MODES:
        raise ValueError(f"{name}: unknown label-flip mode")
    if kind == "novelty":
        if runner != "single-node":
            raise ValueError(f"{name}: novelty discovery needs the single-node runner")
        if attack.get("target", "stream") != "stream":
            raise ValueError(f"{name}: novelty discovery requires stream target")
        if attack.get("training_mode", "discovery") not in {"discovery", "direct_label_poison"}:
            raise ValueError(f"{name}: unknown novelty training_mode")
        cap = attack.get("max_cluster_candidates", 4000)
        minimum = attack.get("min_cluster_size", 15)
        if not isinstance(cap, int) or isinstance(cap, bool) or not isinstance(minimum, int) or cap < minimum or minimum < 2:
            raise ValueError(f"{name}: invalid novelty cluster candidate cap")
    if kind in {"label_flip", "backdoor"}:
        resolve_class_id(attack.get("target_class"), label_map)
        if attack.get("source_class") is not None:
            resolve_class_id(attack["source_class"], label_map, role="source")
        if kind == "backdoor":
            resolve_class_id(attack.get("attack_class", "PortScan"), label_map, role="attack")
    update = attack.get("update_attack") or {}
    if update and (runner != "federated" or update.get("method") not in UPDATE_ATTACKS):
        raise ValueError(f"{name}: update attack requires federation and a known method")
    defense = cfg.get("defense") or {}
    if defense.get("type") not in {None, "small_loss", "knn_consistency"}:
        raise ValueError(f"{name}: unknown defense")

    if runner == "federated":
        fed = cfg["fed"]
        n = fed.get("n_clients", 5)
        if isinstance(n, bool) or not isinstance(n, int) or n < 2:
            raise ValueError(f"{name}: n_clients must be an integer >= 2")
        ids = fed.get("malicious_ids", [fed.get("malicious_id", n - 1)])
        if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)) or any(
            isinstance(i, bool) or not isinstance(i, int) or i < 0 or i >= n for i in ids
        ):
            raise ValueError(f"{name}: malicious client IDs are invalid")
        aggregator = fed.get("aggregator", "fedavg")
        if aggregator not in AGGREGATORS:
            raise ValueError(f"{name}: unknown aggregator")
        n_mal = fed.get("n_mal", len(ids))
        if isinstance(n_mal, bool) or not isinstance(n_mal, int) or n_mal != len(ids):
            raise ValueError(f"{name}: n_mal must match malicious client count")
        if aggregator in {"krum", "multi_krum"} and n <= 2 * n_mal + 2:
            raise ValueError(f"{name}: Krum requires n_clients > 2*n_mal + 2")
        if aggregator == "trimmed_mean" and not 0 <= fed.get("trim_ratio", 0.2) < 0.5:
            raise ValueError(f"{name}: invalid trim_ratio")

    if kind == "backdoor":
        from src.attacks.backdoor import scaled_trigger
        from src.data.sequence import load_feature_cols

        names = cfg.get("feature_names") or load_feature_cols(task_path)
        if not names:
            raise ValueError(f"{name}: backdoor requires task feature names")
        scaled_trigger(attack.get("trigger"), names, task_path)
