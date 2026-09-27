# MOVED — do not use

On 2026-09-27 this subdirectory was promoted to the repository root
(industry-standard single-root layout).

- Code now lives in `../src/`, `../scripts/`, `../configs/`
- Docs in `../docs/` (+ `../docs/papers/`, `../reports/`)
- Data in `../data/`, results in `../results/`

This folder is kept temporarily because live grid workers (started before the
move) are still writing `results/run_groups.log` here. Once they finish:

1. Copy any new `results/*_R_seed*.csv` / `*_summary_seed*.json` to `../results/`
2. Rebuild tables from the repo root
3. Delete this directory

Run everything from the repo root from now on.
