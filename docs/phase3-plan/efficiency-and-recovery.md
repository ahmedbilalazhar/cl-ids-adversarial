# Efficiency, execution and recovery design

Working annex, iteration 2, 24 October 2026 (Asia/Karachi). This specifies future implementation decisions and measurements; it contains no executed runtime benchmark.

## 1. Optimise completed valid evidence per quota-hour

The useful objective is not maximum GPU utilisation or the largest experiment grid. It is the amount of correct, interpretable, recoverable evidence produced for the selected research questions.

Every Kaggle worker simulates **all five federated clients locally** for its assigned experiment. Eight contributor accounts do not turn this into eight FL clients, and no cross-account distributed training is required.

The scientific block is a seed's paired methods/doses under one data/protocol specification. Physical jobs may be smaller resumable pieces. Scheduling must retain compatible hardware, precision and environment within the comparisons whose differences will be interpreted.

## 2. Priority order

| Priority | Work | Why it precedes lower-priority work |
|---|---|---|
| P0 | Canonical data, isolation, state semantics, provenance and recovery | Faster invalid experiments have no evidential value |
| P1 | Reference FT/EI/DR and exact DG/DM/DC admission | These define the scientific comparison |
| P2 | CPU/GPU profiling, fixed buffers, reduced transfers, chunked Fisher | Likely efficiency gains without changing the research question |
| P3 | Required paired final matrix and a meaningful ablation package | Completes the course and core RQs |
| P4 | Class-quota random control and predeclared source-rich-site stress | Addresses attribution and weak-attack reviewer concerns |
| P5 | Auditable independent dataset and/or recurrence sensitivity | Extends the scope of the finding |
| P6 | Compilation, functional multi-model batching, new architectures, real network deployment | More complexity; pursue only if the preceding evidence justifies it |

This is a provisional prioritisation, not a change to the locked Phase 2 protocol. Additional conditions require a prospective amendment and a declared analysis role.

## 3. Measurement sheet before final dispatch

Fill this on development data, on the exact prepared data and code version intended for release.

| Quantity | CPU, 1 thread | CPU, 2 threads | Available GPU, one worker | Dual GPU, two independent workers |
|---|---|---|---|---|
| Hardware/image/Python/torch identity | Pending | Pending | Pending | Pending |
| Startup + import + input validation seconds | Pending | Pending | Pending | Pending |
| FT time by E1/E2/E3/E4 | Pending | Pending | Pending | Pending |
| EI training versus importance time by stage | Pending | Pending | Pending | Pending |
| DR training/cache/replay time by stage | Pending | Pending | Pending | Pending |
| DG/DM/DC scoring and selection time | Pending | Pending | Pending | Pending |
| State serialization/verification time | Pending | Pending | Pending | Pending |
| Complete representative trajectory time | Pending | Pending | Pending | Pending |
| Worker RAM / device allocated/reserved peaks | Pending | Pending | Pending | Pending |
| Completed valid jobs per charged quota-hour | Not GPU quota | Not GPU quota | Pending | Pending |

Use wall-clock timing with CUDA synchronisation at the start/end of measured regions, not at every training step. Record cold setup/compilation separately from warm training, and include both when estimating a new Kaggle job. Report medians and dispersion over repeated development measurements. Do not interpret illustrative timing scenarios as empirical estimates.

Cost comparisons for the paper should be measured in an isolated reference session, not while another worker contends for the same CPU/GPU resources.

## 4. Safe improvements and their limits

### CPU data preparation

- Prepare a canonical FP32 matrix once; keep metadata and row-index manifests separate.
- Use projected columns and explicit dtypes rather than loading unused strings repeatedly.
- Memory-map suitable uncompressed arrays or use Arrow/Parquet for chunked preparation. Benchmark access patterns; a compressed NPZ can require repeated decompression/loading.
- Use a fast row fingerprint as a candidate index, then verify complete canonical input bytes before merging matches. A 64-bit hash alone is not proof that two inputs are equal. Normalise signed zero and byte order first.
- Compute source/package SHA-256 hashes for provenance. Avoid recomputing a whole input hash for every mini-batch or trajectory when an immutable job input has already been verified.
- Avoid copying mounted raw inputs into `/kaggle/working` simply to read them.

