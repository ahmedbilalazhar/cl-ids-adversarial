> Current continuation, 2026-10-25: CPU v3 is verified; Kaggle v4 corrects selected-setting binding. Final scope, actual CUDA equivalence and durable Kaggle recovery remain gated. Historical instructions below retain their original scope. See [continuation audit](../phase3-cpu-v3/continuation-audit.md).

# Recommended Phase 3 plan

**Implementation update:** the user has adopted the corrected 74-input data
amendments and resolved the 16-class annotation taxonomy. Continue at the
[reference implementation](../phase3-reference/README.md) and its
[adoption record](../phase3-reference/adoption.json). The audit narrative below
records earlier planning status; its prospective statements do not undo the
later versioned adoption. The final GPU grid remains non-dispatchable.

Reviewed recommendation, 24 October 2026. Two authors, eight individually operated contributor accounts, five simulated FL clients. No Phase 3 model results or learner/GPU runtime measurements have been produced in this task.

**Latest audit:** begin with [audit-executive-summary.md](audit-executive-summary.md), then read [second-audit-gap-register.md](second-audit-gap-register.md) and [data-release-decision.md](data-release-decision.md) before dispatch. Full candidate data censuses now expose support, clock and isolation issues that the earlier header probe could not establish. Data-audit timings are not learner/GPU benchmarks.

## Latest source-semantics recommendation

Read [feature-semantics-and-final-recommendation.md](feature-semantics-and-final-recommendation.md) first. The preferred prospective corrected-data candidate now omits the two lossy header-total fields (74 inputs, A31), after positive consistency violations survived the earlier negative-only screen. It has 16 train-supported outputs; earlier 76-feature candidate counts remain separately labeled. Adopt the feature/taxonomy changes and retune before final execution.

## The decision

Build a precise, reproducible **empirical study of label-poisoning persistence and new-class acquisition**. Start with the course-complete package, add the control that isolates loss ranking, and add an external replication only after its data audit succeeds. Keep the original complete proposal as a documented option; select any scope amendment before final-test access.

| Target | What it contains | Logical full trajectories | Distinct full executions if nine dev aliases are valid | New E3/E4 diagnostic executions if controls alias primary |
|---|---|---:|---:|---:|
| Course complete | 81 development + 240 core + 72 from-start ablations | 393 | 384 | 12 |
| Focused research starter | Above + 48 class-quota random-control runs | **441** | **432** | **12** |
| Focused research with external replication | Above + 72 independently audited DR/DM/DC external runs | **513** | **504** | **12** |

The original diagnostic has 24 logical pair rows; twelve controls can alias existing primary suffixes. Prefix sharing saves additional partial-stage work. These counts are not GPU-hour estimates or extra independent samples.

The external subset checks the admission comparison on another source. It does not replicate FT-versus-EI-versus-DR conclusions there. Broader claims would require broader replication.

## Why this scope

- FT/EI/DR compare retention mechanisms.
- DM/DC compare admission composition with equal per-client volume and aggregation weights.
- DQ uses DC's exact class quotas but random selection, isolating whether loss ranking contributes.
- No-logit, no-replay-label and FIFO ablations investigate three components from the beginning of training.
- Oracle label repair after E2 probes continued erroneous-label replay, with limited causal interpretation.
- Twelve complete paired seeds remain the statistical units.

DG, additional keep fractions, class-balanced eviction, source-rich attacker selection and recurrence are optional studies tied to specific claims. Do not expand all of them by default.

If selected learner rates differ and the paper intends to attribute susceptibility specifically to retention, budget a conditional FT reference at the other learning rate: at most 24 extra full clean/maximum-dose trajectories. The 441/513 bases compare separately tuned pipelines; they do not isolate learning rate automatically.

## First actions for the two authors

1. **Data gate — Author A.** Adopt the audited release/domain/taxonomy profile; verify its final role/support manifests, benign bundles and per-seed ownership/doses. The local MachineLearningCSV files alone cannot satisfy the proposed session split.
2. **Reference engine — Author B.** Implement the narrow `src/phase3/` state machine, beginning with FT/FedAvg. Reuse the small MLP helper after resolving initial-head semantics. Preserve the legacy runners/results separately.
3. **Cross-review.** A reviews corruption, retained state and optimizer/broadcast order. B reviews split/support, denominators and analysis. Keep a concrete acceptance-evidence report.
4. **Measure.** Profile CPU and the actual available GPU on representative complete workloads. Use prepared arrays, fixed replay buffers, chunked per-example Fisher and minimal host/device synchronization.
5. **Develop.** Run the 18 synchronization pilots, resolve the 60-row tuning grid and the three FT poison diagnostics. Reuse matching pilot rows only with exact identity.
6. **Freeze.** Select scope from measured costs and available quota; freeze code/data/runtime/analysis, twelve final seeds and all deviations before final outcomes are viewed.
7. **Dispatch.** Contributors run immutable paired seed jobs, return saved artifacts and report failures. Each job simulates all five clients; no cross-account distributed training is needed.
8. **Evaluate and write.** Use a common read-only evaluator, paired endpoints, the fixed 29-test Holm family and reproducible figures. Report null/adverse results and incomplete conditions honestly.

## Eight-person compute strategy

Use each person's actual remaining quota and compatible hardware availability. At a hypothetical 30 hours remaining per person with a 20% reserve, aggregate usable capacity is 192 quota-hours. Actual capacity is unverified. Do not multiply it again by the number of GPUs in a session.

