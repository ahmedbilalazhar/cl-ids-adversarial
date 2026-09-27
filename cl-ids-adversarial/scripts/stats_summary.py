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
    # Scaler ablation (Phase 0.4): frozen T0+T1-fit scaler vs per-task scaler,
    # same seeds, same splits, finetune clean.
    ("e1_finetune_frozen", "e1_finetune"),
    # --- Phase-2 chrono+frozen primary suite (_c), random+frozen (_rf) ---
    # scaler effect under random splits (E1 set, locked 7 seeds)
    ("e1_clean_rf", "e1_clean"),
    ("e1_finetune_rf", "e1_finetune"),
    ("e1_ewc_rf", "e1_ewc"),
    ("e1_lwf_rf", "e1_lwf"),
    ("e1_derpp_rf", "e1_derpp"),
    ("e1_joint_rf", "e1_joint"),
    # split effect under frozen scaler (chrono primary vs random secondary)
    ("e1_clean_c", "e1_clean_rf"),
    ("e1_finetune_c", "e1_finetune_rf"),
    ("e1_ewc_c", "e1_ewc_rf"),
    ("e1_lwf_c", "e1_lwf_rf"),
    ("e1_derpp_c", "e1_derpp_rf"),
    # chrono single-node headline + attacks + defences + A2
    ("e1_ewc_c", "e1_clean_c"),
    ("e1_finetune_c", "e1_clean_c"),
    ("e1_derpp_c", "e1_clean_c"),
    ("e1_lwf_c", "e1_clean_c"),
    ("e1_joint_c", "e1_clean_c"),
    ("e2_labelflip_c", "e1_clean_c"),
    ("e3_backdoor_c", "e1_clean_c"),
    ("e4_novelty_c", "e1_clean_c"),
    ("e4_novelty_anchor_c", "e4_novelty_nopois_c"),
    ("e4_novelty_suppress_c", "e1_clean_c"),
    ("e6_defense_smallloss_c", "e2_labelflip_c"),
    ("e6_defense_knnconsist_c", "e2_labelflip_c"),
    ("a2_classil_c", "e1_clean_c"),
    # A1/A3 chrono (order-invariance as first-class result)
    ("a1_buffer_1000_c", "e2_labelflip_c"),
    ("a3_order_alt_c", "e2_labelflip_c"),
    ("a3_order_rev_c", "e2_labelflip_c"),
    # growing-head strategy ablation (single-node finetune clean)
    ("e1_finetune_gh", "e1_finetune_c"),
    # F2 chrono headline: method ranking + dose-response x4 methods (ER: Phase 3)
    ("f2_fed_ewc_p0_c", "f2_fed_finetune_p0_c"),
    ("f2_fed_derpp_p0_c", "f2_fed_finetune_p0_c"),
    ("f2_fed_er_p0_c", "f2_fed_finetune_p0_c"),
    ("f2_fed_finetune_p5_c", "f2_fed_finetune_p0_c"),
    ("f2_fed_finetune_p10_c", "f2_fed_finetune_p0_c"),
    ("f2_fed_ewc_p5_c", "f2_fed_ewc_p0_c"),
    ("f2_fed_ewc_p10_c", "f2_fed_ewc_p0_c"),
    ("f2_fed_derpp_p5_c", "f2_fed_derpp_p0_c"),
    ("f2_fed_derpp_p10_c", "f2_fed_derpp_p0_c"),
    ("f2_fed_er_p5_c", "f2_fed_er_p0_c"),
    ("f2_fed_er_p10_c", "f2_fed_er_p0_c"),
    # Phase-3 centralized-vs-federated ablation, chrono
    ("f2_fed_finetune_p0_c", "e1_finetune_c"),
    ("f2_fed_ewc_p0_c", "e1_ewc_c"),
    ("f2_fed_derpp_p0_c", "e1_derpp_c"),
    ("f2_fed_er_p0_c", "e1_clean_c"),
    # Phase-4 federated defense, chrono
    ("f4_fed_finetune_p5_sl_c", "f2_fed_finetune_p5_c"),
    ("f4_fed_finetune_p10_sl_c", "f2_fed_finetune_p10_c"),
    ("f4_fed_ewc_p5_sl_c", "f2_fed_ewc_p5_c"),
    ("f4_fed_ewc_p10_sl_c", "f2_fed_ewc_p10_c"),
    ("f4_fed_derpp_p5_sl_c", "f2_fed_derpp_p5_c"),
    ("f4_fed_derpp_p10_sl_c", "f2_fed_derpp_p10_c"),
    # --- Phase 3: Byzantine availability (vs clean FedAvg) + per-aggregator recovery ---
    ("bz_ft_sf_fedavg_c", "f2_fed_finetune_p0_c"),
    ("bz_ft_lie_fedavg_c", "f2_fed_finetune_p0_c"),
    ("bz_ft_mr_fedavg_c", "f2_fed_finetune_p0_c"),
    ("bz_ewc_sf_fedavg_c", "f2_fed_ewc_p0_c"),
    ("bz_ewc_lie_fedavg_c", "f2_fed_ewc_p0_c"),
    ("bz_ewc_mr_fedavg_c", "f2_fed_ewc_p0_c"),
    ("bz_ft_lie05_fedavg_c", "f2_fed_finetune_p0_c"),
    ("bz_ewc_lie05_fedavg_c", "f2_fed_ewc_p0_c"),
    ("bz_ft_sf_trim_c", "bz_ft_sf_fedavg_c"),
    ("bz_ft_sf_med_c", "bz_ft_sf_fedavg_c"),
    ("bz_ft_sf_krum_c", "bz_ft_sf_fedavg_c"),
    ("bz_ft_sf_trust_c", "bz_ft_sf_fedavg_c"),
    ("bz_ft_lie_trim_c", "bz_ft_lie_fedavg_c"),
    ("bz_ft_lie_med_c", "bz_ft_lie_fedavg_c"),
    ("bz_ft_lie_krum_c", "bz_ft_lie_fedavg_c"),
    ("bz_ft_lie_trust_c", "bz_ft_lie_fedavg_c"),
    ("bz_ft_mr_trim_c", "bz_ft_mr_fedavg_c"),
    ("bz_ft_mr_med_c", "bz_ft_mr_fedavg_c"),
    ("bz_ft_mr_krum_c", "bz_ft_mr_fedavg_c"),
    ("bz_ft_mr_trust_c", "bz_ft_mr_fedavg_c"),
    ("bz_ewc_sf_trim_c", "bz_ewc_sf_fedavg_c"),
    ("bz_ewc_sf_med_c", "bz_ewc_sf_fedavg_c"),
    ("bz_ewc_sf_krum_c", "bz_ewc_sf_fedavg_c"),
    ("bz_ewc_sf_trust_c", "bz_ewc_sf_fedavg_c"),
    ("bz_ewc_lie_trim_c", "bz_ewc_lie_fedavg_c"),
    ("bz_ewc_lie_med_c", "bz_ewc_lie_fedavg_c"),
    ("bz_ewc_lie_krum_c", "bz_ewc_lie_fedavg_c"),
    ("bz_ewc_lie_trust_c", "bz_ewc_lie_fedavg_c"),
    ("bz_ewc_mr_trim_c", "bz_ewc_mr_fedavg_c"),
    ("bz_ewc_mr_med_c", "bz_ewc_mr_fedavg_c"),
    ("bz_ewc_mr_krum_c", "bz_ewc_mr_fedavg_c"),
    ("bz_ewc_mr_trust_c", "bz_ewc_mr_fedavg_c"),
    ("bz_ft_lie05_trust_c", "bz_ft_lie05_fedavg_c"),
    ("bz_ewc_lie05_trust_c", "bz_ewc_lie05_fedavg_c"),
    # Label-flip p5 x robust aggregators (vs FedAvg p5)
    ("f2r_ft_p5_trim_c", "f2_fed_finetune_p5_c"),
    ("f2r_ft_p5_med_c", "f2_fed_finetune_p5_c"),
    ("f2r_ft_p5_krum_c", "f2_fed_finetune_p5_c"),
    ("f2r_ft_p5_trust_c", "f2_fed_finetune_p5_c"),
    ("f2r_ewc_p5_trim_c", "f2_fed_ewc_p5_c"),
    ("f2r_ewc_p5_med_c", "f2_fed_ewc_p5_c"),
    ("f2r_ewc_p5_krum_c", "f2_fed_ewc_p5_c"),
    ("f2r_ewc_p5_trust_c", "f2_fed_ewc_p5_c"),
    # P1 mechanism: lambda sweep
    ("f2_fed_ewc_p0_l0_c", "f2_fed_ewc_p0_c"),
    ("f2_fed_ewc_p0_l1000_c", "f2_fed_ewc_p0_c"),
    # Breaking point: fraction sweep + budgets past 10%
    ("f2_fed_ft_p5_m2_c", "f2_fed_finetune_p5_c"),
    ("f2_fed_ft_p5_m3_c", "f2_fed_finetune_p5_c"),
    ("f2_fed_ewc_p5_m2_c", "f2_fed_ewc_p5_c"),
    ("f2_fed_ewc_p5_m3_c", "f2_fed_ewc_p5_c"),
    ("f2_fed_ft_p20_c", "f2_fed_finetune_p10_c"),
    ("f2_fed_ft_p40_c", "f2_fed_finetune_p10_c"),
    ("f2_fed_ewc_p40_c", "f2_fed_ewc_p10_c"),
    # Persistent multi-task flip
    ("e2_persist_er_c", "e1_clean_c"),
    ("e2_persist_ft_c", "e1_finetune_c"),
    ("e2_persist_ewc_c", "e1_ewc_c"),
    ("f2_fed_ft_persist_p5_c", "f2_fed_finetune_p5_c"),
    ("f2_fed_ewc_persist_p5_c", "f2_fed_ewc_p5_c"),
    # Adaptive attackers vs their defenses
    ("e2_adaptive_c", "e2_labelflip_c"),
    ("e6_adaptive_sl_c", "e6_defense_smallloss_c"),
    ("e6_knnadapt_knn_c", "e6_defense_knnconsist_c"),
    # Grounded trigger realism comparison
    ("e3_grounded_c", "e3_backdoor_c"),
    # --- Phase 4: UNSW replication (Normal id 7) ---
    ("u_e1_ewc", "u_e1_clean"),
    ("u_e1_finetune", "u_e1_clean"),
    ("u_e1_derpp", "u_e1_clean"),
    ("u_e1_lwf", "u_e1_clean"),
    ("u_e1_joint", "u_e1_clean"),
    ("u_f2_fed_ewc_p0", "u_f2_fed_finetune_p0"),
    ("u_f2_fed_derpp_p0", "u_f2_fed_finetune_p0"),
    ("u_f2_fed_finetune_p1", "u_f2_fed_finetune_p0"),
    ("u_f2_fed_finetune_p5", "u_f2_fed_finetune_p0"),
    ("u_f2_fed_finetune_p10", "u_f2_fed_finetune_p0"),
    ("u_f2_fed_ewc_p5", "u_f2_fed_ewc_p0"),
    ("u_f2_fed_ewc_p10", "u_f2_fed_ewc_p0"),
    ("u_f2_fed_derpp_p5", "u_f2_fed_derpp_p0"),
    ("u_f2_fed_derpp_p10", "u_f2_fed_derpp_p0"),
    ("u_f2_fed_finetune_p0", "u_e1_finetune"),
    ("u_f2_fed_ewc_p0", "u_e1_ewc"),
    ("u_f2_fed_derpp_p0", "u_e1_derpp"),
    ("u_f4_fed_finetune_p5_sl", "u_f2_fed_finetune_p5"),
    ("u_f4_fed_finetune_p10_sl", "u_f2_fed_finetune_p10"),
    ("u_f4_fed_ewc_p5_sl", "u_f2_fed_ewc_p5"),
    ("u_f4_fed_ewc_p10_sl", "u_f2_fed_ewc_p10"),
    ("u_f4_fed_derpp_p5_sl", "u_f2_fed_derpp_p5"),
    ("u_f4_fed_derpp_p10_sl", "u_f2_fed_derpp_p10"),
    # --- Phase 4: IoT replication (Benign id 0) ---
    ("i_e1_ewc", "i_e1_clean"),
    ("i_e1_finetune", "i_e1_clean"),
    ("i_e1_derpp", "i_e1_clean"),
    ("i_e1_lwf", "i_e1_clean"),
    ("i_e1_joint", "i_e1_clean"),
    ("i_f2_fed_ewc_p0", "i_f2_fed_finetune_p0"),
    ("i_f2_fed_derpp_p0", "i_f2_fed_finetune_p0"),
    ("i_f2_fed_finetune_p1", "i_f2_fed_finetune_p0"),
    ("i_f2_fed_finetune_p5", "i_f2_fed_finetune_p0"),
    ("i_f2_fed_finetune_p10", "i_f2_fed_finetune_p0"),
    ("i_f2_fed_ewc_p5", "i_f2_fed_ewc_p0"),
    ("i_f2_fed_ewc_p10", "i_f2_fed_ewc_p0"),
    ("i_f2_fed_derpp_p5", "i_f2_fed_derpp_p0"),
    ("i_f2_fed_derpp_p10", "i_f2_fed_derpp_p0"),
    ("i_f2_fed_finetune_p0", "i_e1_finetune"),
    ("i_f2_fed_ewc_p0", "i_e1_ewc"),
    ("i_f2_fed_derpp_p0", "i_e1_derpp"),
    ("i_f4_fed_finetune_p5_sl", "i_f2_fed_finetune_p5"),
    ("i_f4_fed_finetune_p10_sl", "i_f2_fed_finetune_p10"),
    ("i_f4_fed_ewc_p5_sl", "i_f2_fed_ewc_p5"),
    ("i_f4_fed_ewc_p10_sl", "i_f2_fed_ewc_p10"),
    ("i_f4_fed_derpp_p5_sl", "i_f2_fed_derpp_p5"),
    ("i_f4_fed_derpp_p10_sl", "i_f2_fed_derpp_p10"),
    # Architecture sweep: arch shift on clean + dose within arch
    ("ar_ft_wide_clean_c", "e1_finetune_c"),
    ("ar_ft_tr_clean_c", "e1_finetune_c"),
    ("ar_ewc_wide_clean_c", "e1_ewc_c"),
    ("ar_ewc_tr_clean_c", "e1_ewc_c"),
    ("ar_derpp_wide_clean_c", "e1_derpp_c"),
    ("ar_derpp_tr_clean_c", "e1_derpp_c"),
    ("ar_ft_wide_p5_c", "ar_ft_wide_clean_c"),
    ("ar_ft_tr_p5_c", "ar_ft_tr_clean_c"),
    ("ar_ewc_wide_p5_c", "ar_ewc_wide_clean_c"),
    ("ar_ewc_tr_p5_c", "ar_ewc_tr_clean_c"),
    ("ar_derpp_wide_p5_c", "ar_derpp_wide_clean_c"),
    ("ar_derpp_tr_p5_c", "ar_derpp_tr_clean_c"),
]

