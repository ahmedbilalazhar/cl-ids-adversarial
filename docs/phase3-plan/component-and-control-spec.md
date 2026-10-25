# Components, controls and acceptable causal language

Second audit, 24 October 2026. Prospective implementation detail, not experimental findings. Keep from-start and post-withdrawal interventions distinct. The selected scope is still pending data/profiling gates.

## 1. Exact one-change definitions

| Condition | Change from matching DC | Hold fixed | What it can identify |
|---|---|---|---|
| DC_NoZ | lambda_z = 0 from E1 | Current/replay CE, buffer capacity/stream/insertion, labels, teacher schema, other coefficients/settings | Whole-trajectory contribution of the logit objective under this adapted learner |
| DC_NoY | lambda_y = 0 from E1 | Current CE, logit replay, same retained tuple policy and other settings | Whole-trajectory contribution of replay-label CE |
| DC_FIFO | Replace Algorithm R with a circular FIFO slot, advancing once per admitted first-pass record | Capacity, tuple content, teacher time/mode, sampling and all losses | Effect of eviction policy, including its induced coverage/age distribution |
| DC_ClassBalanced, optional | Explicitly specified class-balanced eviction | Same loss/settings/capacity | Combined contribution of that eviction policy; “balanced” alone is not a reproducible algorithm |
| DQ | Random fixed within-class priority under DC quotas | Scorer-independent class protection, count, small/new exceptions and learner settings | Whether loss ranking adds value beyond class protection under this control |
| DM | Full local-class loss ranking to DC's total count | Same scorer/head/settings and per-client work/weight | Total effect of protecting class quotas rather than ranking all local labels together |

Class-balanced eviction was underspecified in the large optional plan. Section 7 now proposes one precise class-partitioned reservoir adapter. Adoption and implementation remain pending; it is not a reproduction of a named published method. The focused course/research starter excludes this optional condition.

FIFO holds the last 500 stream proposals, not the last 500 minibatches or repeated epochs. For an insertion at persistent stream position j, use slot `(j-1) mod 500`; fill occupancy until capacity. Sample before committing the current batch, as in DR. Preserve the full proposal order and observed widths. This deterministic counter differs from reservoir RNG state but must be checkpointed.

No-logit/no-label ablations retain the declared tuple schema and insertion. They are causal component conditions, not memory/time-optimized ER baselines. If a zero coefficient disables a branch, specify its forward/draw/RNG behavior before development. Multiplying an invalid unused loss by zero can still propagate NaN; it is not a safe implementation of “disabled.”

## 2. Randomness and gradient interpretation

Current and replay CE use dropout; logit replay uses evaluation mode. Skipping replay CE in NoY can change subsequent dropout consumption if one persistent client stream covers every CE forward. That is an implementation convention to freeze, not proof that the ablation is invalid. Its effect is the whole specified pipeline change, not a pathwise subtraction of one gradient on an identical future trajectory.

Prefer independent named loss-role dropout streams if stronger common-random-number alignment is worth the engineering; otherwise record the simpler persistent-client convention and limit the claim. Adding a new stream convention after development requires a versioned change and matched reruns. Replay selection/insertion streams remain separate from dropout in either case.

Every later accepted subset can depend on earlier learned state. A repair or loss intervention can therefore change later admission, memory, updates and predictions. Those mediated changes are part of the total intervention effect. They prevent a claim that the endpoint difference directly measures one term's instantaneous gradient damage.

## 3. Oracle repair needs individual poison availability and exposure

For each maximum-dose DC parent at E2, record the number of stored poisoned IDs, their supplied/reference labels, stored logit widths and their later replay counts. Repair stored labels only; retain logits, weights, occupancy, IDs, counters and RNG states. The control continues from the exact same parent unchanged.

If no poison survives at the fork, the label change is empty and the pair remains. If surviving poison is never drawn because the client is inactive, the intervention has no exposure even though memory is nonempty. Do not discard either case. A zero repair effect does not establish that poisoning caused no earlier weight damage or that logit retention is harmless.

Use an evaluator-side join for this diagnosis. The learner receives no poison mask or reference annotation. Do not repair every currently misclassified example or relabel honest difficult records; those are different oracle interventions.

## 4. Conservation identities for result review

On the fixed Hulk bank at each stage:

`Hulk family recall + Hulk-to-benign error + Hulk-to-other-attack error = 1`.

All three come from the same integer prediction partition. Thus immediate family-recall damage need not equal a binary detection loss. Check this identity in the eventual evaluator acceptance work; retain wrong-family alerts as alerts in the binary view.

For each attacked local group:

`honest admitted + poison admitted = total admitted` and
`honest rejected + poison rejected = total rejected`.

For unfiltered conditions, raw/admitted row counts agree. For DC/DM/DQ at a matched seed/stage/dose, totals and distinct-row FedAvg weights agree; accepted IDs generally do not. At clean dose poison ratios with zero denominator are NA, not perfect removal.

These are necessary accounting checks, not evidence that a model is correct or a defense succeeds. No implementation checks were executed for this document.

## 5. Synchronization pilot interpretation

One round of three epochs and three rounds of one epoch share three local epochs but differ in aggregation frequency **and** Adam-reset frequency. They also induce different broadcasts/batches after the first synchronization. Select the common development budget as specified; do not describe a difference as an isolated causal effect of communication frequency.

