# Implementation gap audit

Status: source inspection, not an executed test report. Started 23 October 2026. Specification: the revised `submissions/phase2-with-claude.tex`. Reference repository HEAD: `fac09ec0d908dc696cc4a250e95d170be9d49fa9`; the working tree also contains local document edits.

## Recommendation

Build a narrowly scoped `src/phase3/` implementation and `configs/phase3/` namespace. Reuse small, understood primitives; preserve the legacy runners and archived artifacts. A separate namespace avoids accidentally mixing the older 211-configuration program with the current six-arm proposal. This is a proposed implementation structure, not an existing CLI.

The existing code is useful scaffolding, but an existing configuration name or passing historical test does not establish conformance to the revised protocol.

## Blocking gaps before final experiments

| ID | Inspected evidence | Revised requirement | Planned action / acceptance evidence |
|---|---|---|---|
| G01 | `src/data/clean.py` reads MachineLearningCSV, drops metadata and uses file-row order as a time proxy. The inspected raw header has no endpoint/session metadata. | Canonical numeric features and session metadata must come from the same TrafficLabelling row. | Acquire and audit canonical records; retain metadata in builder-only tables; do not join releases by row number or feature values. Stop if reliable metadata cannot be recovered. |
| G02 | `src/data/sequence.py` uses the legacy train/test task split; `task_schema.py` validates train/test arrays. | Fixed component-isolated 60/20/20 train/development/test plus isolated T0. | Introduce an explicit data-contract version with separate train, development, test and calibration manifests. |
| G03 | `src/data/sequence.py` fits `StandardScaler`. | Frozen Monday-benign min–max scaler, zero-range denominator one, no clipping or refitting. | Implement the specified transform and record fitted statistics; audit final FP32 model inputs. |
| G04 | Legacy deduplication and exclusion operate on feature/label records or test exclusion after older splits. | Whole session/content connected components; conflicting-label quarantine; provenance links of duplicates retained. | Build the component graph before final split allocation, including identical final model-input links; publish component sizes and exclusions. |
| G05 | Existing task schedules include the older Monday task. | T0 calibrates only; supervised stages are E1–E4. | Separate calibration from learning; require exactly four supervised stages in the protocol. |
| G06 | `fedavg.py` initialises `n_classes` from the complete label map and builds the server with that width. | Append only classes present in the supplied current training labels. | Use a monotonic active class registry, raw-family-to-active-slot mapping and globally identical expanded heads. No future active output rows. |
| G07 | `partition.py` Dirichlet allocation deals individual indices; stable hashing is a different approximately IID control. | Whole connected components receive one persistent owner; Dirichlet(0.5) defines per-family target shares. | Allocate atomic components once per seed and record target-versus-realised shares. Never substitute stable IID hashing for the declared non-IID design. |
| G08 | `fedavg.py` defaults to a configured malicious client ID. | Uniform draw among clients with at least ten eligible Hulk rows, shared across arms/doses for each seed. | Persist ownership, eligible sites, selected site and source-ID ordering in the seed manifest. |
| G09 | `label_flip()` computes `round(len(y) * budget)` and caps by source availability. | `floor(rho * eligible_source_rows)` with nested source-ID prefixes. | Add an explicit source-denominator corruption builder. Existing legacy budget semantics cannot be reused unchanged. |
| G10 | The generic federated runner calls the attack path by task; the configuration supports broader historical attacks. | One client's Hulk labels change to benign in E2 only. | Enforce stage, source, target, site and fixed nested doses in the protocol; no adaptive/Byzantine/backdoor behavior in the primary study. |
| G11 | `small_loss_filter()` ranks all rows, uses rounding, has no immutable-ID tie rule and no per-class protected quota. | DG, matched-volume DM and class-aware DC with ceiling quotas and deterministic ID ties. | Implement independent admission policies with exact selected-ID outputs and parity checks for DC/DM admitted counts and weights. |
| G12 | The legacy filtering call uses a carried client model before the stage's `before_task()` head handling. | Expand the shared head first, freeze an identical scorer, then admit once per stage. | Implement an explicit stage-setup state transition. No scoring with unavailable new-class logits. |
| G13 | The multi-round path calls `before_task()` only on round zero; the base method refreshes Adam only when the head object changes. | Reset Adam after every parameter broadcast. | Make broadcast and optimiser reset explicit at every round, independent of whether a head expands. |
| G14 | `ewc.py::after_task()` squares a mini-batch mean CE gradient and averages over a batch cap. | Mean of squared per-example supplied-label log-likelihood gradients, sample size `min(1024,n)`, dropout off, final shared aggregate. | Implement a simple per-example reference and a chunked `torch.func` version; compare them before using the fast version. |
| G15 | The single-round EI path estimates state before the final aggregate broadcast. In the multi-round path, anchor/model updates are conditional on existing anchor state, and anchors are changed inside the round loop. | Anchor and importance stay fixed throughout a stage; compute importance and commit the new anchor once at the final aggregate. | Explicit EI stage-end lifecycle, including first-stage zero importance, absent clients and new head coordinates. |
| G16 | `derpp.py` stores evaluation-mode logits after `optimizer.step()`. | Store pre-update evaluation-mode dark targets. | Cache required targets before the update, sample existing replay, update, then commit eligible insertions. |
| G17 | Legacy replay logits and replay-label CE use the same training-mode forward. | Logit matching has dropout off with gradients; CE training has dropout on. | Separate the two modes and restore model mode explicitly. Preserve the declared per-record width-normalised MSE. |
| G18 | `derpp.py` appends every observation, then randomly removes overflow; it has no distinct-ID first-pass guard or Algorithm R stream counter. | A uniform 500-slot reservoir over distinct admitted first-pass records, considered only in round 1/epoch 1. | Fixed-capacity arrays, exact Algorithm R, stream counter, pass cursor, per-client RNG and no historical seen-ID set. |
| G19 | Legacy replay state lists features, labels and logits, without the required immutable ID/observed width contract. | Store feature, supplied label, ID, pre-update logit vector and original observed width. | Define a serialisable replay schema with monotonic class coordinates and actual byte accounting. |
| G20 | `BaseCLMethod.set_seed()` seeds global NumPy and torch state; many calls consume these shared generators. | Separate ownership, poison, order, head, replay, importance and dropout streams. | Use named seeded generators; persist their states. A different admitted length must not change poison IDs or head initialisation. |
| G21 | `fedavg.py` evaluates test tasks inside the training loop. | Training writes checkpoints; the sealed evaluator runs after the complete locked run set. | Do not mount final-test arrays in training jobs; run a separate read-only evaluation program. Development evaluation remains a separate allowed interface. |
| G22 | The old ASR computation usually uses the current task's test records, so Hulk may be absent in E3/E4. | Fixed clean Hulk bank at every stage from E2 onward and paired clean subtraction for persistence. | Save all stage checkpoints and evaluate the same source bank; derive H and recall damage from matched trajectories. |
| G23 | Old summaries and the inference bundle centre on R matrices and older endpoint names. | Acquisition A excludes Hulk, source damage is separate, eligible classes are fixed and rare classes remain descriptive. | New prediction/metric tables with denominators, class support, bank hashes and explicit null handling. |
| G24 | `docs/analysis_spec.json` declares the older 27 families / 200 pairs. | One 29-test Holm family in the revised proposal. | Create a new immutable analysis specification; never send new results through the old family list. |
| G25 | `--resume` in the existing launcher skips completed manifest-validated seeds; it is not interrupted-stage recovery. | Kaggle-safe recovery from saved complete state and bounded sessions. | Define recovery boundaries and checkpoint schemas; distinguish completion skipping from continuation recovery. |
| G26 | The old GPU importer expects exactly 12 architecture configs, a legacy task hash and a single-node runner. | Revised federated stage runs across contributor environments. | New generic verified result importer with protocol/source/data/runtime hashes, unique job IDs and conflict rejection. Do not repurpose the old importer blindly. |
| G27 | `_buffer_report()` estimates some payload bytes; `_comm_bytes()` counts raw state tensors. | Full declared replay bytes plus measured allocation/serialisation overhead; upload/download/registry traffic. | Separate theoretical raw payload, serialized model messages, actual simulation resources and end-to-end deployment claims. |
| G28 | The generic runner silently falls back from CUDA to CPU. | Hardware is recorded and comparisons are planned in paired blocks. | Fail or explicitly reassign the complete block when a requested device is unavailable; do not silently mix a partial seed across runtimes. |
| G29 | Several inference/filter paths move an entire NumPy array to the device; per-batch `loss.item()` synchronises CUDA; replay repeatedly stacks Python lists. | Efficient, bounded data movement with unchanged scientific semantics. | Chunk evaluation/scoring, pre-load small prepared arrays when practical, use fixed buffers and reduce scalar synchronisation. Measure end-to-end benefit. |
| G30 | Historical tests check older semantics, for example batch-gradient Fisher and retaining the global model when all clients are inactive. | Per-example importance and a stage invalidation if zero clients are active. | Write a new protocol acceptance suite during implementation; historical green tests cannot override the revised specification. No tests have been run as part of this planning task. |
| G31 | Legacy DER samples replay using the current batch length (`_sample(x.size(0))`). | Replay size is `min(128, occupancy)`, including a short last current-data batch. | Keep current and replay batch lengths independent. Average each loss term over its own records and apply the stored-width mask separately. |

## Reusable pieces

- `src/models/mlp.py`: the 128/64 MLP, dropout 0.1 and head expansion are useful starting points. Verify parameter counts and class-slot semantics in the new runner.
- `src/attacks/flip.py`: class-name resolution and fail-closed target checking are reusable; the legacy dose denominator is not.
- `src/reporting.py`: atomic writes, source/data hashes and completion-manifest ideas are reusable. The payload, analysis and cross-machine contracts need new versions.
- Existing metric arithmetic and plotting helpers can be reused only after checking denominator and averaging conventions against the revised definitions.
- Existing archives and claim ledgers are evidence of earlier work and invalidation. Keep them separate from new validated results.

## Gate order

1. Obtain canonical metadata and pass the split/support audit.
2. Implement the simple, correct reference engine for one small development trajectory.
3. Add protocol acceptance checks and durable restart semantics.
4. Benchmark and optimise only after correctness is established.
5. Tune on development data and freeze the protocol, code and analysis.
6. Dispatch the locked paired runs.

No recommendation in this audit licenses historical results as new evidence. Every future result must identify the exact protocol, code, inputs and runtime that generated it.
