# Phase 3 implementation and experimental evaluation plan

Implementation plan strengthened by a second data and evaluation audit, revised 24 October 2026 (Asia/Karachi). Started 23 October 2026. Proposed implementation settings still require the stated pre-development locks. No model result in this document is an executed Phase 3 finding. New data-only evidence and protocol corrections are indexed in [second-audit-gap-register.md](second-audit-gap-register.md).

Read [START-HERE.md](START-HERE.md) for the focused recommendation and [README.md](README.md) for the complete working package.

The final [feature-semantics review](feature-semantics-and-final-recommendation.md) recommends prospectively omitting two lossy corrected-source header totals (A31, 74 inputs), with updated inventory/resources and A32 benign-provenance reporting. This is a proposed amendment; the original 76-feature specification below remains traceable.

## 1. Recommendation

Build a small, correct implementation of the revised Phase 2 experiment before spending GPU quota. Use Kaggle as an execution service for independent, reproducible experiment blocks. Keep preprocessing, routine debugging, statistics, plotting and report writing off GPU sessions. Benchmark CPU against the actual available GPU before deciding which device runs the final protocol.

The principal scientific contribution should be a controlled investigation of poisoning during new-family acquisition, persistence after withdrawal and the security–adaptation effects of filtering. DC is a deliberately simple class-aware rule; in the primary schedule it protects all supplied new attack labels and filters benign-labelled rows. Its novelty and effectiveness must not be overstated.

The implementation team has two authors. Eight distinct people may contribute compute, each operating their own account. Treat those accounts as separately managed workers with variable remaining quotas. Each worker simulates all five federated clients locally; no cross-account distributed training is needed. Kaggle documentation describes a nominal weekly GPU quota around 30 hours, subject to availability and change. Record each contributor's actual remaining allocation before scheduling. [GPU usage guidance](https://www.kaggle.com/docs/efficient-gpu-usage).

### Decisions that should be made first

1. Obtain the deadline and instructor feedback; neither has been supplied yet.
2. Adopt one audited source/domain/taxonomy profile; do not treat either candidate as a drop-in replacement.
3. Freeze the implementation specification and data contract.
4. Implement and validate one small reference trajectory.
5. Measure representative end-to-end runtimes before locking experiment scope.
6. Preserve 12 paired final seeds; reduce optional conditions before reducing replication.
7. Include ablations even in the constrained Phase 3 package.

## 2. What the finished submission must contain

| Course requirement | Concrete deliverable | Evidence of completion |
|---|---|---|
| 1. Implement the proposed methodology and incorporate feedback | Four-stage federated runner, FT/EI/DR/DG/DM/DC policies, versioned amendment log | Code/config/data hashes, acceptance report, teacher-feedback traceability |
| 2. Dataset and preprocessing | Canonical source manifest, component-isolated splits, T0 transform, ownership manifests | Per-family counts, component census, duplicate/session overlap audits, exact feature list |
| 3. Baseline evaluation | FT, EI, DR and matched DM; DG in the complete package | Complete paired seeds, clean and poisoned outcomes, denominator-aware baseline table |
| 4. Graphical results | Stage trajectories, paired differences, acquisition/security plots, per-family confusion and costs | Figures generated from validated prediction/result tables with a reproducible figure script |
| 5. Compare existing research | Direct within-protocol comparisons and a separate paper-comparison table | Explicit dataset/task/threat/metric/split differences; no unsupported cross-paper superiority claim |
| 6. Ablations | Loss-term removals, eviction policy and, when affordable, matched keep fractions | One-factor changes, fixed settings, matching references and clean/maximum-dose results |
| 7. Analysis and discussion | Answer each RQ, discuss failures, uncertainty, scope and remaining risks | Claim-to-figure ledger; complete deviations; null/adverse findings retained |

The course package and a journal-ready research contribution are different milestones. Good engineering and complete experiments support publication; they cannot guarantee acceptance.

## 3. Scientific specification to preserve

### Core setup

- Historical CICIDS2017 capture; five simulated clients.
- T0: isolated Monday benign records, scaler fitting only.
- E1: benign plus FTP-Patator and SSH-Patator anchors; filters off.
- E2: benign plus the declared DoS families and Heartbleed; exactly one eligible client's Hulk labels may be corrupted.
- E3: benign plus Web attacks/Infiltration; E4: benign plus Bot/PortScan/DDoS.
- No earlier attack family returns as fresh training data in the primary protocol.
- Post-E2 withdrawal stops fresh label corruption; the affected client keeps participating and replay can still contain wrong labels/logits. These are not necessarily wholly clean optimization phases.
- One two-layer 128/64 ReLU MLP with dropout 0.1 and a growing shared head. At 76 input features and 15 outputs it has 19,087 parameters.
- Supplied current training labels alone determine class registration and filtering. The learner receives no reference labels or poison markers.
- Doses are 0, 0.10, 0.30 and 0.50 of the attacked client's eligible Hulk records, using nested ID prefixes and a floor operation.
- Final seeds: 1–11 and 42. Development seeds: 101–103.

