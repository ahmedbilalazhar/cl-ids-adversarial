from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run_cfg(config: str, seed: int | None = None) -> None:
    cmd = [PY, "-m", "src.run_experiment", "--config", f"configs/{config}.yaml"]
    if seed is not None:
        # patch seed via env overlay file is awkward; rewrite config temporarily
        cfg_path = ROOT / "configs" / f"{config}.yaml"
        text = cfg_path.read_text(encoding="utf-8")
        import re

        new_text = re.sub(r"(?m)^seed:\s*\d+", f"seed: {seed}", text)
        cfg_path.write_text(new_text, encoding="utf-8")
    print(f"\n=== {config} seed={seed} ===", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, capture_output=False)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {config} seed={seed}")
    if seed is not None:
        cfg_path = ROOT / "configs" / f"{config}.yaml"
        text = cfg_path.read_text(encoding="utf-8")
        import re

        cfg_path.write_text(re.sub(r"(?m)^seed:\s*\d+", "seed: 42", text), encoding="utf-8")


def main():
    jobs = [
        ("e4_novelty", None),
        ("e4_novelty", 1),
        ("e4_novelty", 2),
        ("e4_novelty_nopois", None),
        ("e4_novelty_nopois", 1),
        ("e4_novelty_nopois", 2),
        ("e4_novelty_suppress", None),
        ("e4_novelty_suppress", 1),
        ("e4_novelty_suppress", 2),
        ("e4_novelty_anchor", 1),
        ("e4_novelty_anchor", 2),
        ("e6_defense_smallloss", None),
        ("e6_defense_smallloss", 1),
        ("e6_defense_smallloss", 2),
    ]
    for name, seed in jobs:
        run_cfg(name, seed)
    print("ALL_DONE")


if __name__ == "__main__":
    main()
