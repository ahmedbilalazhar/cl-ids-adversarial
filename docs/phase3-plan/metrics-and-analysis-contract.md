# Metrics and analysis contract

Proposed implementation specification. Follow the revised Phase 2 equations; this file makes their software and interpretation consequences explicit.

## 1. Banks and prediction space

Maintain an immutable clean-reference bank with row order, labels, component IDs and a bank hash. At stage t, the cumulative confirmatory bank includes the fixed benign union and all scoring-eligible attack families whose supervised arrival has occurred. Future families are excluded until arrival.

Predictions always use every active head row, including trained rare classes excluded from confirmatory averages. A prediction of an active but unscored class is still an error when the true class is eligible, and is an alert when the true class is benign. Do not mask those logits.

Keep distinct inventories for registered/train-supported classes, scoring-eligible classes, supported descriptive families and held-out-only/unlearnable labels. Report the final dataset coverage and exclusions. A descriptive full-inventory view includes supported seen families below the floor; it must not silently become a zero-day evaluation of future/unregistered labels.

Eligibility is frozen before corruption and admission. A low-dose/high-dose supplied-label change or complete rejection of one class never changes which eligible families a method must predict. Zero admitted support is a learning outcome, not a reason to remove a hard family from its macro-F1.

Use a fixed tie rule. With benign in slot zero and first-maximum argmax, an exact benign/attack logit tie predicts benign. Log slot-map identity and validate it before converting slots to family names.

## 2. Confusion counts

For each supported class c on the specified bank:

```text
TP_c = true c and predicted c
FN_c = true c and predicted not c
FP_c = true not c and predicted c
recall_c    = TP_c / (TP_c + FN_c)
precision_c = TP_c / (TP_c + FP_c), when denominator > 0
F1_c        = 2*TP_c / (2*TP_c + FP_c + FN_c)
```

If a supported class is never predicted, recall and F1 can correctly be zero while precision is undefined. Do not turn undefined precision into missing F1, or drop the class from a macro average. A genuinely zero F1 denominator is NA with a reason; the eligible set does not change after observing a model.

Macro-F1 is the equal-class average over the fixed eligible seen classes including benign. Pooled accuracy is the sample-weighted correct fraction on that bank. These are separate from equal-stage continual ACC below.

## 3. Security endpoints

Use the same fixed held-out Hulk records at E2/E3/E4; their count N_H is unchanged across arms/doses/seeds:

```text
ASR_t(rho) = count(true Hulk, predicted benign at t, rho) / N_H
H(rho)     = ((ASR_3(rho)-ASR_3(0)) + (ASR_4(rho)-ASR_4(0))) / 2
Delta_rec  = recall_Hulk,E2(rho) - recall_Hulk,E2(0)
```

H>0 is a persistent attack-associated increase; Delta_rec<0 is immediate family-recall damage. H is an untriggered targeted-error difference, not trigger-conditioned backdoor success. The affected site still participates after E2, and retained state can still contain poison.

Calculate these from integer counts. H has a common denominator 2*N_H; Delta_rec has denominator N_H. Preserve signed negative differences rather than clamping them to zero. Show absolute clean/poisoned ASR and benign FAR alongside H so high baseline error cannot masquerade as robustness.

## 4. Legitimate acquisition

For each t in E2/E3/E4, lock U_t as scoring-eligible newly introduced attack families excluding Hulk. All three sets must be nonempty before outcomes are inspected:

```text
A = (1/3) * sum_t [ (1/len(U_t)) * sum_c_in_U_t(F1_c,t) ]
```

Each F1 uses its full declared stage bank. Hulk is excluded from U_t but remains a negative for the untargeted families. Report precision, recall and confusion sources so an improvement caused by fewer Hulk false positives is not mislabeled improved recognition of new positives. Untargeted does not mean unaffected.

Keep source-including new-family metrics and post-E2-only fork acquisition metrics separately named and descriptive. Do not replace A with them after viewing results.

## 5. Operational binary view

The alert decision is predicted label != benign. Use the same fixed argmax for binary precision, attack recall, F1, attack-miss rate and benign FAR. An incorrect attack-family prediction can still be a correct binary alert.

**Resolve the input bank explicitly:** report these descriptive binary metrics on `full_seen_bank_t`: the fixed benign union plus all supported test families registered by stage t, including trained rare families below the confirmatory floor. Keep the confirmatory multiclass bank separately named `eligible_seen_bank_t`. Held-out-only/unregistered and future families are excluded from this default closed-set view and listed in the coverage table. Do not alternate between these banks across methods or use one bank's prevalence with another bank's numerator. The benign denominator is the same fixed union, so the prespecified E4 benign-FAR contrast is unchanged.

