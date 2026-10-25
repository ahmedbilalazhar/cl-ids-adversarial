# Novelty assessment and publication strategy

Working assessment, 24 October 2026. Recommendation: **proceed with a narrowly framed empirical study; do not claim a new general defense or a first combination of federated, continual and adversarial learning.** Publication remains contingent on results and venue fit.

The novelty-check skill guided the search. Its separate-model Codex MCP verification step could not be performed because that tool is unavailable. This is one source-grounded assessment, not independent reviewer consensus. Search coverage is bounded and cannot prove that no matching work exists.

## 1. Proposed contribution

Study how a one-stage, label-only corruption of one simulated site's newly acquired Hulk family affects immediate classification and later untriggered Hulk-to-benign error after fresh corruption stops. Compare fine-tuning, importance retention and a declared DER++ adaptation, then compare matched-volume admission policies that either protect or globally rank new-labelled evidence.

The most defensible contribution is an experimentally supported account of **when retention preserves harmful supervision and how new-label protection changes the acquisition/security trade-off**. Whether a new finding exists is unknown until the locked experiments are executed.

## 2. Claim-level assessment

| Candidate claim | Current novelty judgment | Consequence for the paper |
|---|---|---|
| “First adversarial federated continual learning” | Low; contradicted by material prior work | Remove this claim |
| “First persistent poisoning after an FL attacker withdraws” | Low; persistence is an established FL security question | Specify the different label-only, class-acquisition threat and endpoint |
| “First corrupted replay or noisy continual learning” | Low | Cite continual IDS and robust noisy-stream work |
| “A novel general class-aware low-loss defense” | Low as currently specified; DC is a simple protection/quota rule | Present DC as a transparent falsifiable intervention/control |
| “A controlled comparison of retention-associated label-poison persistence and matched new-label protection in a flow IDS” | Potentially useful empirical delta; broad uniqueness remains unproven | Build precise controls, diagnostics, paired estimates and reproducible artifacts |

A numerical novelty score would imply precision that this literature review cannot supply. The architectural novelty is modest; the value must come from the finding, causal interpretation and evidence quality.

## 3. Closest primary work and concrete differences

### Label-flipping collaborative IDS — Lavaur et al., Computers & Security, 2025

