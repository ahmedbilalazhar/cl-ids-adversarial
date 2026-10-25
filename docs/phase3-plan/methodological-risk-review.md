# Methodological risk review and prospective amendments

Working review, 24 October 2026. These are deductions from the proposed protocol and literature, not experimental findings. Preserve the specified primary experiment unless an amendment is documented before final testing; no formal external preregistration is being claimed.

## 1. What the study can establish

The primary experiment estimates differences between methods under one historical capture, one fixed component-isolated split, one simulated five-client allocation mechanism, and one source-family label-corruption policy. Twelve training seeds vary the declared random processes. They are not twelve independently collected networks.

Separate three claims:

- **Observation:** attack-associated error remains after fresh corruption stops.
- **Mechanism evidence:** a specified intervention on retained state changes the subsequent error trajectory.
- **Generality:** the behavior persists across different capture populations, attack-site policies or arrival schedules.

The primary experiment supports the first. Matched continuation interventions can support a carefully scoped second claim. A separately audited dataset or recurrence protocol supplies limited additional evidence for the third. None establishes universal defense effectiveness.

## 2. Admission has a deterministic poison-retention floor

For an attacked client's E2 benign-supplied-label group, define:

```text
b = honest benign rows in that client's current shard
q = Hulk rows flipped to the benign supplied label
n_B = b + q
K_B = n_B                         if n_B < 20
      ceil(gamma * n_B)           otherwise, gamma = 0.75
```

Every other supplied E2 attack label is new and is fully protected by DC. Therefore, regardless of the loss ranking:

```text
minimum admitted poison = max(0, K_B - b)
maximum rejected poison = min(q, n_B - K_B)
```

If the required kept volume exceeds the number of honest benign rows, some poison must be kept. Ignoring the ceiling for intuition, eliminating all poison requires `q <= b / 3` at the 75% keep setting. With a local benign pool of 700 and 5,000 flipped Hulk rows, `K_B=4,275`; at least 3,575 poisoned rows must remain. This is a hypothetical arithmetic example, not an observed shard.

DM retains the same total per-client count. Its overall rejection budget is also `n_B-K_B`, so the same minimum retained-poison bound applies. DM may spend some of that budget rejecting honest new-family evidence, whereas DC cannot do so by construction. DG has a different rejection budget and is therefore not an equal-volume comparison.

**Required diagnostics:** publish `b`, `q`, `n_B`, `K_B`, the rejection budget, the lower bound, actual admitted poison and honest rejection per seed/dose/client. Also report the minimum retained-poison fraction only when `q>0`. This explains whether observed limitations arise from ranking, the declared quota, or both. Do not describe the rule as capable of removing arbitrary corruption.

For the proposed class-aware random control DQ, conditional on the fixed class group, expected admitted poison is `q*K_B/n_B`. This provides a transparent random-ranking reference. It is an expectation, not a deterministic benchmark result.

## 3. Effective exposure is not the nominal dose

Record all of the following rather than labeling every run simply “50% poisoning”:

1. Nominal dose `rho` among the attacked client's eligible Hulk rows.
2. Actual flipped count `q=floor(rho*h_k)`.
3. Local pre-admission fraction `q/n_k` and global pre-admission fraction `q/sum(n_j)`.
4. Post-admission flipped count and local/global admitted fractions.
5. The attacked client's FedAvg weight, determined by distinct admitted current rows.
6. Poisoned records retained in replay and sampled for each later loss term.

These count ratios describe exposure. They are not exact measures of parameter influence: Adam, local steps, replay and nonlinear aggregation dynamics prevent that identification.

A random eligible attacker can receive relatively few Hulk records. All such seeds remain part of the primary estimand. A weak or null result must not be “repaired” by choosing favorable final seeds or raising the threat after testing.

**Optional predeclared stress protocol:** select the largest-Hulk owner, preserving the five clients and one label-only attacked feed. Run the maximum dose for the five core arms and twelve seeds: 60 additional full trajectories; clean references may be reused only if all clean semantics are identical. This probes a stronger site-selection policy and must be reported separately. It is not a replacement for the randomly selected primary attacker.

## 4. Memory can remove the intended mechanism before it is measured

A 500-record reservoir is uniform over admitted distinct observations, not balanced by class or stage. Large later shards can dilute earlier source records. Thus a zero label-repair effect can mean that no poisoned exemplars survived, even if poisoned weights still influence predictions.

For a fixed admitted stream of N distinct records containing q poisoned records, a uniform reservoir of size m has expected poison count `m*q/N` when `N>=m`. A hypergeometric zero-count probability is a useful planning calculation for that fixed-stream setting. Do not apply it as a calibrated probability after conditioning on a whole adaptive trajectory: later admission depends on earlier learned states and memory.

