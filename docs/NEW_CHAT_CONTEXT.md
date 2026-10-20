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

- The governing `docs/plan.md` and `docs/roadmap.md` remain in force. The
  plan's reference commit is `9e635aef56c2a48d0c2937d172069a621eb753df`.
  Current `main` is `a4558b582a46352bc8f3708af3ce09aeadb8ef49`, which
  contains the repair work through the E4 diagnostics; inspect current code
  and results rather than assuming the reference commit. Do not reset or
  delete archives.
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
  endpoint fixes changed the source hash. A subsequent nine-seed set under
  source hash `b8081e8…` was archived, with its resource records and logs, at
  `results/_archive/discovery_pre_commit_asr_20260928/`: the later ASR-null
  and buffer-poison fixes changed two `src` files. The current nine-seed diagnostic
  (seeds 1, 2, 3 in each of no-poison, anchor-poison, and direct-label-control
  arms) is complete under `results/diagnostics/runs/`; all nine manifests are
  v3, code-hashed to the **current** source hash
  `94abb1576b44e9d5c52bc70a05b1b1688fd06f0d60458111fba9d83395668dfb`,
  and exploratory. A live `check_artifact` call passed for all nine.
  `results/diagnostics/e4_descriptive.json`
  records ACC means 0.521883, 0.530564, and 0.554113 respectively, and mean
  pooled attack absorption 0, 0.000935, and 0.000935. No final paired effect
  or Colab measure follows from these diagnostics. Current-source seed-1 probes
  used `CL_THREADS=2` on an 8-logical-CPU, 31.8 GB RAM Windows host: 144.2 s /
  862.3 MB, 145.6 s / 863.9 MB, and 124.7 s / 895.0 MB sampled process-tree
  peak RSS respectively. The current runtime bytes are preserved in
  `artifacts/source_snapshots/runtime_94abb1576b44e9d5c52bc70a05b1b1688fd06f0d60458111fba9d83395668dfb.zip`;
  the earlier `runtime_b8081e8…` snapshot belongs to the archived run.
- Both IoT parquets were in fact present locally (correction 2026-09-28:
  the "absent" notes below were wrong when written); the capped build is now
  measured at 107 s / 3.2 GB peak with the fixed builder, artifact
  bit-identical. UNSW/IoT exact cross-pool matches remain (3,723/604) and those
  datasets are excluded from final claims pending deduped correction.
- A small-case E4 cap check at `results/diagnostics/e4_cluster_cap_4000_of_5000.json`
  sampled 5,000 task-2 training candidates and compared full HDBSCAN on them
  with a seeded 4,000-row fit plus frozen assignment. It found 126 versus
  103 clusters and adjusted Rand index 0.628; a 1,000/1,500 check found
  ARI 0.522. This is a material change. The current E4 method is a
  **capped discovery protocol** and must not be presented as equivalent to
  fitting HDBSCAN on all 125,570 novel task-2 training candidates. The
  5,000-row check used 56.2 s and 539 MB sampled peak RSS on the local CPU.
  `results/diagnostics/e4_threshold_sensitivity.json` is a post hoc T1
  threshold audit: attack flagged rate rose from 0.00182 at q0.95 to 0.16648
  at q0.50, while benign false-alert rate rose from 0.014 to 0.35733. This
  does not justify changing the primary q0.95 threshold after seeing outcomes.
- Synthetic tests in `tests/test_discovery.py` cover held-out isolation,
  provisional labels entering training, direct-label control, deterministic
  candidate cap, FWT N/A, and actual dose. The final full 24-test pytest suite
  passed. Fatal Ruff selection and `git diff --check` pass. Full strict Ruff
  reports 72 broader issues and remains a release gate.

### Immediate next gates

1. Investigate the weak baseline E4 detector and material candidate-cap
   sensitivity. Keep q0.95 as the primary threshold unless a new protocol is
   prespecified; do not treat the post hoc threshold audit as confirmatory.
2. Verify the E3 packet trigger through an actual flow extractor before E3
   diagnostics. (The IoT half of this old item is done: both parquets were
   present and the capped build is measured — see correction above.)
3. Continue Phase D controls and prespecified Phase E analysis before any
   selected 12-seed grid. No final comparison or Holm family is complete,
   and the main result tree still has zero validated final seeds. Later gates
   include strict lint, trained deployment benchmark, claim ledger, and clean
   reproduction. Do not interpret the nine E4 seeds as a final effect.

