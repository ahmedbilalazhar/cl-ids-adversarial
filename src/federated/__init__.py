"""Minimal FedAvg simulation over the existing CL + poisoning code (Phase 1).

Design (see docs/proposal.md Phase-1 note in Phase 6):
- 5 simulated clients, 1 federated round per CL task (day).
- Within each task, the task's training pool is partitioned non-IID across
  clients with per-class Dirichlet(alpha=0.5) label skew
  (src/federated/partition.py). Rationale: CICIDS2017's natural non-IID axis
  is attack mix per network segment/day; per-task label skew models segments
  seeing different mixes of the same day's traffic.
- Each client trains the SAME CL method class (finetune/EWC/DER++) with the
  SAME hyperparameters as the single-node configs, for local_epochs=3
  (matches single-node epochs_per_task for Phase-3 comparability).
- Server aggregates with sample-count-weighted FedAvg and broadcasts.
- Client 4 is malicious: it poisons its local shard with the UNCHANGED
  attack functions (label_flip / inject_backdoor) at budget rho of its own
  shard before local training. Global poison fraction ~= rho / n_clients.
- EWC clients: anchor re-synced to the broadcast global weights each round
  (anchor = "previous solution" ~= global model); Fisher keeps accumulating
  locally via the Phase-0-fixed EWC code. No CL/attack code was reimplemented.
"""