# Phase-2 step 10: named Holm families. Pairs absent from this map are
# reported with raw p only (family "unassigned").
WILCOXON_FAMILIES: dict[str, list[tuple[str, str]]] = {
    "e_single_node": [
        ("e1_lwf", "e1_clean"), ("e1_ewc", "e1_clean"),
        ("e1_finetune", "e1_clean"), ("e1_derpp", "e1_clean"),
        ("e1_joint", "e1_clean"), ("e2_labelflip", "e1_clean"),
        ("e3_backdoor", "e1_clean"), ("e4_novelty", "e1_clean"),
        ("e4_novelty_anchor", "e4_novelty_nopois"),
        ("e4_novelty_suppress", "e1_clean"),
        ("e6_defense_smallloss", "e2_labelflip"),
        ("e6_defense_knnconsist", "e2_labelflip"),
    ],
    "f2_headline": [
        ("f2_fed_ewc_p0", "f2_fed_finetune_p0"),
        ("f2_fed_derpp_p0", "f2_fed_finetune_p0"),
        ("f2_fed_finetune_p5", "f2_fed_finetune_p0"),
        ("f2_fed_finetune_p10", "f2_fed_finetune_p0"),
        ("f2_fed_ewc_p5", "f2_fed_ewc_p0"),
        ("f2_fed_ewc_p10", "f2_fed_ewc_p0"),
        ("f2_fed_derpp_p5", "f2_fed_derpp_p0"),
        ("f2_fed_derpp_p10", "f2_fed_derpp_p0"),
    ],
    "fed_ablation": [
        ("f2_fed_finetune_p0", "e1_finetune"),
        ("f2_fed_ewc_p0", "e1_ewc"),
        ("f2_fed_derpp_p0", "e1_derpp"),
    ],
    "f4_defense": [
        ("f4_fed_finetune_p5_sl", "f2_fed_finetune_p5"),
        ("f4_fed_finetune_p10_sl", "f2_fed_finetune_p10"),
        ("f4_fed_ewc_p5_sl", "f2_fed_ewc_p5"),
        ("f4_fed_ewc_p10_sl", "f2_fed_ewc_p10"),
        ("f4_fed_derpp_p5_sl", "f2_fed_derpp_p5"),
        ("f4_fed_derpp_p10_sl", "f2_fed_derpp_p10"),
    ],
    "controls": [
        ("a1_buffer_1000", "e2_labelflip"),
        ("f2_fed_derpp_p0_b100", "f2_fed_derpp_p0"),
        ("f2_fed_derpp_p0_b100", "e1_derpp"),
    ],
    "scaler_effect": [
        ("e1_finetune_frozen", "e1_finetune"),
        ("e1_clean_rf", "e1_clean"), ("e1_finetune_rf", "e1_finetune"),
        ("e1_ewc_rf", "e1_ewc"), ("e1_lwf_rf", "e1_lwf"),
        ("e1_derpp_rf", "e1_derpp"), ("e1_joint_rf", "e1_joint"),
    ],
    "split_effect": [
        ("e1_clean_c", "e1_clean_rf"), ("e1_finetune_c", "e1_finetune_rf"),
        ("e1_ewc_c", "e1_ewc_rf"), ("e1_lwf_c", "e1_lwf_rf"),
        ("e1_derpp_c", "e1_derpp_rf"),
    ],
    "chrono_single": [
        ("e1_ewc_c", "e1_clean_c"), ("e1_finetune_c", "e1_clean_c"),
        ("e1_derpp_c", "e1_clean_c"), ("e1_lwf_c", "e1_clean_c"),
        ("e1_joint_c", "e1_clean_c"), ("e2_labelflip_c", "e1_clean_c"),
        ("e3_backdoor_c", "e1_clean_c"), ("e4_novelty_c", "e1_clean_c"),
        ("e4_novelty_anchor_c", "e4_novelty_nopois_c"),
        ("e4_novelty_suppress_c", "e1_clean_c"),
        ("e6_defense_smallloss_c", "e2_labelflip_c"),
        ("e6_defense_knnconsist_c", "e2_labelflip_c"),
        ("a2_classil_c", "e1_clean_c"),
    ],
    "order_invariance": [
        ("a1_buffer_1000_c", "e2_labelflip_c"),
        ("a3_order_alt_c", "e2_labelflip_c"),
        ("a3_order_rev_c", "e2_labelflip_c"),
    ],
    "head_strategy": [("e1_finetune_gh", "e1_finetune_c")],
    "f2_headline_c": [
        ("f2_fed_ewc_p0_c", "f2_fed_finetune_p0_c"),
        ("f2_fed_derpp_p0_c", "f2_fed_finetune_p0_c"),
        ("f2_fed_er_p0_c", "f2_fed_finetune_p0_c"),
        ("f2_fed_finetune_p5_c", "f2_fed_finetune_p0_c"),
        ("f2_fed_finetune_p10_c", "f2_fed_finetune_p0_c"),
        ("f2_fed_ewc_p5_c", "f2_fed_ewc_p0_c"),
        ("f2_fed_ewc_p10_c", "f2_fed_ewc_p0_c"),
        ("f2_fed_derpp_p5_c", "f2_fed_derpp_p0_c"),
        ("f2_fed_derpp_p10_c", "f2_fed_derpp_p0_c"),
        ("f2_fed_er_p5_c", "f2_fed_er_p0_c"),
        ("f2_fed_er_p10_c", "f2_fed_er_p0_c"),
    ],
    "fed_ablation_c": [
        ("f2_fed_finetune_p0_c", "e1_finetune_c"),
        ("f2_fed_ewc_p0_c", "e1_ewc_c"),
        ("f2_fed_derpp_p0_c", "e1_derpp_c"),
        ("f2_fed_er_p0_c", "e1_clean_c"),
    ],
    "f4_defense_c": [
        ("f4_fed_finetune_p5_sl_c", "f2_fed_finetune_p5_c"),
        ("f4_fed_finetune_p10_sl_c", "f2_fed_finetune_p10_c"),
        ("f4_fed_ewc_p5_sl_c", "f2_fed_ewc_p5_c"),
        ("f4_fed_ewc_p10_sl_c", "f2_fed_ewc_p10_c"),
        ("f4_fed_derpp_p5_sl_c", "f2_fed_derpp_p5_c"),
        ("f4_fed_derpp_p10_sl_c", "f2_fed_derpp_p10_c"),
    ],
    "byzantine_headline": [],  # filled below (34 pairs)
    "adaptive_attack": [
        ("e2_adaptive_c", "e2_labelflip_c"),
        ("e6_adaptive_sl_c", "e6_defense_smallloss_c"),
        ("e6_knnadapt_knn_c", "e6_defense_knnconsist_c"),
    ],
    "robust_defense": [
        ("f2r_ft_p5_trim_c", "f2_fed_finetune_p5_c"),
        ("f2r_ft_p5_med_c", "f2_fed_finetune_p5_c"),
        ("f2r_ft_p5_krum_c", "f2_fed_finetune_p5_c"),
        ("f2r_ft_p5_trust_c", "f2_fed_finetune_p5_c"),
        ("f2r_ewc_p5_trim_c", "f2_fed_ewc_p5_c"),
        ("f2r_ewc_p5_med_c", "f2_fed_ewc_p5_c"),
        ("f2r_ewc_p5_krum_c", "f2_fed_ewc_p5_c"),
        ("f2r_ewc_p5_trust_c", "f2_fed_ewc_p5_c"),
    ],
    "mechanism": [
        ("f2_fed_ewc_p0_l0_c", "f2_fed_ewc_p0_c"),
        ("f2_fed_ewc_p0_l1000_c", "f2_fed_ewc_p0_c"),
    ],
    "breaking_point": [
        ("f2_fed_ft_p5_m2_c", "f2_fed_finetune_p5_c"),
        ("f2_fed_ft_p5_m3_c", "f2_fed_finetune_p5_c"),
        ("f2_fed_ewc_p5_m2_c", "f2_fed_ewc_p5_c"),
        ("f2_fed_ewc_p5_m3_c", "f2_fed_ewc_p5_c"),
        ("f2_fed_ft_p20_c", "f2_fed_finetune_p10_c"),
        ("f2_fed_ft_p40_c", "f2_fed_finetune_p10_c"),
        ("f2_fed_ewc_p40_c", "f2_fed_ewc_p10_c"),
    ],
    "persistent_attack": [
        ("e2_persist_er_c", "e1_clean_c"),
        ("e2_persist_ft_c", "e1_finetune_c"),
        ("e2_persist_ewc_c", "e1_ewc_c"),
        ("f2_fed_ft_persist_p5_c", "f2_fed_finetune_p5_c"),
        ("f2_fed_ewc_persist_p5_c", "f2_fed_ewc_p5_c"),
    ],
    "trigger_realism": [("e3_grounded_c", "e3_backdoor_c")],
    "unsw_single": [
        ("u_e1_ewc", "u_e1_clean"), ("u_e1_finetune", "u_e1_clean"),
        ("u_e1_derpp", "u_e1_clean"), ("u_e1_lwf", "u_e1_clean"),
        ("u_e1_joint", "u_e1_clean"),
    ],
    "unsw_headline": [
        ("u_f2_fed_ewc_p0", "u_f2_fed_finetune_p0"),
        ("u_f2_fed_derpp_p0", "u_f2_fed_finetune_p0"),
        ("u_f2_fed_finetune_p1", "u_f2_fed_finetune_p0"),
        ("u_f2_fed_finetune_p5", "u_f2_fed_finetune_p0"),
        ("u_f2_fed_finetune_p10", "u_f2_fed_finetune_p0"),
        ("u_f2_fed_ewc_p5", "u_f2_fed_ewc_p0"),
        ("u_f2_fed_ewc_p10", "u_f2_fed_ewc_p0"),
        ("u_f2_fed_derpp_p5", "u_f2_fed_derpp_p0"),
        ("u_f2_fed_derpp_p10", "u_f2_fed_derpp_p0"),
        ("u_f2_fed_finetune_p0", "u_e1_finetune"),
        ("u_f2_fed_ewc_p0", "u_e1_ewc"),
        ("u_f2_fed_derpp_p0", "u_e1_derpp"),
    ],
    "unsw_defense": [
        ("u_f4_fed_finetune_p5_sl", "u_f2_fed_finetune_p5"),
        ("u_f4_fed_finetune_p10_sl", "u_f2_fed_finetune_p10"),
        ("u_f4_fed_ewc_p5_sl", "u_f2_fed_ewc_p5"),
        ("u_f4_fed_ewc_p10_sl", "u_f2_fed_ewc_p10"),
        ("u_f4_fed_derpp_p5_sl", "u_f2_fed_derpp_p5"),
        ("u_f4_fed_derpp_p10_sl", "u_f2_fed_derpp_p10"),
    ],
    "iot_single": [
        ("i_e1_ewc", "i_e1_clean"), ("i_e1_finetune", "i_e1_clean"),
        ("i_e1_derpp", "i_e1_clean"), ("i_e1_lwf", "i_e1_clean"),
        ("i_e1_joint", "i_e1_clean"),
    ],
    "iot_headline": [
        ("i_f2_fed_ewc_p0", "i_f2_fed_finetune_p0"),
        ("i_f2_fed_derpp_p0", "i_f2_fed_finetune_p0"),
        ("i_f2_fed_finetune_p1", "i_f2_fed_finetune_p0"),
        ("i_f2_fed_finetune_p5", "i_f2_fed_finetune_p0"),
        ("i_f2_fed_finetune_p10", "i_f2_fed_finetune_p0"),
        ("i_f2_fed_ewc_p5", "i_f2_fed_ewc_p0"),
        ("i_f2_fed_ewc_p10", "i_f2_fed_ewc_p0"),
        ("i_f2_fed_derpp_p5", "i_f2_fed_derpp_p0"),
        ("i_f2_fed_derpp_p10", "i_f2_fed_derpp_p0"),
        ("i_f2_fed_finetune_p0", "i_e1_finetune"),
        ("i_f2_fed_ewc_p0", "i_e1_ewc"),
        ("i_f2_fed_derpp_p0", "i_e1_derpp"),
    ],
    "iot_defense": [
        ("i_f4_fed_finetune_p5_sl", "i_f2_fed_finetune_p5"),
        ("i_f4_fed_finetune_p10_sl", "i_f2_fed_finetune_p10"),
        ("i_f4_fed_ewc_p5_sl", "i_f2_fed_ewc_p5"),
        ("i_f4_fed_ewc_p10_sl", "i_f2_fed_ewc_p10"),
        ("i_f4_fed_derpp_p5_sl", "i_f2_fed_derpp_p5"),
        ("i_f4_fed_derpp_p10_sl", "i_f2_fed_derpp_p10"),
    ],
    "architecture": [
        ("ar_ft_wide_clean_c", "e1_finetune_c"),
        ("ar_ft_tr_clean_c", "e1_finetune_c"),
        ("ar_ewc_wide_clean_c", "e1_ewc_c"),
        ("ar_ewc_tr_clean_c", "e1_ewc_c"),
        ("ar_derpp_wide_clean_c", "e1_derpp_c"),
        ("ar_derpp_tr_clean_c", "e1_derpp_c"),
        ("ar_ft_wide_p5_c", "ar_ft_wide_clean_c"),
        ("ar_ft_tr_p5_c", "ar_ft_tr_clean_c"),
        ("ar_ewc_wide_p5_c", "ar_ewc_wide_clean_c"),
        ("ar_ewc_tr_p5_c", "ar_ewc_tr_clean_c"),
        ("ar_derpp_wide_p5_c", "ar_derpp_wide_clean_c"),
        ("ar_derpp_tr_p5_c", "ar_derpp_tr_clean_c"),
    ],
}
# byzantine_headline: availability drops (vs clean FedAvg) + recoveries (vs FedAvg under attack)
_BZ_M = {"ft": "f2_fed_finetune_p0_c", "ewc": "f2_fed_ewc_p0_c"}
for _m, _base in _BZ_M.items():
    for _a in ["sf", "lie", "mr", "lie05"]:
        if _a == "lie05":
            continue
        WILCOXON_FAMILIES["byzantine_headline"].append((f"bz_{_m}_{_a}_fedavg_c", _base))
