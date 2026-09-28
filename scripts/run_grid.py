"""Grid driver: run one group at its configured 7- or 12-seed protocol.
Only manifest-validated seeds are skipped; legacy files require archival.
Usage: python scripts/run_grid.py <group>  (groups: e1, e2e3, e4, e6a2,
  f2_ft, f2_ewc, f2_derpp). f2_* groups run the federated wrapper
  (src/federated/fedavg.py); all others run single-node src/runner.py.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import time

import yaml

from scripts.groups import FED_GROUPS, GROUPS, seeds_for_group
from src.config_validation import validate_config
from src.paths import RUNS_DIR, find_config
from src.reporting import check_artifact
from src.run_experiment import execute_config


def main() -> None:
    group = sys.argv[1]

    seeds = seeds_for_group(group)
    done, skipped = 0, 0
    t0 = time.time()
    configs = []
    for key in GROUPS[group]:
        cfg = yaml.safe_load(find_config(key).read_text(encoding="utf-8"))
        validate_config(cfg, expected_runner="federated" if group in FED_GROUPS else "single-node")
        configs.append((key, cfg))
    for key, cfg in configs:
        name = cfg.get("name", key)
        for sd in seeds:
            cfg_seed = dict(cfg, seed=sd)
            if check_artifact(RUNS_DIR, name, sd, cfg_seed)["complete"]:
                skipped += 1
                continue
            r = execute_config(cfg_seed, RUNS_DIR, resume=True)
            if r is None:
                skipped += 1
                continue
            done += 1
            print(
                f"DONE {name} seed {sd} acc={r['summary']['acc']:.4f} "
                f"wall={r['summary']['wall_sec']:.0f}s",
                flush=True,
            )
    print(f"group {group}: ran {done}, skipped {skipped}, elapsed {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
