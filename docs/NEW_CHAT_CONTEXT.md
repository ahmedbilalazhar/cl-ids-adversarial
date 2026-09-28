# New Chat Context — CL IDS Adversarial Project

Paste this file into a new chat before asking it to continue work.

## Workspace

- Current repo/workspace: `C:\Users\hp\Desktop\University\5. C Net\1. Project`
- Current date when this context was written: 2026-09-28
- Baseline commit before repair work: `9e635aef56c2a48d0c2937d172069a621eb753df`
- Worktree is intentionally dirty with many uncommitted changes. Do not run destructive Git commands. Do not revert files unless explicitly asked.

## Highest-Priority Rule

The project is safer than it was, but it is not finished or publication-ready.

Do not claim all issues are fixed. Do not claim final scientific evidence. Do not run the full 211-config grid unless the user explicitly asks and resource planning is clear.

Current valid experimental status:

- Main result tables are intentionally header-only or empty of validated current claims.
- Historical result files were invalidated or archived when provenance was unsafe.
- Only exploratory diagnostics have been run after repair:
  - `e1_finetune_dedup`: 3 seeds, isolated under `results/diagnostics`
  - `e1_finetune_t0`: 3 seeds, isolated under `results/diagnostics`
- These six diagnostic seeds are valid smoke/evidence checks, not final paired experiments.

## What Was Fixed

1. Inventory and invalidation:
   - Built a 211-config inventory in `docs/inventory.md`.
   - Added invalidation tracking in `docs/invalidation_table.md`.
   - Archived invalid historical UNSW/IoT outputs and other unsafe artifacts under `results/_archive/` and `data/_archive/`.
   - Main historical active result summaries were not treated as valid because they lacked current manifest/provenance guarantees.

2. Transactional reporting and provenance:
   - Central reporting logic lives in `src/reporting.py`.
   - Result writes now use pending markers, temp writes, manifests, artifact hashing, and provenance checks.
   - Resume/status logic verifies manifests instead of trusting summary-file existence.
   - A bug was fixed where `save_results` could overwrite a pending-only marker before any summary/R file existed.
   - Test coverage was added for pending-only provenance preservation.

3. Entrypoints and validation:
   - Broken imports/entrypoints were repaired.
   - Notebook path/import assumptions were repaired.
   - Makefile lint/check targets now visibly surface issues.
   - Synthetic CLI E2E tests now cover single-node, federated wrong-runner rejection, interrupted write/resume, label/task schema, and related safety paths.

4. Dataset/task integrity:
   - UNSW and IoT task builders now use safer label handling, source checksums, row IDs, feature names/units, scaler metadata, and schema v2 JSON sidecars.
   - IoT sampler was made bounded-memory.
   - CICIDS now has a T0-only arm and a content-deduplicated arm.
   - The legacy CICIDS task remains available but is scientifically unsafe for current claims.

5. Audits:
   - `scripts/audit_tasks.py` and `docs/task_audit.md` document train/test exact-match leakage checks.
   - `scripts/audit_cicids_cross_file.py` and `docs/cicids_cross_file_audit.md` document cross-file duplicate structure in original CICIDS CSVs.
   - CICIDS dedup arm currently reports zero exact train/test duplicate matches and zero same-source row overlap.

## Current Verification Results

Last known verification:

```powershell
python -m pytest -q
# 12 passed

python -m ruff check src scripts tests --select E7,E9,F63,F7,F82
# passed

python -m ruff check scripts/audit_tasks.py scripts/audit_cicids_cross_file.py
# passed

python -m ruff check src scripts tests
# fails with 78 broader legacy style/import issues

git diff --check
# exit 0, only Windows line-ending warnings
```

Diagnostic run commands already executed:

```powershell
$env:CL_THREADS="2"
python -m src.run_experiment --config configs/baselines/e1_finetune_dedup.yaml --seed 1 --results-dir results/diagnostics --resume
python -m src.run_experiment --config configs/baselines/e1_finetune_dedup.yaml --seed 2 --results-dir results/diagnostics --resume
python -m src.run_experiment --config configs/baselines/e1_finetune_dedup.yaml --seed 3 --results-dir results/diagnostics --resume

python -m src.run_experiment --config configs/baselines/e1_finetune_t0.yaml --seed 1 --results-dir results/diagnostics --resume
python -m src.run_experiment --config configs/baselines/e1_finetune_t0.yaml --seed 2 --results-dir results/diagnostics --resume
python -m src.run_experiment --config configs/baselines/e1_finetune_t0.yaml --seed 3 --results-dir results/diagnostics --resume

python -m src.run_experiment --rebuild-table --results-dir results/diagnostics
python scripts/stats_summary.py --results-dir results/diagnostics
```

