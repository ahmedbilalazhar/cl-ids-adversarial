"""Result persistence: per-seed files, master table, rebuild."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from src.paths import REPO_ROOT, find_config


def save_results(result: dict, cfg: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    name = cfg.get("name", "experiment")
    seed = cfg.get("seed", 42)
    R = result["R"]
    with open(out_dir / f"{name}_R_seed{seed}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for row in R:
            w.writerow([f"{v:.6f}" for v in row])
    (out_dir / f"{name}_summary_seed{seed}.json").write_text(json.dumps(result["summary"], indent=2))
    print(json.dumps(result["summary"], indent=2))
    print("R matrix:\n", np.array2string(R, precision=3))


def append_table(result: dict, cfg: dict, out_dir: Path) -> None:
    table = out_dir / "baseline_table.csv"
    header = "name,method,attack,scenario,acc,bwt,fwt,forgetting,asr_mean,seed\n"
    if not table.exists():
        table.write_text(header, encoding="utf-8")
    s = result["summary"]
    atk = s.get("attack")
    if cfg.get("defense"):
        atk = f"{atk}+defense" if atk else "defense"
    row = (
        f"{cfg.get('name')},{s.get('cl_method')},{atk or ''},"
        f"{cfg.get('data', {}).get('scenario')},"
        f"{s['acc']:.6f},{s['bwt']:.6f},{s['fwt']:.6f},{s['forgetting']:.6f},"
        f"{s.get('asr_mean')},{seed if (seed := cfg.get('seed', 42)) else ''}\n"
    )
    with open(table, "a", encoding="utf-8") as f:
        f.write(row)


def rebuild_table(out_dir: Path) -> None:
    rows = []
    seen: set[str] = set()
    # Per-seed summaries live in runs/; also scan out_dir itself so legacy
    # flat layouts rebuild identically.
    candidates = sorted(out_dir.glob("*_summary_seed*.json"))
    runs = out_dir / "runs"
    if runs.is_dir():
        candidates += sorted(runs.glob("*_summary_seed*.json"))
    for p in candidates:
        if p.name in seen:
            continue
        seen.add(p.name)
        s = json.loads(p.read_text())
        name = p.name.replace("_summary_seed", "|").replace(".json", "")
        if "|" in name:
            base, seed = name.rsplit("|", 1)
        else:
            base, seed = name, str(s.get("seed", ""))
        atk = s.get("attack")
        # Defense label: resolve via config (names like f4_fed_* carry defense
        # in the config, not in the filename). Mirrors Gate-D config lookup.
        defended = "defense" in base
        if not defended:
            try:
                _cfg = yaml.safe_load(find_config(base).read_text(encoding="utf-8")) or {}
                defended = bool(_cfg.get("defense"))
            except Exception:
                defended = False
        if defended:
            atk = f"{atk}+defense" if atk else "defense"
        rows.append(
            {
                "name": base,
                "method": s.get("cl_method"),
                "attack": atk or "",
                "scenario": s.get("scenario") or "",
                "acc": f"{s['acc']:.6f}",
                "bwt": f"{s['bwt']:.6f}",
                "fwt": f"{s['fwt']:.6f}",
                "forgetting": f"{s['forgetting']:.6f}",
                "asr_mean": s.get("asr_mean"),
                "seed": s.get("seed", seed),
            }
        )
    fields = ["name", "method", "attack", "scenario", "acc", "bwt", "fwt", "forgetting", "asr_mean", "seed"]
    with open(out_dir / "baseline_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Rebuilt baseline_table.csv with {len(rows)} rows")
