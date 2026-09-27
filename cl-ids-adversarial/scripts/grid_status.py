"""Grid-status helper: per-group/per-config completion vs target seeds."""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml  # noqa: E402

RES = ROOT / "results"
GCONF = ROOT / "configs"

# Read GROUPS/SEEDS from run_grid.py without executing its main body.
_rg = (ROOT / "scripts" / "run_grid.py").read_text(encoding="utf-8")
_ns: dict = {"__file__": str(ROOT / "scripts" / "run_grid.py"), "__name__": "run_grid_meta"}
exec(compile(_rg.split("group = sys.argv[1]")[0], "run_grid", "exec"), _ns)
GROUPS = _ns["GROUPS"]
SEEDS7 = _ns["SEEDS7"]
SEEDS12 = _ns["SEEDS12"]
SEEDS12_GROUPS = _ns["SEEDS12_GROUPS"]

cnt = collections.Counter(p.name.split("_summary_seed")[0] for p in RES.glob("*_summary_seed*.json"))


def main() -> None:
    want = sys.argv[1:] or list(GROUPS)
    total_done = total_target = 0
    for g in want:
        names = GROUPS.get(g, [])
        if not names:
            print(f"{g}: UNKNOWN GROUP")
            continue
        target_seeds = len(SEEDS12 if g in SEEDS12_GROUPS else SEEDS7)
        done = sum(min(cnt[n], target_seeds) for n in names)
        target = target_seeds * len(names)
        total_done += done
        total_target += target
        flag = "DONE" if done >= target else ("part" if done else "TODO")
        print(f"{g:9s} {done:4d}/{target:4d} {flag:4s} | " + " ".join(
            f"{n.replace('_c','').replace('_rf','')}={min(cnt[n], target_seeds)}" for n in names))
    print(f"TOTAL {total_done}/{total_target} ({100*total_done/max(1,total_target):.1f}%)")


if __name__ == "__main__":
    main()
