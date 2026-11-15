# Phase 3 final implementation: poisoning, retention and legitimate adaptation in federated continual intrusion detection

Authors: Saneedullah (23I-2568), Ahmed Bilal (23I-2581). Computer Networks research project.

This folder holds our own Phase 3 implementation, the complete result of its final Kaggle run, and a project brief. The written report is in `../submissions/phase3-report/`.

## Layout
| Path | Content |
|---|---|
| `src/p3lib.py` | The implementation: federated continual learning with five clients, a growing head, learners FT / EI (EWC-style) / DR (DER++), label poisoning by 1 to 5 attackers, admission rules DC / DM / DQ, all metrics |
| `src/p3parallel.py` | Parallel experiment runner (separate worker processes, one result file per run, resumable) |
| `notebooks/phase3-experiments.ipynb` | The notebook that was run on Kaggle (Tesla T4), with its saved outputs. It embeds both code files, so it is self-contained. |
| `results/final-run/part-a-dataset.zip` | Part A: dataset and preprocessing report, per-seed preparation reports |
| `results/final-run/part-b-experiment-runs.zip` | Part B: the 696 run files (one JSON per run) and the run environment |
| `results/final-run/part-c-analysis.zip` | Part C: all tables, figures, statistics and the generated analysis |
| `results/final-run/analysis/` | Part C unpacked (figures as PDF and PNG, tables as CSV, `analysis-and-discussion.md`, `requirement-matrix.md`) |
| `results/final-run/dataset-report/` | Part A unpacked |
| `docs/project-brief.md` | Plain-language description of the whole project (Phases 1-3) |

## How to reproduce
1. Upload `notebooks/phase3-experiments.ipynb` to Kaggle (Internet on, GPU T4 recommended).
2. Run the cells top to bottom. Part A rebuilds the data from the public corrected CICIDS2017 release and verifies every pinned hash; Part B runs the grid (about 2.5 hours on a T4); Part C writes the tables and figures.
3. For a first check set `QUICK = True` in cell B-2 (about 15 minutes), then set it to `False`.

Settings: three ownership partitions (seeds 101-103) x four training replicates = 12 paired units; 696 runs; development bank only.

## Headline results (see the report for details)
- DR retains more earlier-class capability than the FT/EI variants under this protocol. Targeted persistence and final recall damage are now reported separately; use the corrected report for values.
- Attack effects depend on client ownership, within-client corruption, and the learner. A one-client arm is not interchangeable with a five-client arm at a similar total corruption volume.
- At moderate corruption, class-aware random selection is a serious control; at severe corruption all rules show large targeted errors. New-labelled sample retention does not establish successful class acquisition.
- Ablations: the replay-label term and the memory eviction rule decide both retention and how much poison survives.

## Notes
- Final-test rows are excluded. Ownership partitions and training/corruption replicates are not independent captures or sites.
- Original runs use GPU. The new CPU supplement uses CPU-only clean references; device results are kept separate.
- Our DR clean macro-F1 (0.434 on the repository's three partitions) is below the repository's committed value (0.655); this difference is reported, not tuned away.

## Corrected submission analysis

Use `../submissions/phase3-report/phase3-report.pdf` and the corrected CSVs there. The original Part C H is final recall damage, distinct from Phase 2 targeted persistence. Statistical claims in the original generated discussion are superseded by the partition-level exploratory analysis. See that folder README for reproduction and the CPU supplement, exact completion status, and reproduction instructions. New experiment results are used only after validation.

## CPU supplement

Run `python scripts/run_phase3_cpu_study.py` from the repository root. The protocol is `../docs/phase3-cpu-supplement-protocol.md`; results and complete identities are in `../results/phase3-cpu-supplement/`. To regenerate corrected evidence, figures, report and ZIP after completion, run `python scripts/reproduce_phase3_submission.py`. The legacy notebook Part C statistics and metric names are historical evidence, superseded by the corrected analysis.