WILCOXON_FAMILIES["byzantine_headline"] += [
    ("bz_ft_lie05_fedavg_c", _BZ_M["ft"]),
    ("bz_ewc_lie05_fedavg_c", _BZ_M["ewc"]),
]
for _m in ["ft", "ewc"]:
    for _a in ["sf", "lie", "mr"]:
        for _g in ["trim", "med", "krum", "trust"]:
            WILCOXON_FAMILIES["byzantine_headline"].append(
                (f"bz_{_m}_{_a}_{_g}_c", f"bz_{_m}_{_a}_fedavg_c")
            )
for _m in ["ft", "ewc"]:
    WILCOXON_FAMILIES["byzantine_headline"].append(
        (f"bz_{_m}_lie05_trust_c", f"bz_{_m}_lie05_fedavg_c")
    )
FAMILY_OF = {pair: fam for fam, pairs in WILCOXON_FAMILIES.items() for pair in pairs}


def matched_rank_biserial(a: list[float], b: list[float]) -> float | str:
    """Matched-pairs rank-biserial correlation (Kerby 2014): (T+ - T-) / S.

    T+/T- = Wilcoxon positive/negative rank sums (zeros dropped, average
    ranks for ties, mirroring scipy's zero_method="wilcox"). Returns ""
    when undefined. Positive => a tends above b.
    """
    import numpy as np
    from scipy.stats import rankdata

    diffs = np.asarray([x - y for x, y in zip(a, b)], dtype=float)
    nz = diffs[diffs != 0.0]
    n = len(nz)
    if n == 0:
        return ""
    ranks = rankdata(np.abs(nz), method="average")
    t_pos = float(ranks[nz > 0].sum())
    s = n * (n + 1) / 2.0
    return (2.0 * t_pos - s) / s


