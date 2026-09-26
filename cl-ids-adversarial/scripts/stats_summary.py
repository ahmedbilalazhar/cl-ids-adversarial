from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

# Gate D labeling rules (enforced in code so every phase inherits them):
# 1. Random-mode label-flip ASR is definitionally UNDEFINED, never zero.
ASR_NA_LABEL = "N/A (undefined for random-target mode)"
# 2. ER/DER++ replay buffers inherit stream imbalance; they are NOT class-balanced.
BUFFER_NOTE = "Replay buffer (ER/DER++) uses uniform random eviction and inherits stream class imbalance; NOT class-balanced."

METRICS = ["acc", "bwt", "forgetting", "asr_mean"]
DISC_METRICS = (
    "discovery_miss_rate",
    "fictitious_absorption",
    "poison_novel_rate",
    "absorbed_attack_rate",
    "noise_rate_attack",
    "n_fictitious",
)

# Gate D labeling rules (enforced in code so all future phases inherit them):
#  1. Random-mode label-flip ASR is definitionally UNDEFINED (there is no single
#     target class), never "0". Rendered as ASR_NA_LABEL in every table output.
#  2. ER/DER++ replay buffers use uniform random eviction and inherit stream
#     class imbalance; they are NOT class-balanced. Every summary row for a
#     buffer-based method carries BUFFER_NOTE so no reader infers balanced replay.
ASR_NA_LABEL = "N/A (undefined for random-target mode)"
BUFFER_NOTE = (
    "Replay buffer (ER/DER++) uses uniform random eviction and inherits "
    "stream class imbalance; NOT class-balanced."
)
BUFFER_METHODS = {"er", "derpp"}


def _config_by_name() -> dict[str, dict]:
    """Map config display-name (the `name:` field) -> config dict.

    Filenames and display names differ (e.g. file
    `e2_labelflip_random_05pct.yaml` carries `name: e2_labelflip_random_0.5pct`,
    which is what result files are prefixed with), so lookups by result-group
    name must resolve through this map, not through filenames.
    """
    out: dict[str, dict] = {}
    try:
        import yaml
    except Exception:
        return out
    for p in sorted((ROOT / "configs").glob("*.yaml")):
        try:
            cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if isinstance(cfg.get("name"), str):
            out[cfg["name"]] = cfg
    return out


_CONFIGS: dict[str, dict] | None = None


def _attack_mode(name: str) -> tuple[str | None, str | None]:
    """Return (attack_type, attack_mode) for a result-group name, if known."""
    global _CONFIGS
    if _CONFIGS is None:
        _CONFIGS = _config_by_name()
    atk = (_CONFIGS.get(name) or {}).get("attack") or {}
    return atk.get("type"), atk.get("mode", "targeted")


def _cl_method(name: str) -> str | None:
    global _CONFIGS
    if _CONFIGS is None:
        _CONFIGS = _config_by_name()
    return (_CONFIGS.get(name) or {}).get("cl_method")
