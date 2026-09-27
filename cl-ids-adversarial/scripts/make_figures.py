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


# ---------------------------------------------------------------------------
# Phase 2/3 figures (n=12 corrected protocol). Each reads only keys present in
# stats_summary.csv and raises (caught by main -> skipped) while a grid is
# still running, so figures never render partial data silently.
# ---------------------------------------------------------------------------


def _mu_sd(stats: dict, name: str) -> tuple[float, float]:
    if name not in stats:
        raise KeyError(f"{name} missing")
    return float(stats[name]["acc_mean"]), float(stats[name]["acc_std"])


def fig_protocol_effects(stats: dict) -> None:
    """Split x scaler decomposition: the 'limitation -> contribution' figure."""
    pairs = [
        ("ER", "e1_clean", "e1_clean_rf"),
        ("FineTune", "e1_finetune", "e1_finetune_rf"),
        ("EWC", "e1_ewc", "e1_ewc_rf"),
        ("DER++", "e1_derpp", "e1_derpp_rf"),
        ("LwF", "e1_lwf", "e1_lwf_rf"),
        ("Joint", "e1_joint", "e1_joint_rf"),
    ]
    chrono = {"ER": "e1_clean_c", "FineTune": "e1_finetune_c", "EWC": "e1_ewc_c",
              "DER++": "e1_derpp_c", "LwF": "e1_lwf_c", "Joint": "e1_joint_c"}
    per_task, rand_split, chrono_split = [], [], []
    for m, pt, rf in pairs:
        per_task.append(_mu_sd(stats, pt)[0])
        rand_split.append(_mu_sd(stats, rf)[0])
        chrono_split.append(_mu_sd(stats, chrono[m])[0])
    x = np.arange(len(pairs))
    w = 0.27
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x - w, per_task, w, label="per-task scaler + random split (legacy)", color="#c44e52")
    ax.bar(x, rand_split, w, label="frozen scaler + random split", color="#8172b3")
    ax.bar(x + w, chrono_split, w, label="frozen scaler + chrono split (primary)", color="#4c72b0")
    ax.set_xticks(x)
    ax.set_xticklabels([p[0] for p in pairs])
    ax.set_ylabel("Average accuracy (ACC)")
    ax.set_ylim(0, 1.05)
    ax.set_title("Preprocessing decomposition: per-task standardization dominates the split choice")
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, BUFFER_FIG_NOTE, fontsize=6, style="italic")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_protocol_effects.png", dpi=200)
    plt.close(fig)


def fig_federated_corrected(stats: dict) -> None:
    """Corrected federated headline: 4 methods x 4 budgets (n=12)."""
    methods = [("finetune", "FineTune"), ("ewc", "EWC"), ("derpp", "DER++"), ("er", "ER")]
    budgets = ["p0", "p1", "p5", "p10"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(budgets))
    for i, (m, lab) in enumerate(methods):
        means, stds = [], []
        for b in budgets:
            mu, sd = _mu_sd(stats, f"f2_fed_{m}_{b}_c")
            means.append(mu)
            stds.append(sd)
        ax.errorbar(x + (i - 1.5) * 0.1, means, yerr=stds, fmt="-o", capsize=3, label=lab)
    single = {
        "finetune": "e1_finetune_c", "ewc": "e1_ewc_c", "derpp": "e1_derpp_c", "er": "e1_clean_c",
    }
    for m, lab in methods:
        ax.axhline(_mu_sd(stats, single[m])[0], ls=":", lw=1, alpha=0.6, color="gray")
    ax.set_xticks(x)
    ax.set_xticklabels(["0%", "1%", "5%", "10%"])
    ax.set_xlabel("malicious-shard poison budget (targeted flip -> Benign)")
    ax.set_ylabel("Average accuracy (ACC)")
    ax.set_title("Corrected federated headline (5 clients, 1 malicious, n=12, chrono+frozen)\n"
                 "dotted lines = single-node counterparts")
    ax.legend(fontsize=8, ncol=2)
    fig.text(0.01, 0.01, BUFFER_FIG_NOTE, fontsize=6, style="italic")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_f2_federated_corrected.png", dpi=200)
    plt.close(fig)


