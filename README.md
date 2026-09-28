# Continual Learning for Network Security — Adversarial IDS

> **Repair status, 2026-09-28:** Historical per-seed files are executed
> artifacts, not manifest-validated results. The main aggregate CSVs currently
> contain headers only; do not cite older numerical claims or figures as
> current evidence. Six validated seeds in `results/diagnostics/` exercise
> the duplicate-disjoint and T0-only CICIDS sensitivity arms (three each),
> not a final paired comparison.
> Historical E4/E5 discovery outputs were archived on 2026-09-28 because
> held-out flows affected clustering and clusters never affected classifier
> training. FWT in new summaries is unavailable until measured.
> UNSW-NB15 and CICIoT2023 task artifacts retain exact cross-pool content
> matches (3,723 and 604). They are excluded from final claims until a
> duplicate-disjoint correction and paired rerun are complete.
> See `docs/inventory.md`, `docs/invalidation_table.md`, and
> `docs/task_audit.md` and `docs/cicids_cross_file_audit.md`. This is an
> offline simulation, not a deployed IDS.

Adversarial evaluation of the novelty-discovery stage in continual-learning
intrusion detection (CIC-IDS-2017, day-based CII sequence).

| | |
|---|---|
| **Members** | Saneedullah (23I-2568) · Ahmed Bilal (23I-2581) |
| **Status** | See Status table below (2026-09-25) |
| **Write-ups** | [`docs/`](docs/) — proposal, threat model, results overview · [`docs/papers/`](docs/papers/) — papers 1–3 · [`reports/`](reports/) — literature review & phase documents |
| **Results** | [`results/`](results/) — tables, Wilcoxon stats, figures |

## Status (2026-09-25)

| Item | State |
|------|--------|
| CICIDS2017 download + clean + CII sequence | done (2.57M rows) |
| E1 baselines 1–6 (incl. Joint/Oracle) | done, n=7 seeds (1–6, 42; ER also 123) |
| E2 label-flip (stream + buffer, 0.5/1/5%) | done — H1 **not** a collapse (drop real but small, p=0.031) |
| E3 backdoor | prior ASR claim invalidated; 38 legacy seed files archived; corrected trigger/ASR implementation needs reruns |
| E4 novelty poison + **discovery stage (AE→HDBSCAN)** | train-only causal pipeline implemented; synthetic checks in progress; historical outputs archived; corrected numerical comparison pending |
| E5 novelty-detector evasion + pollution | historical JSONs archived; rerun under the revised discovery protocol pending |
| E6 small-loss defence | done n=7 — ACC 0.367 vs 0.317 undefended (**p=0.016**) |
| E6b kNN-consistency defence (H3) | done n=7 — ACC 0.278, **p=0.047 worse** than undefended; Heartbleed/Infiltration retention **0%** even clean |
| A1–A3 ablations | done (3 seeds each) |
| E7 latency/RSS (CPU) | done — real device optional |
| Wilcoxon vs baselines | done (`results/wilcoxon.csv`) — **9 comparisons significant at n=7** (min p=0.0156) |
| Search protocol table | filled 2026-09-24 |
| **Full results write-up** | see `docs/results_overview.md` |

## Scope

| Role | Gap |
|------|-----|
| Primary | Gap 2 — attack the open-world discovery stage (autoencoder → clustering → CIL), Option 2-A; secondary Option 2-B (federated aggregation) |
| Carrier | Gap 1 — CICIDS2017, day-based task sequence, CII scenario |
| Bonus | Gap 3 — one latency + peak-memory table on one real device |

Headline: an attacker influences *what the continual IDS decides to learn*, not only what it predicts.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1. Prove the harness (no dataset needed)
python scripts/smoke_test.py

# 2. Download CICIDS2017 into data/raw/ (8 CSVs, see data/README.md)

# 3. Build the primary per-class capture-order/offline-init task sequence.
# Existing task artifacts must first be archived; builders never overwrite them.
make data-primary