### Phase D source audit added after the E4 diagnostic

`docs/federated_controls_audit.md` traces client partitioning, optimizer,
replay, EWC, aggregators, and the tabular architecture to current code.
Client shards are redrawn for every task while client CL/Adam state persists;
there is no site identity in the task artifact. Thus the current protocol is
resampled simulated clients with persistent state. Krum's configured client
constraint is already validated, but empty clients still submit to unweighted
robust aggregators. No Phase D source change or experiment was made in this
audit. Preserve/archive the nine E4 v3 diagnostics before changing `src`,
because v3 fingerprints the entire source tree. Next concrete implementation
is per-client participation, class-mix, optimizer-step, buffer-memory, and
communication-byte logging with synthetic federated verification, followed
by matched controls.

The current E4 diagnostics were re-run after detecting the source-hash
mismatch described above; their live manifest checks pass. The full 24-test
suite passed before this rerun. No `src` files changed during it. The main
`results/runs/` tree still has zero validated final seeds.
The new source snapshots under `artifacts/` and the newer checksum archive
under `results/_archive/` are local, ignored by Git. They must be included
explicitly in any release bundle; their hashes were verified locally. The
current E4 run manifests and summaries are tracked and changed in the
worktree. No commit was created in this continuation.

### Continuation update — E4 detector and cap audit (2026-09-28)

`docs/e4_detector_cap_audit.md` records a post hoc three-seed no-poison score
audit and two additional 5,000-versus-4,000 T2 cap comparisons. T1 attack
scores rank below benign scores: AE score AUC is 0.120, 0.128, 0.128 and only
5/2,745 T1 attacks are flagged at the unchanged q0.95 threshold in each
seed. The existing q0.50 post hoc check greatly increases benign alerts.
Across seeds 1–3, subset cap ARI is 0.628, 0.728, 0.646, with fewer capped
clusters in every comparison. These are sampled 5,000-row references, not
full-stream equivalence checks or downstream poison-effect runs.

`scripts/audit_discovery_threshold.py` now emits score AUC and class medians.
Its q0.95 rates were checked against all three existing no-poison summaries.
New outputs are `results/diagnostics/e4_score_separation_seed{1,2,3}.json`
and `e4_cluster_cap_4000_of_5000_seed{2,3}.json`. Runtime `src/*.py` remains
at `94abb1576b44e9d5c52bc70a05b1b1688fd06f0d60458111fba9d83395668dfb`;
the nine E4 manifests remain live-checkable. Strict Ruff passes on the edited
audit script. E4 final inference remains gated on an independently specified
detector decision and broader cap/downstream sensitivity. Phase D source
changes have not started, so its audit remains the next implementation guide.

### Continuation update — Phase D controls + Phase E spec (2026-09-28)

Decisions #69–73. Read decisions #69 (E4: keep q0.95, exploratory, gates),
#70 (E3 extractor blocked locally — `docs/e3_extractor_check.md` with
resumable CICFlowMeter commands), and #71–73 below before citing anything.

- E4 handling decided, not implemented in code: q0.95 stays primary; no
  12-seed E4 headline until family-level T1 analysis, a separately specified
  detector protocol, and larger cap/downstream sensitivity. Cap/detector
  numbers (`docs/e4_detector_cap_audit.md`) are post hoc diagnostics.
- E3 packet-to-flow validation is blocked on this host (two Friday flow
  CSVs only, no pcaps, no CICFlowMeter, no scapy). Trigger stays a
  feature-space approximation; E3 diagnostics stay gated.
- The nine E4 diagnostics were copy-preserved (39 files + SHA-256 manifest)
  to `results/_archive/discovery_prefedcontrols_20260928/` BEFORE the first
  `src/` edit, and the runtime snapshot zip was hash-verified. The Phase-D
  edit changed the manifest-v3 fingerprint (now
  `386f115958b3d4a937cea1cbedad1358ceb273c8e89cce12d9e02ce6408b2164`),
  so those nine are 0/9 live-checkable; the archive is their record.
  `results/runs/` still has zero validated final seeds.
