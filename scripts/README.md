# Scripts

All scripts resolve paths from their own location (`ROOT = Path(__file__).parents[1]`),
so run them from the repo root.

## Orchestration

| Script | Purpose |
|--------|---------|
| `run_grid.py <group>` | run one GROUPS entry, skipping finished (config, seed) pairs — safe to re-run |
| `run_groups.py <g…>` | chain groups unattended with per-group logging to `results/run_groups.log` |
| `reproduce.sh <group>` | one-command reproduction: grid → rebuild table → stats → figures |
| `grid_status.py` | authoritative per-group completion count |
| `smoke_test.py` | harness check on synthetic data (no dataset needed) — run first |

## Analysis (write into `results/`)

| Script | Purpose |
|--------|---------|
| `stats_summary.py` | aggregate tables → `stats_summary.csv` + `wilcoxon.csv` (Holm/bootstrap/effects) |
| `make_figures.py` | regenerate `results/figures/` |
| `e5_evasion.py` | E5 discovery-evasion / pollution (per-seed via `--seed`) |
| `e7_deployment.py` / `e8_deployment.py` | latency + peak-RSS tables (real device optional) |

## Data & utilities

| Script | Purpose |
|--------|---------|
| `download_cicids.py` | fetch CIC-IDS-2017 into `data/raw/` |
| `gen_grounded_trigger.py` | grounded backdoor trigger generator (E3) |
| `import_architecture_gpu.py` | import Colab-GPU architecture results (validates manifest + digests) |
| `prepare_colab_architecture.py` | build the Colab upload bundle in `artifacts/` |
| `archive/` | superseded helpers, kept for provenance (see `archive/README.txt`) |

Threading contract: `CL_THREADS=2` (plus `OMP/MKL/OPENBLAS_NUM_THREADS`) must be set
before any run — float reduction order depends on it (see `docs/decisions_log.md` #52).
