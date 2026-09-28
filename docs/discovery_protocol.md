# E4 discovery protocol (experimental, 2026-09-28)

E4 is an offline simulation of unknown-class discovery inside a continual IDS.
The chronological E4 configs use the duplicate-disjoint CICIDS task artifact.
Historical E4/E5 outputs are archived in
`results/_archive/discovery_transductive_20260928/`; they cannot support the
new protocol.

## Causal order

For each task, the runner selects benign training rows and, with the task
seed, holds out 20% of them for threshold calibration. It fits the AE on the
other 80%, then sets the reconstruction threshold at the configured 95th
percentile of the separate calibration scores. Neither stage reads test rows.

The configured poison edits training features before candidate selection.
HDBSCAN fits only on training rows whose AE scores exceed the threshold. To
bound memory, it fits at most 4,000 of these candidates, drawn uniformly
without replacement with a recorded seed. Other training candidates and
held-out test candidates are assigned to the nearest fitted cluster centroid
when their Euclidean distance is no greater than that cluster's maximum
training-member radius. This frozen rule is a documented approximation, not
HDBSCAN's own prediction API. Test rows never alter clusters or centroids.

Each training cluster gets a task-unique provisional class ID. In the
discovery arm, its members use that ID during classifier training; attacker
supplied sentinel labels are ignored. Unclustered training rows retain their
original labels. The `direct_label_poison` control uses attacker supplied
labels in classifier training while still computing discovery diagnostics;
its clusters do not relabel the classifier stream. Cluster-to-provisional-ID
and poison-fraction maps are persisted per task.

## Endpoints and denominators

- Discovery miss rate: attacks below the AE threshold / all held-out attacks.
- Benign false-alert rate: benign rows at or above the threshold / all
  held-out benign rows.
- Attack flagged rate: attacks at or above the threshold / all held-out
  attacks.
- Attack absorption: flagged attacks assigned to a poison-dominated cluster
  / all held-out attacks, and separately / flagged held-out attacks.
- A poison-dominated cluster has at least 50% poisoned training members among
  rows assigned to it. This threshold is a protocol definition, not an
  estimated biological or deployment truth.
- Cluster assignment purity and adjusted Rand index use held-out ground
  truth only for **evaluation**. Per-family classifier recall and benign
  classifier false-positive rate are recorded after training.
- Zero-denominator endpoints are JSON `null` (N/A). Novelty poisoning has no
  single ASR target across provisional classes.

## Measured limitations and next tests

One no-poison seed is exploratory. Its unweighted mean discovery miss rate
across tasks with attacks was 0.755; the T1 attack miss rate was 0.998. The
detector's usefulness must be investigated before interpreting a marginal
poisoning effect. Its resource probe on the local 8-logical-CPU Windows host
used `CL_THREADS=2`; see `results/diagnostics/e4_nopois_seed1_final_resource.json`.

Candidate capping materially changes decisions. On a seeded 5,000-candidate
subset of task 2, exact fitting versus a 4,000-candidate fit yielded 126
versus 103 clusters and adjusted Rand index 0.628. A 1,500/1,000 comparison
gave 0.522. These are small-case checks, not proof of behavior relative to
full fitting on 125,570 task-2 candidates. Treat E4 as a **capped discovery
protocol**; any paper claim must say so. Run matched three-seed no-poison,
anchor-poison, and direct-label-control diagnostics, and quantify seed and
cap sensitivity before selecting a 12-seed comparison. Do not infer an
attack effect from the lone baseline seed.
