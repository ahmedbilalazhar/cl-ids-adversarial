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

Nine code-hashed exploratory seeds (three per arm) are complete. Mean ACC was
0.521883 for no poison, 0.530564 for anchor poison, and 0.554113 for the
direct-label control. Mean pooled attack absorption was 0 in the no-poison
arm and 0.000935 in each poison arm. These are descriptive diagnostics, not a
prespecified or significant paired effect. In no-poison seed 1, the unweighted
mean discovery miss rate across tasks with attacks was 0.755; the T1 attack
miss rate was 0.998. A post hoc threshold audit at T1 found attack flagged
rates of 0.00182 at quantile 0.95 and 0.16648 at quantile 0.50, while benign
false-alert rates rose from 0.014 to 0.35733. The detector's usefulness
must be investigated before interpreting a marginal poisoning effect.
Seed-1 local resource records for all three arms are in `results/diagnostics/`.

Candidate capping materially changes decisions. On a seeded 5,000-candidate
subset of task 2, exact fitting versus a 4,000-candidate fit yielded 126
versus 103 clusters and adjusted Rand index 0.628. A 1,500/1,000 comparison
gave 0.522. These are small-case checks, not proof of behavior relative to
full fitting on 125,570 task-2 candidates. Treat E4 as a **capped discovery
protocol**; any paper claim must say so. The matched three-seed diagnostic is
complete. Quantify cap sensitivity beyond these small subsets and resolve
detector quality before selecting a 12-seed comparison.

A three-seed follow-up audit is in `docs/e4_detector_cap_audit.md`. T1
reconstruction-score AUC is 0.120–0.128, with attack scores typically below
benign scores. Three seeded 5,000-versus-4,000 T2 cap probes have ARI
0.628–0.728 and fewer capped clusters. This reinforces the current hold on
final E4 inference; it does not justify changing q0.95 or treating the cap
as equivalent to fitting the full training candidate stream.
