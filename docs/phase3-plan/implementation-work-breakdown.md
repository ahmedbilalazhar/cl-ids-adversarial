> Current continuation, 2026-10-25: CPU v3 is verified; Kaggle v4 corrects selected-setting binding. Final scope, actual CUDA equivalence and durable Kaggle recovery remain gated. Historical instructions below retain their original scope. See [continuation audit](../phase3-cpu-v3/continuation-audit.md).

# Implementation work breakdown for two authors

Proposed work, 24 October 2026. Estimates are planning ranges and need revision after the first data/reference milestones. Eight compute contributors help with execution; the two authors remain responsible for protocol correctness and interpretation.

## 1. Delivery order and ownership

| ID | Work item | Owner | Dependency | Deliverable / exit evidence |
|---|---|---|---|---|
| W01 | Reconcile instructor feedback and revised Phase 2 | Both | None | Requirement/amendment table; unresolved items explicit |
| W02 | Obtain canonical metadata-bearing release | A | W01 | Source manifest, access route, hashes and sample schema |
| W03 | Build canonical rows, session/content components and T0 | A | W02 | Versioned builder and census, no cross-split component/content overlap |
| W04 | Lock split/support and benign pools | A | W03 | Fixed split manifests and eligibility report; stop if required support fails |
| W05 | Define typed protocol/state schemas | B, A reviews | W01 | Small interfaces from the data contract; legal transition table |
| W06 | Build MLP, active registry and expansion | B | W05 | Parameter count/slot/init evidence; full active head remains trainable |
| W07 | Implement FT and immutable-broadcast FedAvg | B | W06; small synthetic builder input | One reference trajectory; exact client weighting/reset order |
| W08 | Implement seed ownership/corruption | A | W04/W05 | Whole-component allocation and nested source-denominator poison manifests |
| W09 | Implement DG/DM/DC admission | B, A reviews | W06/W08 | Stable ranking/quota evidence; equal DM/DC count and weights |
| W10 | Implement first-pass Algorithm R and DER losses | B | W07 | Fixed buffers, pre-update targets, independent replay batch length, mode/width evidence |
| W11 | Implement per-example importance and stage commit | B, A reviews | W07 | Reference gradient calculation, accumulation, new-coordinate handling |
| W12 | Implement checkpoint/import identities | B | W05/W07; extend through W10/W11 | Atomic complete state, exact restart boundary, conflict rejection |
| W13 | Implement independent evaluation banks/counts | A | W04/W06 | Fixed row order, full active predictions, confusion/endpoint arithmetic |
| W14 | Implement paired analysis and figures | A | W13; use synthetic count examples | 29 contrasts, fixed zero/tie/Holm handling, whole-seed resampling |
| W15 | Produce acceptance evidence | Both cross-review | W08–W14 | Data, state, learner and recovery evidence under fixed runtime |
| W16 | Profile CPU/GPU and optimize measured bottlenecks | B; A records costs | W15 | Cold/end-to-end component timing and resource sheet |
| W17 | Execute development pilot/tuning/diagnostic | Both | W16 | Chosen common budget/settings and clean-learning gate report |
| W18 | Lock final scope, code/data/runtime/analysis | Both | W17 | Immutable release bundle and manifest; final-test access remains separate |
| W19 | Run paired final blocks and selected ablations | Contributors, B coordinates | W18 | Complete verified output bundles, no worker-side method changes |
| W20 | Evaluate and analyze locked artifacts | A, B reviews | W19 selected matrix complete | Prediction/count tables, estimates, figures and failure inventory |
| W21 | Write report and claim ledger | Both | W20 | Every rubric item, limitations, amendments and reproducibility instructions |
| W22 | Critique/revise for publication | Both / later independent reviewer | W21 | Prior-art refresh, claim calibration and identified additional evidence needs |

W02–W04 and W05–W07 can progress concurrently. Large runs do not start while W15 is incomplete. Analysis code can be written against small synthetic count examples before final outcomes exist, reducing outcome-dependent analytic choices.

No acceptance tests or training have been executed as part of this planning task. The items above specify future implementation work, including the checks the authors should run when implementing.

## 2. Small reference before optimized engine

Build the first implementation for clarity:

- One immutable server model per round and explicit per-client local copies.
- Sequential client execution in a single process.
- Ordinary FP32 Adam and batch size 128.
- NumPy/torch fixed-capacity replay arrays.
- A simple per-example gradient loop on a tiny reference sample, then the vectorized implementation.
- Stage/round checkpoints rather than arbitrary-instruction recovery.
- JSON/array result bundles and one central importer.

Avoid a new distributed FL stack, DDP, multiprocessing shared mutable state or a database before the reference behavior is established. A small simulator can implement the research question without reproducing a real federated network.

## 3. Exact update accounting

For client k with n admitted current rows, E local epochs and R rounds:

```text
current updates = R * E * ceil(n / 128), when n > 0
first-pass insertion proposals = n
replay draw per update = min(128, current occupancy)
```

Do not drop the last current batch or shorten replay to match it. Each loss term has its own mean. Log real current/replay sample counts, not just epochs. Filtering changes the number of optimizer updates; equal epochs alone does not equalize computation. DM/DC have equal counts and batch-shape budgets within a matched condition, which is part of their value as a control.

For EI, every active client's stage-end importance sample is exactly `min(1024,n)`, distinct and uniform without replacement. With five active clients and four stages, at most 20,480 per-example gradients are needed per full trajectory; their cost must be measured separately from training. This is an operation count, not a runtime forecast.

For no-logit/no-label component ablations, preserve the declared storage/insertion policy and disable only the specified loss coefficient. Keep the tuple schema and auditing policy consistent; do not silently turn a loss ablation into a different memory method. An unfiltered no-logit ER reference using DR-selected settings is a component comparison, not an independently optimized published ER reproduction.

## 4. Useful common random numbers

Use independent named RNG streams for ownership, attacker selection, poison ordering, initial/head weights, current-row order, replay draws, insertion, importance and dropout. Save each stream's state or an exactly reconstructible key/counter.

A useful order implementation is to generate one uniform permutation of each client's complete current-stage IDs per seed/round/epoch and take the admitted subsequence for each admission arm. This remains a uniform order of each admitted subset and gives common records a common relative order. It can be reused efficiently without letting a shorter accepted list alter the poison or head draws. Freeze this choice before development; it is not a requirement to force identical dropout/replay behavior after treatments diverge.

PyTorch dropout does not accept an ordinary generator argument. Scope and persist the appropriate CPU/CUDA RNG state around each client training segment. Data-loader seed creation and new-head constructors must not consume the dropout or poison stream inadvertently. Validation, logging and oracle auditing must not advance training RNG streams.

## 5. Development dependency order

1. Run 18 clean synchronization pilots with the fixed pilot defaults.
2. Select the common round/epoch budget using the declared development criterion.
3. Run/resolve the 60-row tuning grid, aliasing the nine matching pilot rows only if exact identity is established.
4. Select clean FT/EI/DR settings under the declared tie rule; all admission arms inherit DR settings.
5. Resolve the predeclared clean-gate/model-selection order and check clean acquisition/numerical feasibility.
6. Run the three maximum-dose FT diagnostics only after clean settings pass, using compatible selected clean FT rows as controls. A weak attack is a reportable diagnostic, not an escalation gate.
7. Measure final-block costs, choose scope without final test outcomes, and freeze the package.

Clarify the clean gate per learner/family before implementation: the recommended interpretation checks each required anchor for each unfiltered selected learner, averaged over development seeds, and Hulk at acquisition. A filtered method's later poor acquisition is an experimental outcome; do not invalidate it simply for losing to the clean gate. Any clarification of the original ambiguous wording belongs in the amendment log.

## 6. Minimal contributor handoff

Each contributor receives:

- Private immutable code/dependency and train/development packages with expected hashes.
- Assigned whole seed blocks and a condition list; these are simulated five-client experiments.
- The exact runtime/device/precision requirement and a place to record actual remaining quota.
- A bounded notebook/worker entry point that verifies inputs, continues compatible checkpoints and stops before its time budget.
- Expected output filenames, completeness rules and version-specific download instructions.

The contributor records the environment, runs the assigned package without changing settings, returns its saved version and hashes, and reports a failure code when blocked. The authors validate/import artifacts. No one needs to send a Kaggle credential to the authors.

Do not place final-test arrays or credentials inside a package that will be copied to all contributors. Keep mounted dataset versions immutable; notebook collaboration does not automatically grant dataset access.