WILCOXON_PAIRS = [
    ("e1_lwf", "e1_clean"),
    ("e1_ewc", "e1_clean"),
    ("e1_finetune", "e1_clean"),
    ("e1_derpp", "e1_clean"),
    ("e1_joint", "e1_clean"),
    ("e2_labelflip", "e1_clean"),
    ("e3_backdoor", "e1_clean"),
    ("e4_novelty", "e1_clean"),
    ("e4_novelty_anchor", "e4_novelty_nopois"),
    ("e4_novelty_suppress", "e1_clean"),
    ("e6_defense_smallloss", "e2_labelflip"),
    ("e6_defense_knnconsist", "e2_labelflip"),
    ("a1_buffer_1000", "e2_labelflip"),
    # Phase 2 federated headline: method ranking + poison dose-response per method
    ("f2_fed_ewc_p0", "f2_fed_finetune_p0"),
    ("f2_fed_derpp_p0", "f2_fed_finetune_p0"),
    ("f2_fed_finetune_p5", "f2_fed_finetune_p0"),
    ("f2_fed_finetune_p10", "f2_fed_finetune_p0"),
    ("f2_fed_ewc_p5", "f2_fed_ewc_p0"),
    ("f2_fed_ewc_p10", "f2_fed_ewc_p0"),
    ("f2_fed_derpp_p5", "f2_fed_derpp_p0"),
    ("f2_fed_derpp_p10", "f2_fed_derpp_p0"),
    # Phase 3 centralized-vs-federated ablation (same seeds, clean + poisoned)
    ("f2_fed_finetune_p0", "e1_finetune"),
    ("f2_fed_ewc_p0", "e1_ewc"),
    ("f2_fed_derpp_p0", "e1_derpp"),
    # Phase 4 federated defense (small-loss vs undefended, same method+budget)
    ("f4_fed_finetune_p5_sl", "f2_fed_finetune_p5"),
    ("f4_fed_finetune_p10_sl", "f2_fed_finetune_p10"),
    ("f4_fed_ewc_p5_sl", "f2_fed_ewc_p5"),
    ("f4_fed_ewc_p10_sl", "f2_fed_ewc_p10"),
    ("f4_fed_derpp_p5_sl", "f2_fed_derpp_p5"),
    ("f4_fed_derpp_p10_sl", "f2_fed_derpp_p10"),
    # Matched-memory control: federated DER++ with 100/client (~500 total)
    ("f2_fed_derpp_p0_b100", "f2_fed_derpp_p0"),
    ("f2_fed_derpp_p0_b100", "e1_derpp"),
]


def mean_std(vals: list[float]) -> tuple[float, float]:
    n = len(vals)
    m = sum(vals) / n
    if n < 2:
        return m, 0.0
    var = sum((v - m) ** 2 for v in vals) / (n - 1)
    return m, math.sqrt(var)


def wilcoxon_pair(a: list[float], b: list[float]) -> dict:
    from scipy.stats import wilcoxon

    # align by sorted seed order of caller
    diffs = [x - y for x, y in zip(a, b)]
    if all(d == 0 for d in diffs) or len(diffs) < 1:
        return {"n": len(diffs), "stat": "", "pvalue": ""}
    try:
        res = wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
        return {"n": len(diffs), "stat": float(res.statistic), "pvalue": float(res.pvalue)}
    except ValueError as e:
        return {"n": len(diffs), "stat": "", "pvalue": f"err:{e}"}


def seeds_for(name: str) -> dict[int, dict]:
    out = {}
    for p in sorted(RESULTS.glob(f"{name}_summary_seed*.json")):
        s = json.loads(p.read_text())
        out[int(s.get("seed", -1))] = s
    return out


