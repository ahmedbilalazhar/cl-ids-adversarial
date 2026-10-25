# E1 acquisition diagnosis — 24 October 2026

Extending the original-loss FT schedule from three to twelve rounds restored the existing mean E1 acquisition thresholds in this fixed diagnostic. The same three development seeds were used. This supports testing a longer common training budget before changing the loss. It does not qualify any four-stage learner or unlock final evaluation.

All 4 independent arithmetic/scope fixtures passed. The probe reproduced all nine frozen FT round states, all client dropout states and update/exposure counters exactly. Parent source, delivery scripts and indexed evidence remain unchanged.

## Fixed paired comparison

| Current CE objective | Rounds x epochs | Mean dev FTP recall | Mean dev SSH recall | Mean E1 macro-F1 | Mean benign FAR | E1 mean thresholds |
|---|---|---:|---:|---:|---:|---|
| natural | 3 x 1 | 0.6667 | 0.0000 | 0.4164 | 1.02% | Fail |
| natural | 12 x 1 | 0.6667 | 0.9972 | 0.5535 | 1.93% | Pass (E1 only) |
| equal_class | 3 x 1 | 0.3333 | 0.3322 | 0.3580 | 2.71% | Fail |
| equal_class | 12 x 1 | 0.6667 | 0.9994 | 0.5041 | 2.62% | Pass (E1 only) |

The natural twelve-round FTP recalls are 1.0, 1.0 and 0.0 for seeds101–103. Its SSH recalls are 0.9966, 0.9966, 0.9983. Seed103 remains unable to acquire FTP. A mean gate pass must not conceal that failure.

Equal-class weighting at three rounds did not meet either mean anchor threshold and had lower mean macro-F1 than the natural objective. At twelve rounds it slightly raised SSH recall but still left seed103 FTP recall at zero, with lower mean macro-F1 and higher benign FAR than natural. These cells do not support promoting weighting as the next revision.

The longer schedule jointly changes current-record exposure, synchronization count and Adam reset count. The paired intervention establishes sensitivity to that bundle; it does not identify which part causes the change.

## Location of the failure

The E1 inventory contains 3,500 benign, 2,382 FTP and 1,776 SSH records. This does not show extreme global label imbalance. Three clients have no benign E1 rows; class ownership and per-client update counts are uneven. There are 7,658 distinct FP32 E1 feature vectors and zero cross-label exact feature collisions. This rules out an exact-feature collision bound as the explanation for these particular training errors; it does not prove separability or rule out source-label problems.

| Natural objective, round3 | FTP aggregate recall | Local models with FTP recall >=0.5 | SSH aggregate recall | Local models with SSH recall >=0.5 |
|---|---:|---:|---:|---:|
| Seed 101 | 1.0000 | 4/5 | 0.0000 | 2/5 |
| Seed 102 | 1.0000 | 4/5 | 0.0000 | 0/5 |
| Seed 103 | 0.0000 | 1/5 | 0.0000 | 1/5 |

At 3 natural round3 seed/family comparisons, at least one local endpoint attained recall >=0.50 on the common development bank while the averaged model did not. The shared bank makes these directly comparable outputs. They show loss of that local decision behavior during weight averaging at those transitions, but do not show that aggregation is the sole cause. Local models may have poor precision, benign behavior or other-class recall; full local confusion tables are retained.

## Compute and evidence

Six new physical E1 trajectories produced twelve logical objective/budget cells across three paired development seeds. They used 4,464 local optimizer updates and 551,376 current-record exposures, taking 108.88 measured CPU seconds including readouts. This is additional diagnostic work, separate from the original 69 complete physical clean executions. Prefix replay is verification work and adds no independent replicate.

Per-round training/development CE, probability, logit margins, recalls and confusion matrices; local endpoints; source identities and model hashes are in [the indexed evidence](evidence/review-index.json). The original result folder retains the E1 model arrays. No final-test row was loaded. A preflight bank-slicing defect and its preserved failed attempt are documented in [the log](log.md).

## Next gated experiment

Prepare a distinct v3 development revision with synchronization candidates (3 rounds,4 epochs) and (12 rounds,1 epoch), both twelve local passes. This compares the present three-broadcast schedule with a more frequent-broadcast schedule at equal nominal exposure. Preserve the natural objectives first, repeat method/recovery acceptance for the added budget, then rerun all 18 pilots and the selected-budget 60-row grid. No E1-only result substitutes for EI/DR, E2 Hulk or later acquisition/retention.

The [proposed amendment](proposed-amendment.md) records exact changes, visible evidence, reruns and release gates. It is a proposal for the next implementation milestone. V2 remains the valid record of its failed clean procedure.
