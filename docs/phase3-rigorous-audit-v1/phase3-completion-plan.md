# Phase 3 completion and weakness repair plan

Prepared 16 November 2026; materially updated 17 November 2026. Status: substantial adopted-profile development evaluation complete, but full Phase 3 remains incomplete. The 240-cell core, 24 DQ cells, 48 replay-loss ablations, 96 quota ablations, nine clean confirmations and 24 oracle continuations have cell/metric/checkpoint evidence. The independent follow-up audit is `results/phase3-rigorous-audit-v1/followup-independent-audit.json`; FIFO/class-balanced remain smoke diagnostics, not matched cells.

## Basis and scope

This plan maps the user's seven Phase 3 requirements and the supplied rubric (methodology implementation 10 marks; experimental evaluation/comparison 10; ablation/research validation 10) to the current repository. The screenshot exposes category weights only, not detailed scoring descriptors; no predicted mark is warranted. Phase 2 is `submissions/phase2-with-claude.tex`. The current reliability baseline is the 22-finding audit in this directory, not the older submitted report.

The earlier conversational estimate of 75% was judgment-based, without a counted requirement inventory. It must not be used as a measured completion percentage or grade. Track requirements as verified, partial, blocked, optional/omitted with justification, or superseded by a disclosed amendment. Count implementation coverage separately from experimental validation and evidence quality.

The user adopted the data amendments/taxonomy and authorized implementation of the plan. The 74-feature CPU study has completed the core, DQ, replay-loss, alternative-quota, clean-confirmation and oracle blocks. No held-out outcomes were accessed and no instructor was contacted. The one-worker constraint remains; no further training is scheduled. The follow-up took 32,655 seconds (9.07 hours), exceeding the earlier six-hour CPU ceiling; this deviation and the remaining over-budget matched eviction block are documented.

## What is already established

- 417 unique trajectories (including the 240 core and 24 oracle suffixes) with 1,668 verified stage weights for the earlier 76-feature execution profile. Duplicate files are not independent replications, and these outcomes/weights do not transfer to the adopted 74-feature profile.
- All 60 clean core trajectories were independently rescored from four checkpoints; confusion matrices match. Fixed-cohort continual metrics were reconstructed.
- Corrected local EI, Xavier head expansion, paired attack IDs and matched DM/DC admission counts have audited evidence. Three representative archived trajectories reproduce exactly under the pinned runtime.
- The adopted 74-feature profile has a completed CPU development matrix: 240 core runs (FT/EI/DR/DM/DC × four doses × twelve ownership seeds), 24 matched-random DQ runs, 48 loss-removal ablations, 96 alternative-quota ablations, 24 exact paired oracle continuations, and nine clean confirmations. The core settings follow the historical clean-only selection with DR lambda_y=1 and lambda_z=.1; the fresh gate passes at the learner/gate-mean level while retaining the FTP per-seed 0 recall. These are development-bank results, not independent holdout evidence.
- The separate lambda_z=.5 DR+DC reference remains an implementation milestone only. The 240 core runs must not be conflated with it or with the older 76-feature matrix. An independent current audit verifies 273 result hashes, exact cell coverage, paired attack IDs, clean E1 prefixes, 273 confusion-to-summary metric rows, all 1,092 original core stage-weight files, and the frozen source snapshot in the baseline report ZIP. The follow-up verifier expands this to 417 unique run records, 1,668 full-stage and 48 oracle checkpoints, and all metric rows.
- Source-to-feature, row masks, exclusions/quarantine, 120-second graph/T0, sensitivity and retained split membership now match. The pinned SGKF allocation was reused after exact identity proof, not rerun. Provider/session semantics remain bounded.
- Statistics and claims were corrected; existing findings remain development-only. Import side effects and the zero-effect convention were patched.

These checks should be retained and reused. They do not establish independent test performance or retrospectively fix the historical engine.

## Requirement and rubric map

