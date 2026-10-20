"""Generate the machine-readable Phase-E analysis specification.

Usage: python scripts/write_analysis_spec.py [--output docs/analysis_spec.json]
Single source of truth for comparison families stays in
scripts/stats_summary.py (WILCOXON_FAMILIES); group/seed protocol stays in
scripts/groups.py. This script only joins them with prespecified endpoints,
primary metrics, minimum important differences, and gate statuses. No result
file is read, so writing the spec cannot peek at outcomes.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml

from scripts.groups import GROUPS, SEEDS7, SEEDS12, SEEDS12_GROUPS
from scripts.stats_summary import WILCOXON_FAMILIES
from src.paths import find_config

PAIRED_SEEDS_12 = list(SEEDS12)
PAIRED_SEEDS_7 = list(SEEDS7)

# Prespecified minimum important differences (absolute ACC unless noted).
# Reviewable placeholders: effects are always reported with bootstrap CIs
# regardless of these gates; these only define what counts as "important".
MID_HEADLINE = 0.02
MID_ABLATION = 0.01


def _display_to_key() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in sorted((ROOT / "configs").rglob("*.yaml")):
        try:
            cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if isinstance(cfg.get("name"), str):
            if cfg["name"] in mapping:
                raise ValueError(f"duplicate config display name: {cfg['name']}")
            mapping[cfg["name"]] = path.stem
    return mapping


def _key_groups() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for group, keys in GROUPS.items():
        for key in keys:
            out.setdefault(key, set()).add(group)
    return out


def _required_seeds(key: str | None, key_groups: dict[str, set[str]], *, who: str) -> tuple[int, list[int]]:
    if key is None:
        raise ValueError(f"comparison references unknown config: {who}")
    groups = key_groups.get(key, set())
    if groups and all(g in SEEDS12_GROUPS for g in groups):
        return 12, list(PAIRED_SEEDS_12)
    return 7, list(PAIRED_SEEDS_7)


def _attack_of(display: str) -> dict:
    try:
        cfg = yaml.safe_load(find_config(display).read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return cfg.get("attack") or {}


def _primary_metric(display: str) -> tuple[str, str]:
    attack = _attack_of(display)
    kind = attack.get("type")
    if kind is None:
        return "acc", "no attack: final accuracy"
    if kind == "label_flip":
        if (attack.get("mode", "targeted")) in ("targeted", "persistent", "adaptive", "knn_adaptive"):
            return "targeted_asr", "targeted flip success on eligible test class + acc"
        return "acc", "random-target flip: ASR undefined, accuracy only"
    if kind == "backdoor":
        return "asr_with_denominator", "trigger success over eligible non-target attack examples"
    if kind == "novelty":
        return "discovery_set", "miss rate, absorption (both denominators), benign alert + acc"
    return "acc", "fallback"


def _gate(family: str, name: str, baseline: str) -> str:
    if family == "trigger_realism" or name == "e3_grounded_c":
        return "gated-extractor"
    if name == "a3_order_rev_c":
        return "gated-rev-rebuild"
    if family.startswith(("unsw_", "iot_")) or name[:2] in ("u_", "i_"):
        return "gated-dedup"
    if family in ("byzantine_headline", "robust_defense"):
        return "gated-controls"
    if name.startswith("e4_") or baseline.startswith("e4_"):
        return "gated-detector"
    return "ready-pending-runs"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="docs/analysis_spec.json")
    args = ap.parse_args()
    display_to_key = _display_to_key()
    key_groups = _key_groups()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()

    families = []
    n_pairs = 0
    for family, pairs in WILCOXON_FAMILIES.items():
        members = []
        for name, baseline in pairs:
            _, seeds = _required_seeds(display_to_key.get(name), key_groups,
                                           who=f"{family}:{name}")
            _, seeds_base = _required_seeds(display_to_key.get(baseline), key_groups,
                                            who=f"{family}:{baseline}")
            common = sorted(set(seeds) & set(seeds_base))
            metric, why = _primary_metric(name)
            mid = MID_ABLATION if family in ("mechanism", "head_strategy", "controls") else MID_HEADLINE
            members.append({
                "name": name, "baseline": baseline,
                "required_seeds": common, "n_required": len(common),
                "primary_metric": metric, "primary_metric_why": why,
                "secondary_endpoints": ["acc", "forgetting", "per_task_R",
                                        "benign_false_positive_rate", "family_recall",
                                        "asr_with_denominator", "realized_dose"],
                "mid_absolute_acc": mid, "test": "two-sided Wilcoxon signed-rank",
                "direction": "two-sided",
                "gate": _gate(family, name, baseline),
            })
            n_pairs += 1
        families.append({"family": family, "correction": "Holm-within-family",
                         "n_pairs": len(members), "status": "pending-runs",
                         "members": members})

    spec = {
        "version": 1, "status": "prespecified-pending-runs",
        "created_utc": datetime.now(UTC).isoformat(), "source_commit": commit,
        "protocol": {
            "paired_seeds_12": PAIRED_SEEDS_12, "paired_seeds_7": PAIRED_SEEDS_7,
            "devices": ["cpu", "cuda"], "threads": "CL_THREADS=2",
            "manifest_version": 3, "code_hash_locked": False,
            "pairing_rule": "seeds must be identical on both arms; report paired differences with interval and effect size",
        },
        "rules": [
            "Two-sided tests only; no directional claim was prespecified.",
            "Holm correction within each family; pairs outside families report raw p only.",
            "Never infer immune, equivalent, or no-effect from a nonsignificant test.",
            "Equivalence requires a prespecified margin; none is defined, so no equivalence claim is licensed.",
            "Undefined endpoints (random-target ASR, absent-class ASR, unmeasured FWT) are N/A, never 0.",
            "Replay buffers are unbalanced by protocol; the imbalance note travels with every buffer-method row.",
            "12-seed chrono families are primary; legacy random/per-task families are secondary.",
        ],
        "endpoints": {
            "acc": "final average accuracy from validated R matrices",
            "forgetting": "validated forgetting",
            "per_task_R": "full accuracy matrix per seed",
            "benign_false_positive_rate": "benign test rows predicted non-benign",
            "family_recall": "per attack-family recall on held-out test",
            "asr_with_denominator": "eligible count, successes, clean targeted error rate",
            "realized_dose": "actual changed/eligible/retained counts, not configured budget",
            "fwt": "null unless a measured pretraining baseline exists",
        },
        "n_families": len(families), "n_pairs": n_pairs, "families": families,
        "amendments": [],
    }
    out = ROOT / args.output
    out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    gates: dict[str, int] = {}
    for fam in families:
        for m in fam["members"]:
            gates[m["gate"]] = gates.get(m["gate"], 0) + 1
    print(f"wrote {out}: {len(families)} families, {n_pairs} pairs, gates={gates}")


if __name__ == "__main__":
    main()