For an already full reservoir at a stage boundary with stream counter `J` and `r` poisoned slots, the next stage locks `n` new, poison-free admitted observations before insertion. Conditional on that state and count, the expected surviving poisoned slots after that stage are `r*J/(J+n)`. This follows from the product of per-observation survival probabilities under Algorithm R; it does not predict model error. If the reservoir is not full, account for its fill period separately.

Log per-stage occupancy, class/stage coverage, source IDs, actual poison counts and cumulative replay draws. Audit labels outside learning. A mechanism claim requires the intervention and its actual exposure, not merely a nonempty buffer.

## 5. Continuation forks save compute but change the question

The original full-trajectory ablations remove a component from the start. A post-E2 fork holds acquisition and immediate damage fixed and changes only subsequent learning. These are different estimands and must have different protocol/condition IDs.

### Optional economical continuation package

Clone the complete DC E2 state at clean and maximum dose, for every final seed:

| Fork | Intervention during E3/E4 | New physical continuations |
|---|---|---:|
| FZ | Set the replay-logit coefficient to zero | 24 |
| FY | Set the replay-label coefficient to zero | 24 |
| FM | Clear the buffer and reset its stream counter; then build a new buffer from later data | 24 |
| Original oracle diagnostic | Repair stored poisoned labels at maximum dose only | 12 |
| Total | Existing primary continuations serve as controls | **84** |

For FZ/FY/FM, there are 72 new continuation executions. Their 72 control rows alias existing clean/maximum-dose DC primary suffixes. The oracle diagnostic has 12 new executions and 12 aliased controls. Together this is **168 logical continuation rows but 84 new physical executions**. The Phase 2 table's original 24 diagnostic continuations is a logical pair count, of which only 12 need new training when exact control reuse is valid. Keep all these units distinct in budgets.

For a fork `v`, use the exploratory interaction:

```text
H_v       = mean_t=E3,E4(ASR_v,poison,t - ASR_v,clean,t)
M_v       = H_v - H_primary_DC
```

Removing retention may also damage clean learning. The clean fork is essential to distinguish that cost from a change in attack-associated persistence. Report E3/E4 acquisition separately; the original acquisition A includes E2 and should not be relabeled as a pure post-withdrawal endpoint.

Oracle label repair changes stored labels only. It leaves poisoned logits and earlier weight damage intact and can alter later admission through the resulting model changes. It estimates the total downstream effect of this intervention, not a direct gradient contribution or a practical deployable repair.

This economical package can satisfy the requirement for component studies if the instructor accepts its clearly stated post-withdrawal scope. It does **not** replace the original from-start ablations without a prospective amendment. Prefer from-start ablations for a direct claim about the whole method; prefer forks for a precise persistence mechanism question.

## 6. Loss ranking and class protection need separate controls

DC versus DM controls admitted volume but changes which classes can be rejected. It does not isolate all contributions of loss ranking.

- DQ: same per-class quotas/protection as DC, uniformly random selection within eligible recurring classes. Costs 48 full trajectories at four doses and twelve seeds. This is the highest-value extra control when claiming the ranking rule helps.
- Unfiltered ER: remove the logit term from unfiltered DR, not from filtered DC. Costs 24 full trajectories at clean/maximum dose. A no-logit DC ablation answers a different question.
- Recurrence sensitivity: reserve fresh FTP/SSH components for a later stage, using an independently locked schedule. DM/DC at clean/maximum dose costs 48 full trajectories. It is needed for claims about balancing recurring attack classes, not for the narrower primary new-label-protection claim.

Do not add every control automatically. Prioritize the control required by the intended claim and measure its engineering and compute cost before final scope lock.

## 7. Dataset labels and model-visible inputs are not ground truth

The dataset's reference labels are treated as evaluation annotations, not certified truth. CICIDS2017 has documented construction/labeling defects. Exact canonical-input conflicts should be quarantined before splitting, and unresolved source-label defects disclosed. The known correction study is a separate release, not a silent relabeling of the primary benchmark. [Engelen et al., 2021](https://intrusion-detection.distrinet-research.be/WTMC2021/).

Compute content groups on the actual projected model input, including canonical dtype/order. Check again after frozen scaling/FP32 conversion because projection or rounding can collapse distinct raw rows. Preserve session links and duplicate provenance before selecting a survivor. A fast hash is an index; confirm equal canonical bytes before merging. Hashes do not establish semantic identity or repair incorrect labels.

Session interval merging must compare a next start against the running maximum end of the current session, not only the immediately preceding flow's end. Preserve documented timestamp units, ambiguous date order and local capture time; do not invent a UTC timezone.

Group splitting is a controlled benchmark design. The builder may use reference labels to stratify and audit support, but no clean labels, poison markers or final outcomes are exposed to learning/admission. Stable whole components may prevent exact 60/20/20 proportions or the requested benign target. Report realized sizes; do not split components to force a neat table.