| Phase 3 requirement | Current status and weakness | Planned closure | Rubric category |
|---|---|---|---|
| 1. Implement Phase 2 and document feedback/changes | Substantial audited implementation; multiple historical engines, amended source/schema and synchronization budget; user confirms no specific class feedback was given, and this is documented without claiming approval | Retain the no-feedback disclosure and amendment table; keep all actual methodology changes traceable to Phase 2 or audit findings | Implementation /10 |
| 2. Dataset/preprocessing/setup | Adopted 74-feature package; source-to-FP32, row-mask/exclusion, graph/T0 and retained role-membership audits match. Provider/session semantics remain bounded; SGKF allocator reused from the pinned split | Preserve exact source/data hashes, exclusions, role manifest, T0 and support evidence; keep held-out outcomes sealed until freeze gates pass | Implementation /10; evaluation /10 |
| 3. Baseline evaluation and essential metrics | The adopted 74-profile FT/EI/DR/DM/DC matched core is complete at 12 seeds × four doses; DQ, loss-removal, quota controls, and 29 paired contrasts are reported. It remains development-only; Phase 2 DG now has an executable global 75% low-loss selector; its 48 matched outcomes are absent, and no final-test outcomes exist | Keep the `.1` DR coefficient/selection history explicit; qualify test package and evaluator only after freeze; retain the unrun DG outcome block as an explicit omission unless the separately budgeted study is authorized and completed | Evaluation /10 |
| 4. Graphical results | Audited 76-feature figures, the n=1 lambda_z=.5 reference figure, the adopted-profile core-results figure, matched quota-ablation figure, and a hash-checked 417-trajectory observed wall-time distribution are present. FIFO/class-balanced mechanism and disaggregated cost figures remain | Keep population, unit, and source table visible; generate missing ablation/cost figures only if those cells are completed | Evaluation /10; validation /10 |
| 5. Compare existing research | A contextual literature matrix is linked from the report; matched local FT/EI/DR/DM/DC comparisons now exist on the adopted profile, but the prospective DG code has no matched outcomes, and cited published work is not a numerical leaderboard | Keep paper results qualitative and task-aligned; verify source details for any quoted numerical claims | Evaluation /10 |
| 6. Ablations | DQ clean/.5 matched-random, 48 replay-loss ablations, 96 alternative-quota ablations, and 24 exact DR/DC oracle suffixes are complete and audited. Adopted-profile FIFO/class-balanced matched cells and DG outcomes are absent; smoke runs do not close the eviction block. A synthetic DG implementation check does not count as an empirical arm | Keep profile-specific omissions explicit. The FIFO/class-balanced block alone is forecast at 7.30 hours with reserve (8.52 conservatively), over the current six-hour cap | Ablation/validation /10 |
| 7. Analysis/discussion | Adverse DC results disclosed; mechanism, costs and generalization not fully established | P4 measured costs; P5 question-by-question analysis and limitations | All three categories |

## P0 — Freeze the scientific scope and canonical execution path

**Priority:** critical; precedes new outcomes. **Training:** none.

1. The frozen 74-profile extension identity is in `results/phase3-overnight/identity.json`; its exact source snapshot is preserved in the validated submission archive. The versioned analysis, run identities, seeds, doses, metrics, figures, and package inventory are present. A separate independent cell and metric audit now exists.
2. Use the frozen overnight runner and packaged source as the canonical source for the 74-profile CPU results. Keep `phase3-implementation/src/p3lib.py` and the 76-feature study historical; do not pool their results into the adopted matrix. Validation, execution, scoring, analysis, report, and packaging commands are documented in the overnight plan and report. The lambda_z=.5 reference is a distinct implementation-only protocol.
3. The historical clean-only CPU-v3 selection is recorded. Active settings match: DR uses 12 rounds × 1 epoch, lr=.001, lambda_y=1, lambda_z=.1; EI uses lambda_E=100 (lambda_z is inactive for EI); FT does not use replay coefficients. The fresh three-seed clean gate passed at its mean thresholds, while the one FTP-zero seed remains visible. The original 1×3 versus 3×1 pilot was not rerun in the adopted-profile extension and must remain a disclosed protocol amendment.
4. Build a cell-level inventory for 240 core, optional DG, 192 changed-setting ablations, 24 oracle suffixes and development selection. Verify all changed-q DC/DM pairs and loss removals against original definitions. Distinguish DQ (matched random) from DG (global filtering); they are different controls. Phase 2 allows a reduced scope, but omission must be explicit and cannot now be described as a scope decision made before outcomes.
5. Publish a methodology-change table: corrected release; 76 to 74 predictors; revised 16-label taxonomy; support exclusions; runtime/synchronization changes; stronger historical attacks; statistical/metric corrections. For each, state reason, when adopted, affected evidence and validity limits.
6. Instructor feedback was confirmed unavailable by the user on 17 November 2026 (no specific comments were given). Do not claim feedback-driven changes or instructor approval; the historical draft correspondence is marked unsent/unverified. If comments are later provided, record them verbatim with date/source and implementation disposition; external messaging requires the user's instruction.