At a purely hypothetical ten charged minutes per distinct full execution, the focused starter requires 72 hours and the external version 84 hours **before** suffixes, setup, saving and any evaluation/confirmation work, and before discounting E1 reuse. At twenty minutes those base figures double. Replace these scenarios with category-specific measurements. [Kaggle GPU guidance](https://www.kaggle.com/docs/efficient-gpu-usage).

Keep paired methods/doses on compatible runtime signatures. Twelve seed blocks do not pack evenly into eight accounts: aggregate capacity can pass while a person assigned two expensive blocks exceeds their quota. Rebalance unstarted physical jobs, use compatible block fragments or a later allocation period; never change methods or discard seeds to fit.

Stop GPU sessions during preprocessing, routine debugging, statistics and report work. Use bounded jobs, complete round/stage checkpoints, immutable package hashes and verified saved outputs. A live `/kaggle/working` checkpoint is not durable against every failure.

## Scientific mistakes this plan addresses

1. **Existing code is not the revised methodology.** The original source audit identifies 31 implementation gaps. The second review expands the combined register through G64, including data feasibility, statistical interpretation and optional controls. Documented resolutions still need implementation evidence.
2. **DC is not a demonstrated general purifier.** In the primary schedule it protects every supplied new attack class and filters benign-labelled rows. Its retained-poison floor is `max(0,K_B-b)` for benign quota K_B and honest benign count b.
3. **A small H is not automatically good security.** A model with high clean error has little remaining headroom for poisoning damage. Show absolute clean/poisoned error with H.
4. **Untargeted-new F1 is not an isolated learning measure.** False positives from Hulk can affect it. Show precision/recall and confusion sources.
5. **Poison surviving in memory does not prove causation.** Use explicitly scoped interventions and actual replay exposure; oracle repair leaves earlier weight/logit damage intact.
6. **Generic novelty claims are unsafe.** Prior work already covers adversarial FCL, durable FL attacks, weak single-task poisoning and noisy replay. The paper needs an informative specific finding.
7. **Training instability is a result when the implementation is correct.** Do not replace failing seeds, average only successes or silently stabilize one method.
8. **A simulation is not field deployment.** Report historical capture, simulated sites, fixed split, threat capability and resource boundaries accurately.

## Dataset contingency

The full corrected archive and a commit-pinned public mirror of the original metadata-bearing archive have now been downloaded and integrity-audited. The original candidate has 2,830,743 nonempty records plus 288,602 blank trailing CSV records; its time strings lack AM/PM and mostly lack seconds. Mirror identity is verified; provider authentication remains separate. No form was submitted.

The corrected candidate has 2,099,976 records. With attempted traffic mapped to benign, confirmed E3 web-brute/XSS/SQL counts are only 73/18/13 and ordinary Infiltration has 36; none can meet 50/50/50 rows. Its additional Infiltration-Portscan label requires a semantic taxonomy/stage decision and potentially a sixteen-output maximum. It is not a drop-in fallback. `Attempted Category` never becomes a predictor.

The conditional original component audit also removes substantial source data through T0/content closure. Its clock, calibration and quarantine-link choices must be adopted explicitly, and actual split support checked. Preserve the original and corrected releases as distinct data contracts; they are the same capture, not independent external evidence. See the source census and conditional audit files linked from the release decision.

## Timeline and publication standard

The deadline and actual class feedback remain unknown. Use the ten-working-day course template as an aggressive starting point, then revise from data/reference progress. A publication candidate needs additional time for independent evidence, analysis, literature refresh and actual external critique.

Aim for traceable data, correct baselines, fair controls, measured costs and calibrated claims. Publication cannot be guaranteed before an informative finding exists. A strong negative or conditional result is preferable to an unsupported defense claim.

## Where to work from

- [plan.md](plan.md): complete implementation and rubric plan.
- [implementation-work-breakdown.md](implementation-work-breakdown.md): two-author tasks and dependency gates.
- [data-and-interface-contract.md](data-and-interface-contract.md): builder, typed interfaces and state machine.
- [compute-budget-and-scheduling.md](compute-budget-and-scheduling.md): quota arithmetic and packing.
- [methodological-risk-review.md](methodological-risk-review.md): endpoint interpretation and intervention limits.
- [protocol-closure-spec.md](protocol-closure-spec.md): exact allocators, Monday-only calibration, dose-volume and scoring consequences.
- [evaluation-strengthening.md](evaluation-strengthening.md): operational errors, power, controls, uncertainty and continual-metric limits.
- [component-and-control-spec.md](component-and-control-spec.md): ablation, FIFO, class-partitioned reservoir and mechanism definitions.
- [README.md](README.md): complete index, manifests and primary-source ledger.

- [rubric-and-readiness.md](rubric-and-readiness.md): seven course requirements, current evidence and accountable completion gates.
- [feature-domain-and-precision-review.md](feature-domain-and-precision-review.md): observed invalid domains, prospective quarantine, scaler and FP32 consequences.
- [candidate-data-profiles.json](candidate-data-profiles.json): explicit unselected source/profile alternatives.

## New feasibility decision evidence

The screened corrected candidate passes the required source/anchor and stage support gates with zero component overlap. E3 count support comes from Infiltration-Portscan; web families remain descriptive. Its distinction from Friday PortScan needs semantic justification before claiming a new attack family. Heartbleed is test-only, so there are fifteen train-supported active outputs despite sixteen annotated labels. The proposed bundle selector reaches 3,500 benign examples at all stages. DC is forced to retain poison in ten of twelve maximum-dose seed inventories; this is a quota limit, not an observed accuracy result. See [realized-dose-and-quota-limits.md](realized-dose-and-quota-limits.md) and [capture-context-and-generalization.md](capture-context-and-generalization.md).
