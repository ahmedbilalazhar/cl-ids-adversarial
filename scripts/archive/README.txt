# ARCHIVED 2026-09-26 — superseded by scripts/run_grid.py.
# run_remaining.py rewrote configs/*.yaml seed values IN PLACE while looping
# (racy, lossy: only a hardcoded subset of configs/seeds, restores "seed: 42"
# even if the file originally said otherwise). run_grid.py drives the same
# experiments through src.run_experiment.run() with seed passed in-memory and
# skips already-completed (config, seed) pairs. Kept for provenance only.