**Artifacts:** completion protocol, canonical command guide, change/feedback register, baseline and experiment-cell inventory.

**Acceptance:** every reported result resolves to one method/data/runtime/checkpoint identity; no generic “Phase 2 faithful” claim conceals an amendment; baseline and ablation omissions are named.

## P1 — Close raw-data provenance and quantify isolation limits

**Priority:** critical before test extraction. **Training:** none unless a real data defect is found.

1. **Completed independent source-to-split audit (17 Nov local):** the standard-library parser reconstructed all 2,099,976 corrected rows, labels, timestamps, endpoints, protocol, 74 features and the frozen T0 transform. Source/model-input mismatches: zero; finite FP64 parser round-trip differences: 229,383 cells, with zero resulting FP32 differences. A separate validity/exclusion pass also matched every row's raw/final finiteness, domain/metadata validity, timestamp, label, T0 membership, raw/final conflicting-label quarantine, survivor and retained-split membership (zero mismatches). It found 112 conflict groups in both raw and final FP32 content. The 120-second full-SHA256/SciPy connectivity audit matches the frozen graph/T0 closure; 60/120/300-second sensitivity is recorded. The reused SGKF allocation has the exact frozen source positions and zero cross-role component intersections; its allocator is not rerun because data/split identity reuse is documented and hash-linked. Evidence: `docs/phase3-plan/tools/audit_corrected_source_rows_independent.py`, `docs/phase3-plan/tools/audit_corrected_row_masks_independent.py`, their JSON results, and `results/phase3-rigorous-audit-v1/component-reconstruction.json`. The adopted 74-profile invalidates learned weights/tuning from the prior 76-feature candidate.
2. **Closed for the adopted operational data contract:** all source-row, exclusion/quarantine, component/T0 and retained role-membership comparisons match. Remaining boundaries are provider authentication, physical-event/true-session identity, and no independent execution of the pinned SGKF fold allocator; these do not indicate a mismatch in the adopted frozen split.
3. Publish a per-role/per-stage/per-family support table with row and component counts, original background versus remapped attempted traffic, rare-class exclusions and the exact 74 predictors. Confirm no metadata, future labels or poison markers enter predictors/admission.
4. Retain 60/120/300-second sensitivity. The 300-second graph joins 8,982 train/development components under the frozen split; this is a limitation of the chosen operational grouping. Do not switch thresholds to improve scores. A 300-second robustness experiment requires a newly built split/T0/support contract and complete matched retraining; keep it optional unless a broader isolation claim is retained.
5. If an actual implementation or leakage defect appears, quarantine affected checkpoints and all dependent claims, rebuild inputs, and rerun the complete affected matched block. Unaffected records may be reused only with verified identical scientific inputs.

**Artifacts:** independent raw reconstruction tool/log, source/exclusion census, full comparison report, dataset card, support and split manifests.

**Acceptance:** zero unexplained source/transform/component/role mismatches; documented exceptions and boundaries; test outcomes remain unseen during qualification. This does not certify real application sessions or cross-host/site independence.

## P2 — Complete component validation and missing ablations

**Priority:** high; largest missing Phase 2 experimental block. **Training:** 48 new full trajectories (two policies x two doses x twelve seeds), subject to the authorized cap.