```text
FAR_B = count(true benign, predicted any attack) / N_B
benchmark false alerts per 10,000 benign flows = 10,000 * FAR_B
```

This is not a daily deployment forecast. Report the benchmark's actual prevalence. For optional ranking metrics, define the score `max(active attack logits) - benign logit`; score>0 matches the fixed alert under the declared tie rule. Explicitly distinguish average precision from trapezoidal PR area if reporting “AUPRC”; do not treat them as interchangeable implementations.

The fixed benign union contains the declared held-out benign mixture from all relevant capture periods, even at E1. Stage-wise FAR therefore measures model change on this common mixture, not only the contemporaneous benign traffic of that stage. State this in trajectory captions; no future-only operational claim follows.

## 6. Continual-learning metrics

Partition the fixed benign test bank into four nonempty disjoint cohorts by a seeded balanced whole-component allocation before outcomes are inspected. The cumulative bank uses their union. This accounting partition is not a chronological prediction claim.

Let cohort j contain its eligible newly arrived attack families and its assigned benign cohort. R[t,j] is sample accuracy after stage t on that fixed cohort, using the full currently active head. Entries t<j are unavailable rather than zero. Later-class predictions on old cohorts count as errors.

For T=4:

```text
ACC_4 = mean_j=1..4 R[4,j]
BWT_4 = mean_j=1..3 (R[4,j] - R[j,j])
F_4   = mean_j=1..3 (max_l=j..4 R[l,j] - R[4,j])
```

ACC is equal-stage, not pooled accuracy or equal-family recall. Forgetting includes the final value in the maximum and is nonnegative. BWT may be positive or negative. No forward-transfer score is available without an additional compatible-head protocol.

## 7. Confirmatory contrasts

The machine-readable [analysis-contrasts.json](analysis-contrasts.json) lists exactly 29 tests:

- 18 C1 contrasts: three FT/EI/DR pairs, three nonzero doses, two endpoints H/Delta_rec.
- Four C2 contrasts: DC-DM in A at each dose including clean.
- Six C2 contrasts: DC-DM in H/Delta_rec at the three nonzero doses.
- One C2 contrast: DC-DM clean E4 benign FAR.

H/Delta_rec already subtract their learner's clean reference. Do not subtract that reference a second time in the learner contrast. Acquisition A is not clean-subtracted in its specified DC-DM contrast.

## 8. Signed rank, effects and missingness

Construct one difference per final seed in the fixed list 1–11,42. Drop exact zero differences from ranking, average tied absolute ranks and enumerate all 2^m signs. Use a two-sided absolute signed-rank sum and include observed-or-more-extreme assignments. All-zero contrasts have p=1 and rank-biserial effect zero. Report m and ties.

The rank-biserial effect is `(W_plus-W_minus)/(W_plus+W_minus)` for nonempty ranks. Use rational/count arithmetic for absolute-difference ordering where practical; do not choose rounding after seeing a desired significance result. Exact enumeration assumes sign symmetry and is not distribution-free inference about a mean. The prespecified exploratory exact paired sign test is a sensitivity when that assumption is doubtful, not an alternative protected opportunity to claim success.

Apply one Holm correction to all 29 raw p-values. Report raw/adjusted p, mean/median paired differences and effect direction; do not infer practical value from rejection alone.

For an unrestorable unavailable endpoint, retain its planned contrast with raw p unavailable and use 1 **only as fixed-family Holm bookkeeping**, as the Phase 2 appendix specifies. Do not show this as a computed no-effect p-value. Preserve a clear unavailable status and protocol deviation; no favorable or zero metric is imputed.

## 9. Intervals

The specified descriptive percentile interval bootstraps the mean paired difference with 10,000 whole-seed resamples, drawing twelve pairs with replacement each time and taking the 2.5/97.5 percentiles. Pin the bootstrap RNG namespace and quantile convention.

This interval is not simultaneous across the 29 contrasts and is not the inversion of the signed-rank test. A p-value and interval can differ because they target different summaries/assumptions. With twelve seeds, interval coverage/tails can be unstable. Preserve raw paired points and avoid equivalence/no-harm claims from non-rejection or overlapping intervals.

## 10. Artifact schema and interpretation

Store count tables, denominators, supports, bank/slot hashes and per-seed endpoints before any aggregation. Predicted slots can use uint8 when the active width permits it; optional margins use FP32. Repeated bank IDs/reference labels can be stored once rather than copied into every run file.

The analysis release should contain a complete expected/completed/invalid matrix, alias/parent records, fixed contrast rows, effect/interval tables and deterministic figure inputs. A copied prefix, aliased control, client, batch or inference timing call is not another research replicate.