def main():
    groups: dict[str, list[dict]] = defaultdict(list)
    for p in sorted(RESULTS.glob("*_summary_seed*.json")):
        s = json.loads(p.read_text())
        name = p.name.split("_summary_seed")[0]
        groups[name].append(s)

    rows = []
    for name, items in sorted(groups.items()):
        row: dict = {"name": name, "n_seeds": len(items)}
        atk_type, atk_mode = _attack_mode(name)
        # Gate D rule 1: random-mode label-flip ASR is undefined, never "0".
        asr_undefined = atk_type == "label_flip" and (atk_mode or "targeted") != "targeted"
        # Gate D rule 2: buffer-based methods carry the imbalance note.
        row["replay_note"] = BUFFER_NOTE if _cl_method(name) in BUFFER_METHODS else ""
        for m in METRICS:
            if m == "asr_mean" and asr_undefined:
                row["asr_mean_mean"] = ASR_NA_LABEL
                row["asr_mean_std"] = ASR_NA_LABEL
                continue
            vals = [float(x[m]) for x in items if x.get(m) is not None]
            if not vals:
                row[f"{m}_mean"] = ""
                row[f"{m}_std"] = ""
                continue
            mu, sd = mean_std(vals)
            row[f"{m}_mean"] = f"{mu:.6f}"
            row[f"{m}_std"] = f"{sd:.6f}"
        for m in DISC_METRICS:
            vals = [float(x[m]) for x in items if x.get(m) is not None]
            if not vals:
                vals = [float(x[f"{m}_mean"]) for x in items if x.get(f"{m}_mean") is not None]
            if vals:
                mu, sd = mean_std(vals)
                row[f"{m}_mean"] = f"{mu:.6f}"
                row[f"{m}_std"] = f"{sd:.6f}"
            else:
                row[f"{m}_mean"] = ""
                row[f"{m}_std"] = ""
        seeds = sorted(int(x.get("seed", -1)) for x in items)
        row["seeds"] = ",".join(str(s) for s in seeds)
        rows.append(row)

    out = RESULTS / "stats_summary.csv"
    disc_fields = [f"{m}_{s}" for m in DISC_METRICS for s in ("mean", "std")]
    fields = (
        ["name", "n_seeds", "seeds"]
        + [f"{m}_{s}" for m in METRICS for s in ("mean", "std")]
        + disc_fields
        + ["replay_note"]  # Gate D rule 2: buffer-imbalance note travels with the table
    )
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {out} ({len(rows)} groups)")
    print(f"NOTE (Gate D rule 2): {BUFFER_NOTE}")
    for r in rows:
        extra = ""
        if r.get("discovery_miss_rate_mean"):
            extra = (
                f" miss={r['discovery_miss_rate_mean']}"
                f" absorb={r['fictitious_absorption_mean']}"
                f" poisonN={r['poison_novel_rate_mean']}"
                f" absorbedAtk={r.get('absorbed_attack_rate_mean', '')}"
            )
        print(
            f"{r['name']:32s} n={r['n_seeds']} acc={r['acc_mean']}±{r['acc_std']} "
            f"F={r['forgetting_mean']}±{r['forgetting_std']}{extra}"
        )
    print(f"NOTE (Gate D rule 1): random-mode label-flip ASR is {ASR_NA_LABEL}.")
    print(f"NOTE (Gate D rule 2): {BUFFER_NOTE}")

    # Wilcoxon signed-rank vs paired baseline (common seeds only)
    from scipy.stats import wilcoxon

    wrows = []
    for name, base in WILCOXON_PAIRS:
        a_map, b_map = seeds_for(name), seeds_for(base)
        if not a_map or not b_map:
            continue
        common = sorted(set(a_map) & set(b_map))
        if not common:
            continue
        av = [float(a_map[s]["acc"]) for s in common]
        bv = [float(b_map[s]["acc"]) for s in common]
        if len(common) < 1:
            continue
        try:
            if len(common) == 1 or all(x == y for x, y in zip(av, bv)):
                p, stat = "", ""
            else:
                res = wilcoxon(av, bv)
                p, stat = float(res.pvalue), float(res.statistic)
        except ValueError:
            p, stat = "", ""
        wrows.append(
            {
                "name": name,
                "baseline": base,
                "n": len(common),
                "seeds": ",".join(str(s) for s in common),
                "acc_mean": f"{sum(av)/len(av):.6f}",
                "baseline_acc_mean": f"{sum(bv)/len(bv):.6f}",
                "wilcoxon_stat": stat,
                "pvalue": p,
            }
        )
    wout = RESULTS / "wilcoxon.csv"
    if wrows:
        with open(wout, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(
                f,
                fieldnames=["name", "baseline", "n", "seeds", "acc_mean", "baseline_acc_mean", "wilcoxon_stat", "pvalue"],
            )
            w.writeheader()
            for r in wrows:
                w.writerow(r)
        print(f"wrote {wout}")
        for r in wrows:
            print(
                f"  {r['name']} vs {r['baseline']}: n={r['n']} "
                f"acc {r['acc_mean']} vs {r['baseline_acc_mean']} p={r['pvalue']}"
            )


if __name__ == "__main__":
    main()
