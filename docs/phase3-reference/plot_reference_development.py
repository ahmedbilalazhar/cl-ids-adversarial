"""Regenerate the descriptive one-trajectory 74-feature reference figure."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/phase3-reference/evidence/development-metrics.json"
OUT = ROOT / "docs/phase3-reference/figures"
OUT.mkdir(parents=True, exist_ok=True)

data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
rows = []
for record in data["stages"]:
    rows.append({
        "stage": f"E{record['stage']}",
        "stage_index": record["stage"],
        "eligible_macro_f1": record["eligible_macro_f1"],
        "benign_far": record["binary_full_seen"]["benign_far"],
        "benign_rows": record["binary_full_seen"]["tn"] + record["binary_full_seen"]["fp"],
        "model_sha256": record["model_sha256"],
        "bank_ids_sha256": record["bank_ids_sha256"],
    })

with (OUT / "reference-development-metrics.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 11})
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.7), constrained_layout=True)
stages = [row["stage"] for row in rows]
x = range(len(stages))

left = axes[0]
left.plot(x, [r["eligible_macro_f1"] for r in rows], color="#4355B9", marker="o", linewidth=2.5, markersize=6)
left.set_title("Eligible seen-class macro-F1")
left.set_ylabel("Macro-F1")
left.set_ylim(0, 0.55)
left.set_xticks(list(x), stages)
left.grid(axis="y", color="#D9DEE8", linewidth=0.8)
left.set_axisbelow(True)
for i, row in enumerate(rows):
    left.annotate(f"{row['eligible_macro_f1']:.3f}", (i, row["eligible_macro_f1"]), xytext=(0, 9),
                  textcoords="offset points", ha="center", color="#24316D", fontsize=9)

right = axes[1]
right.plot(x, [r["benign_far"] for r in rows], color="#D05A48", marker="o", linewidth=2.5, markersize=6)
right.set_title("Benign false-alert rate")
right.set_ylabel("False-alert rate")
right.set_ylim(0, 0.32)
right.set_yticks([0, .05, .10, .15, .20, .25, .30], ["0%", "5%", "10%", "15%", "20%", "25%", "30%"])
right.set_xticks(list(x), stages)
right.grid(axis="y", color="#D9DEE8", linewidth=0.8)
right.set_axisbelow(True)
for i, row in enumerate(rows):
    right.annotate(f"{100*row['benign_far']:.1f}%", (i, row["benign_far"]), xytext=(0, 9),
                   textcoords="offset points", ha="center", color="#873B30", fontsize=9)

fig.suptitle("Adopted 74-feature profile · one clean DR+DC reference · seed 101 · untuned", fontsize=11, weight="bold")
fig.savefig(OUT / "reference-development-metrics.pdf", bbox_inches="tight")
fig.savefig(OUT / "reference-development-metrics.png", dpi=220, bbox_inches="tight")
plt.close(fig)
print(json.dumps({"stages": rows, "outputs": [str(OUT / "reference-development-metrics.pdf"),
                                                 str(OUT / "reference-development-metrics.png"),
                                                 str(OUT / "reference-development-metrics.csv")],
                  "uncertainty": "not estimated; one trajectory"}, indent=2))
