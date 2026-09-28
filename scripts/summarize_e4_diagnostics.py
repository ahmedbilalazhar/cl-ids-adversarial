"""Descriptive E4 diagnostics only; no hypothesis test or final Holm claim."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import yaml

from src.reporting import check_artifact

CONFIGS = (
    "e4_novelty_nopois_c",
    "e4_novelty_anchor_c",
    "e4_novelty_label_control_c",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results/diagnostics"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--output", type=Path, default=Path("results/diagnostics/e4_descriptive.json"))
    args = parser.parse_args()
    runs = args.results_dir / "runs"
    rows = []
    for seed in args.seeds:
        for name in CONFIGS:
            cfg = yaml.safe_load((Path("configs/novelty") / f"{name}.yaml").read_text(encoding="utf-8"))
            cfg["seed"] = seed
            state = check_artifact(runs, name, seed, cfg)
            if not state["complete"] or state.get("provenance_level") != "code-hashed":
                continue
            summary = json.loads((runs / f"{name}_summary_seed{seed}.json").read_text(encoding="utf-8"))
            discovery = summary["discovery_rows"]
            n_attack = sum(row["n_attack_test"] for row in discovery)
            n_flagged = sum(row["n_attack_flagged"] for row in discovery)
            n_absorbed = sum(row["n_attack_absorbed"] for row in discovery)
            poison = summary.get("poison_rows", [])
            n_train = sum(row["n"] for row in poison)
            changed = sum(row["changed"] for row in poison)
            rows.append({
                "config": name, "seed": seed, "acc": summary["acc"],
                "forgetting": summary["forgetting"],
                "n_attack_test": n_attack, "n_attack_flagged": n_flagged,
                "n_attack_absorbed": n_absorbed,
                "attack_flagged_rate_pooled": n_flagged / n_attack if n_attack else None,
                "attack_absorption_all_pooled": n_absorbed / n_attack if n_attack else None,
                "attack_absorption_flagged_pooled": n_absorbed / n_flagged if n_flagged else None,
                "poison_changed": changed,
                "poison_realized_global_dose": changed / n_train if n_train else None,
            })
    by_name = {name: {r["seed"]: r for r in rows if r["config"] == name} for name in CONFIGS}
    paired = sorted(set.intersection(*(set(group) for group in by_name.values())))
    descriptive = {}
    for name, group in by_name.items():
        vals = [group[seed]["acc"] for seed in paired]
        absorption = [group[seed]["attack_absorption_all_pooled"] for seed in paired]
        flagged = [group[seed]["attack_flagged_rate_pooled"] for seed in paired]
        changed = [group[seed]["poison_changed"] for seed in paired]
        descriptive[name] = {
            "n_paired": len(vals),
            "acc_mean": float(np.mean(vals)) if vals else None,
            "acc_std": float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
            "attack_absorption_all_pooled_mean": float(np.mean(absorption)) if absorption else None,
            "attack_flagged_rate_pooled_mean": float(np.mean(flagged)) if flagged else None,
            "poison_changed_mean": float(np.mean(changed)) if changed else None,
        }
    output = {
        "status": "exploratory diagnostics; no final paired inference or Holm family",
        "paired_seeds": paired,
        "rows": rows,
        "descriptive": descriptive,
        "limitations": [
            "The detector's no-poison miss rate is high.",
            "Capped HDBSCAN changes clusters on small-case reference checks.",
            "Three seeds on one captured dataset estimate only seed variation.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"paired_seeds": paired, "descriptive": descriptive}, indent=2))


if __name__ == "__main__":
    main()
