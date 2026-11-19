# Autonomous CPU extension: prospective plan, 16 November 2026

The existing submission is preserved. Its 696 GPU and 57 CPU trajectories are
historical development evidence, not 753 independent client partitions.

## Critique and priority

1. The GPU study's clean FTP/SSH acquisition is poor. More repetitions cannot
   repair that validity problem. Restore the already implemented Phase 2 engine:
   Xavier head expansion, batch 128, client-local empirical importance, independently
   retained client dropout/replay RNG, and admitted-count FedAvg. Reuse the historical
   clean-only v3 tuning choice, then require the clean acquisition gates again.
2. Three ownership seeds give weak statistical resolution. Use twelve fixed new
   whole-component ownership seeds (1 through 11 and 42), conditional on this capture.
   These are independent partition/randomization units, not independent captures.
3. Restore the Phase 2 single eligible malicious client, E2-only Hulk-to-benign
   attack and nested doses 0, .1, .3, .5. Never increase attack strength because a
   result is weak. Original majority-attacker results remain exploratory.
4. A deletion control changes memory composition. Add exact oracle label repair
   at E2 for poisoned DR and DC at dose .5. Clone the entire model/client/RNG state;
   change only labels of poisoned IDs in replay, preserve teachers and occupancy.
   This is an explanatory oracle, not a deployable defense.
5. Compare full DR, client-local EI, FT, global loss ranking DM, class-aware DC.
   Add matched random admission DQ, replay loss removals, and matched quota changes
   only after the complete core, in complete twelve-seed blocks.
6. Report stage confusion matrices, early acquisition, final eligible macro F1,
   binary precision/recall/F1/FAR and targeted Hulk-to-benign ASR. Estimate paired
   effects over ownership seeds; do not count stages or repairs as independent.

## Frozen execution and stopping rule

CPU only, two processes, one PyTorch/BLAS thread per process, deterministic FP32.
Use the existing Python 3.12 / PyTorch 2.7 CPU reference environment. No mutation
of historical protocols or results. Immutable input/source hashes and atomic outputs.
Repeat clean feasibility on seeds 101--103 for FT/EI/DR before new-seed training:
mean E1 FTP and SSH recall >= .5, E2 Hulk recall >= .7 for each learner.
Historical selected parameters: 12 rounds, 1 epoch, lr .001; EI lambda 100;
DR label coefficient 1, logit coefficient .1. No holdout-driven retuning.

Core: 5 methods x 4 doses x 12 seeds = 240 full trajectories; exact-label-repair
continuations for DR/DC dose .5 add 24 paired suffixes. Admission q=.75, rare floor20.
Optional blocks, in order: DQ clean/.5 (24); DR label-only/logit-only clean/.5
(48); DM/DC quota .5/.9 clean/.5 (96). A block starts only if measured runtime
predicts completion before the 6.5-hour training cutoff. Blocks are never chosen
by accuracy or attack effect. Reserve 1.5 hours for scientific checks and packaging.
In-flight jobs may finish; missing work is listed explicitly. No fabricated results.

This extension uses the frozen development bank, already used for historical model
selection. It is NOT a new independent final-test claim. Final-test release needs
a separately audited evaluator and a frozen full analysis specification; leave it
sealed during this time-bounded extension. No new dataset is introduced without
provenance and feature/taxonomy validation. Additional capture generalization,
unavailable classroom feedback and live-network deployment cannot be fixed by
CPU hours; report those limitations explicitly.

## Deliverables

Appendix PDF with new results, clean gates, exact repair checks, uncertainty and
CPU timing; machine-readable per-stage matrices; stage weight checkpoints;
source/input/runtime identities; and an updated roll-number ZIP preserving the
main report. An optional experiment is labelled incomplete unless all twelve
predeclared ownership units finish. Equal evidence standards apply to null results.
