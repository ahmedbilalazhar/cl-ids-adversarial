"""Launch the fixed six-seed DC replay eviction development study."""
from pathlib import Path
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUTPUT = ROOT / 'results/phase3-dc-eviction-six-seed-v1'
os.environ['PHASE3_STUDY_OUT'] = str(OUTPUT)

from scripts import run_phase3_eviction_parallel as engine


def main():
    engine.SEEDS = (1, 2, 3, 4, 5, 6)
    freeze_files = (Path(__file__), ROOT / 'docs/phase3-six-hour-extension.md')
    runtime_deadline = time.monotonic() + 5.25 * 3600
    original_block = engine.run_block

    def run_bounded(pool, configs):
        # Complete all four treatments for a seed before starting the next.
        rows = []
        for seed in engine.SEEDS:
            group = [cfg for cfg in configs if cfg.seed == seed]
            pending = [cfg for cfg in group if not (OUTPUT / 'runs' / engine.name(cfg) / 'result.json').exists()]
            per_run = max(450, max((row['elapsed_seconds'] for row in rows), default=0) * 1.2)
            if time.monotonic() + per_run * len(pending) > runtime_deadline:
                raise RuntimeError(f'Budget stop before seed {seed}. Completed trajectories remain available for resume.')
            rows.extend(original_block(pool, group))
        return rows

    original_identity = engine.identity

    def bind_execution(value):
        if 'source' in value and 'inputs' in value:
            value['source'].update({p.relative_to(ROOT).as_posix(): engine.digest(p) for p in freeze_files})
        return original_identity(value)

    engine.identity = bind_execution
    engine.run_block = run_bounded
    sys.argv = [str(Path(__file__)), '--eviction-only', '--eviction-admission', 'DC', '--hours', '5.25']
    with engine.execution_lock():
        engine.main()


if __name__ == '__main__':
    main()