Implement FIFO and the exact Phase 2 class-balanced eviction on the same 500-slot NONE-admission replay state. NONE admission holds insertion eligibility constant even as memory policy changes later model scores. FIFO always inserts each eligible first-pass record and removes the oldest insertion when full. Class-balanced also always inserts; evict the oldest record from the largest supplied-label occupancy, breaking occupancy ties by fixed class ID. Keep bounded insertion-order metadata and count its bytes. Do not replace this with a class-partitioned reservoir.

Use the same twelve ownership seeds (1–11,42), clean and maximum dose .5, q=.75, initialization, training, admission rules, attack IDs and random namespaces as the reservoir reference: 2 variants × 2 doses × 12 seeds = 48 trajectories. Reuse qualified reservoir references; do not count their copies as new runs. Validate eligibility, insert-once semantics, deterministic ties, capacity and resume recovery using small meaningful fixtures before launching the block.

Capture actual replay draws/exposures, poison and class occupancy, honest-new retention, H, A, immediate source recall change, absolute clean/attacked targeted error, benign FAR and class metrics. Occupancy alone does not establish that samples were replayed. Analyze paired seed effects and uncertainty; do not infer independent replication from batches, rounds or records. These are exploratory mechanism tests, with no outcome-driven retuning.

The 48 loss-removal and 96 quota cells are complete. The independent audit verifies their exact cell counts, paired data/attack identities, protocol parity, DM/DC quota matching, result hashes, checkpoint-to-model hashes, and metric-ledger parity. Their comparisons are exploratory and use the reused development bank. The 48-cell FIFO/class-balanced block was initially miscounted as 96; use the corrected 48-cell design and its independent audit. Retain the 24 oracle suffixes as conditional label-repair interventions, including any zero-effect cases, rather than deployable defenses.

**Compute gate:** the old archival estimate for eviction was 5.327 hours including 20% reserve. Instrumented replay was slower and included oracle work; neither is a sufficient current scheduling guarantee. Re-measure representative non-oracle jobs under the actual isolated one-worker runtime. Deduct prior measured budget use and account for all newly scheduled training. Dispatch only a complete matched block whose conservative estimate plus reserve fits. Support transactional pause/resume and retain failures. A reduced block must be declared exploratory in advance and cannot be called completion of twelve-seed Phase 2 ablations.

**Updated feasibility and execution record:** isolated clean diagnostics completed for FIFO (266.36 seconds) and class-balanced (189.75 seconds). The original 8.52-hour forecast was based on the mistaken 96-cell count; the corrected design has 48 cells, and its current runner computes a fresh estimate from matched controls with reserve. A subsequent 408-run CPU follow-up manifest records 32,655 seconds (9.07 hours), exceeding the earlier six-hour ceiling. This is a resource-budget deviation in completed evidence, not a reason to select partial results. The complete follow-up inventory and results are retained.

**Artifacts:** eviction implementation and semantic checks, the 144-cell audit, result/metric/checkpoint verifier, matched results/checkpoints, quota figure, and explicit incomplete status for eviction.

**Acceptance:** all declared cells complete, matched inputs checked, no favorable-seed selection, null/adverse effects retained; otherwise mechanism conclusions remain limited.

## P3 — Qualify and perform independent held-out evaluation

**Priority:** critical for final effectiveness claims. **Training:** normally none when existing checkpoints qualify.