## 8. Acquisition is not security and filtering is not detection

Hulk misclassification into another attack family reduces Hulk recall but still raises the declared binary alert. Targeted Hulk-to-benign error, family recognition and overall attack detection therefore answer different questions. Report them separately.

DC's 100% admission of honestly supplied new-family labels is guaranteed by its rule; it is not empirical evidence that the model learned those classes. Conversely, a method can lower targeted error by predicting almost everything as attack and incur unacceptable benign false alarms. Show clean and poisoned source outcomes, legitimate acquisition and benign FAR together.

Predictions must use the full active head, including train-supported rare classes excluded from confirmatory averages. Do not mask their logits to improve eligible-family scores. Future classes remain inactive until supervised arrival. The fixed benchmark is not a zero-day detector: classes are evaluated for acquisition after their labels become available.

## 9. Statistical failure modes to close before implementation

- Preserve the 29-test Holm family and the complete twelve-seed pair list.
- Derive H and recall damage from fixed-bank integer counts. H has denominator `2*N_Hulk`; recall damage has denominator `N_Hulk`.
- Acquisition F1 can be represented by exact rational count arithmetic for signed-rank ordering. Avoid arbitrary outcome-dependent rounding to create/remove ties.
- Rank absolute nonzero paired differences; average tied ranks; enumerate the `2^m` sign assignments using the declared two-sided statistic. All-zero contrasts get p=1 and zero effect, not a crash or exclusion.
- The smallest two-sided p-value is `2/2^m`: for 12 nonzero pairs, 0.00048828125; for 10, 0.001953125. The first threshold of a 29-test Holm family is about 0.001724. This describes resolution, not statistical power.
- Missing or invalid seeds must be completed or reported as incomplete; no convenient imputation or unpaired substitution.
- A signed-rank location interpretation needs a defensible symmetry assumption. Plot paired differences and state that the exact enumeration relies on sign symmetry; twelve seeds cannot prove that assumption. If a different primary test is required, amend before final testing rather than switching to whichever rejects.
- Whole-seed bootstrap intervals describe variation conditional on the fixed benchmark and runtime design; they are not cross-site confidence bounds or simultaneous intervals.

SciPy explicitly cautions about ties, zero differences and floating subtraction in Wilcoxon calculations. A generic `method='exact'` call is not sufficient evidence that the declared analysis was implemented. [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html).

## 10. Clean error ceilings can reverse a superficial security ranking

H is a clean-subtracted susceptibility endpoint, not an absolute safety score. Suppose a hypothetical FT model has clean/poisoned post-withdrawal source error 0.90/0.95, while DR has 0.05/0.30. H is 0.05 for FT and 0.25 for DR. DR has the larger attack-associated increase but the lower absolute poisoned error. Calling FT the safer detector from H alone would be wrong.

Every main H comparison must therefore be accompanied by absolute clean and poisoned Hulk-to-benign error, source recall and benign FAR. Clean error defines available upward headroom; poor ordinary retention can obscure a poisoning effect. Do not replace H with an outcome-selected normalized score or discard ceiling-affected seeds. A headroom plot can be descriptive, with denominators stated and no causal claim from ratios near a zero denominator.

The clean acquisition gates operate at acquisition and do not guarantee low clean Hulk error at E3/E4. The main finding should distinguish susceptibility, ordinary forgetting and absolute operational error.

## 11. Acquisition F1 is affected by the full bank

The source family is excluded from the *positive family list* in A, but Hulk records remain legitimate negatives for each untargeted family's F1 on the fixed seen-family bank. If poisoning moves Hulk predictions from an untargeted attack class to benign, it can reduce that class's false positives and increase its F1 without improving recognition of its own examples.

This does not invalidate the locked A endpoint or the matched DC–DM comparison. It limits its interpretation. Report each new family's precision, recall, TP/FP/FN and confusion sources alongside F1. “Untargeted” means not directly selected for label corruption; it does not mean unaffected by shared-boundary errors. Do not remove Hulk negatives to make acquisition look cleaner. A separate descriptive recall view is a useful complement.

The eligible seen-family bank grows across stages, so its negative composition and prevalence change. Treat stage-wise F1 changes with that context. Compare methods on the same stage/bank and preserve the predeclared equal-stage/equal-family aggregate.

## 12. Threat capabilities and simulator access must be explicit

The primary attacker compromises one site's labeling feed and changes a prescribed subset of source labels. The trainer, admission rule, counts, optimizer and model uploads still follow the honest algorithm. It is not a Byzantine client that may disable its own filter, replace updates or lie about weights. State how the attacker identifies its source-labelled rows and that selection does not use final-test queries or outcome feedback.

