#!/usr/bin/env bash
# One-command reproduction for every table and figure (Phase-6 step 24).
# Usage: bash scripts/reproduce.sh <group>   (then vgl. groups below)
#   - runs the grid group (skips finished seeds: safe to re-run / resume
#     after free-tier disconnects),
#   - rebuilds baseline_table.csv, regenerates stats_summary.csv +
#     wilcoxon.csv (families/Holm/bootstrap/effects), remakes figures.
# Full paper: run groups c_e1 rf_e1 gh c_e2e3 c_e4 c_e6a2 c_a1 c_a3 c_f2 c_f4
#   bz f2r mech brk perst_sn perst_fed adapt trig ar (in this order; federated
#   groups dominate wall time). Task files required: data/processed/
#   tasks_chrono{,_alt,_rev}.npz, tasks_frozen.npz, tasks_unsw.npz,
#   tasks_iot.npz (builders: src/data/sequence.py --split chrono --scaler
#   frozen; src/data/unsw.py; src/data/iot.py).
set -euo pipefail
cd "$(dirname "$0")/.."
# Thread pinning is part of the reproduction contract (decisions_log.md #52):
# float reduction order depends on the thread count, so results are
# bit-reproducible only at this setting.
export CL_THREADS="${CL_THREADS:-2}"
export OMP_NUM_THREADS="$CL_THREADS" MKL_NUM_THREADS="$CL_THREADS"
export OPENBLAS_NUM_THREADS="$CL_THREADS" NUMEXPR_NUM_THREADS="$CL_THREADS"
GROUP="${1:?usage: reproduce.sh <group>}"
python scripts/run_grid.py "$GROUP"
python -m src.run_experiment --rebuild-table
python scripts/stats_summary.py
python scripts/make_figures.py
echo "reproduced group $GROUP: results/baseline_table.csv, stats_summary.csv, wilcoxon.csv, results/figures/"
