# Continual Learning for Network Security — Adversarial IDS

Research code for studying attacks on continual intrusion detection, including
single-node learning, simulated federation, and a train-only novelty-discovery
stage. This is an offline simulation, not a deployed intrusion detector.

**Members:** Saneedullah (23I-2568) and Ahmed Bilal (23I-2581).

## Current Phase 3 work (2026-10-24)

**Data amendments and the 16-class taxonomy are now adopted.** Start with the
[Phase 3 reference implementation](docs/phase3-reference/README.md) and
[methodology amendment](submissions/phase3-methodology-amendment.md).
The reference uses the corrected 74-feature profile and a clean development
trajectory. The final GPU grid remains gated.

The authoritative methodology for the current course submission is
[phase2-with-claude.tex](submissions/phase2-with-claude.tex). Begin with the
[Phase 3 implementation and evaluation plan](docs/phase3-plan/START-HERE.md)
and its [source-level implementation gap audit](docs/phase3-plan/implementation-gap-audit.md).
The revised four-stage, five-client protocol has **29 confirmatory contrasts**.
The narrow DR+DC reference is implemented under `src/phase3/`; the full
learner/worker grid and final results remain pending. The legacy commands and
analysis specification below do not implement that protocol.

The earlier audit documents/PDFs preserve the data-only evidence available when
they were written. The separate adoption record selects corrected data for the
current reference; it is not independent external replication. Planning-manifest
counts are not completed experiments.

## Historical implementation status (2026-09-28)

The improvement program is in [docs/plan.md](docs/plan.md), with phase gates
and resumable commands in [docs/roadmap.md](docs/roadmap.md). The working tree
contains uncommitted repair work. The plan's reference commit is `9e635ae`;
current `main` is `a4558b5`.

| Area | Status |
|---|---|
| Result integrity | New runs use completion manifests; version 3 fingerprints the runtime `src/*.py` tree. `results/runs/` has zero manifests and the main aggregate CSVs have zero data rows. Historical runs are executed artifacts, not validated paper evidence. |
| Data | The CICIDS2017 duplicate-disjoint and T0-only v2 task artifacts rebuild bit-identically. The former audits at zero exact train/test content matches. UNSW-NB15 and CICIoT2023 retain 3,723 and 604 cross-pool exact matches and are excluded from final claims. |
| E1/E2/E3 | Six manifest-v2 finetune diagnostic seeds (three per CICIDS sensitivity arm) are exploratory. No 12-seed paired headline is complete. The E3 trigger and eligible ASR calculation were repaired, but packet-to-flow validation and corrected dataset runs remain pending. Prior E3 ASR claims are invalid. |
| E4/E5 | E4 now clusters training candidates only and feeds provisional labels into classifier training. Nine three-arm E4 seeds are exploratory; their source-locked copies are archived after a later code change. T1 detection ranking is weak and the clustering cap changes decisions. Historical E4/E5 claims were invalidated; no corrected paired effect exists. |
| Federation and inference | Per-client accounting and inactive-client exclusion are implemented and synthetically tested. Matched clean aggregator, stable-client, and round controls remain pending. A versioned inference-bundle contract exists, but no trained-bundle benchmark or real federation has been demonstrated. |
| Inference and release | [docs/analysis_spec.json](docs/analysis_spec.json) prespecifies 27 Holm families and 200 pairs. None is complete. Strict lint, dependency pinning, clean reproduction, and manuscript reconciliation remain open. |

See the [claim ledger](docs/claim_ledger.md), [invalidation table](docs/invalidation_table.md),
[task audit](docs/task_audit.md), and [results guide](results/README.md) before
using a number in a report. An undefined ASR or unmeasured FWT is **N/A**,
never zero. The joint model is a future-data oracle. Twelve paired seeds on
one capture estimate seed variation, not performance across network sites.

## Legacy implementation quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python -m ruff check src scripts tests --select E7,E9,F63,F7,F82
python scripts/smoke_test.py
```

The tests and smoke test do not require the full dataset. Raw data and derived
tasks are not committed; see [data/README.md](data/README.md). Configurations
for the audited CICIDS sensitivity arms use
`data/processed/tasks_chrono_dedup.npz` and
`data/processed/tasks_chrono_t0.npz`. Existing task artifacts must be archived
before rebuilding; builders do not overwrite them. The old `make data-primary`
target builds `tasks_chrono.npz`, which is a legacy protocol with known test
exposure, so it is not the current primary evidence path.

For a single seed after its task artifact is available:

```powershell
$env:CL_THREADS = "2"
python -m src.run_experiment --config configs/baselines/e1_finetune_dedup.yaml --seed 1 --results-dir results/diagnostics --resume
```

`--resume` checks the manifest and provenance rather than a summary file's
existence. On the CPU laptop, run one seed at a time. The prepared 12-seed
loops and their prerequisites are in [docs/roadmap.md](docs/roadmap.md); they
have not been launched as a final comparison. Rebuild tables and statistics
only from validated runs:

```powershell
python -m src.run_experiment --rebuild-table --results-dir results
python scripts/stats_summary.py --results-dir results
```

## Project map

| Path | Contents |
|---|---|
| [configs/](configs/) | Experiment configurations and protocol variants |
| [src/](src/) | Data, attacks, continual-learning and federated runners, reporting, and inference contract |
| [scripts/](scripts/) | Audits, experiment orchestration, statistics, and figures |
| [tests/](tests/) | Synthetic and integration checks |
| [docs/](docs/) | Plan, roadmap, methods, audits, claim ledger, and paper drafts |
| [results/](results/) | Manifest-checked run outputs, exploratory diagnostics, and preserved archives |

Git-ignored archives and source snapshots must be included explicitly in a
release bundle; [docs/release_bundle_contents.md](docs/release_bundle_contents.md)
lists them. Figures and historical numeric prose must be regenerated from
compatible validated runs before they can support a new claim.

## Kaggle Phase 3 qualification candidate

The separate [notebook workflow](docs/kaggle-phase3/README.md) prepares private,
hash-verified development inputs, stage caching, a candidate FP32 CUDA backend,
bounded round-checkpoint recovery, output integrity checks and whole-seed
assignments for one to eight distinct contributors. The current CPU grid and its
frozen scientific source are preserved. Actual Kaggle runtime qualification,
complete-worker measurements and selected-setting confirmations remain required;
the twelve final seeds and final-test inference stay sealed.

The [v2 weakness review](docs/kaggle-phase3/review-v2.md) records the crash-recovery
correction, hash-locked environments, streaming evaluation and measured synthetic
memory/target-mapping improvements. Earlier notebook bundles and evidence remain
preserved under `results/kaggle-readiness-v1/`.

The latest [v3 architecture decision](docs/kaggle-phase3/architecture-v3.md)
centralizes job/runtime contracts, checkpoint lineage and receipt validation,
isolates CPU/CUDA backends, and adds pinned CPU qualification CI. The current
notebook delivery is under `results/kaggle-readiness-v3/`; v1/v2 remain preserved.
