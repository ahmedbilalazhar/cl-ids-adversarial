# Experimental evaluation: stronger evidence without uncontrolled scope growth

Second audit, 24 October 2026. This extends the existing metric and risk contracts. No model results have been generated. Primary formulas, seeds and the 29-test family remain the revised Phase 2 specification unless a prospective amendment explicitly changes them.

## 1. Separate benchmark validity from operational value

The clean acquisition gates check whether anchors and Hulk can be learned. They do not require an acceptable benign false-alarm rate. Training targets about 3,500 benign rows per stage while retaining many attack rows; the evaluation bank has its own, generally different prevalence. Neither macro-F1 nor source recall alone establishes deployability.

**Required additions to reporting, using existing predictions:**

- Train/development/test benign and attack-family proportions, before and after admission.
- Binary benign FAR, attack recall, precision and the underlying counts at every stage, in clean and poisoned conditions.
- The always-benign and always-alert decision references computed on each bank. These are arithmetic baselines, not additional trained methods.
- Precision/false-alert scenarios at explicitly hypothetical deployment attack prevalences. Hold the observed conditional error rates and attack-family mixture fixed; label that transport assumption. Do not portray this as calibration on a real network.

If pi is an assumed attack prevalence, TPR is binary attack recall and FPR is benign FAR, then

`PPV(pi) = pi*TPR / (pi*TPR + (1-pi)*FPR)`.

For a **hypothetical** TPR=.95 and FPR=.01, PPV is about .087 at pi=.001: roughly nine percent of alerts are attacks under those assumptions. This illustrates why a good-looking detection rate is insufficient. It is not a study result. Show “undefined” if the denominator is zero.

An operational FAR constraint or dev-selected binary threshold would be useful for a deployment claim, but it changes the current argmax protocol. Specify the target, selection rule, tie/feasibility handling and additional metric family **before** final testing. Retain the primary multiclass/argmax outputs. Do not invent a universal acceptable FAR or tune a threshold on final labels.

The always-benign reference has source ASR=1 in both clean and poisoned conditions, hence H=0 and Delta_rec=0, despite detecting no attack. This exact arithmetic reference exposes the danger of calling a small damage difference “robustness.” It also has FAR=0, so reporting FAR alone does not solve the problem. Absolute source detection and acquisition must accompany susceptibility.

## 2. Power and inferential resolution are unresolved

Twelve paired seeds are better evidence than a single run, but the plan has no justified power calculation for its practical effect sizes. More trajectories across doses do not increase the twelve independent training replicates within a contrast. Clients, stages, batches and repeated checkpoint evaluations are not extra seeds.

The current exact two-sided sign enumeration has minimum p = 2/2^m for m nonzero paired differences. The first Holm threshold is .05/29, about .001724. Therefore:

| Nonzero pairs m | Smallest two-sided p | Can be the first rejected member of this Holm family? |
|---:|---:|---|
| 12 | .00048828125 | Yes, if the signs/ranks are sufficiently consistent |
| 11 | .0009765625 | Yes, at the minimum p |
| 10 | .001953125 | No |
| 8 | .0078125 | No |

A contrast unable to pass the *first* threshold could still pass a later Holm step after earlier members reject. These are resolution bounds, not power estimates or guarantees. Ties and many exact zero damage differences can make the actual test coarse. Never jitter differences or replace zero/weak-effect seeds.

Before final lock, choose the scientific interpretation of a small effect in percentage points. Use development-only variability or a transparent range of hypothetical paired-effect distributions for a sensitivity-based sample-size assessment. Preserve dependence within each seed and the fixed family structure. Do not use final outcomes to keep adding seeds until significance appears.

**Recommended decision:** retain the twelve-seed/29-test course protocol and frame non-rejection cautiously. If a publication paper needs a narrow, powered confirmatory question, prospectively designate a smaller scientifically justified primary family and budget sufficient seeds, with the remaining comparisons exploratory. This would be a real methodology amendment, not a cosmetic relabeling after results.

Report mean/median differences and raw pairs alongside p-values. A non-significant result is not evidence of equality, no harm or adequate robustness. The prespecified paired-mean bootstrap interval and signed-rank p target different summaries; do not force them to agree.