Diagnostic summary:

- Dedup 3-seed ACC mean: `0.570222`, std: `0.005885`
- T0-only 3-seed ACC mean: `0.506642`, std: `0.013032`
- Warning: these use different populations/leakage controls. Do not interpret as a causal comparison.

## Important Files to Read First

Read these before making more scientific or experimental claims:

- `docs/inventory.md`
- `docs/invalidation_table.md`
- `docs/task_audit.md`
- `docs/cicids_cross_file_audit.md`
- `docs/HANDOVER.md`
- `results/README.md`
- `src/reporting.py`
- `tests/test_project.py`

## Known Open Work

1. Full paired experiments:
   - The requested 12 paired-seed comparison has not been run.
   - No full 211-config grid rerun has been launched after repair.

2. Lint debt:
   - Fatal Ruff checks pass.
   - Full Ruff still reports 78 broader issues. Treat these as cleanup debt unless the user asks to make lint fully clean.

3. UNSW/IoT integrity:
   - UNSW v2 and IoT v2 have improved schema/provenance.
   - Exact-content overlap still exists across separate source pools:
     - UNSW v2: 3,723 exact matches
     - IoT v2: 604 exact matches
   - This is documented, not solved. Claims using these datasets must be carefully scoped.

4. CICIDS:
   - Legacy CICIDS has exact train/test overlap and unverifiable source identity.
   - T0-only and dedup arms exist to support safer comparisons.
   - The dedup arm currently audits clean for exact duplicate train/test content.

5. Publication state:
   - The repo is not yet a deployable IDS.
   - The empirical package is not yet journal-ready.
   - Strong claims require manifest-validated reruns and updated statistical tables.

## Strong Do-Not-Do List

- Do not delete archived artifacts; preserve archive-never-delete behavior.
- Do not restore invalid historical numbers into active result tables.
- Do not use summary CSV existence as proof of completion.
- Do not compare T0 and dedup diagnostics as if they were final paired controlled experiments.
- Do not run `git reset --hard`, `git checkout --`, or destructive cleanup.
- Do not relaunch the full grid casually.
- Do not modify unrelated user changes in the dirty worktree.

## Good Next Steps

Reasonable next tasks for a new chat:

1. Make the broad Ruff suite clean without changing experimental behavior.
2. Add focused tests around manifest/provenance edge cases.
3. Prepare a small, explicit 12-paired-seed run plan for the T0 and dedup arms only.
4. Run the 12 paired seeds only after confirming runtime/resource expectations.
5. Rebuild result tables and stats after the paired run, then update docs with bounded claims.
6. Improve UNSW/IoT treatment by either implementing content-deduped splits or clearly excluding them from final claims.

## Current Answer to "Are All Issues Fixed?"

No. The integrity gate and many repair blockers are fixed, but the project is not done. The remaining work is mainly final paired reruns, broader lint cleanup, and careful scientific scoping for datasets with documented overlap.

## Continuation update — 2026-09-28 (read before using earlier notes)

- `docs/plan.md` was initially empty when this continuation began, then the
  owner populated it. It is now the governing improvement program (23,715
  bytes). `main` remains at the reference commit
  `9e635aef56c2a48d0c2937d172069a621eb753df`. See the new
  `docs/roadmap.md` for phase statuses, dependencies, and resumable commands.
- Phase A preflight: `src/config_validation.py` now checks method, task path,
  task label-map targets, runner, device, attack budget/mode, update-attack placement, defense,
  malicious-client IDs, aggregator, Krum assumptions, and backdoor trigger
  metadata. `src/run_experiment.py` validates before executing; `run_grid.py`
  prevalidates every config in its selected group before any seed. All 213
  current YAML configs pass. Synthetic tests reject wrong runner, Krum count,
  and invalid budget. No full grid was launched.
