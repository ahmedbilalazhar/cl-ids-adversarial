# Phase 3 submission and reproduction

**Audited revision (16 November 2026):** the current audited report is
`../phase3-audited-report/phase3-report.pdf`, with editable TeX and vector figures
beside it. Read `../../docs/phase3-rigorous-audit-v1/README.md` for the reliability
assessment, corrected experiment counts, patches, checks and remaining gates.
The updated roll-number ZIP opens with that report. The variants and reproduction
instructions below are retained as historical context and do not supersede the
audited revision or restore the original confirmatory claims.

Start with `phase3-report-updated.pdf`; editable source is `phase3-report.tex` (the reproducible narrative source is `report.md`). The report distinguishes the original 696 GPU trajectories from the new CPU supplement. Both use development data; no final-test evaluation is claimed.

## Rebuild the evidence and report

From the repository root, with the observed dependencies available:

    python scripts/reproduce_phase3_submission.py

This verifies archived GPU hashes, recomputes eligible-bank metrics, validates the completed CPU run ledger and intervention parity, regenerates figures/tables, writes the report, exports native LaTeX, compiles/renders the PDF, and rebuilds the ZIP. Pandoc and Tectonic must be installed for this export; the self-contained Overleaf source uses XeLaTeX and needs no external .bib file. It does not train models unless `--train` is supplied.

## Execute or resume CPU training

    python scripts/run_phase3_cpu_study.py

Prepared clean packages are read from `data/processed/phase3-cpu-v2/s101-p000/train` (and s102/s103); the development bank is `data/processed/phase3-reference74-v1/development`. The runner checks pinned training file hashes and role support. It uses CPU, one worker, one PyTorch thread and 12 rounds per stage.

The required 21 trajectories consist of 12 clean/ordinary/oracle/random mechanism trajectories, six DQ clean/poisoned trajectories, and three offline pooled references. If the measured conservative estimate fits the 3.25-hour compute deadline, the mechanism grid expands by 36 trajectories across training replicates 1-3. `--required-only` disables expansion. Completed files are atomically written and reused only if the complete source/input/configuration/runtime identity matches. Changing scientific code requires a new output directory, supplied using `--output`. Resume is at whole-trajectory boundaries.

Outputs and runtime/source/input identities live under `results/phase3-cpu-supplement/`. The exact executed count and validation status are in `completion.json` and `cpu-validation.json`. `docs/phase3-cpu-supplement-protocol.md` specifies the intervention and interpretation limits.

## Data reconstruction

Large prepared arrays and the raw public capture are not duplicated in the submission ZIP. The original self-contained `phase3-implementation/notebooks/phase3-experiments.ipynb`, Part A, records the raw URL, expected bytes, dataset SHA-256, preprocessing steps and pinned preparation checks. Its baseline repository commit is 571b5f8; use that exact revision in an isolated reconstruction checkout rather than following a moving main branch. The original notebook's clone cell only warns on a different commit, so explicitly check out and verify 571b5f8 before reconstruction. The ZIP also includes the preparation source and adopted protocol metadata.

After the reference package is built, rebuild local clean supplied-label packages with:

    python -m src.phase3_v2.prepare --output data/processed/phase3-cpu-v2/s101-p000 --seed 101 --dose 0 1

Repeat for seeds 102 and 103 using matching output names. Preparation can overwrite outputs; reconstruct in a separate checkout and compare hashes before using a new package. The supplement identity lists the exact accepted training/development array hashes. Source-release and preparation environment versions differ from training and are recorded by the original notebook.

## Interpretation and files

- `corrected-runs.csv`: 696 GPU trajectories with corrected targeted persistence and eligible-bank metrics.
- `metric-population-audit.csv`: original versus corrected F1 populations and unsupported row counts.
- `eligible-family-metrics.csv`: supported eligible-family precision, recall, F1, and precision-defined flags.
- `cpu-runs.csv`, `cpu-family-metrics.csv`, `cpu-memory-trajectory.csv`: CPU results and mechanism diagnostics.
- `partition-effects.csv`, `cpu-partition-effects.csv`: complete ownership-partition paired effects.
- `exploratory-comparisons.csv`, `cpu-exploratory-comparisons.csv`: declared exploratory families with combined Holm corrections.
- `claim-evidence-ledger.json`, `package-inventory.json`: evidence links and per-file integrity hashes.

The original notebook Part C is retained as historical evidence. Its H means final recall damage, and its separate multiplicity corrections are superseded by the corrected analysis. Original figures remain in the archive; the final report uses newly labelled figures.

`requirements-cpu-observed.txt` records the locally observed versions, not a guarantee that identical binary wheels exist for every operating system/Python. The CPU runtime is distinct from the archived GPU runtime; results from the two are never pooled for paired effects.

## Verification

    python -m pytest tests/test_phase3_cpu_supplement.py -q

Tests exercise scoring populations, tied/zero signed-rank cases, Holm correction, buffer field alignment, matched deletion, RNG preservation, ordinary-training equivalence, and pre-intervention parity on synthetic trajectories. Synthetic tests validate code invariants and are never presented as research results.

## Earlier report review

The user supplied Saneed's 15-page `C_NET_Project (3).pdf` and its TeX during this session. The revised report preserves its useful confusion, binary detection, retention, ablation and literature views, regenerated from verified data. `source-review/review.md` records the retained strengths and required corrections. The original PDF/TeX remain local for provenance and are excluded from the hand-in ZIP to avoid competing report versions.