def fig_byzantine(stats: dict) -> None:
    """Byzantine availability vs robust aggregation (ft + ewc)."""
    atk = [("sf", "sign-flip"), ("lie", "LIE z=1.5"), ("mr", "model-repl")]
    aggs = [("fedavg", "FedAvg", "#c44e52"), ("trim", "Trimmed-Mean", "#4c72b0"),
            ("med", "Median", "#55a868"), ("krum", "Krum", "#8172b3"),
            ("trust", "Dynamic-Trust", "#dd8452")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, (m, lab) in zip(axes, [("ft", "FineTune"), ("ewc", "EWC")]):
        x = np.arange(len(atk))
        w = 0.16
        for i, (a, alab, c) in enumerate(aggs):
            means, stds = [], []
            for k, (t, _) in enumerate(atk):
                mu, sd = _mu_sd(stats, f"bz_{m}_{t}_{a}_c")
                means.append(mu)
                stds.append(sd)
            ax.bar(x + (i - 2) * w, means, w, yerr=stds, capsize=2, color=c, label=alab)
        clean, _ = _mu_sd(stats, f"f2_fed_{m}_p0_c")
        ax.axhline(clean, ls="--", color="k", lw=1, label="clean FedAvg")
        ax.set_xticks(x)
        ax.set_xticklabels([t for _, t in atk])
        ax.set_title(f"{lab} — Byzantine update attacks x aggregation")
        ax.set_xlabel("update attack")
    axes[0].set_ylabel("ACC")
    axes[0].legend(fontsize=7)
    fig.suptitle("Server-side robust aggregation under Byzantine updates (n=12, chrono+frozen)", y=1.0)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_byzantine.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_order_and_head(stats: dict) -> None:
    """A3 order-invariance + head-strategy ablation (n=12)."""
    items = [
        ("default order", "e2_labelflip_c"),
        ("alt order", "a3_order_alt_c"),
        ("reverse order", "a3_order_rev_c"),
        ("pre-sized head", "e1_finetune_c"),
        ("growing head", "e1_finetune_gh"),
    ]
    means = [_mu_sd(stats, k)[0] for _, k in items]
    stds = [_mu_sd(stats, k)[1] for _, k in items]
    x = np.arange(len(items))
    colors = ["#4c72b0"] * 3 + ["#c44e52"] * 2
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x, means, yerr=stds, capsize=4, color=colors)
    for i, m in enumerate(means):
        ax.text(i, m + stds[i] + 0.01, f"{m:.3f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([k for k, _ in items])
    ax.set_ylabel("Average accuracy (ACC)")
    ax.set_ylim(0, 0.75)
    ax.set_title("Task-order sensitivity (A3) and head strategy (n=12, chrono+frozen)")
    fig.text(0.01, 0.01, BUFFER_FIG_NOTE, fontsize=6, style="italic")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_order_head.png", dpi=200)
    plt.close(fig)


def fig_cross_dataset(stats: dict) -> None:
    """3-dataset replication of the F2 ranking (CICIDS2017 / UNSW-NB15 / CICIoT2023)."""
    methods = [("finetune", "FineTune"), ("ewc", "EWC"), ("derpp", "DER++")]
    datasets = [("CICIDS2017", ""), ("UNSW-NB15", "u_"), ("CICIoT2023", "i_")]
    budgets = ["p0", "p5"]
    fig, axes = plt.subplots(1, len(datasets), figsize=(12, 4), sharey=True)
    for ax, (dname, pfx) in zip(np.atleast_1d(axes), datasets):
        x = np.arange(len(budgets))
        for i, (m, lab) in enumerate(methods):
            means, stds = [], []
            for b in budgets:
                mu, sd = _mu_sd(stats, f"{pfx}f2_fed_{m}_{b}")
                means.append(mu)
                stds.append(sd)
            ax.errorbar(x + (i - 1) * 0.12, means, yerr=stds, fmt="-o", capsize=3, label=lab)
        ax.set_xticks(x)
        ax.set_xticklabels(["0%", "5%"])
        ax.set_title(dname)
        ax.set_xlabel("poison budget")
    np.atleast_1d(axes)[0].set_ylabel("ACC")
    np.atleast_1d(axes)[0].legend(fontsize=8)
    fig.suptitle("Cross-dataset replication of the federated ranking (n=12)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_cross_dataset.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_architecture(stats: dict) -> None:
    """Architecture sweep: is the finding a property of the CL methods?"""
    methods = [("ft", "FineTune"), ("ewc", "EWC"), ("derpp", "DER++")]
    archs = [("", "MLP-128-64"), ("wide", "MLP-256-128"), ("tr", "Transformer")]
    base = {"ft": "e1_finetune_c", "ewc": "e1_ewc_c", "derpp": "e1_derpp_c"}
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = np.arange(len(methods))
    w = 0.26
    for i, (a, lab) in enumerate(archs):
        means, stds = [], []
        for m, _ in methods:
            key = f"ar_{m}_{a}_clean_c" if a else base[m]
            mu, sd = _mu_sd(stats, key)
            means.append(mu)
            stds.append(sd)
        ax.bar(x + (i - 1) * w, means, w, yerr=stds, capsize=3, label=lab)
    ax.set_xticks(x)
    ax.set_xticklabels([lab for _, lab in methods])
    ax.set_ylabel("ACC (clean)")
    ax.set_title("Architecture robustness of the corrected-protocol ranking (n=12)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_architecture.png", dpi=200)
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
    for fn in (
        fig_protocol_effects,
        fig_federated_corrected,
        fig_byzantine,
        fig_order_and_head,
        fig_cross_dataset,
        fig_architecture,
    ):
        try:
            fn(stats)
        except Exception as e:  # partial grids: skip, never crash the pipeline
            print(f"skip {fn.__name__}: {type(e).__name__}: {e}")
    for p in sorted(FIGS.glob("*.png")):
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
