# Results analysis and discussion

12 paired units (3 ownership partitions x training replicates), paired by unit; confirmatory tests follow the Phase 2 plan (Wilcoxon signed-rank, Holm inside each family). Development bank only. Device: runs_cuda.

## 1. Clean baselines
- FT: final macro-F1 0.031 (sd 0.012), backward transfer -0.719, benign false-alarm rate 0.984.
- EI: final macro-F1 0.046 (sd 0.028), backward transfer -0.688, benign false-alarm rate 0.932.
- DR: final macro-F1 0.491 (sd 0.069), backward transfer -0.047, benign false-alarm rate 0.104.

## 2. RQ1: how much does a poisoned stage damage each learner?
Hulk recall lost at E2 (immediate) / persistent damage H at E4, by attack arm (share of Hulk rows poisoned in brackets):
- k5-d0.25 (25%): FT 0.000 / 0.000; EI 0.000 / 0.000; DR 0.000 / 0.032
- k1-d1 (26%): FT 0.031 / 0.000; EI 0.057 / 0.000; DR 0.130 / 0.162
- k5-d0.5 (50%): FT 0.494 / 0.000; EI 0.530 / 0.000; DR 0.612 / 0.785
- k3-d1 (70%): FT 0.835 / 0.000; EI 0.838 / 0.000; DR 0.883 / 0.582
- k5-d0.9 (90%): FT 1.000 / 0.000; EI 1.000 / 0.000; DR 1.000 / 0.993
- C1 tests: 6 of 30 learner-pair comparisons significant after Holm correction (table-confirmatory-tests.csv).

## 3. RQ2: class-aware admission versus a matched global filter
- NONE at k5-d0.9: Hulk recall lost at E2 1.000, H 0.993, acquisition A 0.299, macro-F1 0.393; admits 100.0% of rows, keeps 100.0% of new-class rows, 100.0% of poisoned rows admitted.
- DC at k5-d0.9: Hulk recall lost at E2 0.974, H 0.988, acquisition A 0.175, macro-F1 0.275; admits 79.0% of rows, keeps 100.0% of new-class rows, 77.5% of poisoned rows admitted.
- DM at k5-d0.9: Hulk recall lost at E2 1.000, H 0.995, acquisition A 0.140, macro-F1 0.257; admits 79.0% of rows, keeps 9.5% of new-class rows, 94.0% of poisoned rows admitted.
- DQ at k5-d0.9: Hulk recall lost at E2 1.000, H 0.994, acquisition A 0.269, macro-F1 0.401; admits 79.0% of rows, keeps 100.0% of new-class rows, 75.0% of poisoned rows admitted.
- C2 tests (DC minus DM): 6 of 17 significant after Holm correction.
  - A (acquisition) at clean: mean difference -0.051 (95% CI -0.069 to -0.035), Holm p 0.0083.
  - A (acquisition) at k5-d0.25: mean difference -0.102 (95% CI -0.131 to -0.076), Holm p 0.0083.
  - A (acquisition) at k1-d1: mean difference -0.059 (95% CI -0.083 to -0.034), Holm p 0.0293.
  - A (acquisition) at k5-d0.5: mean difference -0.083 (95% CI -0.110 to -0.059), Holm p 0.0083.
  - dRec at k5-d0.25: mean difference -0.059 (95% CI -0.069 to -0.050), Holm p 0.0083.
  - clean FAR (E4) at clean: mean difference +0.072 (95% CI +0.051 to +0.094), Holm p 0.0083.

## 4. RQ3: mechanisms and ablations (at k5-d0.5)
- DR reference: Hulk recall lost at E2 0.612, H 0.785, macro-F1 0.427 (clean twin 0.491), poisoned records still in memory 630.
- DR: no logit-matching (lam_z=0): Hulk recall lost at E2 0.430, H 0.637, macro-F1 0.401 (clean twin 0.453), poisoned records still in memory 630.
- DR: no replay-label term (lam_y=0): Hulk recall lost at E2 0.883, H 0.000, macro-F1 0.055 (clean twin 0.083), poisoned records still in memory 630.
- DR: FIFO memory: Hulk recall lost at E2 0.561, H 0.000, macro-F1 0.056 (clean twin 0.121), poisoned records still in memory 0.
- DR: memory 100/client: Hulk recall lost at E2 0.355, H 0.513, macro-F1 0.344 (clean twin 0.386), poisoned records still in memory 116.
- DR: memory 1000/client: Hulk recall lost at E2 0.698, H 0.741, macro-F1 0.471 (clean twin 0.522), poisoned records still in memory 1248.
- DR+DC reference: Hulk recall lost at E2 0.510, H 0.495, macro-F1 0.325 (clean twin 0.403), poisoned records still in memory 542.
- DR+DC: quota q=0.5: Hulk recall lost at E2 0.306, H 0.450, macro-F1 0.292 (clean twin 0.396), poisoned records still in memory 419.
- DR+DC: quota q=0.9: Hulk recall lost at E2 0.716, H 0.641, macro-F1 0.336 (clean twin 0.457), poisoned records still in memory 611.
- DR+DC: small-class threshold 5: Hulk recall lost at E2 0.510, H 0.495, macro-F1 0.325 (clean twin 0.403), poisoned records still in memory 542.
- DR+DC: small-class threshold 100: Hulk recall lost at E2 0.510, H 0.495, macro-F1 0.325 (clean twin 0.406), poisoned records still in memory 542.
- EI reference (lam_E=100): Hulk recall lost at E2 0.530, H 0.000, macro-F1 0.036 (clean twin 0.046), poisoned records still in memory 0.
- EI: lam_E=10: Hulk recall lost at E2 0.500, H 0.000, macro-F1 0.033 (clean twin 0.074), poisoned records still in memory 0.
- EI: lam_E=1000: Hulk recall lost at E2 0.489, H 0.000, macro-F1 0.036 (clean twin 0.040), poisoned records still in memory 0.

## 5. Cost

- DR: 53 s per run, 35.5 MB communicated, 940 KB replay memory.
- EI: 38 s per run, 35.5 MB communicated, 0 KB replay memory.
- FT: 20 s per run, 35.5 MB communicated, 0 KB replay memory.

## 6. Limits (state these in the report)
- Development seeds only, one dataset (CICIDS2017-improved), one attack pattern (Hulk relabelled benign in E2, withdrawn afterwards); no final-test data was read.
- The 12 units are 3 ownership partitions (seeds 101-103, the only development seeds the repository allows) times 4 training replicates; replicates inside one partition are not independent of each other, so confidence is bounded by the 3 partitions. Seeds 104 and above stay sealed for the final evaluation.
- The units measure training and ownership variability on a fixed development bank, not variability between captures.
- FT and EI collapse on the clean run (see section 1), so their poisoning damage is bounded by what is left to lose; interpret C1 together with the clean baselines.
- CPU and GPU runs are not bit-identical; all comparisons use runs from one device type.
- The cross-check with the repository's committed results compares two implementations of the same protocol (table-crosscheck-repository.csv); report differences as measured.
