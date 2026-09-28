"""Grid-status helper: per-group/per-config completion vs target seeds."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml

from scripts.groups import GROUPS, seeds_for_group
from src.paths import RESULTS_DIR, find_config
from src.reporting import check_artifact

RES = RESULTS_DIR
RUNS = RES / "runs"


def _config_name(key: str) -> str:
    cfg = yaml.safe_load(find_config(key).read_text(encoding="utf-8"))
    return str(cfg.get("name", key))


def _count_validated(name: str, seeds: list[int]) -> tuple[int, int]:
    """Return (validated, historical unmanifested pairs)."""
    cfg0 = yaml.safe_load(find_config(name).read_text(encoding="utf-8"))
    done = legacy = 0
    for sd in seeds:
        cfg = dict(cfg0, seed=sd)
        hit = check_artifact(RUNS, name, sd, cfg) if RUNS.is_dir() else {"complete": False}
        if not hit["complete"]:
            hit = check_artifact(RES, name, sd, cfg)
        if hit["complete"]:
            done += 1
        elif any((directory / f"{name}_summary_seed{sd}.json").exists()
                 and (directory / f"{name}_R_seed{sd}.csv").exists()
                 for directory in (RUNS, RES)):
            legacy += 1
    return done, legacy


def main() -> None:
    want = sys.argv[1:] or list(GROUPS)
    total_done = total_target = 0
    for g in want:
        names = GROUPS.get(g, [])
        if not names:
            print(f"{g}: UNKNOWN GROUP")
            continue
        seeds = seeds_for_group(g)
        target = len(seeds) * len(names)
        parts = []
        done = legacy_total = 0
        for key in names:
            name = _config_name(key)
            c, legacy = _count_validated(name, seeds)
            done += min(c, len(seeds))
            legacy_total += legacy
            parts.append(f"{key.replace('_c','').replace('_rf','')}={min(c, len(seeds))}")
        total_done += done
        total_target += target
        flag = "DONE" if done >= target else ("part" if done else "TODO")
        print(f"{g:9s} {done:4d}/{target:4d} {flag:4s} (historical pairs {legacy_total}) | " + " ".join(parts))
    print(f"TOTAL {total_done}/{total_target} ({100*total_done/max(1,total_target):.1f}%)")


if __name__ == "__main__":
    main()
