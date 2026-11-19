"""Exploratory discovery study using component-disjoint development partitions only."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from src.discovery.pipeline import evaluate_discovery, fit_discovery_unlabeled, fit_threshold, recon_scores
from src.models.mlp import Autoencoder

PACKAGE = ROOT / "data/processed/phase3-reference74-v1/development"
SOURCE = ROOT / "data/raw/phase3-feasibility-corrected/no-headers-74"
CONFIG = ROOT / "configs/phase3/discovery-development-v1.json"
SENSITIVITY_CONFIG = ROOT / "configs/phase3/discovery-development-sensitivity-v1.json"
REPLICATE_CONFIG = ROOT / "configs/phase3/discovery-development-replicates-v1.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/phase3-followup/discovery-development-v1.json"))
    parser.add_argument("--sensitivity", action="store_true", help="Run the predeclared exploratory quantile/cap grid")
    parser.add_argument("--seed", type=int, help="Override the partition/model seed for an additional exploratory replicate")
    parser.add_argument("--assignment-ablation", action="store_true", help="Compare radius-gated and unrestricted nearest-centroid assignment")
    args = parser.parse_args()
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    sensitivity_cfg = json.loads(SENSITIVITY_CONFIG.read_text(encoding="utf-8"))
    replicate_cfg = json.loads(REPLICATE_CONFIG.read_text(encoding="utf-8"))
    if replicate_cfg["parent_config_sha256"] != sha256(CONFIG):
        raise ValueError("Replicate plan is bound to a different primary config")
    if args.sensitivity and args.output == Path("results/phase3-followup/discovery-development-v1.json"):
        parser.error("--sensitivity requires a distinct --output path")
    if args.seed is not None:
        if args.seed not in replicate_cfg["seeds"]:
            parser.error(f"Partition seeds must come from the frozen list {replicate_cfg['seeds']}")
        cfg["seed"] = args.seed
        if args.sensitivity:
            sensitivity_cfg["seed"] = args.seed
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("role") != "development_only" or sha256(PACKAGE / "manifest.json") != cfg["data_manifest_sha256"]:
        raise ValueError("Development manifest identity/role mismatch")
    for name, digest in manifest["files"].items():
        if sha256(PACKAGE / name) != digest:
            raise ValueError(f"Development artifact hash mismatch: {name}")

    # Reconstruct component IDs from the audited source graph; map immutable row IDs.
    with np.load(SOURCE / "conditional-components-120.npz", allow_pickle=False) as state, \
         np.load(SOURCE / "conditional-candidate-split.npz", allow_pickle=False) as split:
        source_ids = state["row_ids"]
        order = np.argsort(source_ids)
        sorted_ids = source_ids[order]
        ids = np.load(PACKAGE / "ids.npy", allow_pickle=False)
        at = np.searchsorted(sorted_ids, ids)
        if np.any(at >= len(sorted_ids)) or not np.array_equal(sorted_ids[at], ids):
            raise ValueError("Development row IDs do not map exactly to audited source rows")
        source_pos = order[at]
        root_ids = state["roots"]
        canonical = np.full(len(root_ids), np.iinfo(np.uint64).max, dtype=np.uint64)
        np.minimum.at(canonical, root_ids, source_ids)
        component_ids = canonical[root_ids[source_pos]]
        roles = np.full(len(source_ids), -1, dtype=np.int8)
        roles[split["source_positions"]] = split["roles"]
        if not np.all(roles[source_pos] == 1):
            raise ValueError("Development bank contains a row outside the development role")

    seed = int(cfg["seed"])
    components = np.unique(component_ids)
    rng = np.random.default_rng(seed)
    shuffled = rng.permutation(components)
    n_fit = int(len(shuffled) * cfg["component_partition_fractions"]["autoencoder_fit_and_clustering"])
    n_cal = int(len(shuffled) * cfg["component_partition_fractions"]["benign_calibration"])
    fit_groups, cal_groups, eval_groups = np.split(shuffled, [n_fit, n_fit + n_cal])
    fit_rows = np.isin(component_ids, fit_groups)
    cal_rows = np.isin(component_ids, cal_groups)
    eval_rows = np.isin(component_ids, eval_groups)
    if np.any((fit_rows.astype(int) + cal_rows.astype(int) + eval_rows.astype(int)) != 1):
        raise RuntimeError("Component partitions are not exhaustive and disjoint")

    x = np.load(PACKAGE / "x.npy", allow_pickle=False, mmap_mode="r")
    y = np.load(PACKAGE / "y.npy", allow_pickle=False, mmap_mode="r")
    benign = int(manifest["eligible_codes"][0])
    fit_benign = np.flatnonzero(fit_rows & (y == benign))
    cal_benign = np.flatnonzero(cal_rows & (y == benign))
    if not len(fit_benign) or not len(cal_benign) or not eval_rows.any():
        raise ValueError("Insufficient benign fit/calibration or evaluation support")

    torch.manual_seed(seed)
    torch.set_num_threads(1)
    device = "cpu"
    model = Autoencoder(x.shape[1]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["autoencoder"]["learning_rate"])
    batch_size = int(cfg["autoencoder"]["batch_size"])
    model.train()
    fit_order = np.random.default_rng(seed).permutation(fit_benign)
    for _ in range(int(cfg["autoencoder"]["epochs"])):
        for start in range(0, len(fit_order), batch_size):
            xb = torch.from_numpy(np.asarray(x[fit_order[start:start + batch_size]]).copy())
            opt.zero_grad(set_to_none=True)
            loss = torch.mean((model(xb) - xb) ** 2)
            loss.backward()
            opt.step()
    model.eval()
    cal_scores = recon_scores(model, np.asarray(x[cal_benign]), device=device)
    eval_x = np.asarray(x[eval_rows])
    eval_y = np.asarray(y[eval_rows])
    fit_x = np.asarray(x[fit_rows])

    def development_metric_names(metrics: dict) -> dict:
        for old, new in (("n_attack_test", "n_attack_eval"), ("n_benign_test", "n_benign_eval"),
                         ("n_test_assigned", "n_eval_assigned"), ("test_novel_rate", "eval_novel_rate"),
                         ("test_noise_rate", "eval_noise_rate"), ("n_novel_test", "n_novel_eval")):
            metrics[new] = metrics.pop(old)
        return metrics

    def run_setting(quantile: float, cap: int) -> dict:
        threshold = fit_threshold(cal_scores, quantile)
        fitted = fit_discovery_unlabeled(
            model, threshold, fit_x, device=device,
            min_cluster_size=int(cfg["clustering"]["min_cluster_size"]),
            max_cluster_candidates=cap, seed=seed,
        )
        metrics = evaluate_discovery(model, threshold, fitted, eval_x, eval_y,
                                     device=device, benign_label=benign)
        assignment_ablation = None
        if args.assignment_ablation:
            assignment_ablation = development_metric_names(evaluate_discovery(
                model, threshold, fitted, eval_x, eval_y, device=device,
                benign_label=benign, assignment_policy="nearest_centroid",
            ))
        metrics = development_metric_names(metrics)
        return {"quantile": quantile, "candidate_cap": cap, "metrics": metrics,
                "nearest_centroid_ablation_metrics": assignment_ablation}

    primary = run_setting(float(cfg["threshold"]["quantile"]), int(cfg["clustering"]["max_fit_candidates"]))
    sensitivity = []
    if args.sensitivity:
        # Explicitly exploratory grid; it is not used to select a new primary setting.
        if sensitivity_cfg["parent_config_sha256"] != sha256(CONFIG):
            raise ValueError("Sensitivity grid is bound to a different primary config")
        for quantile in sensitivity_cfg["calibration_quantiles"]:
            for cap in sensitivity_cfg["hdbscan_candidate_caps"]:
                sensitivity.append(run_setting(quantile, cap))
    result = {
        "schema": "phase3-discovery-development-result-v1", "status": "exploratory_development_only",
        "config": cfg, "base_config_sha256": sha256(CONFIG),
        "effective_config_sha256": hashlib.sha256(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "development_manifest_sha256": sha256(PACKAGE / "manifest.json"),
        "component_counts": {"fit": len(fit_groups), "calibration": len(cal_groups), "evaluation": len(eval_groups)},
        "row_counts": {"fit": int(fit_rows.sum()), "fit_benign": len(fit_benign), "calibration": int(cal_rows.sum()),
                       "calibration_benign": len(cal_benign), "evaluation": int(eval_rows.sum())},
        "metrics": primary["metrics"], "assignment_ablation_metrics": primary["nearest_centroid_ablation_metrics"],
        "replicate_plan": replicate_cfg, "replicate_plan_sha256": sha256(REPLICATE_CONFIG),
        "sensitivity_plan": sensitivity_cfg,
        "sensitivity_plan_sha256": sha256(SENSITIVITY_CONFIG), "sensitivity_grid": sensitivity,
        "interpretation_limits": ["Development-only exploratory estimate; not final-test performance.",
                                  "One component partition and one seed per run; no population-level claim.",
                                  "Sensitivity grid is exploratory and does not select a replacement primary setting.",
                                  "Labels are used only for benign-only AE/calibration selection and after frozen clustering for evaluation."],
        "final_test_accessed": False,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output),
                      "primary_metrics": primary["metrics"], "sensitivity_rows": len(sensitivity)}, indent=2))


if __name__ == "__main__":
    main()
