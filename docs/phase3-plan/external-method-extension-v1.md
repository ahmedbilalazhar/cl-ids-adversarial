# Prospective external method extension

**Status: train-only pilot authorized by the user's implementation request; held-out test scoring remains gated.** This is a path to assess whether the poisoning-persistence mechanism recurs under a clearly simulated federated setup. It is an independent benchmark extension, not a faithful replication of the primary CICIDS2017 study.

## Train-only intervention selection

`scripts/audit_phase3_external_training_support.py` loads only the four task training-label vectors from each external task archive. It verifies task-artifact hashes from their sidecars and never requests feature arrays, test labels, or test features. The frozen rule chooses the most-supported non-benign class first introduced in task 1, with a minimum support of 50 and label-ID tie-breaking:

| Dataset | Selected source class | Task 1 train support | Benign support |
|---|---|---:|---:|
| UNSW-NB15 | Exploits | 33,393 | 14,000 |
| CICIoT2023 | DoS | 12,000 | 8,000 |

The machine-readable counts and input hashes are in `results/phase3-followup/external-training-support-audit-v1.json`. Selection uses training labels only; the test partitions remain untouched.

An ID-only audit (`results/phase3-followup/external-id-isolation-audit-v1.json`) found no repeated task IDs within either provider train pool or test pool. Train and test IDs are positional within separate source pools, so this does not check cross-pool duplicate flows or session/component isolation.

## Train-only adapter pilot

The versioned protocol is `configs/phase3/external-method-extension-v1.json`. It specifies separate native-dimension MLPs, the dataset-provided four-task schedule and T0-train-fitted preprocessing, five persistent **synthetic** clients, and a task-1 source-to-benign intervention followed by withdrawal before task 2. The train-only pilot is complete: FT, EI, DR, and DR+DC each ran with clean and attacked conditions at seed 101 on both datasets (16 runs, 64 task-stage checkpoints). It uses three rounds, one epoch per round, batch size 128, CPU FP32, and the Phase 3 reference coefficients. These are exploratory implementation settings, not selected final settings. The adapter requests only training feature, label, and ID members. No held-out test array was read and no test metric was computed.

The run inventory and provenance hashes are in `results/phase3-followup/external-method-training-pilot-summary-v1.json`; per-arm traces and checkpoints are in `results/phase3-followup/external-method-training-pilot-v1/`. The executed training files also record archive, synthetic ownership/poison artifact, protocol, and checkpoint hashes. All 16 arms completed with deterministic CPU FP32 execution and finite-value checks enabled by the reused learner. Across four tasks, each run presented 175,341 UNSW training rows or 121,378 CICIoT training rows. The selected attacker's task-1 intervention relabeled 5,740/11,480 UNSW source rows and 1,120/2,240 CICIoT source rows (50%). This is an implementation/execution check only: one seed cannot establish robustness, and no outcome claim can be drawn without the frozen held-out evaluation.

The client assignment is deliberately labeled synthetic. Neither external package contains owner or component/session identifiers comparable to the adopted CICIDS grouping. Thus this design cannot support host-, organization-, campaign-, or session-independent claims. Dataset task construction also differs, and native feature units remain undocumented.

## Gates before any full-method run

1. Implement and pin a separate held-out evaluator and qualify its metric semantics against hand-audited examples without loading test rows; leave the adopted 74-input CICIDS reference code unchanged.
2. Strengthen external row/component/session leakage assessment: current provider IDs are pool-local and do not support cross-pool or real-owner independence claims.
3. Extend the one-seed adapter pilot to the three preregistered paired seeds only after documenting the pilot's single-seed limitations and pinning all source/config hashes.
4. Freeze code, configuration, seed pairing, metrics, and analysis before any external held-out test scoring.

The source-support and ID audits establish enough training support and unique task assignment IDs. They do not clear the missing real-owner provenance, component/session isolation, or held-out evaluation gates. No external test scoring is authorized by this protocol; freeze the adapter and analysis before any test-array access.
