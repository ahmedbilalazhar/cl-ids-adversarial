"""Render the exploratory Phase 3 discovery sensitivity figure from saved JSON."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/phase3-followup/discovery-development-sensitivity-v2.json"
OUTPUT = ROOT / "docs/phase3-plan/figures/discovery-development-sensitivity.svg"


def main() -> None:
    result = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = result["sensitivity_grid"]
    colors = {0.90: "#187C80", 0.95: "#315C8A", 0.99: "#C26D43"}
    markers = {1000: "o", 4000: "D"}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titleweight": "bold", "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": "#F7F8FA",
                         "axes.facecolor": "#F7F8FA"})
    fig, (left, right) = plt.subplots(1, 2, figsize=(10.8, 4.6), constrained_layout=True)
    for row in rows:
        q, cap, m = row["quantile"], row["candidate_cap"], row["metrics"]
        label = f"q={q:.2f}, cap={cap:,}"
        left.scatter(100*m["benign_false_alert_rate"], 100*m["attack_flagged_rate"],
                     s=85, c=colors[q], marker=markers[cap], edgecolors="white", linewidths=1.2,
                     label=label, zorder=3)
        right.scatter(100*m["clustered_attack_rate"], m["cluster_assignment_ari"],
                      s=85, c=colors[q], marker=markers[cap], edgecolors="white", linewidths=1.2,
                      label=label, zorder=3)
    left.set(title="Detection trade-off", xlabel="Benign false-alert rate (%)", ylabel="Attack detection rate (%)")
    right.set(title="Cluster assignment behavior", xlabel="Flagged attacks assigned (%)", ylabel="Adjusted Rand index")
    left.set_xlim(0, 12); left.set_ylim(35, 100); right.set_xlim(55, 95); right.set_ylim(0, .34)
    for ax in (left, right):
        ax.grid(axis="both", color="#DDE2E8", linewidth=.8, alpha=.8)
        ax.set_axisbelow(True)
    handles, labels = left.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(.5, -.06))
    fig.suptitle("Component-disjoint development sensitivity · exploratory only", fontsize=14, weight="bold", color="#172B3A")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
