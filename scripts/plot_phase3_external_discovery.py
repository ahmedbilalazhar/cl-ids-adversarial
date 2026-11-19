"""Plot external discovery task rates from the registered summary JSON."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/phase3-followup/external-discovery-summary-v2.json"
OUTPUT = ROOT / "docs/phase3-plan/figures/external-discovery-by-task.svg"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))["datasets"]
    palette = {"CICIoT2023": "#187C80", "UNSW-NB15": "#315C8A"}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titleweight": "bold", "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": "#F7F8FA",
                         "axes.facecolor": "#F7F8FA"})
    fig, axes = plt.subplots(1, 2, figsize=(10.3, 4.4), constrained_layout=True)
    for dataset, summary in data.items():
        tasks = [summary["tasks"][str(i)] for i in range(4)]
        color = palette[dataset]
        x = list(range(4))
        for ax, metric, title in (
            (axes[0], "attack_flagged_rate", "Attack detection"),
            (axes[1], "benign_false_alert_rate", "Benign false alerts"),
        ):
            y = [100*t[metric]["mean"] for t in tasks]
            e = [100*t[metric]["sd_across_seeds"] for t in tasks]
            ax.errorbar(x, y, yerr=e, marker="o", markersize=6, linewidth=2.2,
                        capsize=3, color=color, label=dataset)
            ax.set_title(title)
            ax.set_xlabel("Sequential task index")
            ax.set_xticks(x, ["T0", "T1", "T2", "T3"])
            ax.grid(axis="y", color="#DDE2E8", linewidth=.8)
            ax.set_axisbelow(True)
    axes[0].set_ylabel("Rate (%)")
    axes[1].set_ylabel("Rate (%)")
    axes[0].set_ylim(bottom=0); axes[1].set_ylim(bottom=0)
    axes[1].legend(frameon=False, loc="upper right")
    fig.suptitle("External discovery replication · mean ± SD across three seeds", fontsize=14, weight="bold", color="#172B3A")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
