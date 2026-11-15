# Local CPU supplement: execution protocol

This protocol implements the accepted six-hour plan. Its experiment source and
configuration identities were recorded before the first completed CPU trajectory.
It extends an already inspected development-bank study; it is not a prospective
registration of the original Phase 2 confirmatory experiment.

## Fixed experiment matrix

Use prepared clean packages `s101-p000`, `s102-p000`, `s103-p000`, the reference
development bank, and the adopted 74-feature taxonomy. No final-test path is read.
Keep the original implementation's architecture, optimizer, 12 rounds per stage,
one local epoch and default DR loss settings. Execute sequentially on CPU with
one PyTorch thread. The first full trajectory measures practical runtime.

1. Three ownership partitions, replicate 0, four conditions: clean DR, poisoned
   ordinary DR, poisoned DR with oracle purge, poisoned DR with random deletion
   matched to the per-client poison count. Twelve trajectories.
2. DQ clean and poisoned, the same three partitions and replicate 0. Six trajectories.
3. Offline pooled MLP, initialization seeds 101/102/103, all classes registered,
   12 complete passes over training records, batch 256, learning rate .001,
   continuous Adam, no replay. Three trajectories. The data inventory is the same
   across these runs; initialization varies, not independent captures.

All poisoned conditions use five attacking clients and 50% within-client Hulk
corruption during E2. E3 and E4 contain no newly corrupted labels.

## State and intervention invariants

Ordinary, oracle and random-deletion trajectories must have identical end-E2
model parameters, active buffer tensors, supplied labels, stored logit widths,
poison metadata, proposal counters and ordinary RNG state hashes, together with
identical E1/E2 confusion matrices and admissions. Reject any violated pair.

Oracle purge removes evaluator-marked poisoned records. Random deletion removes
exactly the same number per client through a separate intervention RNG. Compact
all stored arrays together. Keep historical proposal counts; subsequent insertions
refill vacant slots before using the usual replacement rule. This declared
post-deletion rule does not preserve a uniform sample of the entire original
pre-deletion stream. Its use is identical across the two deletion arms.

The evaluator mask is never supplied to ordinary admission or training. The oracle
is an explanatory intervention and cannot be called a deployable defense.

## Expansion and stopping

After all 21 required trajectories pass, estimate another 36 trajectories at
1.25 times the slowest observed run. Expand the four-condition mechanism matrix
to replicates 1/2/3 only if this estimate fits the 3.25-hour compute deadline.
Retain all completed required results regardless of effect direction. Do not
change budgets, delete unfavorable seeds, or mix GPU and CPU clean references.

Each complete trajectory is atomically written and configuration/source/input
identity validated before reuse. Resume operates at whole-trajectory boundaries.
Changed sources require a separate output directory. Do not edit the scientific
runner or intervention implementation during an active study.

## Endpoints and interpretation

Report absolute Hulk-to-benign ASR and Hulk recall at E2/E3/E4, targeted persistence
H (mean poisoned-minus-clean E3/E4 ASR), signed immediate recall change, final
recall damage, eligible-bank macro-F1, acquisition, benign FAR, and buffer poison
counts/occupancy. Retain full-inventory confusion matrices and per-class support.

The main mechanism contrast is oracle-minus-random deletion. Average training
replicates within partition; show all three partition effects. Conditional
signed-rank sign enumeration accommodates ties/zeros but still requires symmetric
differences and exchangeable signs. The 15 mechanism contrasts form one exploratory
Holm family. Three simulated partitions do not yield independent capture/site
inference or a two-sided exact p below .05.

Oracle improvement supports a contribution from continuing stored poison relative
to the specified random-deletion control. Remaining damage can reflect poisoned
E2 weights; composition and subsequent replay draws also change. A null effect
does not prove that replay never contributed. The pooled reference has future
knowledge and unrestricted historical access and is not memory/optimizer matched.

The replicate index changes model, minibatch, poisoning and replay RNG streams through the declared seed derivation, while ownership remains fixed. Replicate variability therefore includes attack-subset variability, not only optimizer noise.