- Phase C E3 repair: `src/attacks/backdoor.py`, `src/runner.py`, and
  `src/federated/fedavg.py` now use the same validated trigger in model space
  for poisoning and evaluation. Raw feature values are transformed using the
  v2 task sidecar's fitted scaler. Absent trigger features fail, rather than
  modifying an unrelated column. PortScan-absent tasks have `asr: null`
  (reported as N/A) and zero eligible examples. Per-task eligible counts,
  successes, clean targeted errors, and training dose are persisted in the
  summary. The three E3 configs now use `tasks_chrono_dedup.npz`.
- `scripts/gen_grounded_trigger.py` now states that its packet-header check
  does not verify CICIDS flow-extractor output. It removes an inconsistent
  `hping3 -d 40` payload option and describes the proposed trigger as a
  feature-space approximation. The script ran; Scapy is not installed, so
  only the range check ran. Packet-to-flow validation is still pending.
- The 38 prior E3 R/summary files were moved to
  `results/_archive/backdoor_protocol_20260928/`, with checksums and a reason.
  Old E3 ACC/ASR claims, including ASR 1.0, are invalid. The active E3 seed
  count is zero; no corrected dataset experiment has run.
- `tests/test_backdoor.py` has tiny synthetic checks for raw-to-scaled
  conversion, missing/mismatched features, single/federated trigger parity,
  eligible ASR and missing-class N/A. The existing all-config test now invokes
  preflight validation. A further synthetic CLI test confirms single-node and
  federated summaries persist eligible backdoor endpoints. Negative manifest
  tests cover corrupt matrix, wrong seed/config/runner, and mismatched task
  hash. Latest full `python -m pytest -q` after all edits: 18 passed.
  Fatal Ruff selection (`E7,E9,F63,F7,F82`) passes; strict Ruff on the new
  validator/backdoor code and test passes. Full Ruff reports 76 broader
  issues and remains a release gate. `git diff --check` passes, with only
  Windows line-ending warnings.
- `README.md`, `docs/results_overview.md`, `docs/invalidation_table.md`,
  `docs/inventory.md`, `docs/decisions_log.md`, and `docs/ai_disclosure_log.md`
  record the E3 invalidation and current evidence boundary.

### Remaining next gates from `docs/plan.md`

1. Preserve the passing Phase A synthetic exit gate and finish Phase B data/resource checks; UNSW
   and IoT still have documented exact cross-pool content matches.
2. Complete Phase C discovery redesign so held-out flows cannot affect
   clusters and provisional labels actually affect classifier training; fix
   FWT's unmeasured upper triangle; extend measured attack-dose logging.
   Verify the grounded trigger through an actual flow extractor. Only then
   run E3 three-seed diagnostics and selected paired experiments.
3. Phase D controls, Phase E machine-readable analysis specification and
   12-seed selected comparisons, Phases F–H performance, trained inference,
   claim ledger, strict CI/lint, dependency lock, and clean reproduction are
   still pending. Main result tables still have no validated final rows;
   six existing finetune diagnostics remain separate exploratory checks.

## Continuation update — 2026-09-28 (E4, FWT, and source provenance)

- The governing `docs/plan.md` and `docs/roadmap.md` remain in force. Source
  commit is unchanged at `9e635aef56c2a48d0c2937d172069a621eb753df`;
  the worktree is intentionally dirty. Do not reset or delete archives.
- All 157 historical E4 R/summary, E5 JSON, and E4/E5 figure files were
  moved to `results/_archive/discovery_transductive_20260928/` with a
  SHA-256 manifest. E4 had fitted HDBSCAN on training plus held-out test
  rows after classifier training. Its cluster effects and any attributed
  classifier ACC change are invalid. The old E4/E5 claims remain visible
  only as explicitly superseded historical prose in README/proposal/results
  overview/paper draft; do not cite them.
