"""Aggregate paired assignment-rule comparisons over registered partitions."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    2026: ROOT / "results/phase3-followup/discovery-development-assignment-v1.json",
    2027: ROOT / "results/phase3-followup/discovery-development-assignment-seed-2027.json",
    2028: ROOT / "results/phase3-followup/discovery-development-assignment-seed-2028.json",
}
OUTPUT = ROOT / "results/phase3-followup/discovery-development-assignment-summary-v1.json"
METRICS = ("n_eval_assigned", "n_novel_eval", "clustered_attack_rate", "cluster_assignment_purity", "cluster_assignment_ari")


def mean_sd(values):
    return {"mean": statistics.mean(values), "sd_across_partitions": statistics.stdev(values)}


def main() -> None:
    runs = {}
    policies = {"centroid_radius": [], "nearest_centroid": []}
    for seed, path in FILES.items():
        r = json.loads(path.read_text(encoding="utf-8"))
        if r["config"]["seed"] != seed:
            raise ValueError(f"Unexpected seed in {path}")
        for key, slot in (("centroid_radius", "metrics"), ("nearest_centroid", "assignment_ablation_metrics")):
            m = r[slot]
            policies[key].append({name: m[name] for name in METRICS})
        runs[str(seed)] = path.name
    summary = {}
    for policy, rows in policies.items():
        summary[policy] = {key: mean_sd([row[key] for row in rows]) for key in METRICS}
    differences = {}
    for metric in ("clustered_attack_rate", "cluster_assignment_purity", "cluster_assignment_ari"):
        diffs = [b[metric] - a[metric] for a, b in zip(policies["centroid_radius"], policies["nearest_centroid"])]
        differences[metric + "_nearest_minus_radius"] = mean_sd(diffs)
    result = {"schema": "phase3-discovery-assignment-summary-v1", "status": "exploratory_development_only",
              "seeds": list(FILES), "policies": summary, "paired_differences": differences,
              "runs": runs, "interpretation": ["Comparisons are paired on the same AE, threshold, fitted clusters, and evaluation components within each seed.",
                              "Component partitions overlap; SD is descriptive partition sensitivity, not a confidence interval.",
                              "Novelty detection and benign false-alert rates are invariant because assignment is applied after the frozen threshold step."]}
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"policies": summary, "paired_differences": differences}, indent=2))


if __name__ == "__main__":
    main()
