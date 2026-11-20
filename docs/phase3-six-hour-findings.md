# Phase 3 evidence extension findings

This supplement extends the [audited Phase 3 report](../submissions/phase3-audited-report/phase3-report.pdf). The new analyses use the adopted 74-feature development bank and paired ownership seeds from a single capture. The effects and 95% whole-seed bootstrap intervals below are descriptive. The original 29-comparison family remains as specified.

## Completed evidence analyses

The DG-v5 audit verified 48 DG trajectories, 192 stage checkpoints and 96 matched DM/DC controls. E1 admissions and model hashes agree across all three arms. DG is an unmatched volume baseline, so the DG–DC contrast combines differences in sample count and composition. In the .5 dose cell, DG increased acquisition A by 0.0791 relative to DC (95% interval 0.0190 to 0.1283) and reduced benign FAR by 0.0870 (−0.1180 to −0.0657). Its targeted persistence H increased by 0.0272 (0.0049 to 0.0597). This is a trade-off between acquisition, false alarms and persistence. The full comparison includes DG relative to DM. [Audit report](../results/phase3-dg-baseline-v5/audit/report.md) · [Paired results](../results/phase3-dg-baseline-v5/audit/paired-comparisons.csv) · [Figure](../results/phase3-dg-baseline-v5/audit/dg-dm-dc-comparison.pdf)

The DR/NONE eviction audit verified 48 FIFO and class-balanced trajectories and 192 stage checkpoints. At dose .5, FIFO reduced E4 macro F1 by 0.5059 relative to reservoir (−0.5463 to −0.4548) and increased H by 0.0871 (0.0120 to 0.1827). Class-balanced eviction increased E4 macro F1 by 0.0333 (0.0040 to 0.0669). Its H difference was −0.0085 (−0.0247 to 0.0001) and its acquisition difference was −0.0014 (−0.0237 to 0.0192). Those intervals leave uncertainty about the latter effects. Both eviction variants were compared at the same capacity and without admission filtering. [Audit summary](../results/phase3-eviction-baseline-v2/audit/summary.json) · [Paired results](../results/phase3-eviction-baseline-v2/audit/paired-comparisons.csv) · [Figure](../results/phase3-eviction-baseline-v2/audit/eviction-policy-comparison.pdf)

## New DC eviction study

The audit verified all 24 trajectories and 96 checkpoints for six paired
ownership seeds. At dose .5, the table shows each policy minus the matched
DC reservoir. Differences and descriptive 95% bootstrap intervals are in
percentage points. Higher acquisition and macro F1 are favorable. Lower
persistent error and benign false alarms are favorable.

| Metric | FIFO | Class-balanced |
| --- | ---: | ---: |
| Acquisition A | −15.86 [−21.12, −11.51] | −3.77 [−9.03, +0.95] |
| Persistent error H | +5.95 [−0.06, +17.75] | +0.04 [−0.01, +0.09] |
| E4 eligible macro F1 | −37.83 [−42.37, −34.26] | −0.03 [−7.15, +6.64] |
| E4 benign false-alarm rate | +29.04 [+10.83, +48.80] | +2.42 [−3.59, +8.65] |

FIFO showed worse acquisition, final macro F1 and false alarms on this
development bank. Class-balanced eviction offered no clear improvement over
reservoir under DC. Admission counts matched, while admitted IDs differed
from reservoir in 72 stage comparisons. The contrast measures the total
effect of the replay policy, including changes in which records the scorer
admits. The other six planned ownership seeds and real held-out evaluation
remain open.

[Frozen protocol](phase3-six-hour-extension.md) · [Audit summary](../results/phase3-dc-eviction-six-seed-v1/audit/summary.json) · [Paired effects for both doses](../results/phase3-dc-eviction-six-seed-v1/audit/paired-comparisons.csv) · [Figure](../results/phase3-dc-eviction-six-seed-v1/audit/eviction-policy-comparison.pdf)
