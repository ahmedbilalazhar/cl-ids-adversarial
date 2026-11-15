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

Settings: three ownership partitions (seeds 101-103, the only development seeds the repository allows) x four training replicates = 12 paired units; 696 runs; development bank only.

## Headline results (see the report for details)
- Replay (DR) is the only learner that retains earlier attack families (clean macro-F1 0.49 against 0.03-0.05 for FT and EI), but it also keeps poisoned knowledge after the attacker withdraws (persistent damage 0.79 at 50% poisoning, 0.99 at 90%).
- A single attacker among five clients is diluted by federated averaging.
- None of the tested admission rules reduced persistent damage. The class-aware quota kept all new-class rows (the global filter kept 9.5% under the strongest attack), but ranking by loss inside the quota lowered acquisition and macro-F1.
- Ablations: the replay-label term and the memory eviction rule decide both retention and how much poison survives.

## Notes
- No final-test data were read; seeds 104 and above stay sealed for the final evaluation.
- CPU and GPU runs are not bit-identical; all reported runs used the GPU.
- Our DR clean macro-F1 (0.434 on the repository's three partitions) is below the repository's committed value (0.655); this difference is reported, not tuned away.
