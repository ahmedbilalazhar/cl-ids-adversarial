# Compute budget and scheduling for eight contributors

Planning scenarios, 24 October 2026. **No runtime in this file is a measurement of the proposed implementation.** Replace scenario values with pilot observations before dispatch. Each contributor operates their own account; each worker simulates the five FL clients locally.

## 1. Count the right units

| Package | Logical full trajectories | Distinct full executions with nine valid dev aliases | Final full trajectories per seed | Distinct E1 prefixes per final seed | New oracle E3/E4 executions with valid control aliases |
|---|---:|---:|---:|---:|---:|
| Core only | 321 | 312 | 20 | 3 | 12 |
| Course with three from-start ablations | 393 | 384 | 26 | 6 | 12 |
| Complete original plan | 633 | 624 | 46 | 8 | 12 |
| Strengthened candidate | 729 | 720 | 54 | 9 | 12 |

The core alone does not complete the ablation rubric. The largest candidate is a menu to evaluate, not the default recommendation. Additional controls outside these packages must be budgeted separately.

The distinct-full column does not yet discount partial E1 reuse. Do not call an E1 cache a full-trajectory saving. Final full trajectories are statistical conditions; compute nodes can be shared when exact prefix identity is established.

## 2. Measure category-specific costs

Record an end-to-end profile for each relevant dataset/method/runtime category:

| Cost field | Meaning |
|---|---|
| Startup/import/input load | Time from runtime allocation to usable prepared inputs |
| E1–E4 training | Current updates and declared replay/importance work |
| Admission | Scoring/ranking and index construction, including zero-cost “none” |
| Importance | EI sampling/per-example gradients/commit |
| Checkpoint | Serialization, hashing and output publication |
| Evaluation | Only charged to GPU quota if a GPU remains allocated |
| Saving/stopping | Runtime time before accelerator release |
| Provider charging | Observed charged quota relative to wall time/device configuration |

Use medians and high observed costs for job packing. Few pilot runs do not justify a precise statistical p95. Keep cold setup separate from warm component timing, and do not extrapolate a tiny balanced sample to full skewed shards without row/update counts.

Different datasets and EI/replay methods can have very different costs. A single average minute-per-run is acceptable only as a transparent rough scenario, not the final scheduler.

## 3. Quota arithmetic

For contributor i:

```text
usable_i = remaining_displayed_quota_i * (1 - reserve_fraction_i)
required_i = sum(charged_cost_of_assigned_jobs_i)
feasible only if required_i <= usable_i for every contributor
```

If all eight actually had 30 hours remaining and a 20% reserve, usable aggregate capacity would be 192 quota-hours. This is a hypothetical ceiling, not verified available capacity. A 20% capacity reserve is equivalent to requiring `1.25 * base_work <= raw_capacity`; use one expression, not both.

Two GPUs visible inside one session do not automatically double quota. Verify charging and measure completed valid work per charged hour. Prefer independent jobs on the two devices if useful; synchronizing this small model with DDP is unlikely to justify its complexity without measurement.

### Rough full-work sensitivity, before prefix savings and all other costs

| Hypothetical average minutes per distinct full execution | Core: 312 | Course: 384 | Complete: 624 | Strengthened: 720 |
|---|---:|---:|---:|---:|
| 5 | 26 h | 32 h | 52 h | 60 h |
| 10 | 52 h | 64 h | 104 h | 120 h |
| 20 | 104 h | 128 h | 208 h | 240 h |

Add the independently measured E3/E4 continuation, cold setup, saving, evaluation and expected failure costs. Prefix sharing may lower the base cost. If development runs on CPU, subtract its GPU cost only after counting its wall time and confirming that selected settings are evaluated under the locked final runtime.

These scenarios show why an eight-account plan can be feasible without being guaranteed. They also show why increasing the grid before profiling is inefficient.

## 4. Aggregate capacity is not sufficient

Twelve seeds on eight workers means four workers initially receive two complete seed blocks. If a block costs B quota-hours and every worker has 24 usable hours, a whole-block assignment needs `2*B <= 24` for those workers.

For illustration, the complete plan has 46 final full trajectories per seed. At a hypothetical 20 minutes each, a block costs 15.33 hours before savings/overhead. Twelve blocks use 184 hours, below 192 in aggregate, but a worker assigned two uses 30.67 hours and exceeds 24. The packing is infeasible despite aggregate capacity. Development and diagnostics make the gap larger.

Resolve this **before final dispatch** through one or more of:

- Smaller scope or measured safe optimizations/prefix reuse.
- A second weekly allocation, scheduled against each account's actual reset time.
- Split a scientific seed block across physical jobs/accounts with the same locked compatible GPU/software/precision signature, maintaining exact state and pair identity.
- Efficient CPU execution of development or complete blocks when justified and prospectively recorded.

The statistical block need not belong to one account. It must remain a correctly paired seed under the specified compatible runtime design. Do not solve quota packing by putting every instance of one method on a different hardware type.

