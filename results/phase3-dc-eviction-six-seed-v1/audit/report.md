# Replay eviction comparison

The audit verified 24 trajectories and 96 checkpoints across 6 paired ownership seeds under DC admission.
Outcomes use the development bank of one historical capture.

Effects below subtract the matched reservoir outcome at dose .5. The 95% bootstrap intervals resample whole seeds and are descriptive. Higher A and macro F1 are favorable. Lower H and FAR are favorable.

| Policy | Metric | Mean difference | 95% interval |
| --- | --- | ---: | ---: |
| FIFO | Acquisition A | -0.1586 | -0.2112 to -0.1151 |
| FIFO | Targeted persistence H | +0.0595 | -0.0006 to +0.1775 |
| FIFO | E2 Hulk recall change | +0.0000 | -0.0000 to +0.0000 |
| FIFO | E4 eligible macro F1 | -0.3783 | -0.4237 to -0.3426 |
| FIFO | E4 benign FAR | +0.2904 | +0.1083 to +0.4880 |
| Class-balanced | Acquisition A | -0.0377 | -0.0903 to +0.0095 |
| Class-balanced | Targeted persistence H | +0.0004 | -0.0001 to +0.0009 |
| Class-balanced | E2 Hulk recall change | +0.0000 | +0.0000 to +0.0001 |
| Class-balanced | E4 eligible macro F1 | -0.0003 | -0.0715 to +0.0664 |
| Class-balanced | E4 benign FAR | +0.0242 | -0.0359 to +0.0865 |

Admitted IDs diverged from reservoir in 72 stage comparisons. This is a downstream effect of the replay policy through the DC scoring model.

[Per-run metrics](cell-metrics.csv) · [Paired effects](paired-comparisons.csv) · [Comparison figure](eviction-policy-comparison.pdf) · [Audit summary](summary.json)