def bootstrap_ci(
    vals: list[float], n_boot: int = 10000, ci: float = 0.95, seed: int = 0
) -> tuple[str, str]:
    """Percentile bootstrap CI of the mean. Deterministic (fixed seed)."""
    import numpy as np

    x = np.asarray(vals, dtype=float)
    if len(x) < 2:
        return "", ""
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n_boot, len(x)), replace=True).mean(axis=1)
    lo = float(np.percentile(means, (1.0 - ci) / 2.0 * 100.0))
    hi = float(np.percentile(means, (1.0 + ci) / 2.0 * 100.0))
    return f"{lo:.6f}", f"{hi:.6f}"


def holm_correct(pvals: list[float | str]) -> list[float | str]:
    """Holm-Bonferroni adjusted p-values (order-preserving output)."""
    idx = [i for i, p in enumerate(pvals) if isinstance(p, float)]
    if not idx:
        return list(pvals)
    order = sorted(idx, key=lambda i: pvals[i])
    m = len(order)
    adj: dict[int, float] = {}
    running = 0.0
    for k, i in enumerate(order):
        running = max(running, min(1.0, (m - k) * float(pvals[i])))
        adj[i] = running
    return [adj[i] if i in adj else pvals[i] for i in range(len(pvals))]


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
        # "persistent"/"adaptive"/"knn_adaptive" are targeted-like: defined.
        asr_undefined = atk_type == "label_flip" and (atk_mode or "targeted") not in (
            "targeted",
            "persistent",
            "adaptive",
            "knn_adaptive",
        )
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
        # Bootstrap 95% CI of mean ACC (second, continuous-resolution
        # estimator alongside Wilcoxon — Phase 2 step 9).
        acc_vals = [float(x["acc"]) for x in items if x.get("acc") is not None]
        row["acc_ci_lo"], row["acc_ci_hi"] = bootstrap_ci(acc_vals) if acc_vals else ("", "")
        rows.append(row)

    out = RESULTS / "stats_summary.csv"
    disc_fields = [f"{m}_{s}" for m in DISC_METRICS for s in ("mean", "std")]
    fields = (
        ["name", "n_seeds", "seeds"]
        + [f"{m}_{s}" for m in METRICS for s in ("mean", "std")]
        + ["acc_ci_lo", "acc_ci_hi"]
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

    # Wilcoxon signed-rank vs paired baseline (common seeds only).
    # Phase-2 step 10: raw p + Holm-within-family + matched rank-biserial
    # effect size + bootstrap CI of the paired mean difference. `pvalue`
    # stays the RAW two-sided p (locked rows reproduce exactly).
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
        diffs = [x - y for x, y in zip(av, bv)]
        dlo, dhi = bootstrap_ci(diffs) if len(diffs) > 1 else ("", "")
        wrows.append(
            {
                "name": name,
                "baseline": base,
                "family": FAMILY_OF.get((name, base), "unassigned"),
                "n": len(common),
                "seeds": ",".join(str(s) for s in common),
                "acc_mean": f"{sum(av)/len(av):.6f}",
                "baseline_acc_mean": f"{sum(bv)/len(bv):.6f}",
                "diff_mean": f"{sum(diffs)/len(diffs):.6f}",
                "diff_ci_lo": dlo,
                "diff_ci_hi": dhi,
                "wilcoxon_stat": stat,
                "pvalue": p,
                "effect_r": matched_rank_biserial(av, bv),
                "p_holm": "",
            }
        )
    # Holm correction within each family (over numeric raw p only).
    fam_idx: dict[str, list[int]] = {}
    for i, r in enumerate(wrows):
        fam_idx.setdefault(r["family"], []).append(i)
    for fam, idxs in fam_idx.items():
        adj = holm_correct([wrows[i]["pvalue"] for i in idxs])
        for i, a in zip(idxs, adj):
            wrows[i]["p_holm"] = a
    wout = RESULTS / "wilcoxon.csv"
    if wrows:
        with open(wout, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "name", "baseline", "family", "n", "seeds", "acc_mean",
                    "baseline_acc_mean", "diff_mean", "diff_ci_lo", "diff_ci_hi",
                    "wilcoxon_stat", "pvalue", "effect_r", "p_holm",
                ],
            )
            w.writeheader()
            for r in wrows:
                w.writerow(r)
        print(f"wrote {wout}")
        for r in wrows:
            print(
                f"  {r['name']} vs {r['baseline']}: n={r['n']} "
                f"acc {r['acc_mean']} vs {r['baseline_acc_mean']} p={r['pvalue']} "
                f"p_holm={r['p_holm']} r={r['effect_r']} [{r['family']}]"
            )


if __name__ == "__main__":
    main()