Client-local admission cannot defend against an adversary with arbitrary control over client execution merely because it is called a poisoning defense. Results should be scoped to the label-feed capability. Stronger adversaries need separately declared experiments.

The logical FedAvg server receives the declared registry/model/count messages. The physical research simulator and experiment archive hold all simulated client data/state. Consequently, this study can enforce an algorithmic message contract but does not demonstrate deployed privacy, encrypted transport, secure aggregation or organizational data isolation. Recovery archives contain replay exemplars and should be described as research artifacts rather than private-server-only state.

## 13. Withdrawal and corrective-data availability are separate

Lavaur et al. already examine stopped label-flipping attacks in a fixed-class federated IDS and report rapid recovery of aggregate accuracy. Their ongoing class/data setting and endpoint differ from this class-arrival experiment. Our E3/E4 contain no fresh Hulk records, so they remove both fresh source corruption and fresh corrective source supervision. [Author manuscript](https://orbilu.uni.lu/handle/10993/65906).

A persistent error in our study would not establish that ordinary FL cannot recover, or that continual learning alone caused the persistence. C1 compares retention mechanisms conditional on the same no-fresh-source schedule. The oracle memory repair is a limited corrective intervention; it cannot substitute for an experiment with fresh clean source data.

If the paper intends to identify the effect of fresh corrective data itself, design a separate matched source-recurrence/remediation protocol using prospectively reserved training components. Both schedules need a compatible reservation rule and clean/poisoned controls. Do not borrow final-test/development Hulk rows, reintroduce old IDs as supposedly fresh, or insert source recurrence into the primary withdrawal protocol. This extension is optional and is not included in the 513-row focused plan.

The existing FTP/SSH recurrence sensitivity tests general recurring-class balancing; it is a different question from clean Hulk remediation. Keep their names, counts and claims separate.

## 14. Withdrawal is cessation of fresh corruption

The affected client continues normal participation in E3/E4. Only the external manipulation of fresh labels stops. A replay learner can still train on retained wrong labels and contaminated stored logits; EI can retain contaminated importance/anchors. Therefore “fresh-stage labels are clean” does not imply “all later optimization uses clean supervision.”

Use precise labels in figures and code: `rho=0 clean reference`, `E2 fresh corruption`, and `post-E2 no fresh corruption`. Do not describe E3/E4 as attacker-free updates, client removal or wholly clean retraining. The poison is now retained state under an honest trainer, rather than an attacker making new interventions.

This distinction is part of the mechanism being investigated. It also prevents an unfair comparison with experiments that restore every repeatedly used local record's true label when an attack stops. Oracle buffer repair changes one retained supervision channel; it does not undo every contamination path.

## 15. Separately tuned learners are pipeline comparisons

FT, EI and DR select learning rates independently from the clean development grid. Their C1 contrasts are therefore comparisons of tuned pipelines. Clean subtraction does not remove a learning-rate-by-poisoning interaction. A larger H for EI than FT cannot, by itself, be attributed exclusively to the importance penalty when their rates differ.

The primary comparison remains useful and valid for its stated estimand. Report selected rates/coefficients prominently and describe it as tuned-method susceptibility. The matched admission and component ablations hold the DR settings fixed and answer narrower questions.

If a stronger retention-attribution claim is intended, an economical optional control is FT at the other grid learning rate, at clean/maximum dose over twelve seeds. Because the grid has only two learning rates, at most 24 additional full trajectories supply both FT rate references; zero are needed if the relevant primary rates already match. Compare EI/DR with the FT reference at their own rate and preserve clean/poisoned pairing. This is exploratory unless amended and is not included in the 441/513 base counts.

It does not isolate every optimization consequence: removing a replay term can change stochastic forwards and learned states. Independent loss-role RNG streams could improve pairing but add implementation overhead and require a frozen convention. Do not claim pathwise gradient attribution from a conventional component ablation.

## 16. Publication positioning and stop conditions

Prior work already covers adversarial FCL, noisy replay, and post-attacker persistence. A credible paper needs a precise empirical finding, a fair control and a reproducible implementation. A new acronym, more GPU hours or a longer ablation list does not supply novelty.

**Continue toward an empirical paper** if the data/protocol is feasible, baselines learn, paired comparisons yield interpretable behavior, and the mechanism analysis supports a qualified explanation. Null security effects can remain useful if accompanied by strong exposure measurements and a limited, informative conclusion.

**Revise before final runs** if canonical metadata/support fails, the numerical pipeline cannot learn under the fixed settings, or the method is indistinguishable from prior work at the intended claim level. Keep the course implementation objective separate from an unproven publication target.

**Do not claim:** first poisoning in FCL; first persistent FL attack; general novel class-aware purification; defense against model replacement/backdoors/arbitrary malicious client code; cross-organization privacy guarantees; globally future-only evaluation; production latency or energy from simulated payloads.
