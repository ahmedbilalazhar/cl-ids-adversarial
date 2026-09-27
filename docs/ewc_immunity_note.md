# Why EWC is immune to federated-averaging divergence (mechanistic note, Phase-3 step 19)

Status: principled argument + testable predictions, NOT a theorem. The
measurements it must explain (locked, chrono rebuild pending): under
federation, finetune 0.299→0.224 (p=0.031) and DER++ 0.274→0.224 (p=0.031)
drop, while EWC transfers intact 0.307→0.308 (p=0.94) — with or without
poisoning, and the IID control (α=1000) recovers finetune only to 0.216,
so label skew is NOT the driver.

## Argument

1. **EWC = quadratic trust region around the shared solution.** The penalty
   (λ/2)·Σ F_i(θ_i − θ\*_i)² bounds how far any client's local optimum can
   move from the broadcast point θ\* (anchor reset to the global model after
   every round in our fedavg.py). FedAvg of models that all stayed inside
   overlapping trust regions lands back inside the low-loss region — the
   average of anchored solutions is itself an anchored solution. Fisher
   matrices differ per client under skew, but every penalty is still centred
   at the SAME θ\*, so the constraint is coherent across clients.
2. **Finetune has no drift constraint.** Unconstrained local optimisation on
   small skewed shards moves each client toward a distant local optimum
   (the standard client-drift problem motivating FedProx, Li et al. 2020).
   With 1 round/task there is no reconvergence: the average lands in a
   high-loss region between client optima, and the error compounds per task
   (forgetting −0.05 vs single-node). Skew-independence (α=1000 control)
   follows: even IID shards diverge in one round because each shard is a
   small-sample optimum, not because labels differ.
3. **DER++/ER replay cannot anchor what it never saw.** Each client's buffer
   inherits its OWN shard skew (uniform eviction, no balancing — disclosed);
   replaying a skewed buffer rehearses the skew. Distillation teachers are
   locally drifted snapshots. Plus the 5× total-memory confound (quantified
   by the b100 arm: matched-memory gap n.s.). Hence DER++ behaves like
   finetune-with-noise under federation.
4. **Poison-invariance follows, not precedes.** At ≤10%-of-shard budgets the
   poison signal is second-order next to averaging divergence; EWC's
   immunity to the first-order effect (drift) masks the second-order one.
   Prediction: past the breaking point (Phase-3 sweeps), EWC must break too.

## Testable predictions (registered before running)

- P1 (lambda sweep): EWC immunity scales with λ. λ=0 federated EWC ≈
  federated finetune (no anchor → drift returns); λ=1000 ≥ λ=100 retention.
  Configs: f2_fed_ewc_p0_l0_c, f2_fed_ewc_p0_l1000_c. If P1 fails, the trust-
  region story is wrong and §1 is rewritten, not patched.
- P2 (rounds, follow-up): if drift-per-round is the mechanism, more
  rounds/task should recover finetune toward single-node. Needs a fed.rounds
  loop (not yet implemented) — runs only if P1 is inconclusive.