1. A separate evaluator exists at `src/phase3_v2/final_evaluate.py`; it accepts a locked final-role manifest and checkpoint/run inventory and has no training interface. Twelve synthetic tests, including rare taxonomy rows excluded from the eligible macro-F1 set and a complete one-shot frozen-run path with hashed row-aligned predictions, pass. Qualification exposed and fixed missing JSON import, checkpoint hash-key mismatch, and early-stage handling of future labels. The development evaluator remains role-pinned. No real final-test package exists, so real role disjointness and held-out execution remain gated.
2. Synthetic contract tests cover a valid final-role fixture, refusal of a development-role manifest, duplicate IDs, component identity drift, and incomplete checkpoint inventory. Expand qualification as needed for all registered prediction columns, fixed denominators/support, benign cohort allocation, finite logits, class-map integrity, deterministic parity, resume/duplicate protections, and a real frozen analysis inventory. Preserve evaluator identity and predictions keyed by immutable ID.
3. Build the final-test package separately after P0/P1 pass. Use the original frozen test-role allocation; do not resplit using favorable support or outcomes. Verify content/component/T0 isolation and support without feeding outcomes to model selection. Training workers must have no test-package path or test-result callback.
4. Freeze the complete checkpoint matrix, eligibility, original 29 contrasts and failure policy before a single locked inference batch. Score all four stage checkpoints for each retained core trajectory, not only clean models or winning arms. Keep the test payload read-only and record access/completion/failure logs. The current not-ready/authorization flags remain in force until evaluator qualification and the recorded release gate are satisfied.
5. Produce H, immediate recall change, A, anchor metrics, benign FAR, per-family support/precision/recall/F1, eligible macro-F1, full-inventory descriptive metrics, confusion matrices, ACC/BWT/forgetting on fixed cohorts. Keep genuinely undefined values explicit. Missing contrasts retain p=1 for fixed-family bookkeeping with a reason; do not impute favorable values.
6. Apply one Holm family of 29 paired tests, exact ties/zeros, whole-seed intervals and sign-test sensitivity. Clearly disclose that development outcomes informed this repair effort. An untouched test bank can provide held-out evidence for a prospectively frozen amended study; it cannot restore the original study's lost confirmatory status retrospectively.

**Artifacts:** isolated evaluator, qualification log, freeze manifest, held-out prediction/metric bundle, 29-contrast table and access log.

**Acceptance:** every frozen available cell scored once through the qualified path, denominators and model identities verified, no tuning after outcomes. Isolation/support failures block release and remain recorded.

## P4 — Measure resource costs rather than infer them

**Priority:** high for Phase 2 cost commitments. **Training:** reuse P2 instrumentation where possible; additional repeated training is budgeted.

Measure disjoint training, admission scoring, replay, Fisher, aggregation, checkpoint I/O, evaluator and oracle times. Preserve total elapsed time too; components must have a documented nesting policy to avoid double counting. Report CPU/device, threads, versions and co-load. Use matched methods/seeds/configurations for comparisons; observational archived timing alone is not a controlled benchmark.

Measure actual array/state allocations, replay metadata/logits/labels/IDs, EI importance/anchors and process RSS separately; explain shared allocations and peak measurement. Serialize real upload/download messages including class registry, counts and framing. Report measured serialized bytes separately from analytical weight-byte estimates; do not claim measured network delay without a network experiment.

For inference, use evaluation mode, batches 1 and 256, 10 warmups and 100 measured calls, reporting median, p95 and dispersion. Sample independent matched training repetitions only when the remaining budget supports them. If repeated timings cannot be completed, report representative observations and the limitation.

**Artifacts:** instrumentation contract, raw timing/byte records, latency distributions and accuracy/acquisition versus measured-cost figures.

**Acceptance:** resource claims name the measured quantity, included stages and measurement population; no edge-device, energy or deployment claim from desktop timings.

**Existing cost evidence:** `results/phase3-rigorous-audit-v1/measured-cost-summary.json` summarizes the earlier 76-feature records. New `submissions/phase3-audited-report/observed-run-costs-summary.json` independently verifies the adopted 74-profile completion hashes, collapses 273 exact copies, and summarizes elapsed wall time and compressed four-stage checkpoint sizes for all 417 unique trajectories. Its figure retains the two ~7,800-second quota-run outliers. The 74-profile result files add memory occupancy and limited inference observations, but do not separate training/admission/replay/Fisher/aggregation/I/O times or measure process RSS/allocation and serialized communication messages. Those cannot be recovered from elapsed totals; P4 remains partial and no training-only or communication-cost comparison is supported.

## P5 — Complete comparison, graphics and research discussion

**Priority:** high; required submission work. **Training:** none for report generation; an additional literature implementation needs an explicit cost/design card.

Build one results table covering FT, local EI, DR, matched DM and proposed DC, with identical split/seed/dose/metric definitions. DG is a separate Phase 2 global-filter control and is not fulfilled by DQ. Its selector is now implemented, but matched outcomes remain absent. Keep historical algorithms/results explicitly separate. Present per-seed values, effects and uncertainty alongside averages.