This is especially close prior work. It includes attacks that stop after a fixed round, paired clean references and rapid subsequent aggregate-accuracy recovery in fixed-class binary FIDS experiments. The label-only attacker also cannot modify honest trainer behavior. Our delta is therefore not withdrawal or a restricted feed attacker by itself. It is the class-arrival/no-fresh-source schedule, explicit retention comparisons, fixed-source endpoints and matched acquisition controls. Fresh corrective data availability and metric differences prevent treating contrary-looking outcomes as a direct contradiction. [Author manuscript](https://orbilu.uni.lu/handle/10993/65906), [official code/results](https://github.com/leolavaur/cose_2025).

### SacFL — Zhong et al., IEEE TNNLS, 2025

SacFL evaluates adversarial tasks in federated continual learning, including label flipping/backdoors, and reports historical-task behavior with subsequent benign tasks. Its image/text, encoder–decoder and proxy-history design materially overlaps the broad problem framing. Our intended difference is a constrained flow-label feed attack, paired source-specific persistence, retention-mechanism comparisons and quota-controlled new-label protection. That difference must be demonstrated, not reduced to a claim that SacFL is “static.” [Paper](https://arxiv.org/abs/2505.00365), [published version](https://openreview.net/pdf/b7f9849f358729f58c73135d36981d5ff5248a09.pdf).

### Adaptive IDS with adversarial investigation — Ariffin et al., 2026 preprint

This continual IDS already studies benign recurrence, balanced replay and buffer poisoning. Its label-flip experiment corrupts stored exemplars, with buffer budget controlling poisoned volume. Our feed corruption lasts one supervised stage and cannot directly edit retained storage. These attack capabilities and denominators are not interchangeable. [Preprint](https://arxiv.org/abs/2608.04602).

The [official ReplayIDS repository](https://github.com/um-csnet/ReplayIDS) supplies a reproduction path but also discloses historical ASR estimates above 100% due to evaluation defects and an effective training-cap distinction. Treat those as author-disclosed artifact limitations. Do not turn historical percentages into a direct leaderboard or claim that running its CLI would reproduce our protocol. Verify a specific commit/config and keep reproduced, corrected and paper-reported values separate.

### Neurotoxin — Zhang et al., ICML 2022

The durability of FL backdoors after an attacker stops uploading was its explicit objective. It uses a stronger model-update/backdoor capability than our label-only feed attacker. Cite it when explaining persistence and distinguish trigger-conditioned success from untriggered source-family error. [Publisher page](https://proceedings.mlr.press/v162/zhang22w.html).

### Single-task poisoning — Pawlak et al., CoLLAs 2025 / PMLR 2026

This work already investigates a weak attacker limited to one task, without model or past/future-task access, and shows effects on stability and plasticity. The primary setting is exemplar-free vision with image corruptions. Our network-flow, label-only, federated and retained-state comparisons are a different scoped experiment; the weak one-task premise alone is not new. [Publisher page](https://proceedings.mlr.press/v330/pawlak26a.html).

### AER/ABS and PuriDivER — robust noisy-stream continual learning

AER/ABS studies replay under noisy labels and loss-based separation. PuriDivER manages purity/diversity and robust use of contaminated memory. Both limit generic claims about inventing continual purification. Their training, sampling and vision assumptions differ from this protocol. Consider a clearly declared adapter only if claiming competitive noise robustness; its additional development budget and changed semantics must be counted. [AER/ABS, BMVC 2024](https://bmva-archive.org.uk/bmvc/2024/papers/Paper_680/paper.pdf), [PuriDivER, CVPR 2022](https://openaccess.thecvf.com/content/CVPR2022/papers/Bang_Online_Continual_Learning_on_a_Contaminated_Data_Stream_With_Blurry_CVPR_2022_paper.pdf).

### FIL-ZTA and EdgeFedCIL — recent network-context work

FIL-ZTA combines network-oriented federated incremental learning with poisoning/robustness evaluation, using authentication attributes and different client-control capabilities. EdgeFedCIL combines federated class-incremental IDS with replay/distillation and communication compression. Together they make broad “first integration” or “first efficient federated CIL IDS” claims untenable. Neither supplies a directly comparable numerical result under our source-bank, label-only withdrawal protocol. [FIL-ZTA](https://www.mdpi.com/1999-5903/18/3/154), [EdgeFedCIL](https://www.mdpi.com/1424-8220/26/14/4630).

### Replay need not be uniformly beneficial

Recent theory gives settings in which replay increases forgetting even without noise. It supports caution about universal retention claims; its linear-regression assumptions do not prove anything about our MLP or poisoned trajectory. [Mahdaviyeh et al., PMLR 2026](https://proceedings.mlr.press/v330/mahdaviyeh26a.html).

## 4. Search coverage and limits

The investigation searched claim variants around adversarial FCL, single-task poisoning, replay corruption, noisy-label class-incremental learning, new-class rejection and network IDS. It included published primary papers, author code, 2024–2026 sources and recent arXiv coverage.

The explicit latest-six-month arXiv window was 24 April–24 October 2026. Searches included:

- `"federated continual" AND (poisoning OR adversarial)`
- `continual AND intrusion AND (poisoning OR replay)`
- Web variants: federated continual learning label poisoning; persistent poisoning after withdrawal; class-incremental small-loss noisy labels; class-aware poisoning admission; continual intrusion replay poisoning.

The first exact-phrase recent arXiv query returned no records; the broader IDS query returned Ariffin et al. and an unrelated model-stealing defense. **A zero query result is not evidence that the field contains no matching paper.** Older material prior work was recovered with broader searches. Indexed publisher text was used when direct pages were blocked; full reproduction and paper-by-paper revalidation remain implementation tasks.

The evidence ledger [sources.json](sources.json) records primary URLs, verification depth and limits. Findings are provisional until the final paper's literature cutoff is refreshed.

A final broader six-month search replaced the exact FCL phrase with `federated AND (continual OR incremental) AND (poisoning OR backdoor)`. It recovered STAIN-FL, whose full abstract describes contextual-trigger federated video anomaly detection with gradient masking and post-attack persistence. This is recent durability context, not the same label-only class-arrival experiment. Its full methods were not reviewed, so it is an abstract-verified lead rather than a direct benchmark. Other returned watermarking, packet-evasion and fintech papers were screened out for scope. [STAIN-FL preprint](https://arxiv.org/abs/2608.23952).

## 5. Choose the paper type before choosing more experiments

### Preferred: an empirical security/continual-learning study

Lead with the restricted threat, source-specific persistence and acquisition consequences. Treat DC as an interpretable intervention and matched comparison. Required evidence is a correct implementation, paired clean controls, exposure diagnostics, nontrivial component analysis and transparent limitations. A surprising negative or conditional result can be scientifically useful.

Candidate working title:

> Retaining the Wrong Labels: A Controlled Study of Poisoning Persistence in Federated Continual Intrusion Detection

This title describes the question; it does not assert an outcome before measurement. Use a neutral title if results do not establish persistence.

### More demanding: a competitive defense paper

This needs stronger evidence than the current DC rule: published noise-aware comparisons, additional attacker knowledge/capabilities, sensitivity beyond one capture, and an identified algorithmic advantage that survives fair controls. Eight compute contributors do not by themselves meet those requirements. Do not expand the claim merely because more jobs fit.

### Course-complete implementation report

All seven rubric items can be completed with a smaller, honest study. Use within-protocol FT/EI/DR/DM/DC comparisons, meaningful ablations, full preprocessing and a contextual literature comparison. Explicitly document omitted exploratory extensions. Completing the course is a deliverable; publication is a later evidence-dependent decision.

## 6. Prospective claim-to-evidence contract

| Intended claim | Minimum supporting comparison | Limit to state |
|---|---|---|
| Poisoning harms source recognition immediately | Clean/poisoned source recall at E2, paired seeds | This source family, threat and benchmark |
| Targeted error persists after fresh corruption stops | Fixed Hulk bank at E3/E4, matched clean subtraction | Association does not identify memory as the cause |
| Retained labels contribute downstream | Oracle repair and matched control; actual surviving poison | Earlier weights and stored logits remain contaminated |
| A replay term contributes after withdrawal | Clean and poisoned post-E2 forks | Post-withdrawal intervention, not whole-method ablation |
| Protecting new labels changes acquisition | DC–DM with equal per-client count and weights | Primary schedule protects new attacks, not recurring attack balance |
| Loss ranking adds value | DC–DQ with identical per-class quotas | Additional contrast is exploratory unless amended |
| Behavior extends beyond one setting | Independently audited external/recurrence protocol | No pooled claim of multi-site field validation |
| Efficient enough for the study | End-to-end measured cost on recorded hardware | Not production edge latency/energy |

## 7. Artifact and writing standards

Use versioned protocol/amendments, exact data/build provenance, pinned dependencies, full seed matrices, raw denominators and automatic figure generation. Connect each paper claim to a validated result row and executable analysis. Separate exploratory from confirmatory claims and retain null/adverse results.

Use the NIST and NeurIPS documents as reporting guidance, not certification or a substitute for the course rubric. A public GitHub repository alone does not establish reproducibility. Check venue format, artifact policy and dataset redistribution rights when selecting an actual venue; no venue or acceptance claim is being assumed now.

## 8. Next decisions

1. Resolve canonical dataset feasibility and teacher feedback.
2. Select the empirical contribution and minimum control set.
3. Profile the correct implementation and lock the scope before final testing.
4. Execute all paired conditions, analyze without favorable-seed selection, and decide whether the finding warrants a manuscript.
5. Refresh related work and perform an actual independent review before submission.
