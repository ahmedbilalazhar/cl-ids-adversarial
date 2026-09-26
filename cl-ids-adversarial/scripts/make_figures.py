from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGS = RESULTS / "figures"

# Gate D labeling rules (mirror scripts/stats_summary.py so figures inherit them):
ASR_NA_LABEL = "N/A (undefined for random-target mode)"
BUFFER_FIG_NOTE = (
    "Note: ER/DER++ replay buffers use uniform random eviction and inherit "
    "stream class imbalance; NOT class-balanced."
)


def asr_label(row: dict) -> str:
    """Gate D rule 1: random-mode ASR renders as N/A, never 0."""
    v = row.get("asr_mean_mean", "")
    if v == "" or v == ASR_NA_LABEL or "N/A" in str(v):
        return "N/A"
    try:
        return f"{float(v):.1e}"
    except (TypeError, ValueError):
        return "N/A"


def load_stats() -> dict[str, dict]:
    out = {}
    with open(RESULTS / "stats_summary.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["name"]] = r
    return out


def mean_std(row: dict, m: str) -> tuple[float, float]:
    return float(row[f"{m}_mean"]), float(row[f"{m}_std"])


def fig_baselines(stats: dict) -> None:
    names = ["e1_joint", "e1_lwf", "e1_clean", "e1_ewc", "e1_finetune", "e1_derpp"]
    labels = ["Joint\n(oracle)", "LwF", "ER\n(clean)", "EWC", "FineTune", "DER++"]
    means, stds = [], []
    for n in names:
        mu, sd = mean_std(stats[n], "acc")
        means.append(mu)
        stds.append(sd)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(labels, means, yerr=stds, capsize=4, color=["#4c72b0"] + ["#55a868"] + ["#c44e52"] * 4)
    ax.set_ylabel("Average accuracy (ACC)")
    ax.set_ylim(0, 1.05)
    ax.set_title("E1 — Clean baselines on CICIDS2017 CII sequence (n=7 seeds)")
    for i, m in enumerate(means):
        ax.text(i, m + stds[i] + 0.02, f"{m:.3f}", ha="center", fontsize=8)
    fig.text(0.01, 0.01, BUFFER_FIG_NOTE, fontsize=6, style="italic")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_e1_baselines.png", dpi=200)
    plt.close(fig)


def fig_r_matrix() -> None:
    files = sorted(RESULTS.glob("e1_clean_R_seed*.csv"))
    mats = [np.loadtxt(f, delimiter=",") for f in files]
    R = np.mean(mats, axis=0)
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(R, vmin=0, vmax=1, cmap="viridis")
    ax.set_xlabel("Task trained on")
    ax.set_ylabel("Task evaluated on")
    ax.set_xticks(range(R.shape[1]))
    ax.set_yticks(range(R.shape[0]))
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            ax.text(j, i, f"{R[i, j]:.2f}", ha="center", va="center", color="white" if R[i, j] < 0.6 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, label="accuracy")
    ax.set_title(f"E1 — Task-accuracy matrix, ER clean (mean of {len(mats)} seeds)")
    fig.text(0.01, 0.01, BUFFER_FIG_NOTE, fontsize=6, style="italic")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_r_matrix_er_clean.png", dpi=200)
    plt.close(fig)


def fig_discovery(stats: dict) -> None:
    names = ["e4_novelty_nopois", "e4_novelty", "e4_novelty_anchor"]
    labels = ["no poison\n(control)", "recon-max\npoison", "anchor\npoison"]
    cols = [("absorbed_attack_rate", "#c44e52", "attack absorption"), ("fictitious_absorption", "#8172b3", "benign absorption")]
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(names))
    w = 0.35
    for k, (m, c, lab) in enumerate(cols):
        means, stds = [], []
        for n in names:
            mu, sd = mean_std(stats[n], m)
            means.append(mu)
            stds.append(sd)
        ax.bar(x + (k - 0.5) * w, means, w, yerr=stds, capsize=4, color=c, label=lab)
    miss = [mean_std(stats[n], "discovery_miss_rate")[0] for n in names]
    ax.plot(x, miss, "k--o", label="discovery miss rate (invariant)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("rate")
    ax.set_title("E4 — Discovery-stage poisoning, ρ=1% (n=7 seeds)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_e4_discovery.png", dpi=200)
    plt.close(fig)


def fig_defences(stats: dict) -> None:
    names = ["e2_labelflip", "e6_defense_smallloss", "e6_defense_knnconsist"]
    labels = ["undefended", "+ small-loss\nfilter", "+ kNN-consistency\nfilter"]
    means, stds, asrs = [], [], []
    for n in names:
        mu, sd = mean_std(stats[n], "acc")
        means.append(mu)
        stds.append(sd)
        asrs.append(asr_label(stats[n]))  # Gate D rule 1: N/A-safe ASR rendering
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#c44e52", "#55a868", "#8172b3"]
    ax.bar(labels, means, yerr=stds, capsize=4, color=colors)
    for i, (m, a) in enumerate(zip(means, asrs)):
        ax.text(i, m + stds[i] + 0.015, f"{m:.3f}\nASR {a}", ha="center", fontsize=8)
    ax.set_ylabel("Average accuracy (ACC)")
    ax.set_ylim(0, 0.5)
    ax.set_title("E6 — Defences under targeted 1% label flip (n=7 seeds)")
    fig.text(0.01, 0.01, BUFFER_FIG_NOTE, fontsize=6, style="italic")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_e6_defences.png", dpi=200)
    plt.close(fig)


def fig_federated(stats: dict) -> None:
    """Phase 2 headline: federated finetune vs EWC vs DER++ across poison budgets,
    plus small-loss defense at p5/p10. Gate D: buffer footnote; N/A-safe ASR."""
    methods = [
        ("f2_fed_finetune", "FineTune"),
        ("f2_fed_ewc", "EWC"),
        ("f2_fed_derpp", "DER++"),
    ]
    budgets = ["p0", "p1", "p5", "p10"]
    x = np.arange(len(budgets))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, (prefix, lab) in enumerate(methods):
        means = [float(stats[f"{prefix}_{b}"]["acc_mean"]) for b in budgets]
        stds = [float(stats[f"{prefix}_{b}"]["acc_std"]) for b in budgets]
        ax.errorbar(x + (i - 1) * 0.12, means, yerr=stds, fmt="-o", capsize=3, label=f"{lab} (undefended)")
        defended = {}
        for b in ("p5", "p10"):
            key = f"f4_fed_{prefix.split('_fed_')[1]}_{b}_sl"
            if key in stats:
                defended[b] = (float(stats[key]["acc_mean"]), float(stats[key]["acc_std"]))
        if defended:
            dx = [budgets.index(b) + (i - 1) * 0.12 for b in defended]
            ax.errorbar(dx, [v[0] for v in defended.values()], yerr=[v[1] for v in defended.values()],
                        fmt="s--", capsize=3, label=f"{lab} +small-loss")
    ax.set_xticks(x)
    ax.set_xticklabels(["0%", "1%", "5%", "10%"])
    ax.set_xlabel("malicious-shard poison budget")
    ax.set_ylabel("Average accuracy (ACC)")
    ax.set_title("Federated class-incremental IDS under poisoning (5 clients, 1 malicious, n=7)")
    ax.legend(fontsize=7)
    fig.text(0.01, 0.01, BUFFER_FIG_NOTE + " Poison budget = fraction of malicious client's shard.", fontsize=6, style="italic")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_f2_federated.png", dpi=200)
    plt.close(fig)


def fig_e5() -> None:
    seeds = [1, 2, 42]
    data = [json.loads((RESULTS / f"e5_evasion_seed{s}.json").read_text()) for s in seeds]
    tasks = data[0]["per_task"]
    tids = [r["task"] for r in tasks]
    ev = np.mean([[r["evasion_rate"] for r in d["per_task"]] for d in data], axis=0)
    poll = np.mean([[r["pollution_rate"] for r in d["per_task"]] for d in data], axis=0)
    x = np.arange(len(tids))
    w = 0.35
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x - w / 2, ev, w, label="evasion (discovered attacks hidden)", color="#c44e52")
    ax.bar(x + w / 2, poll, w, label="pollution (benign forced into discovery)", color="#4c72b0")
    ax.set_xticks(x)
    ax.set_xticklabels([f"T{t}" for t in tids])
    ax.set_ylabel("rate")
    ax.set_ylim(0, 1)
    ax.set_title("E5 — Bidirectional manipulation of the novelty detector (3 seeds, ε=0.5)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_e5_evasion.png", dpi=200)
    plt.close(fig)


def main() -> None:
    FIGS.mkdir(exist_ok=True)
    stats = load_stats()
    fig_baselines(stats)
    fig_r_matrix()
    fig_federated(stats)
    fig_discovery(stats)
    fig_defences(stats)
    fig_e5()
    for p in sorted(FIGS.glob("*.png")):
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