- Phase D implemented per `docs/federated_controls_audit.md`: per-client
  pre/post-defense counts, class mix, participation, optimizer steps, buffer
  occupancy/bytes, comm bytes; inactive submissions excluded from unweighted
  rules with exclusions recorded; plain-FedAvg path byte-unchanged;
  `DynamicTrust` index map (backward compatible). `tests/test_fedcontrols.py`
  adds 4 tests; full suite is 28 passed; fatal Ruff selection passes; new
  code adds zero lint issues (5 pre-existing style issues in the touched
  files were left alone).
- Phase E prespecified WITHOUT reading results:
  `scripts/write_analysis_spec.py` generates `docs/analysis_spec.json` from
  `WILCOXON_FAMILIES` + group seed protocol (27 families, 200 pairs,
  two-sided Wilcoxon, Holm-within-family, MIDs 0.02/0.01). Gates: 105
  ready-pending-runs, 42 gated-controls, 46 gated-dedup, 6 gated-detector,
  1 gated-extractor. Regenerate deterministically after any family change.
- Still pending: E4 detector/cap gates, E3 extractor measurement,
  stable-client/round sensitivity, same-aggregator clean controls, Phases
  F–H. No commit was created in this continuation; the worktree is dirty.
- Release-bundle inventory: `scripts/write_bundle_inventory.py` generates
  `docs/release_bundle_contents.md` (13 archives + 2 runtime snapshots with
  hashes). It tolerates the one legacy list-format manifest
  (`architecture_cpu_pre_gpu`). Re-run it on the bundling host; a bundle
  without those git-ignored paths is incomplete.