The clean learning gate, common data and exact update ledger remain necessary. A clean-selected schedule is not a poisoned-outcome tuning opportunity. Count every additional development revision, including a second-budget search after an infeasible clean grid.

## 6. Importance contamination is not automatically harmful protection

EI's anchor is the final shared aggregate, not the poisoned client's pre-aggregation local model. A wrongly supplied benign label can produce a large gradient at a global model that still recognizes Hulk correctly. Squaring that gradient can increase importance around a useful shared solution. Therefore “the poison increased importance” alone does not establish that EI protected a wrong decision or caused persistence.

Report per-layer importance/penalty summaries and evaluator-side annotation joins for the exact importance-sample IDs. These are descriptive channels, not signed gradient attribution. An importance-specific causal claim would need an intervention.

An optional explanatory fork can recompute **only the E2 importance increment** at the same poisoned E2 aggregate, on the same sampled IDs, repairing supplied labels of poisoned IDs. Preserve prior accumulated importance, weights, anchor, future order and all RNG states. Continue E3/E4 against the unchanged primary EI control. At clean dose this label repair is the identity. This would require twelve new maximum-dose suffixes plus the specified recomputation, with primary controls reusable only by exact identity. It is outside the base manifest and is not a practical defense. Do not add it unless the intended claim warrants the extra engineering and prospective analysis specification.

## 7. Proposed class-partitioned reservoir adapter

For the optional `DC_ClassBalanced` condition, a narrow reference choice is `local_class_partitioned_reservoir_v1`:

1. Maintain the local set C of supplied classes ever present in admitted current data, plus one integer proposal count j_c per such class. Add the current stage's admitted supplied classes at stage setup. This uses allowed local labels, not reference annotations or future classes. The set never shrinks.
2. Capacity M=500. In increasing append-only global slot order, give each class `floor(M/|C|)` slots and give the first `M mod |C|` classes one extra. Save exact quotas. This is a deterministic remainder rule, not a learned preference for benign.
3. When C expands, old class quotas cannot grow under this rule. Uniformly subsample any over-quota retained class tuples down to the new quota with a dedicated saved RNG, preserving proposal counts. Do not retrieve evicted history. Newly registered classes begin empty.
4. For each admitted first-pass record of supplied class c, increment j_c once. Apply Algorithm R inside that class's quota: fill while j_c<=quota_c; otherwise draw uniformly from 1..j_c and replace a class slot only when the draw is <=quota_c. Preserve tuple content, pre-update teacher timing and ordered batch commits.
5. Draw the replay batch uniformly without replacement over **all occupied slots**, as in DR. Do not also change to class-balanced replay sampling. Keep losses, current order, scoring and DC admission fixed.
6. Checkpoint C, quotas, j_c, slot-to-class assignments, tuple arrays and all sampling/shrink/insertion RNG states. Fixed class namespaces make one class's sampling independent of incidental execution order.

Under a fixed stream, shrinking a uniform per-class reservoir by uniform subsampling preserves a uniform sample at the smaller quota. Rare classes with fewer observations than quota leave unused slots; actual occupancy can be below 500. Report that occupancy and replay-batch consequences. The condition tests this complete bounded eviction/storage policy, not equal occupied memory at every update or an independently tuned state-of-the-art method.

If external taxonomy has more than M classes, this adapter needs a separate zero-quota rule; it is outside the present 15/16-class candidate. Freeze adoption before development and provide acceptance evidence during implementation.

## 8. Strong pairing invariants and teacher contamination

With the specified unfiltered DR policy, current IDs/order, active head, batch counts and client participation are identical across doses. Reservoir insertion and uniform replay draw depend on IDs/order/counters/RNG, not labels or model gradients. Given identical E1 state and independent named streams, **buffer IDs and replay slot draws should therefore match exactly across doses**. Supplied labels, cached logits and model weights may differ. EI's uniformly sampled importance IDs should likewise match across doses when its current pool is unchanged.

For DM/DC/DQ at the same seed/dose, per-client admitted counts, stage proposal counts, batch shapes and occupancy match. Accepted IDs can differ. Under the declared shared replay/insertion stream identity, reservoir stream-position decisions and replay slot indices can align even though the records in those slots differ. Record this useful common-random-number structure without claiming identical trajectories.

These invariants do not apply automatically to class-aware eviction, which uses supplied-label histories, or different loss-role RNG conventions. They are specifications for eventual acceptance work, not checks already executed on a trainer.

Call a tuple on a flipped-label ID a **poison-bearing record**. Its pre-update teacher vector is not necessarily changed by that record's own wrong label: the vector is cached before the corresponding update. In particular, unfiltered DR's common first E2 batch has the same pre-update model across doses; common-record teacher vectors can be identical there. Later vectors can reflect earlier poisoned updates.

Use paired clean/poisoned stored vectors for matching retained IDs to describe teacher divergence, with original widths and acquisition position recorded. A large vector difference is an outcome of the preceding training treatment; it does not establish that dark replay caused future damage. Oracle label repair intentionally leaves this channel unchanged. Avoid describing every cached vector on a poison-bearing record as a demonstrated corrupted target.
