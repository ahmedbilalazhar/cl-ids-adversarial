# cl-ids-adversarial

Adversarial evaluation of the novelty-discovery stage in continual-learning intrusion detection.

**Project:** Continual Learning for Network Security · Saneedullah (23I-2568) · Ahmed Bilal (23I-2581)

## Status (2026-09-25)

| Item | State |
|------|--------|
| CICIDS2017 download + clean + CII sequence | done (2.57M rows) |
| E1 baselines 1–6 (incl. Joint/Oracle) | done, n=7 seeds (1–6, 42; ER also 123) |
| E2 label-flip (stream + buffer, 0.5/1/5%) | done — H1 **not** a collapse (drop real but small, p=0.031) |
| E3 backdoor | done — ASR 1.0 all 7 seeds |
| E4 novelty poison + **discovery stage (AE→HDBSCAN)** | done n=7 — nopois + **anchor variant**: miss rate invariant; attack absorption 0 → 0.143 (anchor vs nopois p=0.047) |
| E5 novelty-detector evasion + pollution | done ×3 seeds — 69% of discovered attacks evadable; benign pollution +40pp (`scripts/e5_evasion.py`) |
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

# 2. Download CICIDS2017 into data/raw/ (8 CSVs, see docs/proposal.md)

# 3. Clean + build day-based sequence
python -m src.data.clean --raw data/raw --out data/processed
python -m src.data.sequence --processed data/processed --out data/processed/tasks.npz --scenario cii

# 4. Run experiments (config-driven)
python -m src.run_experiment --config configs/e1_clean.yaml
python -m src.run_experiment --config configs/e1_joint.yaml
python -m src.run_experiment --config configs/e2_labelflip.yaml
python -m src.run_experiment --config configs/e4_novelty.yaml
python -m src.run_experiment --config configs/e4_novelty_nopois.yaml
python -m src.run_experiment --config configs/e4_novelty_anchor.yaml
python -m src.run_experiment --config configs/e6_defense_knnconsist.yaml

# 5. Rebuild tables + stats + Wilcoxon + figures
python -m src.run_experiment --rebuild-table
python scripts/stats_summary.py
python scripts/e7_deployment.py
python scripts/make_figures.py
python scripts/e5_evasion.py          # E5: discovery evasion/pollution (3 seeds via --seed)
```

Every number in the report must be regenerable from a config in `configs/`.

## Datasets

Raw and processed data are **not** committed — they total ~1.7 GB and GitHub rejects files over 100 MB.

- **CIC-IDS-2017** (8 CSVs, ~8.8 GB unzipped) — <https://www.unb.ca/cic/datasets/ids-2017.html>, or fetch automatically:

  ```bash
  python scripts/download_cicids.py          # writes into data/raw/
  python -m src.data.clean --raw data/raw --out data/processed
  python -m src.data.sequence --processed data/processed --out data/processed/tasks.npz --scenario cii
  ```

- Regenerated artifacts in `data/processed*/` (`*.parquet`, `*.npz`) come from the two commands above.
- Everything else in this repo — code, configs, docs, `results/` tables and figures — is versioned.

## Layout

```
docs/          proposal, threat model, search protocol, results overview
configs/       one YAML per experiment (E1–E7, A1–A3)
src/data/      cleaning + day-based task sequence
src/attacks/   label flip, backdoor, novelty poisoning
src/cl/        FineTune, EWC, LwF, ER, DER++, Joint (oracle)
src/defenses/  small-loss purification, kNN label-consistency filter
src/discovery/ AE recon threshold + HDBSCAN discovery metrics (Option 2-A)
src/models/    tabular MLP, autoencoder
src/metrics.py ACC, BWT, FWT, Forgetting, ASR
src/run_experiment.py
scripts/       smoke_test, e7_deployment, stats_summary, download_cicids, run_remaining, e5_evasion, make_figures
results/       baseline_table, stats_summary, wilcoxon, e5_evasion, figures/, per-run R matrices
```

## Reproducibility rule

Fix seeds (≥3), report mean ± std, full task-accuracy matrix, and Wilcoxon signed-rank vs baselines. Never report average accuracy alone.

## Division of labour

| Owner | Experiments |
|-------|-------------|
| Data / protocol / baselines | E1, E2, E7, statistics, cleaning |
| Attacks / defences | E3, E4, E5, E6 |

Both write. Do not split as "one codes, one writes".