# 4. Run experiments (config-driven; bare names also work: --config e1_clean)
python -m src.run_experiment --config configs/baselines/e1_clean.yaml
python -m src.run_experiment --config configs/baselines/e1_joint.yaml
python -m src.run_experiment --config configs/label_flip/e2_labelflip.yaml
python -m src.run_experiment --config configs/novelty/e4_novelty.yaml
python -m src.run_experiment --config configs/novelty/e4_novelty_nopois.yaml
python -m src.run_experiment --config configs/novelty/e4_novelty_anchor.yaml
python -m src.run_experiment --config configs/defenses/e6_defense_knnconsist.yaml

# 5. Rebuild tables + stats + Wilcoxon + figures
python -m src.run_experiment --rebuild-table
python scripts/stats_summary.py
python scripts/e7_deployment.py
python scripts/make_figures.py
python scripts/e5_evasion.py          # E5: discovery evasion/pollution (3 seeds via --seed)
```

Or via Make: `make smoke`, `make data`, `make tables`, `make figures`, `make test`.
Every number in the report must be regenerable from a config in `configs/`.
`make data` is the legacy random/per-task protocol, not the primary build.
The primary T0+T1 scaler sees T1 training rows before T0 training (offline
initialization). `tasks_chrono_t0.npz` is the strictly future-blind T0-only
sensitivity arm.

## Datasets

Raw and processed data are **not** committed — see [`data/README.md`](data/README.md).

- **CIC-IDS-2017** (8 CSVs, ~8.8 GB unzipped) — <https://www.unb.ca/cic/datasets/ids-2017.html>, or fetch automatically:

  ```bash
  python scripts/download_cicids.py          # writes into data/raw/
  python -m src.data.clean --raw data/raw --out data/processed
  python -m src.data.sequence --processed data/processed/cicids2017_clean.parquet --out data/processed/tasks_chrono.npz --scenario cii --split chrono --scaler frozen
  ```

## Layout

```
configs/       one YAML per experiment, grouped by family (see configs/README.md)
src/
  data/        cleaning + day-based task sequence (+ UNSW-NB15 / IoT mirrors)
  attacks/     label flip, backdoor, novelty poisoning, Byzantine
  cl/          FineTune, EWC, LwF, ER, DER++, Joint (oracle)
  defenses/    small-loss purification, kNN label-consistency filter
  discovery/   AE recon threshold + HDBSCAN discovery metrics (Option 2-A)
  federated/   FedAvg + robust aggregators (Krum, median, trimmed-mean)
  models/      tabular MLP, autoencoder, tabular transformer
  metrics.py   ACC, BWT, FWT, Forgetting, ASR
  methods.py   CL-method registry · tasks.py task loading · paths.py path helpers
  runner.py    training loop · reporting.py tables · run_experiment.py CLI
scripts/       smoke_test, run_grid/run_groups, stats_summary, make_figures,
               e5_evasion, e7/e8_deployment, download_cicids, reproduce.sh
               (see scripts/README.md)
notebooks/     architecture_colab.ipynb (+ artifacts bundle)
docs/          proposal, threat model, search protocol, results overview,
               decisions log, handover, papers/ (paper-1..3)
reports/       literature/ + phases/ (university phase documents)
data/          raw / processed / external (see data/README.md, not committed)
results/       baseline_table, stats_summary, wilcoxon, e5_evasion,
               figures/, per-run R matrices, _archive/prefix0 (invalid, kept for provenance)
tests/         pytest regression suite (no dataset needed)
models/        checkpoints (gitignored, .gitkeep skeleton)
```

## Reproducibility rule

Fix seeds (≥3), report mean ± std, full task-accuracy matrix, and Wilcoxon signed-rank vs baselines. Never report average accuracy alone.

```bash
bash scripts/reproduce.sh <group>   # one-command reproduction per group
```

Pinned CPU environment: see `Dockerfile` (`CL_THREADS=2` thread pinning).

## Division of labour

| Owner | Experiments |
|-------|-------------|
| Data / protocol / baselines | E1, E2, E7, statistics, cleaning |
| Attacks / defences | E3, E4, E5, E6 |

Both write. Do not split as "one codes, one writes".