- Bug-hunt over completed phases (decisions #74–75, 33 tests passing):
  reverse-order Monday-benign duplication fixed (consumed-id tracking, 24
  rev files archived, alt verified clean, `gated-rev-rebuild` in spec);
  flip-ASR eval now scores the train-time flipped class with source carried
  in ASR rows (numeric sources no longer silent N/A); joint summaries carry
  `joint_oracle`; empty-task skip hardened. Suspects dismissed with
  evidence: `_source_row_id` never enters model features (outer df
  untouched), CI task file verified correct class-IL, backdoor KeyError
  unreachable behind validation, reporting aggregation reviewed clean.
- This-turn additions (decisions #76, 36 tests passing): notebook bundle name
  restored to v2 (producer still writes v2; test was right), federated
  aggregation extracted to `_aggregate_updates` with direct degenerate/
  exclusion unit tests, buffer-target persist-and-validate test. Reporting,
  sequence, runner, and dispatch paths re-read clean.
- Claim ledger (decision #77): `docs/claim_ledger.md` links every
  README/proposal/overview/memo/draft statement to evidence. Aggregates are
  0-row, `results/runs/` has 0 manifests — all numeric results are
  executed-only; README status is stale (2026-09-25); abstract PENDING slots
  correct. Fixed a stray typo in `docs/plan.md` (byte-identical to HEAD).
- Recursive pass (decisions #78–80, 40 tests passing): both v2 artifacts
  rebuild bit-identically under the fixed builder (temp-only outputs);
  synthetic round probe (steps exact 3x, comm stable, buffer capped —
  diagnostic only); `src/inference.py` contract (versioned bundles, weight
  hashes, strict schema, counted imputation, batch bound, explicit abstain,
  latency) with 4 tests. Earlier "28/36 passing" notes above are dated
  history. Nothing committed; worktree dirty.
- Autonomous stretch (decisions #81–84, 43 tests): IoT builder fixed
  (11.3→3.1 GB, identical bytes, consolidation test); "parquets absent"
  notes corrected; T1 family audit (SSH 0.04–0.06, FTP 0.16, Bot 0.006 —
  post hoc); E8 dims restored to artifact (19,087 params match docs);
  lint 79→30 behavior-preserving; generator-determinism tests. Suite
  green, fatal lint clean. Still uncommitted.
- Fresh-hunt round (decisions #85, #87–88 — #86 is a same-day pointer to
  #87/#88, not evidence; 50 tests): cleaner wipe-guard
  (string metadata raises instead of emptying files; first reorder attempt
  reverted after it changed dedup semantics 2.57M→2.31M — guards proven
  byte-identical on full rebuild); CI fail-closed contract (benign-after-T0
  rejected); arch/hidden validation (214/214 pass); figures gated to
  validated manifests only + honest wrote/kept reporting (12/12 skip
  cleanly). Reviewed clean with evidence: pipeline (ARI edge finite),
  replay determinism (numpy seeded, no stray random use), EWC fixes intact,
  byzantine math, run_experiment wiring, paths/models, UNSW builder
  (no sport columns in mirror; seed param cosmetic).
- Hunt round 2 (decisions #89–90, 54 tests): GPU import version gate (v2
  cross-machine, v3 same-machine-only; full cross-machine v3 awaits GPU
  redesign); downloader import side-effect removed; stray nested
  threat-model duplicate deleted (fully superseded); transformer docstring
  fixed with single-token claim verified in code; UNSW seed documented
  provenance-only. Reviewed clean: LwF (+moot fed check), EWC, replay/RNG
  audit, byzantine, run_experiment, paths/models factory, defenses,
  grid_status, task_schema core.
- Hunt round 3 (decision #91): comparison-name resolution hardening — spec
  generator raises on unknown pair names / duplicate display names (214
  unique, all 200 pairs resolve); stats_summary prints orphan warnings
  (none on empty aggregates). No suite change; full re-verify pending.
- Hunt round 4 (decisions #93–94, 56 tests): stats-math audit (Holm/Kerby/
  bootstrap/sample-std verified; dead `wilcoxon_pair` removed); build/CI
  reproducibility (pytest/ruff pinned, Makefile lint aligned to gate, CI
  lint step, queue continues past failed groups, snapshot off-root fixed).
- Hunt round 4 (decision #92, 57 tests): EWC analytic characterization
  (anchor/Fisher-accumulation/closed-form loss, head-growth safety).
  Decisions renumbered to sequential (pointer #86 preserved). Paper prose
  verified free of attention claims.
- Hunt round 5 (decision #95, 58 tests): 7 tracked stale figures archived
  with manifest; quarantine lint churn reverted + `scripts/archive/`
  excluded from ruff; dev pins aligned across pyproject/requirements.
- Hunt round 6 (decision #99): audit rendering honesty (separate-pool
  overlap is n/a, not 0) + archive crash-safety (partial manifests,
  testable move/write split, inventory surfaces incompleteness).
- Hunt round 7 (decision #100): Colab notebook output completeness —
  manifests copied to Drive, resume via manifest validation, source_commit
  recorded; all code cells compile; regression test extended. v3
  cross-machine tree mismatch stays documented, not silent.
- Hunt round 8 (decision #101): rerun-identity tests (fed + single-node
  bit-identical) lock the reproducibility contract; federated EWC anchor
  semantics characterized coherent (no behavior change). Decisions kept
  sequential 59–101.
- Hunt round 9 (decision #102): cross-process CLI determinism (byte-identical
  R, summaries equal modulo wall time, equal matrix hashes, JSON type
  stability). Process lesson: always verify the true file tail before
  appending decisions — mid-file anchors re-scramble numbering.
- Hunt round 10 (decision #103): cited-number sweep (all match source
  JSONs), tracked-file secret scan (clean), randomized invariant tests,
  decisions-order guard test (sequential 59–103 enforced by suite).
- Implementation round (decisions #96–98, 65 tests): stable-partition
  variant (`fed.partition`, id-hash, validated); multi-round federation
  (`fed.rounds`, poison-once, per-round work rows, legacy path
  whitespace-proven untouched); trained T0 bundle benchmark (19,087
  params, host latency/throughput/RSS in diagnostics) + hash-chained
  versioning with fail-closed rollback.

- Hunt round 11 (decision #104): replay/kNN profiling verdict — buffer ops
  ~3ms/observe (~10%), reservoir rewrite declined on measurement; kNN
  time-quadratic (~190s @139k) but memory-flat; two stale results/README
  lines fixed (E4 live-hash expired, phantom e7 file); e7 logic verified
  sound. Decisions re-sequenced 59–104 programmatically.
- Config round (decision #105): matched `c_f2x` sensitivity group
  (dedup-baseline, stable-partition, 2-round arms on v2 tasks; legacy tasks
  lack ids for stable). 217/217 validate, 0/36 TODO, no spec family yet,
  no runs launched.

---

# PASTE-READY HANDOFF (written 2026-09-28, source tree `ac9fa311…`, main `a4558b5`)

Continue the project in `C:\Users\hp\Desktop\University\5. C Net\1. Project`
per `docs/plan.md` (reference commit `9e635ae…`; current main is AHEAD at
`a4558b5` — inspect current code/results, never reset). Worktree is
intentionally dirty (~126 changed/new paths, no commit requested). Do not
run `git reset --hard`, `git checkout --`, or destructive cleanup. Do not
delete `results/_archive/`, `data/_archive/`, or `artifacts/source_snapshots/`
— they are git-ignored and must be copied explicitly into any release bundle
(see `docs/release_bundle_contents.md`, regenerated by
`python scripts/write_bundle_inventory.py`).

## Non-negotiable rules

- Never fabricate results or call an unexecuted experiment complete. A failed
  or null attack is a valid finding; post-hoc retuning to manufacture
  significance is forbidden (plan §2).
- Historical results without v3 manifests are executed-only, never evidence.
  `results/runs/` has 0 manifests; all aggregate CSVs are 0-row.
- Undefined endpoints are N/A/null, never 0. Replay buffers are unbalanced by
  protocol. The joint model is a future-data oracle (`joint_oracle` flag).
- Three seeds on one captured dataset = seed variation only. Twelve paired
  seeds required for any headline; Holm within family (see
  `docs/analysis_spec.json`: 27 families, 200 pairs, two-sided Wilcoxon).
- `CL_THREADS=2`, one seed at a time on the CPU laptop. Manifest v3
  fingerprints all of `src/*.py` — any `src/` edit invalidates live results;
  copy-preserve to `results/_archive/` FIRST (see
  `scripts/archive_artifacts.py`; precedent:
  `discovery_prefedcontrols_20260928/`).
- Full pytest exceeds the 600s tool timeout: run `tests/` without
  `test_project.py` first, then `tests/test_project.py` alone (~6 min).
- Every fix gets an execution proof in the same turn (test, rebuild-compare,
  or measured rerun). Decisions-log entries stay sequential; #86 is a pointer
  to #87/#88, never evidence.

## Done (code, tested — 77 tests: 61 + 16 split, fatal Ruff selection clean)

Phase 0/A/B/C code, E3 trigger/ASR repair, causal E4 pipeline + control,
FWT=null, dose logging, Phase-D per-client logging + inactive exclusion
(locked FedAvg byte-identical, extracted `_aggregate_updates`), E4
detector/cap/family audits, E3-blocked doc, claim ledger
(`docs/claim_ledger.md`), analysis spec (+`gated-rev-rebuild`,
strict name resolution), bundle inventory, inference contract
(`src/inference.py`), v2 artifacts reproduce bit-identically, IoT builder
fixed (11.3→3.1 GB, identical bytes), E8 dims restored (19,087 params),
lint 79→30 (remainder is deliberate debt), cleaner wipe-guards, CI/arch/
defense/grid fail-closed validation, figures gated to validated manifests,
GPU import version gate, downloader/CWD hardening, transformer docstring.
Decisions #1–91 in `docs/decisions_log.md` (entries now sequential).

## Remaining phases and gates

- **D remainder**: stable-client/site comparison, work-matched 1-vs-N-round
  study (synthetic 3x probe done only), same-aggregator clean controls,
  EWC anchor/loss analytic audit, single-token rename in paper prose.
- **E**: all selected 12-seed runs (104 ready / 42 controls-gated / 46
  dedup-gated / 6 detector-gated / 1 extractor-gated / 1 rev-rebuild-gated),
  then rebuild stats, figures, ledger, manuscript. Resumable loops live in
  `docs/roadmap.md` — do not launch without explicit user go-ahead.
- **F remainder**: replay-reservoir, kNN/HDBSCAN bounds, inference batching
  profiling (IoT ingestion done: profiled, fixed, measured).
- **G remainder**: trained-bundle benchmark on real dims, monitoring/rollback,
  real-federation design (contract code exists, proxy E8 numbers stay proxy).
- **H remainder**: reconcile manuscript from the ledger, novelty DB
  verification (Su 2025 page, Scholar/Xplore/Scopus counts), pin
  deps/container digest, clean-room table+figure reproduction.
- **Blocked locally**: raw pcaps / CICFlowMeter / scapy (E3 stays
  approximation), Colab GPU (importer now version-gated for its return),
  E4 detector + cap gates, UNSW/IoT dedup (3,723/604 cross-pool matches —
  excluded), rev-order rebuild + rerun.
- Housekeeping discipline: keep decisions entries sequential and
  non-duplicative; dated history in context/roadmap stays untouched —
  append, don't rewrite.