### Learners and selection

| Arm | Learner | Admission | Purpose |
|---|---|---|---|
| FT | Current-data cross-entropy | All current rows | No explicit retention reference |
| EI | Current CE plus the declared online-EWC-style penalty | All current rows | Importance-based retention |
| DR | Declared DER++ adaptation | All current rows | Replay reference |
| DG | Same DER++ | Rank across local classes; retain 75% | Unmatched-volume filter reference |
| DM | Same DER++ | Rank across local classes with DC's exact admitted count | Equal-volume control |
| DC | Same DER++ | Per-class quota, all new/small supplied-label classes retained | Proposed class-aware comparison |

The distinction between supplied and true classes matters: a corrupted Hulk record carries the benign supplied label and is ranked within the benign group.

FT/EI/DR are separately tuned pipelines, potentially with different learning rates. Their clean-subtracted susceptibility contrast does not isolate retention independently of optimization settings. A conditional same-rate FT reference (up to 24 extra full runs at clean/maximum dose) is available for a stronger exploratory attribution claim; it is outside the base package counts.

### Implementation order inside one stage

1. Build supplied labels with E2 corruption applied once.
2. Share the union of supplied current class IDs; expand all heads identically.
3. Freeze a scoring snapshot and lock accepted IDs for the whole stage.
4. For each locked round: broadcast weights, reset local Adam, train admitted mini-batches and aggregate with distinct admitted-row weights.
5. During replay learning, draw from the old buffer, use pre-update stored targets and insert eligible new records only in the first epoch of the first round.
6. At stage end, broadcast the final aggregate. EI then computes per-example importance and commits its next anchor once.
7. Save a versioned complete checkpoint. Final testing is a later, separate operation.

Within a stage, EI importance and the previous-stage anchor remain unchanged across all broadcasts and local updates. They must not be reset to each round's local model.

## 4. Existing code: reuse selectively

The source audit identifies 31 implementation gaps in [implementation-gap-audit.md](implementation-gap-audit.md). The largest are the old scaler/splits, full future head, legacy dose denominator, old Fisher estimate, post-update replay targets, non-reservoir pruning, repeated insertion, missing class-aware admission and training-time test evaluation.

The [second audit](second-audit-gap-register.md) adds data-release/clock feasibility, exact component allocators, calibration eligibility independent of future labels, dose-dependent work/weights, baseline/ablation definitions, inferential resolution and claim limits. These additions make the plan more executable; they do not convert the legacy runner into the revised engine.

Do not run the old 211-config grid for this submission. It contains a different research program, different analysis families and historical artifacts with documented invalidation.

### Proposed implementation structure

These modules and interfaces are to be implemented; their names are not existing runnable commands.

```text
src/phase3/
  protocol.py          # typed immutable specification and validation
  data_builder.py      # canonical records -> manifests and arrays
  components.py        # session/content grouping and split checks
  ownership.py         # whole-component client allocation
  corruption.py        # E2 source-denominator nested label flips
  registry.py          # append-only active class slots
  admission.py         # none, DG, DM, DC and optional controls
  model.py             # verified small MLP / head-growth adapter
  learners.py          # FT, EI, replay losses
  replay.py            # fixed-capacity Algorithm R and variants
  importance.py        # per-example reference and vectorised implementation
  engine.py            # explicit stage/round state machine
  checkpoint.py        # atomic, complete recovery snapshots
  worker.py            # bounded execution from a planned manifest
  evaluate.py          # sealed, read-only checkpoint evaluation
  analysis.py          # paired endpoints, fixed tests, tables
  figures.py           # exportable result figures
configs/phase3/
docs/phase3-protocol/
results/phase3/<protocol-hash>/
```

Keep ordinary Python, NumPy, PyTorch, Arrow/Parquet and the existing atomic-write ideas. A database server, Kubernetes, Ray cluster or real network federation is unnecessary for the controlled five-client simulation. Add infrastructure only if a research question requires it.

## 5. Data preparation is the first release gate