### Training and replay

- Use a correct eager reference first. The 19k-parameter model does not require an elaborate memory-saving stack.
- Replace Python lists of replay records with fixed-capacity arrays/tensors.
- Keep model, shard and replay tensors resident when practical; remove unnecessary per-update NumPy stacking and host/device copies.
- Keep the replay sample size at `min(128, occupancy)` even when the final current-data batch is smaller. The existing code's use of the current batch size is a protocol mismatch.
- Repeated `.item()` and `.cpu()` calls can synchronise CUDA. Accumulate logs on the device and materialise them at deliberate intervals.
- Do not blindly add DataLoader workers. With prepared in-memory tabular data, zero workers or direct tensor indexing may be faster than multiprocessing.

### Per-example importance

Compute the specified empirical diagonal importance using `torch.func.grad` and `vmap` over single-record CE/log-likelihood gradients. Disable dropout and square **before** averaging. Reduce squared gradients immediately within chunks instead of retaining a 1,024-by-parameter tensor.

At maximum model size, a 128-record gradient tensor alone is `128 × 19087 × 4 = 9,772,544` bytes, before temporary tensors/activations. This is a theoretical allocation calculation, not a measured peak. The chunk size changes implementation cost, not the sampled records or denominator. [PyTorch per-sample gradient tutorial](https://docs.pytorch.org/tutorials/intermediate/per_sample_grads).

### Grad modes must remain distinct

- Teacher targets: evaluation mode plus `no_grad`, so stored tensors can safely participate later as constants in autograd losses.
- Logit replay: evaluation mode **with gradients enabled**.
- CE training: training mode with dropout.
- Sealed prediction: evaluation mode plus inference mode.

`model.eval()` does not disable gradients. Inference-mode tensors have stricter later-autograd restrictions than no-grad tensors; do not substitute inference mode everywhere. [PyTorch autograd guidance](https://docs.pytorch.org/docs/stable/notes/autograd).

### What not to optimise away

Do not enlarge the logical training batch, merge client gradients, drop the last partial batch, reduce epochs only for expensive arms, use AMP/TF32 in only some methods or skip a required importance/state update. Those change the experiment rather than just its implementation.

## 5. Exact prefix reuse

| Candidate reuse | Allowed condition | Important exclusion |
|---|---|---|
| E1 across doses for one method | Same code/data/runtime, initialisation, hyperparameters, budget, client shards and RNG state | Not just matching the seed integer |
| E1 across DR/DG/DM/DC | Filters are off and all DR-family learner settings are identical | No-logit/no-label and changed eviction policies can already differ in E1 |
| E2 scorer logits across admission arms/doses | Identical expanded scorer, class slots, input rows, transform and runtime | Recompute CE losses using each dose's supplied labels; never reuse selected IDs blindly |
| Primary continuation as a diagnostic control | Exact parent state, future data/order, RNG, code and runtime establish identity | An alias is not an extra independent observation |
| Across methods or tuned configurations | Only a proven semantically identical prefix | Default is separate prefixes; do not build complicated cross-method reuse for negligible savings |

Cache keys must include all causes of the prefix state. A useful parent manifest records source/data/protocol/config hashes, resolved active classes, ownership/admission hashes, RNG states and hardware/precision identity.

Here the configuration key is the explicitly resolved **prefix specification**, not an equality requirement on every future field of the consumer's full run configuration. Preserve both identities and the documented dependency projection; see [prefix-reuse.md](prefix-reuse.md). Ordinary resume of the same scientific run still requires full-run compatibility.

E1's smaller row count means saving many E1 executions may save only a small fraction of total time. Estimate savings from measured stage costs rather than treating four stages as equally expensive.

## 6. Optional dark-target cache optimisation

A correct reference caches all eligible first-pass current records' evaluation-mode logits before the update. Later epochs/rounds do not propose insertions, so their cache passes can be skipped without changing learner state.

A more aggressive optimisation may propose Algorithm R insertion decisions from a dedicated insertion RNG before the update, compute pre-update logits only for records whose tuples will actually be committed, read the **unchanged old buffer** for replay, perform the update, then commit the proposals. Preserve exact stream positions and use a separate replay-sampling RNG. If multiple proposals replace one slot within a batch, preserve stream order or select the last replacement deterministically.

Accept this optimisation only after parity checks against the reference on fixed inputs and resume boundaries. Do not rely on GPU writes with duplicate indices; their ordering can be nondeterministic. Changing cache batch shapes may introduce small floating-point differences, so declare the supported tolerance and pin the implementation used for final runs.

## 7. RNG isolation is an implementation task

Named seeds alone are insufficient if operations still consume a shared global generator. Use stable keyed seed derivation or `SeedSequence`, not Python's process-randomised `hash()`.

| Stream | Scope | Pairing rule |
|---|---|---|
| Component ownership | Seed | Same complete assignment across methods/doses |
| Attacker site/source ordering | Seed and site | Same selected site and nested source IDs in the primary comparison |
| Initial model/new head rows | Seed and stage | Same initial arrays for paired arms, independent of other random calls |
| Current-row ordering | Seed/client/stage/round/epoch | Seeded declared shuffle; filtering may change the realised batches |
| DQ random admission priorities, if used | Seed/client/stage | Separate from current ordering/replay; common candidate priorities across doses where declared |
| Replay sampling | Seed/client | Separate from insertion decisions |
| Reservoir insertion | Seed/client | Persistent stream position/state; first-pass proposals only |
| Importance sampling | Seed/client/stage | Uniform fixed-size subset, independent of dropout/order |
| Dropout | Seed/client | Independent local state retained across the declared training sequence |

Ordinary `nn.Dropout` consumes torch's default generator. A simple reference can enter a `torch.random.fork_rng` context for a client's local training, load/capture that client's CPU/CUDA RNG state and restore the process state on exit. Limit the context to the actual device rather than unintentionally initialising all devices. A custom generator-aware dropout implementation is an alternative that needs its own parity/specification review. [torch.random documentation](https://docs.pytorch.org/docs/main/random.html).

DataLoader iterator construction and random head initialisation also consume generators; account for them explicitly. An admission change must not alter future poison draws or head initialisation through unrelated RNG consumption.

## 8. Quota and concurrency accounting

Use one reserve convention consistently:

```text
Q_total = sum(actual remaining quota over available contributors)
Q_usable = (1 - reserve_fraction) × Q_total
admit the planned workload only if H_base <= Q_usable
```

A 20% capacity reserve is equivalent to requiring `1.25 × H_base <= Q_total`. Do not apply both transformations and accidentally reserve twice.

Here `H_base` is charged accelerator-session time, including overhead, before reserve. The total does not shrink merely because eight people work concurrently; concurrency reduces elapsed execution time and adds separately available quotas.

For dual-GPU sessions, measure the provider's quota charge and the throughput under two workers. Do not assume that two GPUs double weekly quota. If each worker slows because CPU/I/O is shared, use the observed concurrent throughput rather than doubling a single-worker result.

An ideal lower bound for the compute-only makespan is `H_base / concurrent_sessions` when all sessions charge in the same units and can sustain balanced throughput. Real completion includes queueing, the slowest assigned worker, incomplete blocks, setup, retries and the sequential development/data gates.

## 9. Recovery boundaries and transaction semantics

Prefer complete round or stage boundaries. The checkpoint must represent a single committed state, not weights from after an update with a buffer/RNG state from before it.

1. Write state arrays/tensors into a temporary checkpoint directory.
2. Write schema, scientific identity, hardware identity, parent references and progress cursors.
3. Hash and validate all payloads.
4. Publish the manifest last with an atomic rename/replace.
5. Mark a run complete only after the required final stage payload exists and validates.

At a round boundary where the next operation resets Adam, the optimiser can be reconstructed. Mid-round recovery needs current local optimiser state, unaggregated client results/accumulator, completed-client cursor, admitted IDs and precise batch position. Add it only if measured round cost makes it worthwhile.

A filesystem checkpoint protects against a process interruption. It does not guarantee recovery after the entire remote session disappears. Finish bounded jobs normally, retrieve a version-specific output bundle and verify it locally or in a durable permitted store before relying on it as the next job's input. Interactive persistence is best-effort, not a substitute for this process. [Kaggle staff persistence explanation](https://www.kaggle.com/product-feedback/355440).

Use typed tensor/array-plus-JSON state or restricted `weights_only` loading for trusted tensor payloads. Do not accept arbitrary pickled Python objects from a contributor merely because a hash is present. Hashes detect mismatch/corruption; they do not prove honest execution or authenticity by themselves.

## 10. Completion skipping versus resuming

The existing `--resume` primarily skips completed validated seeds. It does not implement the complete interrupted-state continuation required here.

The new worker needs two separate operations:

- **Skip:** a complete, compatible result already exists.
- **Continue:** an incomplete compatible checkpoint exists and its next transition is known.

An interrupted but exactly recovered run is not a different scientific replicate. A methodological bug or changed code/data identity requires quarantine and a documented decision about the affected matched reruns.

## 11. Contributor artifact merging

Use separate immutable output bundles per worker/job. Do not let eight workers append to one central CSV.

The importer should verify scientific run identity, source/data/config/analysis hashes, parent state, runtime signature, schemas, expected stage count, completeness and payload hashes. It should reject stale or incompatible results and quarantine conflicting outputs with the same intended run identity. Identical duplicates can be deduplicated; differing duplicates require explanation, not a silent “latest wins” rule.

After validation, one analysis process builds aggregate tables and figures. Keep unvalidated, exploratory, superseded and final evidence in distinct namespaces.

## 12. Resource reporting boundaries

Report separately:

1. **Retained learner state:** parameters, EI anchors/importance, replay, counters and RNG.
2. **Working data/state:** current shards, accepted-ID arrays, batches and temporary tensors.
3. **Research storage:** checkpoints, telemetry, prefix caches and historical results.
4. **Measured execution resources:** process RSS, device allocated/reserved memory, actual elapsed times and serialized messages.

For CICIDS2017 the declared replay slot has 381 raw bytes and a 500-slot client buffer has 190,500 raw bytes. It does not follow that the whole client or process uses only that amount. External datasets can have different feature/head widths and therefore different bytes per record.

Communication accounting must use each stage's actual model width and actual upload/download/registry messages. In-process copies and raw tensor bytes are not measurements of real WAN latency, secure aggregation or physical edge-device energy.

## 13. Development reuse reduces physical executions

The Phase 2 budget counts 81 logical development trajectories: 18 synchronization pilots, 60 hyperparameter configurations across seeds, and three poisoned FT diagnostics. It already reuses the diagnostic's clean FT references.

There is another possible reuse: after selecting the common round/epoch budget, the pilot defaults for FT, EI and DR are all members of the tuning grid. For each of the three development seeds, those three selected-budget pilot trajectories can serve as tuning observations. This yields nine aliases and **72 distinct full development executions**, if source, data, precision, runtime, initial state, learner settings and evaluation contract match exactly. A code or protocol repair between pilot and tuning invalidates that reuse. Keep 81 as the conservative logical budget and record actual saved work.

Thus the original 633-full-trajectory plan can require 624 distinct full executions before prefix sharing, rather than 633, when these nine aliases are valid. The original 24 logical oracle-diagnostic rows can require only 12 new E3/E4 executions because the other 12 alias primary DC suffixes. No alias adds an independent replicate.

The same conditional arithmetic gives 312 distinct full executions for the 321-logical core package, 384 for the 393-logical course package, and 720 for the 729-logical strengthened candidate. These are execution counts, not GPU-hour estimates. Prefix caching can further save partial-stage work without removing any logical condition.

## 14. Keep development optimization proportionate

The declared grid has only twenty clean configurations across three development seeds. Reusing matching pilot runs and prepared inputs is a direct saving. An adaptive pruning framework adds engineering and can select the wrong objective if it stops configurations based on E1 before later acquisition/retention are measured. Preserve the specified complete-stage development score and candidate set unless prospectively amended.

Within EI tuning, the E1 retention penalty is zero. At a fixed learning rate, initialization/order/runtime and importance draw, different lambda_E candidates can potentially share the same E1 trained model and committed importance. This is an additional conditional partial-prefix optimization, not included in the conservative nine full development aliases. DR coefficients can already affect E1 because replay starts within that stage, so the same shortcut does not apply across its coefficient grid.

Use one long-lived process per device for a bounded pack, share immutable prepared arrays and keep per-client row-index manifests. Do not repeatedly parse CSVs, reload a Python environment per condition or copy the entire dataset once per simulated client. Record Adam backend options such as foreach/fused explicitly if they affect reproducibility; choose a common implementation before final dispatch and count any optimization validation cost.

## 15. Bounded diagnostics and trace storage

Do not save every replay ID, per-batch tensor or RNG snapshot across the full matrix by default. A small buffer does not imply small research logs: replay draws repeatedly reuse up to 128 IDs per update, and a complete trace can dominate checkpoint storage. Profile trace size before enabling it.

Save compact counters and complete stage/round state: current/replay sample counts, insertion proposals, accepted-ID/order manifests, stream states before/after, stage-boundary buffer IDs/labels/widths and resource summaries. Use a short detailed trace only for implementation acceptance/debugging.

Exact replay-exposure diagnostics can be reconstructed on CPU from locked accepted IDs, current ordering, the specified reservoir/eviction algorithm, insertion cursor and independent RNG streams. Reconstruction does not require model optimization because these replay choices depend on declared state and supplied labels rather than model gradients. It must first match a small recorded reference trace under the pinned RNG implementation; an approximate reconstruction is not evidence of exact exposure.

The evaluator can then join IDs to reference annotations/poison markers and aggregate per-stage/client/class counts. Keep that oracle information outside learner/admission interfaces. If this reconstruction is not implemented reliably, report stage-boundary occupancy and a bounded audited exposure trace with its limits; do not invent complete exposure statistics.

Same replay IDs for CE and logit matching do not imply equal gradient contribution. Counts are exposure diagnostics, not parameter-influence estimates.

Store full retained feature/logit tuples as declared. A nominal 500-ID buffer that secretly reloads evicted history from a global archive is a different memory method. The research controller may retain prepared datasets for reproducibility, but the learner's allowed historical access remains the actual bounded retained state.

Avoid full torch-profiler traces for every final run. Profile representative development workloads, then measure normal execution separately. Do not let per-batch scalar extraction, tensor printing or verbose hashing create the overhead being reported.

Padding current training batches to simplify compilation/CUDA graphs also needs care: extra padded examples can consume dropout RNG even when their loss is masked. Preserve the reference's last-batch and RNG semantics or declare a common revised convention before development.

## 16. Numerical feasibility gate

T0-only min–max scaling without clipping can produce large later-stage values, particularly for features constant in the calibration pool. Before final runs, record transformed feature ranges/out-of-range rates and confirm finite losses, gradients, parameters and optimiser state on the development trajectories.

If training becomes non-finite, do not silently add gradient clipping, refit the scaler, change representation or stabilise only one arm. A common prospective numerical/preprocessing amendment may be justified, but it changes the experiment and must be documented and retuned before final testing. The original maximum-dose threat is not escalated merely to produce a publishable-looking effect.