Create a literature comparability table: primary paper/code source, dataset/release, features, task (binary versus class-incremental), federation/ownership, attacker capability, split policy, metrics and available uncertainty. Verify quoted numerical claims against primary sources during execution. Do not rank incompatible reported accuracies as evidence that this method wins. Where an existing implementation can be run under the same scientific contract, document adaptation and add a matched experiment card before evaluation. If fair reimplementation is infeasible, make the contextual comparison and its limitations explicit.

Required figure/data inventory:

1. Learning curves by stage for baseline/proposed arms, with seed-level uncertainty.
2. Poison dose versus immediate damage and persistent error; absolute clean/attacked values alongside differences.
3. DC-minus-DM acquisition and FAR effects, showing the adverse trade-off.
4. Per-family precision/recall/F1 heatmap plus supported confusion matrices, with rare-class exclusions visible.
5. Ablation effects for loss, quota and eviction; actual poison exposure/occupancy over stages and oracle repair effects.
6. Measured training/inference/state/communication costs and associated performance trade-offs.

Each figure needs units, metric population, sample count, uncertainty definition, source table and generation command. Use readable vector exports; inspect the rendered report and caption consistency. Never hide zero, adverse or missing results by choosing axes or subsets.

Discuss each original question separately: learner susceptibility/persistence; acquisition-security trade-off of DC versus DM; what component interventions actually identify. DC currently has clean A about .2957 versus .3988 for DM and FAR about .1137 versus .0561. Diagnose admission composition, per-client/per-class score distributions, retained poison exposure, rare-class learning and aggregation weights using existing ledgers. If diagnostics expose a bug, repair the entire affected matched block. If they expose an unfavorable design trade-off, retain it as a scientific result. Any newly redesigned defense is a separately declared method, not a hidden replacement for Phase 2.

**Acceptance:** all seven assignment components point to explicit evidence; claims follow observed effects and design limits; figures/tables agree with predictions and analysis; no promised superiority or rubric mark.

**Post-audit mechanism diagnostic (read-only, 17 November):** `scripts/analyze_phase3_admission_mechanisms.py` verifies the completion-manifest hashes for all 96 primary DR/DM/DC result files, pairs 12 ownership seeds at four doses, and checks 192 matched admission-stage comparisons. Per-client, per-supplied-class raw/admitted counts are identical between DM and DC in all pairs; the per-client admitted-ID-set hashes differ in 109/240 client-stage comparisons at each dose. At dose .5, stored known-poison IDs average 163.1 (DM) versus 131.0 (DC) at E2 and 117.0 versus 92.1 at E4; paired whole-seed bootstrap intervals for DC-minus-DM are [-45.4,-19.1] and [-38.6,-11.8]. Stage-4 family F1 effects are retained by class and dose in `results/phase3-rigorous-audit-v1/admission-mechanism-v1/family-f1-effects.csv`. These summaries are consistent with selection identity and memory retention differing despite quota parity, but do not identify replay draws, gradient exposure, per-example score ranks, or client aggregation weights. They do not causally explain the FAR/acquisition outcomes. All analysis is on the reused development bank; no test data or training were used.

## P6 — Optional external evidence and final reproducibility handoff

The separate external check is optional under Phase 2 when infeasible. It is not a generic Phase 3 requirement to evaluate two datasets. Choose and document either qualified replication or justified omission before any external held-out outcomes. The existing 16 one-seed train-only pilot arms do not establish external efficacy.

For replication, lock the external release/schema/taxonomy, T0 transform, role isolation, stage support and dose semantics first. Transfer architecture/settings only. Use a separately estimated twelve-seed DR/DM/DC × clean/.5 design (72 full trajectories) if it fits authorized resources. A reduced exploratory design must be declared before outcomes. Do not pool metrics across incompatible feature spaces or claim deployment generalization.