- `src/discovery/pipeline.py` now fits clusters on training candidates only.
  AE fitting and threshold calibration use disjoint benign training subsets.
  HDBSCAN sees at most 4,000 seeded training candidates; remaining training
  candidates and held-out flows use a fixed nearest-centroid/max-training-
  radius rule. The cap and assignment approximation require sensitivity
  checks before a headline. Provisional cluster IDs are task-unique and
  enter classifier training. `configs/novelty/e4_novelty_label_control_c.yaml`
  adds a direct-label-poison control. Four chronological E4 configs use the
  duplicate-disjoint CICIDS task artifact. There are now 214 YAML configs.
- Per-task discovery output now includes the candidate cap count,
  eligible/flagged/absorbed attack counts, both absorption denominators,
  benign false-alert rate, assignment purity/ARI, downstream class recall,
  benign classifier false-positive rate, and cluster-to-provisional-ID map.
  `src/runner.py` and `src/federated/fedavg.py` record actual poison counts,
  eligible counts, configured budget, and defense retention. The dose fields
  still need broader attack-family review before Phase C exit.
- `src/metrics.py` now returns FWT `null` unless a measured pretraining
  baseline is supplied. Neither runner measures the future-task upper
  triangle, so current new summaries correctly report FWT N/A; old
  diagnostic `fwt=0` fields are invalid and must not be cited. Reporting
  accepts null FWT and renders an empty table cell.
- New manifest version 3 hashes all `src/*.py` bytes, including uncommitted
  code. `execute_config` compares the hash before and after a seed. The
  reader checks it again for version-3 results. Older version-2 diagnostics
  are marked `pre-code-hash` and remain exploratory, not release-grade.
- A first E4 no-poison seed was archived under
  `results/_archive/discovery_pre_code_hash_20260928/` with its resource
  record because it preceded manifest v3. Its first v3 rerun was archived
  under `results/_archive/discovery_pre_asr_null_20260928/` after later
  endpoint fixes changed the source hash. It took 116.0 s and 895.3 MB
  sampled peak process-tree RSS (`CL_THREADS=2`) on an 8-logical-CPU, 31.8 GB
  RAM Windows host. Its ACC was 0.542228 and mean discovery miss rate across
  attack-containing tasks was 0.755247. A final v3 seed-1 rerun is in
  progress; verify its manifest and resource JSON before using even the
  exploratory baseline. No paired effect, final estimate, or Colab measure.
- Raw IoT parquets are absent locally; capped IoT build peak RSS is still
  unmeasured. UNSW/IoT exact cross-pool matches remain (3,723/604) and those
  datasets are excluded from final claims pending deduped correction.
- A small-case E4 cap check at `results/diagnostics/e4_cluster_cap_4000_of_5000.json`
  sampled 5,000 task-2 training candidates and compared full HDBSCAN on them
  with a seeded 4,000-row fit plus frozen assignment. It found 126 versus
  103 clusters and adjusted Rand index 0.628; a 1,000/1,500 check found
  ARI 0.522. This is a material change. The current E4 method is a
  **capped discovery protocol** and must not be presented as equivalent to
  fitting HDBSCAN on all 125,570 novel task-2 training candidates. The
  5,000-row check used 56.2 s and 539 MB sampled peak RSS on the local CPU.
- Synthetic tests in `tests/test_discovery.py` cover held-out isolation,
  provisional labels entering training, direct-label control, deterministic
  candidate cap, FWT N/A, and actual dose. The full 24-test pytest suite
  passed before the latest ASR/dose source edits; 23 tests excluding the long
  CLI restart case passed afterward. Run the complete suite once more after
  the final seed-1 diagnostic. Fatal Ruff selection passes. Full Ruff reports
  72 broader issues and remains a release gate.

### Immediate next gates

1. Finish `python -m pytest -q`, fatal Ruff, strict lint counts, and
   `git diff --check`; resolve any failures. Update this context with results.
2. Inspect the v3 E4 no-poison diagnostic, especially high baseline miss
   rate, and quantify the 4,000-candidate approximation on a manageable
   exact-reference subset. Then run matched 3-seed anchor/no-poison/direct
   label-control diagnostics in `results/diagnostics/`, one seed at a time.
   Do not infer an attack effect from the lone baseline seed.
3. Verify the E3 packet trigger through an actual flow extractor before E3
   diagnostics. Continue Phase D controls and prespecified Phase E analysis
   before any selected 12-seed grid. No final comparison or Holm family is
   complete, and the main result tree still has zero validated final seeds.
