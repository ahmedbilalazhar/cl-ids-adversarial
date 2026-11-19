# Phase 3 rubric and evidence gates

This is an evidence map, not a completed-results claim. Status updated 17 November 2026: the adopted 74-feature study has a 240-cell core, 24 DQ cells, 48 replay-loss ablations, 96 alternative-quota ablations, nine clean confirmations, and 24 oracle continuations. A new independent audit verifies 417 unique full-run records, 273 exact cross-directory copies, all 1,716 unique stage/oracle checkpoint files against recorded model identities, and all 417 confusion-derived metric rows including paired H and immediate-recall calculations. These are development-bank outcomes under the historically selected DR lambda_z=.1 and do not replace the separate untuned lambda_z=.5 implementation reference. DG has a deterministic selector but no adopted-profile outcomes; FIFO/class-balanced eviction, final held-out evaluation, and full cost measurement remain incomplete. The follow-up completion manifest reports 32,655 seconds (9.07 hours) for its 408-run execution count, exceeding the earlier six-hour training ceiling; no further training is scheduled.

## Required submission components

| Rubric item | Required concrete evidence | Present state | Completion action |
|---|---|---|---|
| 1. Implement methodology and feedback | Versioned engine, protocol-to-function map, actual feedback/deviation record | Substantial corrected engines exist; the adopted 74-feature CPU extension executes FT/EI/DR/DM/DC with a frozen 12-seed protocol and has a separate one-shot evaluator. FIFO/class-balanced are smoke-run only. User confirmed no specific class feedback was given; no approval is claimed. Final test remains gated | Retain the disclosed profile/method amendments and exact frozen source/data identities; add genuine feedback only if received |
| 2. Dataset and preprocessing | Release/member hashes, schema/units, calibration IDs, exclusion ledger, components, train/dev/test IDs, per-class/site/stage counts | Corrected 74-feature profile adopted; independent audits match all 2,099,976 source rows, all 74 FP32 inputs, validity/exclusion/quarantine masks, survivors and retained split positions. Independent 120s graph/T0 matches; zero cross-role component overlap. SGKF output was reused after exact identity proof, not rerun. Test rows remain sealed/unexported | Preserve the frozen data package and support tables; keep provider/session validity limits explicit and export test data only after the final freeze gate |
| 3. Baselines and metrics | Correct FT/EI/DR, fair development selection, clean/poisoned paired outcomes, confusion-derived endpoints | Audited 240-run matched adopted-profile development core covers FT/EI/DR/DM/DC × four doses × twelve seeds, plus 24 DQ cells and 24 oracle suffixes. It uses previously selected settings and a fresh clean gate, not independent tuning or holdout. DG outcomes and FIFO/class-balanced eviction ablations are absent; the DG selector is implemented but unrun on the adopted data. Adopted-profile replay-loss and alternative-quota ablations are present. The separate lambda_z=.5 reference remains n=1. No final-test outcomes | Preserve the historical selection provenance and frozen settings; no additional training fits the six-hour cap, so report missing cells honestly |
| 4. Graphical results | Reproducible figures with fixed denominators, uncertainty units, raw seed points and count tables | Audited 76-profile figures, the 74-profile core-results figure, and the matched quota-ablation figure exist; the core plot reports ownership-seed uncertainty and is backed by the 240-cell metric table. The separate lambda_z=.5 reference stage figure remains n=1. FIFO/class-balanced mechanism and complete cost figures remain absent | Refresh figures after matched experiments and identify population/uncertainty/source for every plot |
| 5. Existing research comparison | Closest comparable methods, protocol alignment table, traceable published versus reproduced results | A contextual protocol-alignment matrix is linked from the reference report. The local FT/EI/DR/DM/DC comparisons now use matched adopted-profile runs; published results remain qualitative and no incompatible paper scores are ranked against them | Verify primary-source details for any quoted numerical claim; complete matched local baselines under the adopted profile |
| 6. Ablations | From-start NoZ/NoY/FIFO, DQ matched quotas if selected; complete controls and exploratory labels | The adopted-profile 48 replay-loss and 96 alternative-quota cells are complete and pass the paired input/settings audit. FIFO and class-balanced have smoke runs only; the matched 96-trajectory block remains unrun because its conservative estimate is 8.52 hours with reserve. The follow-up study execution itself took 9.07 hours, exceeding the earlier six-hour ceiling. | Record the block as incomplete unless a separately authorized feasible compute budget becomes available; do not mislabel smoke runs |
| 7. Discussion and reproducibility | Claim/evidence matrix, limitations, cost measurements, artifact recipe and independent exercise where claimed | Adverse DC effects and limitations are discussed in the generated CPU-extension report; all 273 confusion-derived table rows were independently rescored from stored matrices. Observational elapsed/weight-size costs and a reproducible CPU forward-pass microbenchmark exist. The latter measured 62.6 to 64.1 microseconds median for batch 1 and 0.181 to 0.196 milliseconds per batch of 256 (0.706 to 0.764 microseconds/record); preprocessing, loading, RSS, serialized messages, network delay, energy and training-only component costs remain unmeasured. Complete clean-directory reproduction remains absent | Refresh report/package from accepted evidence and keep all unsupported claims bounded |