The executable **planning calculation**, [statistical-resolution.json](statistical-resolution.json), uses only hypothetical fixed ranks and independent signs; it reads no experimental measurements. With twelve distinct nonzero absolute ranks, passing the first cutoff requires a minority-sign rank sum at most two. Under its illustrative P(positive)=.8 sign model, the probability of passing that cutoff is about .103; with equal magnitudes it is about .069. These are scenario-specific resolution illustrations, not estimated study power. They show why merely retaining twelve seeds cannot justify an “adequately powered” statement.

## 3. A “better trade-off” needs an explicit meaning

Security, acquisition and false alarms are separate endpoints. A significant acquisition improvement with an inconclusive security difference does not establish “same security with better adaptation.” Likewise, a reduction in H with a large increase in absolute source error or benign FAR is not an overall win.

Use this vocabulary:

| Evidence | Defensible wording |
|---|---|
| Estimated improvement in A, uncertain H/FAR | Better measured acquisition; security/false-alarm implications remain uncertain |
| Lower H but worse absolute poisoned source error | Lower poisoning-associated susceptibility with worse absolute error |
| One metric improves and another worsens | A measured trade-off, with both magnitudes shown |
| All observed endpoint means improve | Descriptive dominance in this benchmark; uncertainty and multiplicity still apply |
| Failure to reject harm | Inconclusive; not a non-inferiority finding |

A non-inferiority or equivalence claim needs a justified margin, compatible confidence/testing procedure and adequate precision specified before final outcomes. The current two-sided superiority family does not provide it. Avoid creating a weighted utility score from observed results.

## 4. Report component and seed variability separately

The twelve seeds vary initialization, partition, attacker, order and retained-state sampling on one fixed capture/split. Their intervals describe that combined training-protocol variability. They do not estimate uncertainty across independent captures or organizations.

Also show per-family support and component concentration: a thousand rows from two large sessions do not provide a thousand independent network episodes. The five-components-per-split floor is a feasibility rule. It is not a power guarantee or proof that host/day leakage is absent.

If adding a descriptive test-population interval, resample **whole fixed test components**, carrying all their rows and family/benign membership together. Use the same component draws across paired methods and seeds. Distinguish:

1. Seed bootstrap: vary whole paired training replicates, fixed test bank.
2. Component bootstrap: vary the test-component composition, fixed trained models.
3. A deliberately specified two-way procedure: vary both; explain its conditional assumptions and shared-bank structure.

Do not resample individual flows independently or resample the same shared bank independently per seed and then call it cross-site uncertainty. Low-support bootstrap replicates can have missing classes; freeze handling rather than dropping inconvenient families. This extension is optional and descriptive; the existing seed interval remains the primary reported convention.

## 5. Baseline strength must match the claim

FT/EI/DR are appropriate retention references for the current RQ. They do not by themselves establish superiority over modern robust continual-learning methods or a benefit from federation. Separate three evidence layers:

| Layer | Evidence needed | Cost priority |
|---|---|---|
| Specified retention-pipeline comparison | Correct FT/EI/DR, clean learning, paired poisoning, precise EI/DER adaptations | Required |
| Attribution of admission mechanism | DM equal volume; DQ same class quotas; per-class honest/poison rejection and quota bounds | Highest-value extra control |
| Broad competitive defense claim | A justified noise-aware method adapter, own clean tuning, matched information/resource disclosure | Only if the paper makes that claim |

A centralized joint-history model or local-only model would answer additional questions about history access or federation. It is not necessary to add both to a focused poisoning-persistence study. If included, label their information/resource advantages. Joint-history retraining is an oracle reference, not a deployable equal-memory baseline or guaranteed upper bound.

An inexpensive development-only classical classifier can help diagnose a broken feature/label pipeline. It cannot replace the final continual-learning baselines or establish temporal/federated superiority. Do not turn every sanity reference into another twelve-seed training family.

