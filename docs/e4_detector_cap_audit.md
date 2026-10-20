# E4 detector and cap audit (2026-09-28)

This is a post hoc diagnostic of the duplicate-disjoint CICIDS E4 no-poison
arm, using seeds 1–3. It does not change the q0.95 primary threshold, select
a new detector, estimate a poisoning effect, or complete a Holm family. Runtime
`src/*.py` stayed at source hash
`94abb1576b44e9d5c52bc70a05b1b1688fd06f0d60458111fba9d83395668dfb`.
The three audit runs reproduce the q0.95 attack and benign rates in the
existing manifest-v3 no-poison summaries exactly.

## Reconstruction scores

`scripts/audit_discovery_threshold.py` now records the held-out score AUC and
attack/benign median scores in addition to the threshold sweep. Higher AE
reconstruction score means more likely to be flagged. AUC is descriptive
ranking on each task's held-out flows; it does not choose a threshold.

| Task | Held-out attacks | AUC, seeds 1/2/3 | Attack median score, seed 1 | Benign median score, seed 1 | q0.95 attack flagged, seeds 1/2/3 |
|---|---:|---|---:|---:|---|
| T0 | 0 | N/A | N/A | 0.263 | N/A |
| T1 | 2,745 | 0.120 / 0.128 / 0.128 | 0.128 | 0.260 | 5 / 5 / 5 |
| T2 | 58,122 | 0.895 / 0.910 / 0.900 | 12.109 | 0.251 | 42,938 / 39,694 / 42,674 |
| T3 | 654 | 0.664 / 0.639 / 0.668 | 0.412 | 0.278 | 31 / 29 / 31 |
| T4 | 39,422 | 0.678 / 0.700 / 0.673 | 8.660 | 0.334 | 7,531 / 14,632 / 14,123 |

T1 attacks have *lower* scores than benign flows under this high-error
detector. The existing seed-1 threshold sweep found that moving from q0.95
to q0.50 raises T1 attack flagged rate from 0.00182 to 0.16648, but also
raises benign false-alert rate from 0.014 to 0.35733. Lowering the one-sided
threshold after seeing these outcomes is not a defensible primary analysis.
The mechanism behind the inverted T1 ranking is unproven; it may involve the
task's attack families or benign fit population. A redesigned detector would
need a separate development protocol and new versioned runs.

The source data are `results/diagnostics/e4_score_separation_seed{1,2,3}.json`.
Reproduce one audit with:

```powershell
$env:CL_THREADS = "2"
python -m scripts.audit_discovery_threshold --seed 1 --output results/diagnostics/e4_score_separation_seed1.json
```

## Candidate cap

The no-poison T2 training stream has 109,504–125,570 candidates at q0.95
across the three seeds, but the current protocol fits HDBSCAN on only 4,000.
For each seed, `scripts/compare_discovery_cap.py` draws a seeded 5,000-row
training-candidate subset and compares fitting all 5,000 with fitting 4,000
plus frozen centroid/radius assignment on the same subset.

| Seed | Full-subset clusters | Capped clusters | Adjusted Rand index | Full / capped assigned fraction |
|---:|---:|---:|---:|---|
| 1 | 126 | 103 | 0.628 | 0.815 / 0.798 |
| 2 | 127 | 102 | 0.728 | 0.825 / 0.829 |
| 3 | 122 | 94 | 0.646 | 0.854 / 0.808 |

Thus cap effects persist across these sampled subsets. Their ARI values
compare **assignments on 5,000-row subsets**, not against HDBSCAN fitted on
the full 100,000-plus candidate stream. The capped method is the actual E4
protocol; it is not a validated approximation to full-stream HDBSCAN.
No cap-specific downstream classifier or poison-effect sensitivity has been
run. Source data are the three
`results/diagnostics/e4_cluster_cap_4000_of_5000*.json` files.

## Decision boundary

Keep E4 diagnostics exploratory. Do not launch a 12-seed E4 headline
comparison until the detector's intended unknown-class endpoint is judged
viable on a separately specified protocol. If E4 remains in the paper with
the current detector, report the weak T1 ranking and capped clustering as
limitations and keep the original q0.95 rule. The next useful detector work
is family-level T1 score analysis and an independently specified development
split; the next cap work is a bounded larger reference and downstream
sensitivity with measured peak memory.