## Gates and accountable outputs

### Gate 0: Freeze the data question - Author A, reviewed by B

The adopted profile, source/member digests, exclusion/quarantine masks, support tables, component/T0 contract, retained splits, ownership IDs and realized dose counts are frozen and independently audited. Remaining limits include provider authentication and physical/session identity; do not describe these as resolved.

Stop on absent source support, ambiguous aliases or inconsistent identities. Do not solve insufficient support by changing split seeds until a favorable table appears. Keep rare families visible/descriptive and justify any stage amendment prospectively.

### Gate 1: One correct complete reference trajectory - Author B, reviewed by A

The adopted 74-feature CPU runner completed the 240-cell matched development core and passed independent cell, result-hash, confusion-score, and checkpoint-file audits. The separate final evaluator passed nine synthetic contract tests, but has not been qualified on a real final package or held-out data.

Give each requirement an artifact path, code revision, reviewer and disposition. A successful launch or decreasing loss is insufficient evidence.

### Gate 2: Durable recovery and efficient execution - both authors

Demonstrate a resumed trajectory continues the complete model/client/replay/RNG/cursor state, and imports artifacts with matching identities. Preserve PCG64's 128-bit integers without JSON rounding. Profile CPU and actual Kaggle hardware with category-specific workloads; report charged session time separately from training time. Avoid running preprocessing/statistics while a GPU session is charged.

### Gate 3: Development and scientific lock - both authors

Resolve clean-gate selection order, hyperparameter ties, development-runtime compatibility and scope. Record knowledge already visible, including prior legacy benchmark analysis and all candidate data censuses. The development identity, twelve seeds, historical selection provenance, and exploratory/confirmatory separation are frozen. Do not treat the development-bank scores as final confirmation. A genuine final-test run remains gated on qualifying the real package and preserving its one-shot role boundary.

### Gate 4: Complete selected matrix and sealed evaluation

The 240-cell CPU core and 144 adopted-profile replay-loss/quota ablations pass independent cell and metric audits. DG outcome cells and matched FIFO/class-balanced remain unrun; the fixed-fraction DG selector is coded and synthetically checked. The later follow-up manifest records 9.07 hours, above the earlier six-hour cap; do not schedule further training under that cap.

Run the one-shot evaluator only after a valid real-package freeze is established. No final-test payload or score is presently included in the evidence archive.

### Gate 5: Submission and publication decision

The course report must satisfy all seven rows with real results. A paper additionally needs a specific informative finding, fair closest-method comparison, calibrated threat/generalization claims and actual external critique. Independent artifacts, captures and organizations are different evidence levels. Neither eight worker accounts nor thousands of session components establishes eight sites or thousands of independent attack campaigns.

## Minimum useful next milestone

Complete the remaining non-training work: reconcile all audit documents, include raw follow-up evidence and the independent verifier in a versioned evidence archive, verify primary literature claims, and document the unresolved held-out/DG/eviction/cost/instructor-feedback limits. No further training block is scheduled.
