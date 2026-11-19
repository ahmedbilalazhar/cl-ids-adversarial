"""Summarize repeated component partitions without treating flows as replicates."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    2026: ROOT / "results/phase3-followup/discovery-development-sensitivity-v2.json",
    2027: ROOT / "results/phase3-followup/discovery-development-seed-2027.json",
    2028: ROOT / "results/phase3-followup/discovery-development-seed-2028.json",
}
OUTPUT = ROOT / "results/phase3-followup/discovery-development-replicates-summary-v1.json"
KEYS = ("attack_flagged_rate", "benign_false_alert_rate", "cluster_assignment_purity",
        "cluster_assignment_ari", "clustered_attack_rate", "noise_rate_attack", "eval_novel_rate")


def main() -> None:
    runs = {}
    for seed, path in FILES.items():
        result = json.loads(path.read_text(encoding="utf-8"))
        if result["config"]["seed"] != seed:
            raise ValueError(f"Unexpected configured seed in {path}")
        runs[str(seed)] = {"source": path.name, "metrics": result["metrics"],
                           "component_counts": result["component_counts"], "row_counts": result["row_counts"]}
    summary = {}
    for key in KEYS:
        vals = [runs[str(seed)]["metrics"][key] for seed in FILES]
        summary[key] = {"mean": statistics.mean(vals),
                        "sd_across_component_partitions": statistics.stdev(vals)}
    out = {"schema": "phase3-discovery-component-replicates-summary-v1",
           "status": "exploratory_development_only", "seeds": list(FILES),
           "metrics": summary, "runs": runs,
           "interpretation": ["Each seed makes a new component-level fit/calibration/evaluation partition and model initialization.",
                              "The partitions overlap in source population; SD is descriptive partition sensitivity, not a confidence interval.",
                              "All evaluation remains within the development role; no final-test data were opened."]}
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    OUTPUT.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(OUTPUT)


if __name__ == "__main__":
    main()