UNB distinguishes labelled flow records from the machine-learning CSV distribution. The canonical data and metadata must be projected from the same record. Existing MachineLearningCSV files are insufficient for the declared endpoint/time session grouping by themselves. Never reconstruct session identity by assuming two releases share row positions. [Official CICIDS2017 description](https://www.unb.ca/cic/datasets/ids-2017.html).

**Updated acquisition evidence:** complete original-mirror and corrected archives/censuses now exist. The original has blank trailing records and lossy/ambiguous clock strings; the corrected release has E3 support/taxonomy incompatibilities. Neither is automatically final-ready. Read [data-release-decision.md](data-release-decision.md) and the conditional component/split audits before adopting a source. T0 fitting eligibility uses Monday-only validity/benign annotation; later cross-day conflicts exclude learning/evaluation and extend closure without refitting.

### Builder pipeline

1. **Acquire and identify.** Record source URL/release, retrieval date, licence text, byte counts and SHA-256 hashes. Obtain original metadata-bearing flow files. A mirror may be used only with a documented provenance chain; a community licence label is not proof of the original redistribution permission.
2. **Parse without losing metadata.** Use explicit column names and dtypes; read in chunks where useful. Preserve source file, original row number, endpoint pair, protocol, timestamp and flow interval in builder-only tables. Reject ambiguous timestamps or malformed intervals under versioned rules.
3. **Normalise.** Fix documented label aliases, repeated headers and duplicate schema columns. Quarantine non-finite features and known disputed records using declared rules. Preserve exclusion counts by family and reason.
4. **Freeze calibration independently.** Select Monday-only own-source-valid benign fitting IDs under the adopted domain rule. Fit min-max statistics once, without later-day reference conflicts deciding fit eligibility. Do not train weights on T0.
5. **Audit representations and links.** Project the final FP32 representation, canonicalize signed zero, and build raw/final exact-input links without labels in the feature key. Build unordered endpoint-pair/protocol sessions at the declared 120-second gap. Preserve full provenance and conservative excluded-record links.
6. **Quarantine and isolate.** Quarantine conflicting reference annotations for learning/evaluation; exclude the complete T0-linked closure from all model roles. Later conflicts never refit the scaler or alter its fitting IDs. Retain deterministic survivors only after provenance links exist. Do not repair leakage after model outcomes.
7. **Allocate splits.** Use a deterministic, versioned group-stratified 60/20/20 allocation. Record the algorithm, seed, target/realised proportions and indivisible groups. Inspect no model outcomes to select a split. Large components or failed support floors require a disclosed protocol decision.
8. **Select fresh-stage pools.** Keep attack-family arrival fixed. Select cross-stage benign bundles by component toward 3,500 rows per stage; preserve prescribed attack records and one role/owner for every retained component member. Excluded benign records stay reserved to train. Publish realised counts and the explicit A20 amendment. Never reuse a record as fresh data in a later stage.
9. **Allocate clients.** Assign whole training components using the declared per-family Dirichlet targets; keep owners fixed within each seed. Publish realised label/row shares and the eligible attacker sites.
10. **Package once.** Store canonical prepared arrays plus small row-index manifests. Reuse them across all runs rather than reparsing CSVs or refitting transforms.

### Data acceptance checklist

- Exact ordered 76-feature schema verified, or a prospective feature-schema amendment recorded.
- Metadata provenance, timestamp units, session-gap convention and duplicate survivor rule fixed.
- No shared record IDs, final model inputs or session components between train, development, test and T0.
- Required anchors and Hulk meet 50/50/50 rows and 5/5/5 components; each acquisition stage has an eligible untargeted family.
- Rare supported classes remain visible in the data inventory even when excluded from confirmatory scoring.
- Benign test records can form four non-empty disjoint component cohorts.
- Every prepared FP32 value is finite; no later-stage clipping/refitting is introduced.

The local machine has an inspected four-core/eight-thread i7-10610U and roughly 32 GiB of RAM. It can do much of the CPU preparation without occupying a Kaggle GPU. This is a hardware inventory, not a measured throughput claim.

### If canonical metadata is unavailable

Time-box recovery. Do not spend the whole project trying to infer metadata from machine-learning features. Either obtain a trustworthy metadata-bearing release, use an explicitly justified alternative, or amend the design to a weaker feature-content-isolated experiment before final testing. A feature-only protocol cannot claim session-disjoint evaluation. Re-extracting all PCAPs is an expensive last resort, not the default efficient path.

## 6. Correctness and reproducibility contract

During implementation, create acceptance checks for the following. They are planned checks; none have been executed in this planning task.

The detailed [data-and-interface-contract.md](data-and-interface-contract.md), [numerical-and-state-decisions.md](numerical-and-state-decisions.md) and [metrics-and-analysis-contract.md](metrics-and-analysis-contract.md) resolve interfaces and identify pre-development clarifications. “Global” ranking in DG/DM is across labels within a client, not a central ranking of all clients' raw records.

### Data and information boundaries

- Held-out rows never reach optimisation, scaler fitting or admission.
- Reference labels and poison markers exist only in corruption-building/evaluator interfaces; the learner receives supplied labels.
- Future class outputs do not exist before supplied-label registration.
- DC and DM have exactly the same per-client admitted counts and FedAvg weights at each stage/dose.
- Rejected IDs never enter training or replay.

### Learning semantics

- First-stage EI importance is zero; new head coordinates have zero prior importance.
- Per-example importance equals a simple small-sample reference within declared numerical tolerances.
- EI importance/anchor commit only after the final shared aggregate.
- Replay capacity never exceeds 500; Algorithm R counts distinct admitted first-pass records only.
- Buffer targets are pre-update, evaluation-mode logits with immutable observed coordinate width.
- Replay logit loss disables dropout but keeps gradients; CE uses training dropout.
- Adam resets at every broadcast; all active head rows remain trainable.
- Zero active clients invalidate the stage rather than silently advancing it.

### Recovery and artifacts

- Interrupted and uninterrupted execution agree on a small deterministic reference run.
- Completion is accepted only after hashes validate; a CSV or checkpoint's existence is insufficient.
- Source/data/config/analysis/runtime identity is included in each result manifest.
- Requested CUDA absence does not silently create a CPU result in a GPU block.
- New Phase 3 artifacts never silently enter the old analysis families or importers.

PyTorch documents that seeded runs need not be identical across releases/platforms. Pin the environment and hardware signature for each paired block and record deterministic settings. [PyTorch reproducibility guidance](https://docs.pytorch.org/docs/2.14/notes/randomness.html).

## 7. Optimise the real bottlenecks

### First benchmark, then choose the device

Use development data only. Compare a fixed representative FT workload, replay workload, importance calculation, admission pass and complete stage on:

- Local CPU with one and two torch/BLAS threads.
- A Kaggle CPU runtime, if useful for throughput.
- The GPU type actually available to the account.
- Two independent GPU workers only if a dual-device session is available and its quota charging is understood.

Measure startup, imports, input loading, training, state updates, serialization and evaluation separately. GPU event timings alone do not establish lower end-to-end quota consumption. The small MLP may be CPU-competitive; this remains an empirical decision.

### High-value, low-risk improvements

1. Parse/clean/scale once and reuse immutable prepared arrays and manifests.
2. Avoid global thread oversubscription. Set CPU thread variables before importing numerical libraries; start with one worker/thread per GPU and measure.
3. Use contiguous FP32 arrays, int64 training labels and fixed-capacity replay arrays.
4. Keep the current shard and tiny replay state on the device when memory permits; otherwise use measured pinned-memory/non-blocking transfer paths.
5. Do not call `.item()`, `.cpu()` or print CUDA tensors on every batch. Aggregate scalar logs at safe intervals.
6. Chunk per-example importance with `torch.func.functional_call`, `grad` and `vmap`, preserving square-before-average semantics. Start with chunks of 64–128 and validate against the reference. [Official per-sample gradient tutorial](https://docs.pytorch.org/tutorials/intermediate/per_sample_grads).
7. Score/evaluate in bounded chunks with inference mode, without changing training batch size.
8. Reuse exact eligible E1 prefixes across DR/DG/DM/DC and doses; record parent checkpoint hashes.
9. Reuse the original primary DC continuation as the memory-diagnostic control only if complete checkpoint/RNG/runtime identity establishes that it is the same trajectory. This creates an alias, not a new independent replicate.
10. Keep a long-lived worker process across a small job pack so imports and data loading are not repeated per trajectory.

The PyTorch performance guide identifies host/device synchronization and transfers as common overhead sources. Its recommendations must be benchmarked on this in-memory tabular workload; more DataLoader workers are not automatically faster. [Performance tuning guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html).

### Optimisations requiring additional scrutiny

- Cache only pre-update dark targets that can actually be inserted, after proving the reservoir proposal/commit order preserves replay and RNG semantics.
- Cache E2 **logits**, rather than losses or accepted IDs, across admission arms/doses only when the expanded scorer weights, features, class slots and runtime match exactly. Supplied labels and resulting losses differ by dose.
- Benchmark `torch.compile` only after correctness, counting compilation and head-shape recompilation time. Use it only if the complete job saves time.
- A functional/batched multi-model engine is optional; it must preserve independent optimisers and RNG streams. It is not the first implementation milestone.

### Preserve the scientific budget

Keep primary training in the declared FP32 configuration and batch size 128. AMP, TF32, larger logical batches, gradient accumulation, activation checkpointing and DDP are not automatic upgrades for this tiny model. They can change numerical behavior, optimiser updates, replay exposure or the declared methodology. A dual GPU is normally better used for two independent experiment blocks than for synchronising one 19k-parameter model.

Do not spend GPU hours on CSV preparation, broad architecture searches or repeatedly installing a new CUDA/PyTorch stack. Use the working Kaggle image, record it and pin only necessary additional packages.

## 8. Experiment packages and priorities

The original full Phase 2 plan is retained as the complete package. The recommended implementation sequence is course-complete, then the focused research controls, then a valid external replication if feasible. A constrained package must still satisfy Phase 3's ablation requirement; select and document any scope amendment before final testing.

| Package | Development full runs | Final full runs | Total full runs | Diagnostic continuations | Meaning |
|---|---:|---:|---:|---:|---|
| Original core only | 81 | 240 | 321 | 24 | Does **not** by itself complete Phase 3 ablations |
| Constrained course package | 81 | 312 | 393 | 24 | Core plus DC without logit term, DC without replay-label term, and DC FIFO; each at clean/maximum dose |
| Focused research starter | 81 | 360 | 441 | 24 | Course package plus DQ, the matched class-quota random control |
| Focused research with external replication | 81 | 432 | 513 | 24 | Starter plus independently audited external DR/DM/DC at clean/maximum dose |
| Complete Phase 2 package | 81 | 552 | 633 | 24 | All six arms, all eight changed ablation settings and the separately audited external check |
| Publication-strengthened candidate | 81 | 648 | 729 | 24 | Complete package plus class-aware random selection (48 runs) and a separate DM/DC recurrence sensitivity (48 runs) |

Counts are logical planned trajectories, not measured GPU hours or proof of feasibility. Nine pilot/tuning aliases can reduce distinct full development executions from 81 to 72 when exact identity is verified. Twelve original oracle control continuations can alias existing primary suffixes, leaving 12 new diagnostic executions. See [efficiency-and-recovery.md](efficiency-and-recovery.md) and [prefix-reuse.md](prefix-reuse.md) for the conditional accounting. The publication additions are prospective recommendations, not implemented or formally preregistered changes. An optional unfiltered ER component reference at clean/maximum dose adds 24 full trajectories; it is not a separately tuned state-of-the-art baseline.

The machine-readable [experiment-manifest.json](experiment-manifest.json) enumerates the 729 logical full rows in the largest candidate, package membership and worker assignment. It is explicitly not dispatchable: settings, data feasibility and hashes remain unresolved. [analysis-contrasts.json](analysis-contrasts.json) enumerates the 29 confirmatory contrasts.

### Required before selecting the final package

- Time the actual data and implementation.
- Verify current quotas/access and publication rights for the input bundle.
- Check the deadline, which remains unknown.
- Lock the package and analysis before final outcomes are viewed.

Do not drop difficult seeds, shorten only losing methods, escalate the attack after viewing test results or remove an ablation because it contradicts the preferred explanation.

### High-value additional controls

**Class-aware random selection.** Keep DC's exact per-class quotas but choose retained benign/recurring-class rows uniformly rather than by loss. It distinguishes loss ranking from quota protection. Preserve the primary DC–DM comparison; label new contrasts exploratory unless prospectively added to a revised fixed analysis family.

**Recurrence sensitivity.** In a separate protocol, reserve fresh earlier-family training components for a later stage so recurring attack classes actually face class-aware quotas. Do not reintroduce fresh Hulk into the primary withdrawal experiment. Use identical reserve rules and supplied-label information in its paired conditions; do not pool it with the primary result.

## 9. Kaggle execution and recovery

Kaggle documents versioned notebook environments, approximately 12-hour CPU/GPU session limits and a 20 GB saved working area; actual account/runtime settings must be checked before launch. It also distinguishes Quick Save from Save & Run All, which executes the notebook again. Optional interactive persistence is best-effort and is not a backup guarantee. [Notebook documentation](https://www.kaggle.com/docs/notebooks), [staff explanation of persistence](https://www.kaggle.com/product-feedback/355440).

### Three kinds of package

1. **Code package:** immutable source archive or wheel, dependency additions, source/config/analysis hashes and the runner entry point.
2. **Learning data package:** prepared train/development arrays, scaler/class maps and seed manifests. Do not mount final-test arrays in worker training jobs.
3. **Worker output:** checkpoints, manifests, resource logs and completed-run records. Final predictions are generated later by the evaluator.

Data and notebook collaboration permissions are distinct. Add contributors only to the resources they need. Each contributor keeps their own credentials and launches their own assigned jobs.

### Statistical block versus physical job

The scientific block is one seed across its paired methods and doses. Prefer one recorded hardware/software environment for the whole block. A physical job can contain a complete block or a resumable part of it. Do not put FT on CPU, EI on one GPU generation and DR on another and interpret their differences as pure method effects.

Select a job duration after measuring the block. A 2–3 hour pack is a useful initial target, but a complete 6–8 hour block can be more efficient when it comfortably fits the displayed session/quota limits and has reliable saving margins. Never schedule right up to the advertised maximum.

### Recovery state

At a complete round/stage boundary save:

- Protocol/code/data/config/parent checkpoint hashes and run/seed/stage/round identifiers.
- Shared model and append-only active class map.
- Every client's replay contents, observed logit widths and Algorithm R counter/cursor.
- Every EI importance tensor and anchor.
- All named RNG states, including torch CPU/CUDA state for the process.
- Admitted-ID manifest and fixed client ownership.
- Completed work counters and resource records.
- Adam state only when the recovery boundary requires it; stage/round boundaries before a reset can reconstruct a fresh optimiser as declared.

Mid-round recovery requires additional partially accumulated client/aggregation state. Avoid introducing that complexity until measured round duration justifies it. Distinguish an interruption recovered from an exact checkpoint from a scientifically invalid run requiring a protocol repair and matched reruns.

Write checkpoint payloads to temporary files, hash and validate them, then atomically publish the manifest last. A local `/kaggle/working` checkpoint is not durable against every session failure. Finish bounded jobs normally, download and verify their saved outputs, and attach/version verified output bundles for the next job. Do not rely on Python-variable persistence or a browser staying open.

The official CLI supports pushing a run, checking status and retrieving a specific version's outputs. Current CLI flags vary by installed version, so save `kaggle --version` and use that version's help. These are verified provider interfaces, not the future Phase 3 runner:

```bash
kaggle kernels init -p <kernel-folder>
kaggle kernels push -p <kernel-folder>
kaggle kernels status <owner/kernel-slug>
kaggle kernels output <owner/kernel-slug/version> -p <local-output-folder>
```

`push` normally starts execution; do not use it repeatedly as an innocuous save operation. Keep provider metadata private until a deliberate release decision. [Official CLI kernel commands](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md).

## 10. Two authors and eight compute contributors

### Author responsibilities

| Person | Primary ownership | Cross-review responsibility |
|---|---|---|
| Author A | Data provenance, components/splits, metrics, statistics and report evidence | Review learner state, corruption and recovery logs |
| Author B | Model/learner engine, admission, checkpointing, packaging and dispatch | Review splits, denominators, analysis specification and figures |
| Contributors C–H | Execute assigned immutable blocks and return verified artifacts using their own accounts | Record environment, quota, failures and output hashes; do not change methodology |

Agree contribution credit and acknowledgments based on actual contributions and venue policy. Compute access alone is not a reason to fabricate scientific authorship.

### Initial seed assignment

| Worker | Seed blocks |
|---|---|
| A | 1 and 9 |
| B | 2 and 10 |
| C | 3 and 11 |
| D | 4 and 42 |
| E | 5 |
| F | 6 |
| G | 7 |
| H | 8 |

This is a starting allocation, not an assumption that all machines have identical throughput. Rebalance whole unstarted blocks using measured capacity. Keep ownership/poison IDs fixed by seed, not by the account name.

The two-account fallback assigns complete seed blocks between A and B. If a GPU is unavailable, do CPU development/analysis or wait for a permitted allocation rather than silently changing an active final block.

## 11. Compute budget: measure before promising hours

Define each account's usable quota as its displayed remaining allocation minus a reserve for retries, saving and validation. A nominal 30 hours on each of eight accounts gives a planning ceiling of 240 quota-hours, not a guaranteed 240 available hours or a completion estimate. Do not multiply again by two just because a session exposes two GPUs; verify quota charging and measured jobs completed per quota-hour.

The planning formula is:

```text
required charged hours =
  sum(measured stage work by method, dose and seed)
  + startup/loading/serialization time
  + evaluation time if performed with an accelerator allocated
  + expected retries and saving overhead

completion time depends on the slowest assigned worker,
the sequential implementation/development gates,
and actual concurrent availability.
```

Use a 20–30% planning reserve until failure rates are measured. Apply it once: a 20% quota reserve gives `usable=0.8*remaining`, equivalently `base_work<=0.8*remaining`; do not also inflate work by 25% and compare it with the already reserved capacity. Report example budgets as scenarios, not benchmarks. For example, 633 full trajectories averaging five minutes each would require 52.75 hours before continuations, setup, evaluation and reserve. At twenty minutes each the same arithmetic is 211 hours before those additions. Neither timing is currently measured, and a category-specific measured budget is better than a common average.

Preprocessing and statistics do not consume GPU quota when run without a GPU allocation. Development may run on CPU if it is efficient, but record device choices and verify the final selected settings under the locked runtime.

Prefix caching reduces executed work without changing logical run counts or the 12 independent seed-level replicates. It does not justify treating cloned prefixes or aliased diagnostic controls as extra samples. E1 is much smaller than later stages in the legacy inventory, so report measured savings rather than a stage-count percentage.

## 12. Evaluation and analysis

### Primary and descriptive outcomes

- Preserve the fixed clean source bank at E2–E4.
- Immediate harm: poisoned-minus-clean source recall at E2.
- Persistence H: mean paired increase in Hulk-to-benign error over E3/E4, shown with absolute clean/poisoned error to expose ceiling effects.
- Legitimate acquisition A: equal-stage/equal-family F1 on eligible untargeted new families, excluding Hulk and benign.
- Benign false alarms, source/anchor recall, macro-F1, final ACC, BWT and forgetting with their declared denominators.
- Full-inventory per-family confusion/support, including rare supported classes as descriptive evidence; untargeted-new precision/recall accompany acquisition F1 because false positives can originate from Hulk.
- Poison/admission/occupancy/resource diagnostics, evaluated outside learning.

Report binary precision, recall, F1 and false alarms from the same fixed argmax decision. If adding AUROC/AUPRC descriptively, use a documented continuous score, ideally `max_attack_logit - benign_logit` to align ranking with the non-benign argmax decision; save it in FP32. Report benchmark prevalence. Do not imply a daily production alarm count from a resampled dataset.

### Statistics

Retain the revised single family of 29 two-sided paired signed-rank tests and Holm correction unless a prospective amendment is justified before final testing. The unit is one seeded trajectory, not a flow, client, stage or batch. Preserve paired differences, zero/tie handling, exact sign enumeration, effect sizes and descriptive whole-seed bootstrap intervals.

Twelve seeds are a resource choice and provide finite p-value resolution; they are not a demonstrated power guarantee. A non-significant result does not show equivalence, immunity or no harm. New controls and sensitivities remain exploratory unless the frozen analysis is formally changed before outcomes are observed.

Do not use the old `docs/analysis_spec.json` family list for these results. Retain raw paired trajectories alongside every aggregate.

If an endpoint is unrestorable, mark its raw test unavailable and use p=1 only for the fixed 29-family Holm bookkeeping, as the Phase 2 appendix specifies. Do not present that as a computed no-effect result. Bootstrap intervals target the mean paired difference; signed-rank significance has a different symmetry-based interpretation.

### Efficient prediction artifacts

Store a shared immutable bank with row IDs/reference labels once. A per-stage output can store predicted class IDs, the bank hash and optional FP32 binary scores rather than repeating all 15 logits and row IDs for every run. Keep the full replay dark targets in the checkpoint where they are actually needed. Validate output row order and class-map identity before computing metrics.

## 13. Figures and tables to produce

| Artifact | Purpose | Required safeguards |
|---|---|---|
| Data/support/ownership table | Show the actual benchmark and non-IID setting | Counts before/after quarantine, split components, eligible families |
| Main clean/poisoned performance table | Compare FT/EI/DR/DM/DC, plus DG when run | Mean and dispersion, paired effects, exact metric averaging |
| Stage-wise source error and anchor recall panels | Show acquisition, forgetting and post-withdrawal persistence | Fixed source bank; show clean references and individual seeds |
| Acquisition versus persistence plot | Display the security–adaptation trade-off | Clearly labelled dose, method and uncertainty; no claim of no harm from overlap |
| Per-family confusion/recall view | Reveal rare/new-family failures hidden by accuracy | Supports and full active output space disclosed |
| Admission and replay diagnostics | Explain selected volume, poison retention and retained state | Diagnostics do not feed back into the learner |
| Ablation paired-difference plots | Identify component contributions | One-factor changes and matched reference rows |
| Runtime/memory/communication table | Establish measured resource costs | Same hardware for comparisons; distinguish raw payload from measured bytes |
| Literature comparability table | Position results against published work | Protocol differences explicit; original reported numbers separated |

Generate figures from validated tables rather than notebook cell state. Save vector PDF/SVG and high-resolution PNG, use readable fonts and consistent method/dose colours, and include scripts/configuration that regenerate every figure. Never use illustrative curves as if they were results.

## 14. Comparison with existing research

Use three clearly separated layers:

1. **Direct comparison:** reimplemented baselines under this exact dataset, split, threat, architecture and evaluation contract.
2. **Faithful reproduction:** only claim it when the original protocol is actually reproduced and verified.
3. **Contextual literature comparison:** reported paper results with differences in data, feature type, tasks, client setup, attack knowledge, dose denominator, metrics and tuning/test access.

For example, a fixed binary federated IDS, a packet-CNN class-incremental benchmark and this multiclass flow-MLP withdrawal study do not share a single directly comparable F1 leaderboard. Explain the overlap and differences instead of subtracting published headline percentages.

Use [literature-comparison-template.md](literature-comparison-template.md) for direct versus contextual tables. In particular, Lavaur et al. already stop label-flipping attacks and report recovery in a fixed-class FIDS; the class-arrival, retention and fresh-source availability differences must be stated.

The source-based [novelty-and-publication.md](novelty-and-publication.md) assessment identifies material overlap: SacFL studies adversarial FCL, Neurotoxin studies post-attacker persistence, single-task poisoning studies weak one-stage attackers, and continual IDS/noisy-stream papers already investigate replay corruption. FIL-ZTA also combines network-context federated incremental learning and poisoning. Position this as a precise empirical comparison; do not claim first integration or a proven general defense. Primary references and verification limits are recorded in [sources.json](sources.json).

## 15. Milestone schedule

Deadline is unknown. The following is a dependency-based ten-working-day template for two implementation authors, with contributor compute used after the protocol is ready.

| Milestone | Indicative time | Exit gate |
|---|---|---|
| M0: scope and feedback reconciliation | Half day | Signed-off specification and amendment list |
| M1: canonical data and split audit | Days 1–2 | Provenance, support and isolation gates pass |
| M2: reference engine | Days 2–4 | FT, EI, replay/admission and stage lifecycle agree with the specification |
| M3: acceptance/recovery and runtime profiling | Days 4–5 | Recovery evidence, compatible environment and measured stage costs |
| M4: development pilots/tuning | Days 5–6 | Clean-learning feasibility and selected common budget/settings |
| M5: protocol lock and contributor release | Day 6 | Immutable code/data/config/analysis package and verified worker setup |
| M6: final paired experiments and ablations | Days 7–8, runtime dependent | Complete validated selected matrix; no missing pairs hidden |
| M7: sealed evaluation, statistics and figures | Days 8–9 | Complete prediction/analysis tables and checksums |
| M8: report, reproducibility bundle and critique | Days 9–10 | Every required section and claim is traceable; limitations and failures included |

Eight accounts shorten the execution stage; they do not remove the sequential data, correctness and development gates. If the deadline is shorter, reduce optional research scope, not data isolation or result provenance.

## 16. Report and release structure

Suggested paper sections: introduction/contribution; related work; threat model and research questions; data/protocol; implementation and amendments; main results; ablations/mechanism diagnostics; costs; discussion/limitations; reproducibility/data availability; conclusion.

Release a compact package containing the frozen protocol, amendment log, source snapshot, dependency/environment records, data acquisition/build instructions, manifests/hashes, selected configurations, validated metrics/predictions, figure/analysis scripts and a claim ledger. Include complete local state only where required to reproduce continuation experiments. Do not publish third-party raw data or credentials without the appropriate rights.

## 17. Remaining experimental risks

- Canonical metadata and session/component support may make the exact primary protocol infeasible.
- New prior art may substantially narrow the contribution.
- DC's primary schedule does not test general recurring-class balancing.
- A weak/null attack is possible and must remain reportable.
- Hardware/runtime variation can confound method or resource comparisons if blocks are scheduled poorly.
- Rare supported classes, benign subsampling and a single historical capture limit external validity.
- A bounded record buffer does not by itself bound all telemetry, prepared data, optimiser or process memory.
- Additional controls improve attribution but also add time, comparisons and implementation risk.
- A second dataset is useful only if its own provenance, split and feature/metadata limitations are honestly audited.

The [methodological-risk-review.md](methodological-risk-review.md) derives the poison-retention floor, distinguishes full-trajectory ablations from post-E2 forks, and reviews ceilings, acquisition F1, corrective-data availability and separately tuned pipelines. [failure-and-amendment-policy.md](failure-and-amendment-policy.md) defines operational and scientific failure handling. These risks become implementation/data-audit decisions; no experimental success is assumed by the reviewed plan.

## 18. Second audit: evidence and readiness

Read [audit-executive-summary.md](audit-executive-summary.md), [feature-domain-and-precision-review.md](feature-domain-and-precision-review.md), [data-release-decision.md](data-release-decision.md) and [rubric-and-readiness.md](rubric-and-readiness.md). Conditional archive/component/split/ownership counts are data-feasibility results, not model-performance results. [candidate-data-profiles.json](candidate-data-profiles.json) keeps the two prospective profiles unselected. The revised learner, acceptance evidence, runtime profiling and final evaluation remain pending.