The supplied-label empirical-importance estimator is one EWC-style variant. Published analysis shows that Fisher computation and tuning details matter. Name it precisely rather than treating any EWC implementation as universally representative. [Van de Ven, 2025](https://arxiv.org/abs/2502.11756).

## 6. Hypothesis and analysis status for extra controls

The fixed 29 contrasts do **not** include DQ, FIFO, no-logit, no-label, oracle repair, recurrence, alternative keep fractions or external data. Their default status is exploratory/descriptive. Adding them to the experiment manifest does not give their p-values confirmatory protection.

For every included control, freeze its exact reference, endpoint, direction, seed pairing and analysis role before testing. If making several exploratory comparisons, show the complete inventory and avoid a list containing only favorable p-values. A separate prospective multiplicity family is possible, but it must be explicit; it does not silently inherit Holm correction from the 29.

Reusing exact clean controls and prefixes is scientifically valid when identity holds, but creates dependent contrasts. It does not increase sample size. Holm controls its declared family without requiring independence of those tests; bootstrap and interpretation must still preserve pairing/shared controls.

## 7. Local diagnostics cannot create real-site claims

One pooled bank evaluates the global model. It does not measure worst-site performance, adaptation on a new organization or fairness across actual sites. Whole-component Dirichlet clients are synthetic ownership units. The same alpha can yield very different realized heterogeneity when indivisible components dominate. [Scott and Cahill, ICML 2024](https://proceedings.mlr.press/v235/scott24a.html).

Required zero-training-cost diagnostics are per-client current counts, label distributions, inactive stages, aggregation weights, poison exposure and memory occupancy. Optional held-out synthetic-client views need a frozen outcome-independent ownership rule for test components and support-aware reporting. Such views remain synthetic; do not create them with each method's predictions or call them independent organizations.

A real host-held-out or future-time sensitivity could strengthen generalization evidence, but CICIDS families are tied to capture times/hosts. Report lost support and changed estimand. Do not break components or choose the sensitivity split using which model wins.

Session/content components are also not independent attack campaigns. Thousands of connections can originate in one scripted execution against one victim. Report known capture windows/host concentration and avoid converting the component floor into a number of independent attack realizations.

Plots of H against realized poison fraction or retained-poison occupancy are descriptive. Ownership also changes shard difficulty, and memory/admission can change because of the treatment. Such a regression does not isolate a causal effect of exposure or justify adjusting away the admission response in the primary contrast. Use the declared same-parent interventions for narrower mechanism questions.

## 8. Cost and reproducibility evidence

Account for development, failed attempts, data preparation, artifact transfer, checkpoint saving, evaluation and analysis separately from successful training. Report actual charged GPU session time as well as measured process time; they answer different questions. Claiming efficiency from raw parameter bytes or the tiny model alone is insufficient.

For each final method report retained-state bytes and peak working memory. EI needs importance/anchor tensors; replay needs exemplars/logits/counters. Do not call 500 replay slots equal total resources across methods. Also show performance/cost trade-offs without post-hoc changing the scientific budget to equal wall time.

Release code/data recipes, locked identities, minimum and full reproduction paths, expected outputs, runtime ranges, failures and a claim-to-artifact map. Archive an immutable release where rights permit. A GitHub upload is useful availability but is not independent results reproduction or a formal artifact badge. [ACM CCS 2026 artifact criteria](https://www.sigsac.org/ccs/CCS2026/call-for/call-for-artifacts.html).

## 9. Continual accuracy can conceal attack-family forgetting

The fixed benign test bank is divided into four cohorts for R[t,j], and each cell is sample accuracy. If benign rows dominate a cohort, benign recognition dominates its ACC/BWT/forgetting contribution. Equal weight across stages does not correct imbalance **within** each stage.

For a hypothetical old cohort with 9,900 benign and 100 FTP rows, a model with perfect benign prediction and FTP recall .5 has accuracy .995. If FTP recall later falls to zero while benign remains correct, accuracy is .99: only .005 forgetting in that cohort despite losing all previously acquired FTP detections. This is arithmetic, not an observed result.

Keep the specified R matrix and equations. Add a descriptive family-recall heatmap with supports and acquisition-stage markers, plus old-attack balanced recall and benign FAR separately. Label the aggregation and exclude future/unregistered families until their supervised arrival. Do not replace the primary metrics post hoc or describe a high ACC as proof that the attack families were retained.