## 7. Timeline with honest scope

### Course-complete track

The ten-working-day table in the main plan is an aggressive dependency template, feasible only if canonical data access and the small reference engine stabilize promptly. Budget approximately 15–20 author person-days across the two authors, then revise from measured progress. Reserve time for failed data gates and matched reruns.

### Publication-candidate track

Allow additional weeks for a genuinely informative control set, independently audited external evidence where justified, result interpretation, literature refresh and actual independent critique. A planning allowance of 15–25 working days is more realistic than promising a publishable paper in ten days; this is still conditional, not a delivery guarantee. Results may show that the current proposal supports a course report but needs a different contribution for publication.

### If the deadline is short

Preserve valid data, paired seeds, baseline learning and meaningful ablations. Defer DG, broad keep-fraction sweeps, external data or recurrence according to the pre-test priority decision. Use post-E2 forks only if their narrower question and methodology amendment are accepted. Never substitute legacy incompatible results or manufacture a positive security claim to fill the report.

## 8. Definition of done

The implementation phase is ready for analysis only when the selected matrix is complete/validated or every missing condition has an explicit failure disposition. The report is ready when every claim maps to a validated table/figure and every rubric item has concrete evidence. A repository upload or a notebook that ran once is not this completion criterion.


## Continuation tasks and dependencies (25 October 2026)

The earlier work breakdown is historical planning. These tasks control the next
phase; none authorizes final data access. See [execution contract](kaggle-execution-contract.md).

| ID / objective | Prerequisites / interfaces | Procedure and acceptance evidence | Failure / downstream |
|---|---|---|---|
| K01 Actual runtime qualification | v4 bundle, notebook generator, `runtime.configure`, `checks.run`; actual CUDA allocation | Install pinned environment; run CPU then CUDA fixtures; preserve logs and device/build hashes. Compare primitive tensors using existing tolerances, exact integer/ID state and recovery; independently disposition dropout-stream differences before whole-trajectory claims | Preserve failure; do not relax tolerances. Blocks K02, K04 |
| K02 Target clean feasibility and cost | K01, `selection.selected_settings`, `worker.run_job`, `evaluate.evaluate`; matching packages for dev101–103 | Execute selected FT/EI/DR clean conditions on actual target runtime. Record component and command costs, mean acquisition gates and every per-seed result. No seed replacement; pass only with intact hashes and declared gates | Keep adverse results. Scientific change needs prospective revision and affected matched reruns. Blocks K04 |
| K03 Provider durability | K01, worker/checkpoint/handoff modules | Interrupt fixture after committed round; save/download/hash output; end session; restore matching source/runtime; resume; compare full state/predictions to uninterrupted fixture; corrupt payload and duplicate-writer attempts must reject | Keep partial segments and retry lineage; no new replicate. Blocks K04 |
| K04 Final scope and adapters | K01–K03, `continuation-scope.json`, original manifest, component specification | Explicitly freeze included arms/datasets/doses and intervention semantics; implement separately identified missing FIFO/oracle/other selected adapters with exact single-change and recovery tests; bind final seed/data registry and alias graph | Remain non-dispatchable if scope or numerical semantics unresolved. Blocks K05/K06 |
| K05 Analysis registry integration | K04, `phase3_delivery.import_counts`, frozen `statistics` and all_29 spec | Build persistent manifest-backed import CLI and endpoint assembler; validate all condition/seed/bank identities, reject alias/retry duplicates; synthetic incomplete pairs remain missing, full R/count schemas reconcile, all29 tests retain one Holm family | Quarantine malformed artifacts; no imputation or family split. Blocks K06 |
| K06 Explicit release review | K01–K05, 15-gate audit, complete command receipts | Human reviews exact code/data/runtime/scope/analysis freeze and grants final authorization; preserve signed/date-stamped decision. Only then implement/enable separately versioned final dispatcher/evaluator | No approval inferred from this implementation task. Final artifact and publication gates follow execution |

Local completed work: immutable selected settings binding, explicit override guard,
resource/session preflight, synthetic count import, complete-seed mean/SD,
duplicate-writer rejection and continued final-seed rejection. A candidate with
local tests passed is not equivalent to K01–K03 completed on Kaggle.