The current audited nine-page report includes the hash-checked adopted-profile wall-time distribution, the matched DM/DC admission and stored-poison diagnostic, its reproducible source CSV/summary/figure, the DG omission, and the 2026 contextual citation. The current roll-number ZIP is fully hash-validated; the original pre-deadline ZIP remains preserved at SHA-256 `c219925799b2fe3b1d73e4203e25d1f94987b6c401f0288290f5f0bb67a2311f`. Full-evidence v26 contains the follow-up results/checkpoints, frozen source, primary-source ledger, cost and mechanism outputs, report/PDF validation, final-evaluator source and qualification; its independent verification passed with no final-test payload. Full-evidence v27 superseded v26 and added the report-clean-rebuild verifier and its passing record plus the updated feedback disposition; standalone verification passed for all 6,621 members. The latest full-evidence v28 supersedes v27 and packages the reconciled reproduction guide and current no-feedback status. Its digest and inventory are in `submissions/phase3-completed/full-evidence-v28-validation.json` and `results/phase3-rigorous-audit-v1/evidence-archive-verification-v28.json`. The previous eight-page report revision was exactly rebuilt from a fresh v21 extraction. The current nine-page revision has now also been rebuilt from a fresh selective extraction of v26: report TeX, source ledger, revision provenance, and cost CSV/summary match byte-for-byte; all nine pages match in extracted text and rendered pixels. The record is `results/phase3-rigorous-audit-v1/report-clean-rebuild-v26.json`, reflected in the detached v26 validation record. The checked-in verifier is `scripts/verify_phase3_report_clean_rebuild.py` and can be rerun with `python scripts/verify_phase3_report_clean_rebuild.py`. PDF container bytes differ because generated metadata may vary. Neither report build reproduces training or the full data audit. Full clean-directory scientific audit/re-execution has not been performed; historical 76-feature GPU weights remain unavailable.

The 696 historical GPU results lack saved model weights. Search existing named archives/checkpoint locations and request the original artifacts if necessary; never invent them. If unavailable, close the reporting obligation by retaining the explicit historical reproducibility limitation. New qualified results do not prove old executions.

## Exhaustive disposition of the 22 audited findings

| Finding IDs | Required disposition |
|---|---|
| R01, R10 | P0 amendment register; retain corrected threat/source/taxonomy claims |
| R02, R03, R20 | Preserve corrected semantics; P0/P2 regression acceptance; quarantine historical engine |
| R04, R05, R06, R08, R15 | Retain corrected statistics, endpoints, cohorts, counts and null convention; apply consistently in P3/P5 |
| R07, R19 | P0 canonical/frozen identities and P6 clean-directory reproduction |
| R09 | P3 qualified held-out evaluation; pending until gates pass |
| R11, R12 | P2/P5 diagnostics and honest adverse/weak-effect interpretation; no forced favorable result |
| R13 | P2 FIFO/class-balanced experiment or explicit incomplete Phase 2 ablation scope |
| R14 | P4 measured costs and bounded claims |
| R16, R21 | P1 independent upstream reconstruction and threshold sensitivity; retained limits |
| R17 | P6 qualified external replication or justified optional omission |
| R18 | P0 genuine feedback evidence or explicit unavailable status |
| R22 | P6 original-weight recovery if possible; otherwise permanent historical evidence limit |

## Execution order, resource boundaries and completion definition

Execute P0 → P1 → evaluator qualification in P3. Implement P2 semantics and P4 instrumentation before scheduling any new training; forecast complete blocks against remaining resources. Finish the declared development ablations and freeze scientific choices before releasing P3 held-out outcomes. Then generate P5 and complete P6 packaging. P6 external protocol design may proceed independently; its outcomes follow its own qualification/freeze gates.

Do not give a reliable total wall-clock promise before raw-reconstruction I/O, evaluator throughput and actual training timings are measured. Existing evidence estimates eviction near the prior six-hour cap; a full external study or a data-defect rerun is not implicitly funded by that estimate. If mandatory work cannot fit, record the exact incomplete requirement and revise scope transparently; do not call the full Phase 2 experimental plan complete.

Completion means: all seven Phase 3 requirements have traceable artifacts; every retained Phase 2 commitment is verified or explicitly amended/limited; all claimed comparisons use qualified matched evidence; completed baselines and ablations are reported with essential metrics; figures are reproducible; the final report explains whether each research objective was supported, contradicted or inconclusive. Negative findings are acceptable. Missing evidence, favorable-looking plots or more experiment files do not substitute for these conditions.
