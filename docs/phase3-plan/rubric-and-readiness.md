# Phase 3 rubric and evidence gates

This is an evidence map, not a completed-results claim. The audit improves the plan and supplies conditional data feasibility evidence. The revised learner and final experimental evaluation remain to be built.

## Required submission components

| Rubric item | Required concrete evidence | Present state | Completion action |
|---|---|---|---|
| 1. Implement methodology and feedback | Versioned engine, protocol-to-function map, actual feedback/deviation record | Legacy implementation has material differences; exact Phase 3 specifications now detailed; actual instructor feedback unavailable | Implement the reference engine, cross-review its semantics, record real feedback |
| 2. Dataset and preprocessing | Release/member hashes, schema/units, calibration IDs, exclusion ledger, components, train/dev/test IDs, per-class/site/stage counts | Two full archives and conditional censuses/audits available; final profile not adopted | Resolve source/domain/taxonomy/sampling amendments and export immutable training/evaluator packages |
| 3. Baselines and metrics | Correct FT/EI/DR, fair development selection, clean/poisoned paired outcomes, confusion-derived endpoints | Baseline and analysis contracts specified; no revised learner outcomes | Implement, obtain acceptance evidence, develop and freeze settings before final matrix |
| 4. Graphical results | Reproducible figures with fixed denominators, uncertainty units, raw seed points and count tables | Figure specifications and data-feasibility plots only | Produce model-result figures from sealed predictions after complete selected runs |
| 5. Existing research comparison | Closest comparable methods, protocol alignment table, traceable published versus reproduced results | Primary-source ledger and limits documented; no reproduced research outcomes | Choose claim-relevant comparisons; prohibit direct leaderboard ranking across incompatible protocols |
| 6. Ablations | From-start NoZ/NoY/FIFO, DQ matched quotas if selected; complete controls and exploratory labels | Exact interventions and run counts specified | Execute selected package and report all conditions, including adverse/unavailable results |
| 7. Discussion and reproducibility | Claim/evidence matrix, limitations, cost measurements, artifact recipe and independent exercise where claimed | Interpretation and resource contracts detailed; actual measurements/results absent | Discuss observed magnitudes and failure modes; archive immutable materials and record reproduction evidence |

## Gates and accountable outputs

### Gate 0: Freeze the data question - Author A, reviewed by B

Deliver an adopted profile with exact release, taxonomy/stage mapping, domain policy, clock, canonical feature order/units, calibration eligibility, graph construction, split, benign selection and ownership rules. Attach source/member digests, additive exclusion ledger, support by role and component, and per-seed realized dose/ownership counts. Candidate counts are useful evidence but do not sign off the final profile automatically.

Stop on absent source support, ambiguous aliases or inconsistent identities. Do not solve insufficient support by changing split seeds until a favorable table appears. Keep rare families visible/descriptive and justify any stage amendment prospectively.

### Gate 1: One correct complete reference trajectory - Author B, reviewed by A

Implement the narrow growing-head FT/FedAvg engine. Add EI and replay only after broadcast/optimizer/state semantics are clear. Required acceptance work includes hand-checkable quota/poison examples, class registration/head preservation, immutable client starts, per-example importance, pre-update targets, first-pass reservoir accounting, full-head evaluation and no final-test access. These are planned acceptance requirements; this audit did not run model tests.

Give each requirement an artifact path, code revision, reviewer and disposition. A successful launch or decreasing loss is insufficient evidence.

### Gate 2: Durable recovery and efficient execution - both authors

Demonstrate a resumed trajectory continues the complete model/client/replay/RNG/cursor state, and imports artifacts with matching identities. Preserve PCG64's 128-bit integers without JSON rounding. Profile CPU and actual Kaggle hardware with category-specific workloads; report charged session time separately from training time. Avoid running preprocessing/statistics while a GPU session is charged.

### Gate 3: Development and scientific lock - both authors

Resolve clean-gate selection order, hyperparameter ties, development-runtime compatibility and scope. Record knowledge already visible, including prior legacy benchmark analysis and all candidate data censuses. Freeze code/data/runtime/analysis identities, all twelve seeds, missingness rules and primary/exploratory designations. No final learner outcome is currently known from this audit.

### Gate 4: Complete selected matrix and sealed evaluation

Use eight individually operated contributor workers to execute immutable paired seed jobs; each runs five simulated clients. Check completeness, parent identities, failure dispositions and runtime compatibility. Preserve planned failed cells. A corrected implementation rerun needs a documented invalidation scope; a scientifically adverse result is not an invalid run.

Use a common read-only evaluator after the selected matrix gate. Publish counts and all metric banks, including rare-family/full-seen binary denominators and the fixed benign mixture. Keep exploratory results distinct from the 29-test confirmatory family.

### Gate 5: Submission and publication decision

The course report must satisfy all seven rows with real results. A paper additionally needs a specific informative finding, fair closest-method comparison, calibrated threat/generalization claims and actual external critique. Independent artifacts, captures and organizations are different evidence levels. Neither eight worker accounts nor thousands of session components establishes eight sites or thousands of independent attack campaigns.

## Minimum useful next milestone

Adopt the audited data profile and build one complete correct reference trajectory. The next milestone is not a larger GPU grid. Use [implementation-work-breakdown.md](implementation-work-breakdown.md), [protocol-closure-spec.md](protocol-closure-spec.md) and [component-and-control-spec.md](component-and-control-spec.md) for the detailed construction tasks.
