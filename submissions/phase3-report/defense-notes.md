# Explaining and defending the study

## Ninety-second explanation

We study a network intrusion detector that learns new annotated attack families
over four stages while five simulated clients collaborate using FedAvg. A label
feed corrupts Hulk examples during stage E2 and stops afterward. We ask whether
the detector retains useful knowledge and also retains attack-associated errors.

Our original grid compares fine-tuning, EWC-style regularisation and DER++-style
replay, plus volume-matched and class-aware admission controls. The CPU supplement
adds an intervention after identical poisoned training: remove known-poisoned
memory, or remove the same number of randomly selected memory records. This
distinguishes continuing poisoned replay from merely deleting memory volume.

The report presents the actual completed outcomes, including failed baselines and
defense trade-offs. Our conclusions are limited to one corrected historical
capture and development split. We do not claim independent-site generalization,
zero-day discovery or a deployable oracle defense.

## Likely questions

**What is the proposed contribution if DC is not consistently beneficial?**
The evaluated contribution is a controlled study of poisoning persistence and
legitimate adaptation, including a tested admission hypothesis and component
ablations. A negative defense result remains a result; it must not be rewritten
as successful protection. Explain the actual trade-off shown in the final tables.

**Why report both recall loss and targeted ASR?**
Hulk predicted as another attack loses family recall but can still trigger an
alarm. Hulk predicted benign evades detection. H uses the clean-matched targeted
error over E3/E4; final recall damage is a separate diagnostic.

**Why does FT/EI show zero final recall damage?**
Their clean models already forget Hulk at E4. There is little remaining recall
to lose. Compare immediate E2 damage, absolute targeted errors and clean
performance before interpreting a clean-matched difference as resistance.

**Is the oracle purge usable in deployment?**
No. It uses evaluator-only poison provenance. It diagnoses a mechanism relative
to count-matched random deletion; ordinary training/admission never receives the
mask. A deployable detector for poisoned records would require separate work.

**Does the purge prove weights were unaffected?**
No. All arms start with the same already-poisoned E2 model. Better later recovery
supports a contribution from continuing stored poison under this continuation;
memory composition, later replay draws and recovery dynamics also change.

**Are there twelve independent experiments?**
There are three simulated ownership partitions with four training replicates in
the original grid. Replicates share ownership and all runs share one capture and
split. We show partition-level effects and do not call these independent sites.

**Why are there no significant partition-level p-values?**
Three partition units provide very coarse exact inference; the smallest possible
two-sided signed-rank sign-enumeration p-value is .25. Large descriptive effects
can still be informative within this protocol, without a population-level claim.

**Why use five attackers out of five clients?**
This is a severe label-feed corruption stress test, not a Byzantine-tolerance
guarantee. Training agents still follow the protocol. The grid also includes one
and three attackers; client count and within-client corruption are reported
separately. No general honest-majority robustness claim is made.

**Why is CICIDS2017 acceptable, and what does it miss?**
The corrected public release enables a pinned, auditable experiment. It remains
an old historical capture, so modern traffic, cross-capture generalization and
live deployment are unresolved. Corrected and original releases are not
independent datasets.

**Why is an offline pooled classifier included?**
It checks whether the feature representation and architecture can learn when
historical data and future classes are available. It is not memory-, optimizer-
or federation-matched, and is not a guaranteed mathematical upper bound.

**Why not rank our accuracy against another paper?**
Dataset version, split, label taxonomy, task, attack and metric definitions differ.
The report separates direct local comparisons from contextual published research.

**What changed from Phase 2?**
Use the report's methodology-change table. The scope, attacker grid, repetition
structure and exploratory analysis changed. The original persistence definition
was restored; instructor approval is not invented.

## Demonstration order

1. Open the report's clean baseline and attack/withdrawal figures.
2. Explain the CPU intervention table and the E2-state parity validation.
3. Show one run JSON, its configuration/source identity, and confusion matrices.
4. Show CPU completion/hash validation and the one-command analysis reproduction.
5. End with the limitations and the distinction between an oracle and deployment.