## 5. Scheduling algorithm

1. Inventory actual remaining quotas, reset times, available accelerator models, environment signatures and contributor availability.
2. Separate compatible runtime pools. Prefer one common hardware type for the primary study.
3. Build a dependency graph: immutable prepared inputs -> compatible E1 prefix -> condition suffix -> complete checkpoint -> sealed evaluation. Include conditional dev aliases only after validating them.
4. Estimate each block/job from measured category costs, then sort unstarted jobs by decreasing expected cost.
5. Assign the next job to the compatible worker with the earliest feasible finish and sufficient remaining quota/session margin. Keep paired conditions together where practical.
6. Rebalance **unstarted** jobs after measured completion/failure information. Do not change method settings or seed membership.
7. Check every contributor's quota inequality and session-size constraint, not only the aggregate.
8. Recompute after each saved job. Preserve the predeclared experiment scope; final model outcomes do not drive allocation or optional-scope selection.

The initial A–H seed table is a convenient starting assignment. Its quotas are unknown and it is not a proven feasible schedule. Authors A/B also have development work; do not assume their GPU budgets remain as free as those of contributors C–H.

## 6. Bounded job packing and durable handoff

### Illustrative balanced allocation for the focused starter

At the hypothetical twenty-minute common full-trajectory cost, the focused starter has a ten-hour final block per seed and an eight-hour distinct development block per development seed. Assign two final seed blocks each to A–D (20 hours each), one final block each to E–H (10 hours each), and the three development blocks to E/F/G (18 hours each including their final block). This is 144 base hours in total and leaves per-person margin under the illustrative 24-hour usable allocation. Add independently measured suffix/setup/saving costs before calling it feasible.

Contributors may execute development packages after the authors freeze their candidate grid; the authors still make/record development decisions. There is no requirement that A/B spend their own GPU allocation on every development job. At different measured costs, use the scheduling algorithm rather than this example.

The external version has larger blocks and needs its own packing calculation. Do not extrapolate this assignment by adding its jobs uniformly and assuming it still fits.

Choose pack size from measured work and current session limits. A 2–3-hour first pack limits exposure while the recovery path is new. Longer packs can be more efficient after safe saving is demonstrated. Save a complete checkpoint at declared round/stage barriers and finish normally with a margin before the displayed runtime/quota limit.

A worker should decline to start the next expensive transition when its measured upper planning cost plus save margin exceeds the remaining job budget. A checkpoint only in a live VM is not a backup. Verify/download the saved version's outputs before dependent jobs start.

Dataset references can resolve to updated versions when a provider source is specified only by owner/slug. Use immutable release-specific sources where possible and always enforce the exact expected input hashes. A matching slug is insufficient.

## 7. Local CPU strategy

The inspected local machine has four physical cores/eight logical threads and about 32 GiB RAM. Start with one/two torch or BLAS threads and measure, avoiding simultaneous jobs that oversubscribe the CPU. Use it for data preparation, small semantic checks, analysis, plotting and report generation.

If the tiny MLP is CPU-competitive, a completely recorded CPU block can preserve GPU quota. Do not mix arbitrary CPU/GPU conditions within a seed to make a partial schedule fit. If heterogeneous execution is planned, state the design and compare within compatible blocks; hardware variation is then part of the conditional variability, not pure seed variation.

If development/tuning runs on a different runtime from final training, budget up to nine additional clean confirmations: three selected unfiltered learners by three development seeds on the final runtime. These are not included in the original 81 logical development rows. The three poisoned FT diagnostics should then use compatible clean FT confirmations. If all development and final training use the same locked runtime, this extra package is unnecessary.

Choose one common, recorded evaluation runtime for final checkpoints. It may be CPU if appropriate, provided every condition uses the same evaluation contract. Do not mix CPU and GPU predictions opportunistically or reuse cached predictions across different evaluation identities.

## 8. Runtime reporting

For training, report complete job and component timings including admission, importance and saving. For inference, use the Phase 2 batch-1/batch-256 timing convention with explicit synchronization, warm-up and dispersion. State whether feature extraction/loading is excluded.

Compare resource ratios within the same hardware/runtime blocks. Report unsuccessful development and invalidated-run compute in the research compute inventory even though those outcomes are excluded from performance claims. GPU allocation time is neither electrical energy nor an edge-device latency measurement.

## 9. Recommendation after profiling

Choose the **course package** as the conservative implementation target: 12 paired seeds, five core arms, four doses, three meaningful from-start ablations, and the oracle diagnostic. Prefer adding DQ when testing whether loss ranking helps. Add broader sweeps, external data and recurrence only when a specific claim needs them and both engineering and compute margins remain.

The original complete Phase 2 proposal remains the specified target unless a smaller prospective amendment is selected. No formal external preregistration is being claimed. The most efficient publication candidate is the smallest plan that supports the intended finding with fair controls. The 729-row candidate is an optional expansion.
