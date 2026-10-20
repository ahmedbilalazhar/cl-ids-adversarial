# Computer Networks — Phase 2
## Extended Literature Review, Refined Research Gap and Proposed Methodology

**Research title:** Evaluating Poisoning, Forgetting and Rare-Attack Retention in Federated Class-Incremental Intrusion Detection

**Evidence cutoff:** 5 October 2026. **Document status:** literature-grounded research proposal. Runtime extensions and final experiments described below are planned; published results are attributed to their authors.

### Abstract

Continual intrusion detection must acquire emerging attacks while preserving historical knowledge. Federated training introduces heterogeneous clients and potentially corrupted supervision, creating a conflict between resisting poisoning and accepting legitimate new evidence. This proposal synthesizes nine additional peer-reviewed studies published in 2025–2026 and formulates a controlled evaluation of fine-tuning, EWC and DER++ under targeted client-data poisoning. The proposed defense uses class-aware admission, with controls for admitted sample volume and memory policy; trusted-label review is an optional separately budgeted extension. The methodology measures past-class retention, new-class acquisition, post-attack targeted error and computational cost using audited sequential data and paired runs. Its contribution is an empirical characterization and testable intervention, rather than a presumed robustness guarantee.

### Contents

1. [Deliverable 1: Extended literature review](#deliverable-1-extended-literature-review)
2. [Deliverable 2: Refined research gap](#deliverable-2-refined-research-gap)
3. [Deliverable 3: Proposed research methodology](#deliverable-3-proposed-research-methodology)
4. [Appendix A: Repository audit](#appendix-a-repository-audit-and-implementation-boundaries)
5. [Appendix B: Evidence notes](#appendix-b-evidence-and-qualification-notes)
6. [Appendix C: Self-review and revision decisions](#appendix-c-self-review-and-revision-decisions)

The three deliverables form one argument and use a shared paper index P1–P9. The detailed engineering audit is retained in an appendix so the submission follows literature → gap → methodology.

## Deliverable 1: Extended Literature Review

### 1.1 Project context and Phase 1 recheck

- **Research domain:** adversarial robustness of continual network intrusion detection, primarily federated class-incremental learning (FCIL), with a separate secondary study of poisoning against novelty detection and clustering.
- **Phase 1 scope:** compare adaptation mechanisms for unknown DoS discovery, federated acquisition of emerging attack classes, and RF-fingerprint drift. The submission identifies three directions: realistic validation data, attackers targeting adaptation, and measured deployment cost. The implemented project concentrates on the second direction. RF authentication is outside the implemented network-flow study.
- **Codebase:** C:/Users/hp/Desktop/University/5. C Net/1. Project. Flow preparation and sequencing are in src/data; MLP/AE models in src/models; fine-tuning, EWC, LwF, ER and DER++ in src/cl; simulated federation, partitioning and aggregation in src/federated; poisoning/evasion in src/attacks; filtering in src/defenses; novelty discovery in src/discovery; experiment execution and manifests in src/runner.py and src/reporting.py.


The [Phase 1 source](<C:/Users/hp/Desktop/University/5. C Net/1. Project/submissions/phase1.tex>) supports an adaptation-security question:

> “If clustering goes wrong, every later step is affected” — line 85.

> “they assume the coordinating server and all clients are honest” — line 100.

> “attackers who specifically target the adaptation mechanism itself” — line 225.

These excerpts identify vulnerable assumptions, rather than establish that poisoning of continual IDS has never been studied. The three existing Phase 1 papers are not counted among the nine additional papers below. The current [proposal](<C:/Users/hp/Desktop/University/5. C Net/1. Project/docs/proposal.md:26>) makes federated poisoning the primary question and explicitly separates it from novelty-discovery attacks.

The existing MLP, continual learners, federation simulator, label-flipping attack and filtering modules provide the primary implementation foundation. Appendix A separates existing components from required extensions and identifies configuration/data-integrity prerequisites. The discovery branch remains exploratory because its current detector and capped clustering need independent validation.

The primary study compares three learners under the same FCIL protocol, then compares admission rules under a fixed learner and matched information/budget conditions. A new backbone, unsupervised class discovery and Byzantine-update defense are extensions rather than prerequisites for completing this milestone.

### 1.2 Search and qualification protocol

Consensus supported targeted discovery; publication records, full manuscripts, publisher pages and author repositories supplied verification. Queries covered FCIL intrusion detection, replay and forgetting under evolving attacks, federated label-flipping and poisoning defenses, unsupervised continual novelty detection, and HDBSCAN poisoning. This is a targeted, critically screened review, not a PRISMA systematic review or an exhaustive proof of novelty.

**Nine papers are selected**, satisfying the requested 8–10 additional-paper range. Each has a 2025–2026 peer-reviewed publication, identifiable methods and datasets, quantitative experiments, and a free full-text route. Green OA author versions are distinguished from publisher OA; an arXiv URL alone was not accepted as evidence of peer review. CND-IDS is independently listed in the [official DAC 2025 research program](https://archive.dac.com/portals/0/62dac/program/62dacprogram.860185f3fd.pdf). Sonic is counted through its 2026 Information Sciences publication, not its 2024 preprint.

Journal quartiles below use **2024 JIF category quartiles in the June 2025 JCR release**, reproduced in the [ranking source](https://uefiscdi.gov.ro/resource-865584-JCR_2024.iunie2025.pdf). These are not asserted to be 2026 quartiles or SJR quartiles. DAC qualifies through premier peer-reviewed proceedings rather than a journal quartile. JISA and Future Internet are Q2 in Computer Science, Information Systems; CMES is Q2 in Engineering, Multidisciplinary. Applied Soft Computing is Q1 in Artificial Intelligence. The remaining selected journals use their documented Q1 categories. The publisher of P9, Tech Science Press, qualifies under the assignment’s provision for other recognized academic publishers.

| ID | Full paper title | Published venue/year; qualification | Publication DOI | Free full-text route | Dataset / direct relevance |
|---|---|---|---|---|---|
| P1 | A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats | IEEE Transactions on Network and Service Management 23, 3865–3880; 2026; Q1 | [10.1109/TNSM.2026.3675031](https://doi.org/10.1109/TNSM.2026.3675031) | [Author manuscript PDF](https://domenicociuonzo.wordpress.com/wp-content/uploads/2026/03/early_access_tnsm26_fedcil_ids.pdf) | TON_IoT, IoT-NID, Edge-IIoTset; FCIL client/server protocol |
| P2 | Investigating the Impact of Label-flipping Attacks against Federated Learning for Collaborative Intrusion Detection | Computers & Security 156, 104462; 2025; Q1 | [10.1016/j.cose.2025.104462](https://doi.org/10.1016/j.cose.2025.104462) | [University repository PDF](https://orbilu.uni.lu/bitstream/10993/65906/1/Investigating_the_Impact_of_Label_flipping_Attacks_against_Federated_Learning_for_Collaborative_Intrusion_Detection.pdf) | NFV2-UNSW-NB15, NFV2-CSE-CIC-IDS2018; client poisoning and matched attack controls |
| P3 | CND-IDS: Continual Novelty Detection for Intrusion Detection Systems | 62nd ACM/IEEE Design Automation Conference; 2025; premier proceedings | [10.1109/DAC63849.2025.11132541](https://doi.org/10.1109/DAC63849.2025.11132541) | [Author-version PDF](https://arxiv.org/pdf/2502.14094) | X-IIoTID, WUSTL-IIoT, CICIDS2017, UNSW-NB15; continual novelty detector |
| P4 | WeiDetect: Weibull distribution-based defense against poisoning attacks in federated learning for network intrusion detection systems | Journal of Information Security and Applications 95, 104275; 2025; Q2 | [10.1016/j.jisa.2025.104275](https://doi.org/10.1016/j.jisa.2025.104275) | [Author-version PDF](https://arxiv.org/pdf/2504.04367) | CIC-Darknet2020, CSE-CIC-IDS2018; validation-based server filtering |
| P5 | Continual learning for adaptive IoT network intrusion detection via domain-incremental learning methods | Applied Soft Computing 203, 116022; available online 21 July 2026; Q1 | [10.1016/j.asoc.2026.116022](https://doi.org/10.1016/j.asoc.2026.116022) | [Publisher OA full text/PDF](https://www.sciencedirect.com/science/article/pii/S1568494626014705) | UQ-IoT-IDS-2021, Kitsune, CICIDS2017; matched CL-family baselines |
| P6 | CTWA: a novel incremental deep learning-based intrusion detection method for the Internet of Things | Artificial Intelligence Review 58, 374; 8 October 2025; Q1 | [10.1007/s10462-025-11358-9](https://doi.org/10.1007/s10462-025-11358-9) | [Publisher OA PDF](https://link.springer.com/content/pdf/10.1007/s10462-025-11358-9.pdf) | CICIoT2023, BoTNetIoT; representation sharing and head alignment |
| P7 | Continual Learning for Intrusion Detection Under Evolving Network Threats | Future Internet 17(10), 456; 4 October 2025; Q2 | [10.3390/fi17100456](https://doi.org/10.3390/fi17100456) | [Publisher OA full text/PDF](https://www.mdpi.com/1999-5903/17/10/456) | UNSW-NB15, CICIDS2017, TON_IoT; adaptive memory and class imbalance |
| P8 | Sonic: Fast and transferable data poisoning on clustering algorithms | Information Sciences 738, 123140; 2026; Q1 | [10.1016/j.ins.2026.123140](https://doi.org/10.1016/j.ins.2026.123140) | [Final university OA PDF](https://iris.unica.it/bitstream/11584/470685/1/sonic-editorial.pdf) | 20 Newsgroups, MNIST, Fashion-MNIST, CIFAR-10; direct HDBSCAN attack-component relevance |
| P9 | Resilient Federated Ensemble Learning for IoT Intrusion Detection in Adversarial and Imbalanced Environments | Computer Modeling in Engineering & Sciences 147(3), 48; 30 June 2026; Q2 | [10.32604/cmes.2026.082021](https://doi.org/10.32604/cmes.2026.082021) | [Publisher OA PDF](https://cdn.techscience.cn/files/CMES/2026/TSP_CMES-147-3/TSP_CMES_82021/TSP_CMES_82021.pdf) | CICIoT2023; streaming federation, imbalance and update gating |

**Access interpretation:** P1–P4 include author/repository routes; P5–P9 include publisher or final institutional OA. Free access does not imply public executable code, identical author/final revisions, or an automatically reproducible artifact. Some publisher sites block automated retrieval; their public OA labels and accessible indexed full text are distinct from a successful automated PDF download.

P8 is deliberately a component-level security paper, not an IDS benchmark. Its clustering mechanism directly matches the implemented HDBSCAN stage. Its image/text results cannot be treated as demonstrated network-traffic attacks.

Two particularly relevant 2025 papers were also critically read: Cerasuolo et al., [Attack-Adaptive NIDS](https://doi.org/10.1016/j.comnet.2025.111228), and [Adaptable, incremental, and explainable NIDS](https://doi.org/10.1016/j.engappai.2025.110143). Publicly readable author manuscripts were found, but a stable publisher/institutional complete-PDF route and its version/access status were not sufficiently established in this audit. They remain supplementary and are **not counted** in the nine selected papers. Automated download failure alone is not a paywall or a reason to exclude a publisher-verified OA article. The first reports TON-IoT classification F1 95.30 ± 1.46 with optimized packet fields/memory; the second examines cross-network incremental adaptation and provides [sample code/data](https://github.com/jmpr0/incremental-nids). Their input perturbations and domain shifts do not establish malicious-training resistance. [Public manuscript 1](https://www.researchgate.net/publication/389901457_Attack-Adaptive_Network_Intrusion_Detection_Systems_for_IoT_Networks_through_Class_Incremental_Learning); [public manuscript 2](https://www.researchgate.net/publication/389474292_Adaptable_incremental_and_explainable_network_intrusion_detection_systems_for_internet_of_things).

Unverified preprints, including ACORN-IDS and replay-buffer poisoning manuscripts without a confirmed peer-reviewed venue, are excluded from the qualifying count. ACIL and CAT-IDS were not selected because a sufficiently verified free complete manuscript route was not established. A 2026 date on an index or DOI suffix alone is insufficient.

### 1.3 Technical synthesis of the nine selected papers

**P1 — Carillo et al.** Authors: Raffaele Carillo, Francesco Cerasuolo, Giampaolo Bovenzi, Domenico Ciuonzo and Antonio Pescapè. FCIL combines FedAvg/FedProx/FedDyn with rehearsal, distillation and old/new bias correction. The early-traffic CNN uses packet-field matrices, rather than aggregate CSV features. Table IV reports TON_IoT S2, FedProx–MEMENTO+, R=100 F1: old 79.05%, new 68.10%, all 74.49%. Adapt its synchronized class expansion and old/new evaluation to the existing federated MLP; a packet CNN requires a separate adapter. This is clean FCIL evidence, not a poisoning result. [Full text](https://domenicociuonzo.wordpress.com/wp-content/uploads/2026/03/early_access_tnsm26_fedcil_ids.pdf).

**P2 — Lavaur et al.** Authors: Léo Lavaur, Yann Busnel and Fabien Autrel. The study systematically varies label-flipping and heterogeneous collaborative IDS configurations using common NetFlow representations. Its 10,670 experiments distinguish absolute attack success from improvement over clean targeted error; clean binary models generally exceed 0.90 accuracy/recall/F1. It supplies the project's attack-budget and matched-control design. Its static FL setting does not measure continual replay persistence or forgetting. [Full text](https://orbilu.uni.lu/bitstream/10993/65906/1/Investigating_the_Impact_of_Label_flipping_Attacks_against_Federated_Learning_for_Collaborative_Intrusion_Detection.pdf); [author code](https://github.com/leolavaur/cose_2025).

**P3 — Fuhrman et al.** Authors: Sean Fuhrman, Onat Güngör and Tajana S. Rosing. CND-IDS learns an encoder with reconstruction, cluster-separation and historical-encoder distillation; trusted benign embeddings fit a PCA novelty detector. On CICIDS2017, Table II reports 1.93× AVG and 2.64× FwdTrans relative to LwF. Best-F selects thresholds using labeled test batches; these reported endpoints and its diagonal AVG differ from this repository's final-row accuracy. Benchmark its encoder/PCA as a separate novelty arm with validation-only calibration. It does not recognize newly named attack classes or certify poisoning resistance. [Full text](https://arxiv.org/html/2502.14094v1); [code](https://github.com/Sean-Fuhrman/CND-IDS).

**P4 — Sameera et al.** Authors: Sameera K. M., Vinod P., Anderson Rocha, Rafidha Rehiman K. A. and Mauro Conti. WeiDetect evaluates local models on server-held auxiliary validation data and fits a Weibull distribution to reject suspicious scores before aggregation. The author version reports target-class recall improvements up to 70% and global F1 gains of 1–14%; these are reported improvement ranges, not a universal final F1. Implement it as a server-defense comparator with a declared trusted-data budget. Under FCIL, validation coverage of an emerging class must be measured before treating a low score as malicious. [Author full text](https://arxiv.org/html/2504.04367v2); [publication](https://doi.org/10.1016/j.jisa.2025.104275).

**P5 — Delgado et al.** Authors: Oliver Delgado, Hyunjae Kang, Ulysses Lam, Jung Taek Seo and Dan Dongseong Kim. Eight continual strategies are compared across MLP/LSTM/Transformer and nine attack-arrival stages. Replay retains final macro-F1 0.92–0.98 with forgetting below 0.05; reported MLP CL state is below 0.4 MB with 100 samples per class. The output remains binary, making this domain-incremental learning despite new attack-family arrivals. Reuse the matched architecture, memory and imbalance comparisons; do not transfer those values to multiclass FCIL or poisoned replay. [Publisher OA study](https://www.sciencedirect.com/science/article/pii/S1568494626014705).

**P6 — Wang et al.** Authors: Haizhen Wang, Yutong Yang and Pan Tan. CTWA combines residual convolutional AE and TCN features, shared representation, Gaussian task routing, task heads, weight alignment and weighted output fusion. CICIoT2023 results include accuracy 0.9643 and F1 0.9645; training takes 789.58 s over 40 epochs on the authors' setup. It motivates a head-alignment comparator and representation ablation. Task routing and feature-axis convolution require scrutiny before claiming task-free or physically temporal inference; poisoning is not evaluated. [Publisher full text](https://link.springer.com/article/10.1007/s10462-025-11358-9).

**P7 — Guo et al.** Authors: Chaoqun Guo, Xihan Li, Jubao Cheng, Shunjie Yang and Huiquan Gong. DP-Means diversity and high-entropy selection update memory; logit/feature/attention alignment and meta-weighting address label scarcity and class imbalance. CICIDS2017 reported accuracy is 83.4% and F1 82.1%; removing DP-Means reduces reported F1 to 76.4%. Evaluate its memory-selection idea under the same record/byte limits. High uncertainty is informative for honest learning but can also preferentially admit attacker-generated outliers. The paper does not establish safety of that admission rule under targeted poison. [Publisher full text](https://www.mdpi.com/1999-5903/17/10/456).

**P8 — Villani et al.** Authors: Francesco Villani, Dario Lazzaro, Antonio Emanuele Cinà, Matteo Dell'Amico, Battista Biggio and Fabio Roli. Sonic accelerates genetic poisoning search through an incremental FISHDBC surrogate and transfers attacks to clustering targets. On 20 Newsgroups, Table II's low-budget HDBSCAN-target setting reports AMI 0.15 between original and poisoned cluster assignments, at perturbation bound 0.2 and controlled-sample fraction 0.01. This is clustering disagreement, not classification accuracy or ground-truth AMI. Adapt the objective to training-only network candidates and feasible flow manipulations, then measure downstream family recall. Image/text perturbation feasibility is not network packet feasibility. [Final OA paper](https://iris.unica.it/bitstream/11584/470685/1/sonic-editorial.pdf).

**P9 — Prasad et al.** Authors: Arvind Prasad, Ibrahim Aljubayri, Mohammad Zubair Khan and Abdulfattah Noorwali. CICIoT2023 is reduced to binary labels and normalized features; similarity-balanced initialization feeds a Bernoulli-NB/Passive–Aggressive/SGD ensemble with client update gating. Table 6 reports aggregate accuracy 0.979596. Complete label inversion produces rejected updates, but partial/adaptive poisoning, expanding family labels and replay retention are not evaluated. Benchmark a declared gating variant separately; Sections 3.3 and 4.7 give additive and multiplicative tolerance formulations, respectively, requiring explicit resolution before reproduction. [Publication and CC BY access](https://www.techscience.com/CMES/v147n3/67913); [complete PDF](https://cdn.techscience.cn/files/CMES/2026/TSP_CMES-147-3/TSP_CMES_82021/TSP_CMES_82021.pdf).

### 1.4 Three-paper cross-paper comparison

**Focus Paper 1 = P1 (Carillo); Focus Paper 2 = P2 (Lavaur); Focus Paper 3 = P5 (Delgado).** These studies motivate the primary federation, poisoning and continual-memory experiments. P3 supports optional discovery, but binary novelty detection is less representative of the main supervised FCIL question than a controlled replay-versus-regularization comparison.

| # | Paper Title | Year of Publication | Dataset Used | Preprocessing Techniques | Models / Techniques Used | Evaluation Metrics Used | Results | Limitations / Research Gap |
|---|---|---|---|---|---|---|---|---|
| 1 | P1: A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats | 2026 | TON_IoT; IoT-NID; Edge-IIoTset | Label harmonization; undersampling; first-packet fields; padding | CNN; FL/CIL combinations; replay/bias correction | Old/new/all F1 | TON_IoT S2 FedProx–MEMENTO+, 100 rounds: all 74.49%, old 79.05%, new 68.10% | Clean FCIL; packet representation differs from this code |
| 2 | P2: Investigating the Impact of Label-flipping Attacks against Federated Learning for Collaborative Intrusion Detection | 2025 | NFV2-UNSW-NB15; NFV2-CSE-CIC-IDS2018 | Common NetFlow representation; sampling; stratified 80/20 split | Binary FL; label flipping; heterogeneous clients/defenses | Accuracy, F1, targeted/relative ASR | 10,670 experiments; clean scores generally >0.90 | Static training does not measure sequential retention |
| 3 | P5: Continual learning for adaptive IoT network intrusion detection via domain-incremental learning methods | 2026 | UQ-IoT-IDS-2021; Kitsune; CICIDS2017 | Statistical features; binary labels; balanced/skewed sampling; sliding training stages | Eight CL strategies; MLP/LSTM/Transformer | Macro-F1, forgetting, PR-AUC, FPR, training/state cost | Replay final F1 0.92–0.98; forgetting <0.05 | Clean binary DIL; replay uses attack-family metadata; no poisoning evaluation |

Sources: [Focus Paper 1](https://domenicociuonzo.wordpress.com/wp-content/uploads/2026/03/early_access_tnsm26_fedcil_ids.pdf), [Focus Paper 2](https://orbilu.uni.lu/bitstream/10993/65906/1/Investigating_the_Impact_of_Label_flipping_Attacks_against_Federated_Learning_for_Collaborative_Intrusion_Detection.pdf), [Focus Paper 3](https://www.sciencedirect.com/science/article/pii/S1568494626014705).

### 1.5 Cross-paper methodological synthesis

P1 informs decentralized acquisition and old/new calibration; P2 informs attack definitions and clean-matched error accounting; P5 informs memory-versus-regularization comparisons. P4 supplies an auxiliary-data-dependent server comparator, P7 supplies adaptive memory ideas, and P6 motivates head-alignment controls. P3/P8 support the separate detector-and-clustering branch.

Three requirements follow. Compare learners with the same stream, head policy and client ownership before attributing differences to memory. Report poisoning-induced changes relative to each learner's clean control; attacked accuracy alone confounds baseline quality with robustness. Evaluate legitimate adaptation alongside resistance because excluding difficult new evidence can lower attack success while damaging useful learning.

Reported F1 values are not a leaderboard. Binary DIL, multiclass FCIL, novelty detection, packet matrices and aggregate features differ in information and scoring conventions. An adapted mechanism is named as an adaptation; exact reproduction requires the original representation and protocol.

## Deliverable 2: Refined Research Gap

### 2.1 Research gap matrix

The focus-paper mapping is fixed in Section 1.4. Each entry describes demonstrated scope rather than establishing an omission across all literature.

| Research Gap | Evidence from Paper 1: P1 | Evidence from Paper 2: P2 | Evidence from Paper 3: P5 | Proposed Research Opportunity |
|---|---|---|---|---|
| G1: Retention under targeted poisoning | Clean FCIL | Poisoned static FL | Clean continual replay | Matched FCIL learner comparison with past/new F1 and targeted-error differences |
| G2: Protecting honest new/rare evidence | New-class acquisition | Heterogeneous defenses | Imbalanced continual detection | Class-aware admission against volume-matched global selection |
| G3: Interpreting persistence | No poisoned memory | No continual replay lifecycle | Replay preserves supervision | Withdrawal evaluation; distinguish failed acquisition from forgetting |
| G4: Fairness of combined evaluation | Packet-based FCIL | Binary NetFlow FL | Binary DIL and measured cost | Common flow schema, persistent ownership, matched memory and measured cost |

Sources are the three focus manuscripts linked in Section 1.4.

### 2.2 Current mechanisms and their technical limitations

Federated CIL, replay, regularization, distillation and poisoning defenses already exist. The opportunity is a controlled investigation of their interaction under changing attack-family labels and corrupted training supervision. Replay can preserve useful knowledge and corrupted labels. Regularization protects parameters without verifying supervision. Loss-based rejection ranks agreement with a current model and may penalize honest novelty. Server validation requires trusted data covering the relevant distribution.

Neither clean continual accuracy nor static poisoning resistance alone establishes a suitable adaptive defense. Public benchmarks also require explicit chronology, duplicate exposure, class support and simulated organizational ownership. These are evaluation constraints, not claims that every selected paper contains leakage.

**Closest additional counterexample:** P9 already combines streaming federated IDS, imbalance and poisoning defense. Therefore, the gap cannot be “no adversarial streaming federated IDS.” The narrower opportunity is expanding attack-family outputs, partial targeted poisoning, replay controls and separately measured acquisition/retention. P9 supplements the required three-paper matrix rather than being concealed by its focus selection.

### 2.3 Refined problem, objectives and necessity

**Primary research question:** Under an audited class-incremental network-flow stream with persistent non-IID clients, how do fine-tuning, EWC and DER++ differ in poisoning-induced loss of past knowledge and acquisition of new attacks, and does class-aware admission improve the security–adaptation tradeoff relative to global selection admitting the same number of samples?

The objectives are:

1. Measure learner-specific poison damage against paired clean training, including old-class retention and target-family error.
2. Test class-aware versus global admission while controlling sample volume, memory policy and information access.
3. Measure later error after attacker withdrawal without conflating incomplete initial learning with forgetting.
4. Report computational/memory cost under a reproducible, bounded protocol.

The academic contribution is a falsifiable comparison and mechanism analysis. The practical contribution assesses the cost of rejecting legitimate evidence: an apparently safer filter is insufficient if it suppresses rare attacks or creates excessive benign alarms.

### 2.4 Proposed mechanism and information requirements

The primary intervention is **class-aware admission without additional trusted labels**. Established, sufficiently supported classes use within-class loss ranking. New or very small supplied-label classes receive a protected admission rule so an old model cannot reject their entire evidence pool. Decisions use currently available training data. This is supervised filtering, not an unsupervised novelty detector.

Keep the same learner, head policy and replay sampling across defense arms. A global-loss control admits exactly the same number of rows on each client as the class-aware rule, separating class protection from the effect of more training data.

Trusted review is a separately budgeted extension with equal-information global-plus-review and review-only controls. The primary contribution does not depend on review access. The primary adversary alters data/labels while the training agent executes the defense; fully Byzantine clients require separate server-side evaluation.

### 2.5 Hypotheses and observable outcomes

These are proposed hypotheses for a new versioned analysis plan, not retrospectively registered conclusions.

| Question | Testable hypothesis | Evidence needed | What would weaken or refute it? |
|---|---|---|---|
| RQ1: Does the CL method alter poison damage? | H1: poison-induced change differs between learners | Paired learner-by-poison interaction on pre-attack E1 attack-family F1; targeted error separately | Zero-centered/wide intervals or inconsistent datasets |
| RQ2: Does class protection help? | H2: class-aware admission improves targeted error and new/rare-class F1 over volume-matched global selection | Same learner/head/memory; ASR, new-class F1 and admission logs | Gains explained by more samples, or worse new-class F1/benign alerts |
| RQ3: Does an attack leave later damage? | H3: target-error differences persist after withdrawal in some learner/dose settings | Pre-attack, attack-stage and later checkpoints; buffer contamination | Poor initial acquisition explains the deficit; no later clean-matched difference |

H1 does not predict that replay always fails. H2 requires both security and adaptation outcomes. H3 alone does not prove replay causality; buffer-policy and loss-component ablations must support a mechanism.

A secondary discovery question requires independent detector viability. The milestone can be completed with the supervised FCIL study.

### 2.6 Intended contribution and claim boundaries

The intended contribution is **a reproducible evaluation of client-data poisoning in supervised FCIL, a controlled class-aware admission intervention, and analysis of retention, adaptation and persistence**. Within-class trimming and protected quotas are simple established ideas; the proposal does not claim that this heuristic is a newly invented robust-learning algorithm. Its merit depends on controlled evidence and the security–adaptation tradeoff. The planned reservoir and teacher/head repairs define new baselines; historical results from the existing buffer are not interchangeable with them.

P4 already studies server defenses, P5/P7 study continual memory, and P8 attacks clustering. “First” claims remain unsupported. Findings are conditional on simulated clients, benchmark streams, supplied class labels and declared attacker capabilities. A null or harmful defense result remains reportable as a bounded characterization.

## Deliverable 3: Proposed Research Methodology

### Step 1 — Define the research input

Represent the stream for client \(k\), stage \(t\), as

\[
D_{k,t}=\{(x_i,\widetilde y_i,u_i,g_i,s_i)\}_{i=1}^{n_{k,t}},
\qquad x_i\in\mathbb R^d.
\]

Here \(u_i\) is an immutable sample/content identifier; \(g_i\) is capture/session/device grouping metadata; \(s_i\) is timestamp or a declared ordering proxy; \(\widetilde y_i\) is the available training label. Evaluator-only true labels and poison status are stored separately. Timestamps, addresses and identifiers are excluded from model inputs.

The expanding label set is \(\mathcal C_t=\mathcal C_{t-1}\cup\mathcal C_t^{new}\). Benign recurs across stages; inference receives no task identity. Allow \(P_{k,t}(x,y)\neq P_{\ell,t}(x,y)\) and \(P_{k,t}\neq P_{k,t-1}\). Distinguish multiclass FCIL, fixed-label binary domain-incremental detection, and unlabeled novelty detection throughout.

The initial trust boundary comprises the coordinating server, audited calibration/review data and honest clients. In the primary data-poisoning protocol, one of five clients has attacker-controlled selected training rows/labels, while its training agent still executes the declared admission and learning procedure. This assumption is necessary for a local admission defense. A fully Byzantine client that can bypass filtering or directly forge updates belongs to a separate model-poisoning protocol; local admission alone provides no protection against that capability. Server compromise is outside the experiment. A sensitivity study uses two malicious clients without implying that every robust aggregator supports that fraction.

### Step 2 — Data collection and sourcing

Use [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) as the implementation-continuity dataset and [CICIoT2023](https://www.unb.ca/cic/datasets/iotdataset-2023.html) as a more recent IoT external-validity benchmark. These are historical controlled captures, not live 2026 deployment data. Add UNSW-NB15 only after resolving or explicitly excluding its audited train–test content overlap.

Record source URL, release version, license, extractor version, download date, SHA-256, original row counts and post-cleaning counts. Do not combine incompatible packet-field and aggregate-flow schemas. A P1 packet-CNN reproduction is a separately labeled extension using PCAP extraction, not a relabeling of the existing CSV MLP.

### Step 3 — Preprocessing and cleaning

Extend [clean.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/data/clean.py>) and [sequence.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/data/sequence.py>) to preserve grouping/order metadata before dropping it from model inputs. Log invalid-row removal and support changes. Use feature-content hashes independent of labels for leakage grouping, with separate feature-plus-label hashes for conflict diagnostics. Identical features with different labels must not evade the overlap audit.

**Split construction.** The target allocation is 60/20/20 training/development/test by row count within each scored capture day. Reconstruct session IDs and ordering from source metadata or PCAP before dropping identifiers. Treat a session as atomic; sort sessions by start time, breaking ties by content ID, and choose the group boundaries nearest the 60% and 80% cumulative-row cutoffs. Ratios are approximate because sessions cannot be divided. A capture day defines an experience and may contain sessions in different partitions; the session, rather than the entire weekday capture, is the isolation unit. Record the session reconstruction rule and actual ratios. Remove later-partition feature-content duplicates of training rows, and test duplicates of development rows; quarantine contradictory duplicate labels and publish support losses. Fit scaling on the initial benign training pool only and freeze it.

**Feasibility gate.** Verify nonzero training/development/test support for both E1 attack families and the E2 DoS-Hulk target before locking the primary endpoint. Other unsupported families are disclosed and excluded by a fixed support rule, not by their measured performance. If grouping leaves a required family entirely in one partition, do not split its session or silently shuffle it: revise the data protocol prospectively or report the primary experiment as infeasible. If trustworthy session/time metadata cannot be reconstructed, the existing within-class ordering may support a separately identified content-disjoint ordered-class benchmark; it does not establish chronological session generalization.

**Initialization and scored experiences:** Monday/T0 supplies benign scaler/calibration data and is not counted as a supervised classification experience. Tuesday/T1 supplies the first benign-plus-attack stage E1; Wednesday, Thursday and Friday become E2–E4. This avoids interpreting one-class softmax training as learned attack discrimination. All admission arms are disabled during clean E1 initialization, giving the DER++ defense comparisons an identical learned starting checkpoint. The existing five-stage legacy matrix remains separately labeled for compatibility.

Use capture-day order and the available within-class capture-order proxy. Claim globally chronological streaming only if timestamps/grouped splits establish it. CICIoT2023 requires its own capture/family progression; CICIDS weekday semantics cannot be transferred. The initial supervised stage must contain benign and at least one attack class.

Poison selection occurs after splitting and affects training only. Hidden clean training labels remain evaluator-only, except for an explicitly restricted optional review service. Sparse evaluation families produce N/A endpoints rather than fabricated support.

### Step 4 — Feature engineering and representation

Retain the audited numeric flow schema and MLP backbone as the primary representation, limiting architecture as a confound. Save a feature dictionary, units, allowed bounds, categorical/flag constraints and extractor provenance; mark unknown units/bounds explicitly rather than inventing them.

A secondary representation study compares the existing AE with a CND-IDS-inspired encoder/PCA detector using clean development data. If feature-token attention is added, define each numeric feature token as \(e_j=w_jx_j+b_j+p_j\), rather than reusing the current single-flow-token model as a claim of cross-feature attention. Packet CNNs and temporal windows require explicitly new data adapters and equal development budgets.

For feature-space attacks, define feasible bounds and immutable fields. Until a modified flow is realizable through the traffic generator/extractor, describe it as a feature-space attack; raw/scaled consistency alone does not establish packet feasibility.

### Step 5 — Proposed model and architecture

Use the existing MLP \(f_\theta(x)=W_t h_\theta(x)+b_t\). The primary experiment changes admission rather than adding a backbone.

**Common head protocol.** Current training labels announce candidate classes as the stream reaches them; future evaluation labels cannot announce classes. Before filtering, the server expands heads consistently, preserving old rows and assigning the same new-row initialization across paired arms. All arms receive the same currently available label identities. Reset Adam state on every global-model broadcast, consistently across arms, while retaining only the method-specific replay/Fisher/teacher state. State the choice because retaining client momentum after replacing its model parameters defines a different optimizer protocol. Supplied labels do not certify attack identity.

**Continual objectives.** DER++ uses current-label CE, stored-logit matching and replay-label CE:
\[
L_{\mathrm{DER++}}=
\mathbb E_{D^{adm}_{k,t}}\mathrm{CE}(f_\theta(x),\widetilde y)
+\alpha\mathbb E_{M_{k,t-1}}\frac{\|P_i f_\theta(x)-z_i\|_2^2}{|P_i|}
+\beta\mathbb E_{M_{k,t-1}}\mathrm{CE}(f_\theta(x),y).
\]
\(P_i\) selects coordinates existing when exemplar \(i\) was stored. Coordinate masking is a common planned protocol refinement, not an exclusive ingredient of the proposed defense; legacy padding is a separate ablation. Replay terms are zero when memory is empty. Store supplied replay labels, never evaluator-only clean labels. Capture post-update teacher logits in evaluation mode, then restore training mode; the existing implementation stores them with dropout active, a separately disclosed legacy difference.

EWC adds
\[
L_{\mathrm{EWC}}=L_{\mathrm{CE}}+\frac{\lambda}{2}
\sum_jF_j(\theta_j-\theta^{anchor}_j)^2.
\]
Document the actual batch-gradient Fisher approximation and DER++ post-update stored logits.

**Primary admission rule.** Score rows once per stage with its frozen pre-update checkpoint after common head expansion. Reuse the accepted-ID set for every local epoch and any additional rounds of that stage. Let \(n_{k,c,t}\) be client-local current supplied-label support, \(q=0.75\) the proposed keep fraction, and \(n_{\min}=20\) the small-support boundary:
\[
K_{k,c,t}=
\begin{cases}
n_{k,c,t},&c\notin\mathcal C_{t-1}\ \text{or}\ n_{k,c,t}<n_{\min},\\
\max(1,\lceil qn_{k,c,t}\rceil),&\text{otherwise}.
\end{cases}
\]
For every nonempty client-local class, admit the \(K_{k,c,t}\) lowest-loss rows within class \(c\), breaking ties by deterministic seeded IDs. New/under-supported classes receive full admission at that stage; poison may also benefit from this protection. The rule uses supplied classes, not hidden clean labels. Primary source-to-benign flipping does not include attacker-invented label identities.

The previous global label set \(\mathcal C_{t-1}\) determines whether a class is new; low support is computed locally. A class already known globally but unseen on one client is not globally new. The choice \(n_{\min}=20\) is a prespecified heuristic, not a literature-derived optimum; report local protection counts and assess 10/20/50 only as a separately locked sensitivity.

With \(N_{k,t}^{adm}=\sum_cK_{k,c,t}\), the matched-volume global control independently computes the same quota from the same supplied-label counts, then admits that many lowest-loss rows across classes on client \(k\). It never receives another arm’s losses, accepted IDs or true labels. Retain the original global-75% filter from E2 onward as another comparator. Log per-class admissions and realized poison fraction. Empty shards do not train or contribute weight.

**Memory and aggregation.** All primary replay/defense arms use a planned uniform reservoir of 500 total records/client. On the first admitted encounter of each immutable ID, increment the client’s lifetime seen-ID counter \(v\); append while \(v\le M\), otherwise draw \(j\sim\mathrm{Uniform}\{1,\ldots,v\}\) and replace slot \(j\) only if \(j\le M\). Subsequent epochs may train/replay that flow but do not insert it again. Store its first-encounter supplied label and post-update logits. This gives each distinct admitted historical flow inclusion probability \(\min(1,M/v)\). It requires an ID-aware buffer extension; it is not the current code. Keep the same teacher-capture/head-mask convention in every primary DER++ arm.

The task manifest must place each training ID in exactly one stage and client. Gate insertion to the first local epoch of the first round of that stage; later passes do not insert, avoiding an unbounded lifetime seen-ID set. The reservoir needs the lifetime counter and at most 500 stored IDs, in addition to its data/logits.

The existing random-overflow buffer both favors recent arrivals and permits repeated IDs across epochs. Retain it as an explicitly named legacy compatibility comparison. To isolate policy effects, compare reservoir, random-overflow and class-balanced replacement with the same one-insertion-per-ID schedule; do not call the legacy combination a pure replacement-policy ablation. Record occupied slots, distinct IDs, age/class distributions, logits and actual bytes. Use FedAvg weights \(w_{k,t}=N_{k,t}^{adm}/\sum_\ell N_{\ell,t}^{adm}\), based on admitted current rows, as the existing runner does. Class-aware and matched-volume global arms consequently have identical per-client weights, active clients and current-data batch counts. No-filter/global-75% arms may change those quantities, which must be reported. Replay samples do not add aggregation weight. Include uniform averaging before interpreting differences from unweighted robust aggregators.

**Optional review.** A budget \(b_{k,t}=\lfloor0.01n_{k,t}\rfloor\) limits distinct reviewed training IDs/client/stage. Deterministic within-class uncertainty selects queries before labels are returned. Simulated review may access clean labels for those training IDs only; no test labels or poison masks are exposed. Compare class-aware-plus-review, global-plus-review and review-only arms at the same budget. Report reviewer assumptions and annotation demand, not an unmeasured human cost.

### Step 6 — Baseline methods

| Comparison tier | Required arms | Purpose |
|---|---|---|
| Primary learners | Fine-tuning, EWC, DER++ without filtering | Learner-by-poison interaction |
| Primary defenses | Fixed DER++: no filter, global 75%, matched-volume global, class-aware | Separate class selection from sample-volume effects |
| Mechanism controls | ER/LwF; memory and logit-mask ablations | Explain replay/distillation effects |
| Optional review | Class-aware-plus-review, global-plus-review, review-only | Control additional trusted information |
| Optional server defenses | Median/trimmed/Krum or WeiDetect-style validation | Separate Byzantine-update threat model |
| Reference ceiling | Joint training on historical data | Quantify retention with greater historical access |

Fix DER++ for the defense tier before final outcomes. Poor clean performance triggers a documented development reassessment and protocol revision, not selection of the learner giving the largest final defense gain.

The repository's robust aggregators are unweighted while FedAvg is sample-weighted. Include uniform averaging. Validate Krum's count condition against actual active submissions and check Multi-Krum/trimming parameters; no theoretical guarantee is inferred from executing a named function. The original Krum count requirement is \(n>2f+2\), with additional gradient-distribution assumptions: five active clients/one Byzantine client meet the count requirement; five/two do not. Meeting the count requirement does not establish its original theoretical assumptions for non-IID federated local updates. [Foundational algorithm source](https://papers.nips.cc/paper/2017/file/f4b9ec30ad9f68f89b29639786cb62ef-Paper.pdf). This older methodological reference is not counted among the nine 2025–2026 selected papers.

Binary DIL, packet CNNs and novelty detectors are extensions. Implementing every reviewed architecture is unnecessary for the primary milestone.

### Step 7 — Experimental design

**Proposed lock parameters, subject to independent development checks:**

| Parameter | Primary specification |
|---|---|
| Supervised experiences | E1–E4; T0 is initialization/calibration |
| Clients / corruption | Five persistent clients; one data-poisoned client |
| Label skew | Dirichlet concentration 0.5; once-assigned group ownership |
| Learners | Fine-tuning/EWC/DER++; common MLP/head protocol |
| Attack | Source-to-benign flipping in E2, where DoS-Hulk occurs |
| Doses | 0/1/5/10% of the attacked client's stage training shard |
| Defense learner | DER++, fixed before final outcomes |
| Memory | 500 records/client; uniform reservoir; one insertion per admitted ID |
| Admission | q=0.75; protected new/small-support classes; volume-matched control |
| Local compute | Three epochs, batch 256; one synchronized round/stage initially |
| Paired seeds | 1–11 and 42; development seeds 101–103 |
| Optional review | 1% distinct training-label queries/client/stage |
| External validity | DER++ no filter / matched-volume global / class-aware, 0% and 5% doses, 12 paired seeds on audited CICIoT2023 |

One round is a low-compute reference, not a convergence claim. As a declared feasibility threshold, each E1 anchor attack family must reach development recall at least 0.50 for each learner on all three clean development seeds. This operational threshold does not prove deployment readiness. If it fails, revise the common round/epoch budget within the development protocol and lock again before final testing; if no feasible protocol is found, report the limitation instead of treating absent initial knowledge as forgetting.

Tune at most 12 configurations/method using seeded capped searches over applicable ranges: learning rate \(\{10^{-4},10^{-3}\}\), EWC lambda \(\{1,10,100\}\), DER++ alpha/beta \(\{0.1,0.5,1\}\). Tune global hyperparameters on the separate development-seed streams using only their development partitions; freeze them before all final-seed runs. This is offline protocol development and can inspect the full development sequence. During a final run, the learner/admission rule receives only current/past training data: no future-stage development labels, retuning or test-driven checkpoint selection. Rank learner configurations by mean stage-wise macro-F1 over seen classes, averaged across the three clean development seeds; break exact ties by a prespecified lexicographic configuration order. Do not tune the learner separately for each poisoning dose or defense arm. Admission starts at the proposed fixed settings; development changes are recorded before final locking.

Use named random streams for ownership, attack-ID ranking, head initialization, current-row order, replay sampling and dropout. Derive each stream from seed/stage/client/purpose; a shared integer seed alone does not guarantee pairing after arms consume different numbers of random draws. Rank current IDs once per epoch and restrict that order to each admitted subset. Match new-data schedules, initialization, ownership, attack selection and common protocol choices. Replay adds examples/state, so record total optimizer steps, current/replay exposures and elapsed cost rather than claiming identical compute across different learners.

Draw one five-client probability vector \(\pi_c\sim\mathrm{Dirichlet}(0.5,\ldots,0.5)\) for each training family. For each atomic training session, identify its most frequent pre-poison label (lexicographic tie rule), draw its owner from that label’s fixed \(\pi_c\), and persist the group-to-client map. Keep all its training rows on that owner across stages. Group allocation yields approximate label skew rather than the exact row-wise Dirichlet procedure; publish realized per-client label counts. Full-stream training-family labels used by this simulation partitioner are an experimental allocation assumption, unavailable to learners. Stable row hashing is not an equivalent label-skew control. Before training, choose the attacked client uniformly with the dedicated attack RNG from nonempty clients containing DoS-Hulk E2 training rows; reuse that client for every method, defense and dose, including its clean control. This conditions the threat on source access. Report this conditioning, source support and realized dose; do not transfer rows or redraw ownership to manufacture an effective attack.

For eligible rows,
\[
B_{k,t}=\min(\lfloor\rho n_{k,t}\rfloor,n^{eligible}_{k,t}).
\]
The primary label-only attacker knows the source/target training labels and its own shard, but uses a seeded uniform source-ID ranking rather than gradient/loss-guided selection. Flip the first \(B_{k,t}\) IDs; E1, E3 and E4 are unmodified. Use nested seeded attack-ID sets across doses. Report changed/shard, changed/source and retained/replayed fractions. Malicious-client fraction \(\mu=1/5\) differs from local poison fraction \(\rho\).

**Temporal interpretation:** the primary E2 attack targets a newly introduced family. Later error can reflect corrupted acquisition rather than forgetting that family. Evaluate previously learned E1 classes separately, retain pre-attack/E2/E3/E4 checkpoints, and reserve forgetting claims for previously learned classes. A clean-prefix-then-poisoned-suffix source-family probe is an optional separately declared sensitivity. The primary attack is a bounded nonadaptive data-poisoning test; success against it does not establish resistance to loss-aware or fully Byzantine attackers.

**Bounded run tiers:** the learner grid contains \(3\times4\times12=144\) complete runs. Three additional DER++ admission arms across four doses add 144, reusing the no-filter DER++ runs. The core thus has 288 unique runs for one dataset. The external-data confirmation tier contains three DER++ admission arms × two doses × 12 seeds = 72 additional runs, giving 360 primary/confirmation runs across two datasets. Lock the CICIoT2023 class-arrival schedule and source family from capture/support metadata before final outcomes; do not select its easiest or most vulnerable target retrospectively. External effects are reported separately, without pooling seed tests across datasets. Development and mechanistic/optional controls are additional; measure pilot runtime before execution. If resources require omitting confirmation, state the single-dataset limitation and retain complete primary pairs.

Freeze task/config/source hashes. This report does not amend the existing [analysis specification](<C:/Users/hp/Desktop/University/5. C Net/1. Project/docs/analysis_spec.json>) automatically. A prospective amendment is required for the revised initialization, endpoints and comparison families.

### Step 8 — Quantitative evaluation metrics

For supported class \(c\),
\[
P_c=\frac{TP_c}{TP_c+FP_c},\quad
R_c=\frac{TP_c}{TP_c+FN_c},\quad
F1_c=\frac{2P_cR_c}{P_c+R_c},\quad
F1_{\mathrm{macro}}=\frac1{|\mathcal C^{eval}|}\sum_cF1_c.
\]
Use the count form \(F1_c=2TP_c/(2TP_c+FP_c+FN_c)\) when its denominator is positive. Prespecify zero-denominator handling and report support. A supported but never-predicted class receives F1 zero; an absent class endpoint is N/A. Report old/new/rare-family macro-F1 and accuracy. Define the benign false-alarm rate explicitly:
\[
FAR_B=\frac{\#\{i:y_i=\mathrm{benign},\ \widehat y_i\ne\mathrm{benign}\}}{\#\{i:y_i=\mathrm{benign}\}}.
\]
This is not the false-positive count of a classifier treating benign as the positive class. For binary detection use attack probability \(1-p(\mathrm{benign})\), average precision \(AP=\sum_i(R_i-R_{i-1})P_i\) at ranked score thresholds, and recall at a validation-selected false-alarm target. Label AP separately from trapezoidal PR-AUC.

Let \(R_{t,j}\) be fixed-test accuracy on stage \(j\) after learning stage \(t\), and \(Q_{t,j}\) the separately named macro-F1 matrix. With \(T\) stages,
\[
ACC_T=\frac1T\sum_{j=1}^TR_{T,j},\quad
BWT=\frac1{T-1}\sum_{j=1}^{T-1}(R_{T,j}-R_{j,j}),
\]
\[
F_{\mathrm{old}}=\frac1{T-1}\sum_{j=1}^{T-1}
\left(\max_{i=j,\ldots,T}R_{i,j}-R_{T,j}\right).
\]
For the supervised primary stream, \(T=4\) means E1–E4; benign T0 is outside the classification matrix. Compute separately named \(Q_{t,j}\)-based macro-F1 backward transfer and forgetting. At stage \(t\), old classes are \(\mathcal C_{t-1}\) and new classes are \(\mathcal C_t\setminus\mathcal C_{t-1}\). **Primary retention endpoint:** let \(\mathcal C_{anchor}=\mathcal C_{E1}\setminus\{\mathrm{benign}\}\), fixed before poisoning. Compute confusion counts on the fixed entire E1 test bank (benign plus its attack families) after every stage, then average F1 only over the anchor attack families. This includes false anchor predictions on E1 benign/other-anchor rows and keeps the evaluation distribution constant. Call the final value anchor-family F1; show its E1 baseline and stage trajectory. This prevents the poisoned, newly introduced E2 target from being counted as previously learned knowledge. Report final all-old-class F1 (classes introduced before E4) as a secondary descriptive endpoint and benign false alarms separately. Stage-matrix BWT can mix acquisition and retention when benign recurs, so it supplements the anchor-family endpoint rather than replacing it. For acquisition at stage t, compute confusion counts on the cumulative E1–Et test bank, then average only its newly introduced supported families. The acquisition endpoint is the mean of those stage values immediately after E2/E3/E4; disclose any empty stage. A true newly scheduled family absent from the supplied-label head receives zero F1, not an evaluator-created output row. This measures acquisition rather than relabeling final-stage performance as acquisition.

A rare-family diagnostic uses a prospectively fixed training-support threshold, proposed <1% of a stage's clean training population. This evaluator grouping cannot become hidden clean-label input to admission. Admission retention verifies how the rule operates; it is not proof of successful learning. The substantive adaptation endpoints are held-out new/rare-class F1.

The current metrics module averages forgetting over all \(T\) stages, including a zero term for the last stage. Keep its legacy result and this old-stage definition explicitly named; do not overwrite conventions without versioning.

Forward transfer requires measured pre-learning scores and a matched baseline:
\[
FWT=\frac1{T-1}\sum_{j=2}^T(R_{j-1,j}-b_j).
\]
The present runner does not measure that upper triangle, so current FWT is N/A. An unseen class has no output in strict expanding-head FCIL; future binary novelty detection must be reported separately rather than inventing a multiclass FWT.

For source-family attack-to-benign poisoning:
\[
ASR=\frac{\#\{\text{held-out source attacks predicted benign}\}}{N^{eligible}},
\qquad
\Delta ASR=ASR_{\mathrm{poison}}-ASR_{\mathrm{clean}}.
\]
This exposes pre-existing targeted errors. For backdoors, define trigger eligibility and the denominator before evaluation. No eligible rows means N/A. Track ASR after attacker withdrawal and cumulative contamination, not merely the final attack stage.

Measure adaptation collateral damage using
\[
Retention^{honest,new}_t=
\frac{N^{admitted}_{honest,new,t}}{N^{eligible}_{honest,new,t}},
\qquad
Contamination_t=\frac{N^{poison}_{replay,t}}{|M_t|}.
\]
Evaluator metadata determines these diagnostics only after decisions are logged. An empty buffer gives N/A contamination. In duplicate-containing legacy buffers, report slot-weighted and distinct-ID contamination separately; the primary reservoir has unique IDs.

For discovery, report score ROC/PR-AUC, detection rate, benign alert rate, cluster ARI/AMI, fictitious-cluster counts, persistent class identity consistency and downstream family recall. Cluster quality alone is not an IDS security outcome.

For resources report trained-model p50/p95 latency at batches 1/256, throughput, adaptation wall time, peak process memory, replay/optimizer/Fisher bytes and serialized update bytes. Five \(M\)-record client buffers consume up to \(5M\) records; include a global-memory-matched centralized comparison. Serialized bytes are not measured network latency. Energy and real edge latency are N/A unless actually measured on the stated device.

### Step 9 — Statistical and comparative analysis

Pair complete seeded runs, not individual flows:
\[
d_s=m_s^{intervention}-m_s^{control}.
\]
Report seed-wise differences, mean/median effects, paired bootstrap 95% intervals from 10,000 seed-vector resamples, two-sided Wilcoxon tests and rank-biserial effect sizes. Use Wilcoxon with zero differences removed and average ranks for ties; an all-zero comparison is reported as no observed difference with p=1. Use an exact procedure only where its no-tie assumptions hold, otherwise identify the approximation. Rank-biserial correlation uses positive versus negative nonzero rank sums; it is N/A when no nonzero differences exist. The seed-vector bootstrap resamples paired complete runs, retaining all stages/doses of a seed together. Wilcoxon interpretation assumes approximately symmetric paired differences; inspect their distribution and disclose severe asymmetry rather than treating its p-value as assumption-free.

For learners A/B, test poison interaction:
\[
I_s^{A,B}(\rho)=
[m_s^A(\rho)-m_s^A(0)]-
[m_s^B(\rho)-m_s^B(0)].
\]
This separates learner-specific poison damage from clean baseline differences. Contamination–error correlation alone does not establish replay causality.

The proposed amended primary families are:

| Family | Planned comparisons | Endpoint / interpretation |
|---|---|---|
| F1: learner interaction | Three learner pairs × three nonzero doses = 9 | Final anchor-family macro-F1 interaction |
| F2: class-aware versus matched-volume global | Four doses × two F1 endpoints, plus three nonzero-dose ASR contrasts = 11 | Final anchor-family F1; mean new-class acquisition F1; post-withdrawal clean-matched targeted error |
| F3: mechanism/collateral diagnostics | Admission counts, rare-family F1 and benign alerts | Descriptive; extra tests require prospective declaration |

Apply Holm correction within F1/F2. Ordinary bootstrap 95% intervals are not simultaneous family-adjusted intervals; label interval type. Optional ablations are exploratory unless prespecified. These new family definitions are proposed amendments, not an executed registration, and preserve the current two-sided/no-equivalence rules.

Use the mean E3/E4 clean-matched source-family ASR change as the scalar post-withdrawal endpoint and show both stage values. Compare the class-aware and matched-volume global changes relative to their own clean arms. A zero-dose change is identically zero by definition, so it receives no inferential ASR contrast; report raw clean ASR descriptively. Use the mean acquisition F1 defined in Step 8, not an unspecified best stage. Use the locked support sets across all arms; supported but never-predicted classes score zero. Failed runs are rerun under identical locked inputs. If a planned seed remains unavailable, disclose the missing seed and failure reason; suppress the affected confirmatory comparison until its required complete pairs are restored. Never replace seeds, drop unfavorable classes or impute a failed run as zero.

Seeds estimate conditional training/partition variability rather than independent deployments. Broader capture uncertainty requires separate usable capture units. Report intervals and power limitations; nonsignificance is not immunity.

**Decision rule:** lower ASR alone does not establish a successful defense. Report all F2 endpoints, rare-family outcomes and benign alarms, including adverse tradeoffs. Formal preservation/noninferiority would require a justified prospective margin; none is asserted.

### Step 10 — Ablation and component contribution

Prioritize prospectively locked tests of:

1. Class protection against matched-volume global ranking.
2. Reservoir versus random-overflow versus class-balanced replacement at fixed capacity and identical first-ID insertion. Report the duplicate-inserting legacy buffer separately.
3. DER++ replay-label/logit terms under the same head policy.
4. E2 burst and E3/E4 withdrawal; separately declared learned-source recurrence if feasible.

Round count, ownership changes, review and discovery/cap studies are optional tiers. Changing sampling, head policy and filtering together cannot establish an admission effect.

An evaluator-only oracle-purified replay arm may diagnose whether stored poison drives later error. Label its hidden-mask access and exclude it from deployable-defense claims. Interpret it with matched capacity and exposure because purification also changes sample content.

Log new-class and rare-established-class protection separately. A primary security gain without reduced contamination is not evidence of poison removal. Sample-count retention is a mechanism check; held-out classification measures learning.

### Step 11 — Error and failure-mode analysis

Stratify errors by family, class support, client, stage and attack budget. Inspect confusion matrices, benign false alarms, honest-client rejection, buffer class composition and source-to-target errors. Diagnose whether degradation arises from forgetting, poisoning, label skew, insufficient head expansion or detector failure.

For discovery, separately measure the fraction of true unknown attacks that never become candidates, those assigned as noise, and those absorbed into fictitious clusters. Persistently align cluster proposals across stages; do not count each task's new cluster ID as a newly verified attack type. Replace ground-truth fallback for unassigned rows with an explicit unresolved/review state in the unsupervised arm.

The current inverted T1 AE ranking is a development failure case, not evidence that an attacker suppressed discovery. Threshold redesign requires separate development data and a new protocol version. Failed detector viability can justify retaining discovery as a documented negative/diagnostic study while keeping FCIL poisoning primary.

### Step 12 — Final research outputs and code integration

| Existing file/module | Planned integration |
|---|---|
| [sequence.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/data/sequence.py>) | Metadata-preserving grouped chronology, frozen-scaler and duplicate-exclusion manifests |
| [mlp.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/models/mlp.py>) | Coordinated head expansion with preserved old weights and explicit optimizer policy |
| [Continual methods](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/cl>) | ID-aware uniform reservoir; policy controls; provenance; evaluation-mode stored logits and old-logit coordinate masks |
| [Federated modules](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/federated>) | Persistent group ownership, synchronized labels, matched aggregation controls |
| [Defenses](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/defenses>) | Primary class-aware and matched-volume admission; optional bounded review; evaluator-blind decisions |
| [runner.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/runner.py>) | Central/federated parameter parity; staged attack and withdrawal evaluation |
| [pipeline.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/discovery/pipeline.py>) | Explicit unresolved samples, persistent cluster identity and cap sensitivity |
| [metrics.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/metrics.py>) | Named macro-F1/retention metrics, eligibility denominators and legacy-compatible matrices |
| [reporting.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/src/reporting.py>) | Locked manifests and valid-run admission |
| [stats_summary.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/scripts/stats_summary.py>) | Prespecified paired intervals/tests and complete corrected families |
| [bench_trained_bundle.py](<C:/Users/hp/Desktop/University/5. C Net/1. Project/scripts/bench_trained_bundle.py>) | Reproducible trained-model cost measurements |

This document proposes these changes; it does not claim they have been implemented.

Final outputs comprise Deliverables 1–3 in this single report, with the shared nine-paper bibliography and verification record; refined threat model and hypotheses; versioned protocol/configuration; audited task/data manifests; per-seed accuracy and macro-F1 matrices; attack-dose and buffer audits; paired analysis with corrected tests and intervals; ablations and failure cases; trained inference bundles; measured cost profiles; and an IEEE/ACM-style research manuscript. Every final numerical claim must trace to manifest-validated outputs and an updated claim ledger.

## Appendix A: Repository Audit and Implementation Boundaries

| Component | Current implementation | Phase 2 consequence |
|---|---|---|
| Flow preparation | Label canonicalization, invalid-value removal, deduplication, numeric flow features, versioned task artifacts and content identifiers | Preserve capture/group metadata outside model features; require train–test content-disjoint audits |
| Temporal ordering | CICIDS2017 day sequence and within-class capture-order splits | This is an ordered benchmark, not a globally timestamped live stream |
| Scaling | T0-only and offline T0+T1 initialization options exist | Use frozen T0-only scaling for the future-blind primary protocol |
| Classifier | MLP with 128/64 hidden units; expandable output layer | Coordinate expansion across all federated clients; prevent future-class head disclosure |
| Continual methods | Fine-tuning, batch-gradient Fisher approximation for EWC, LwF, ER, DER++ | Name implementation variants; current overflow sampling is not reservoir sampling and repeated epochs can insert duplicate IDs |
| Federation | Persistent client learner state; Dirichlet partitioning; FedAvg and robust aggregation options | Current per-task repartitioning changes sample ownership; add persistent, controlled label-skew allocation |
| Defenses | Global small-loss and kNN label-consistency filtering | Measure retention of legitimate new/rare samples, not just aggregate accuracy |
| Discovery | Benign AE, held-out calibration, training-only capped HDBSCAN, centroid/radius assignment | This is a hybrid supervised protocol when unassigned rows keep their true labels; it is not fully unsupervised class discovery |
| Provenance and inference | Run manifests, data/config/source checksums and trained inference bundles | Lock code/config hashes and admit only validated runs to headline tables |

Specific corrections precede final experiments. A reviewed federated DER++ configuration still points to the legacy task artifact. The centralized runner does not forward DER++ beta in the same manner as the federated runner. Default preallocated classifier heads need an explicitly synchronized expansion protocol for strict FCIL. The tabular attention model represents an entire flow as one token, so it does not implement attention among individual feature tokens. These are implementation facts, not evidence against the general methods.

The [analysis specification](<C:/Users/hp/Desktop/University/5. C Net/1. Project/docs/analysis_spec.json>) labels comparisons as pending runs and has no locked code hash. Its 12-seed protocol must not be confused with historical seven-seed results. The [claim ledger](<C:/Users/hp/Desktop/University/5. C Net/1. Project/docs/claim_ledger.md>) does not currently authorize the main aggregate claims.

The [discovery audit](<C:/Users/hp/Desktop/University/5. C Net/1. Project/docs/e4_detector_cap_audit.md>) reports T1 score AUC 0.120–0.128 and only 5 of 2,745 attacks flagged at q0.95. The 4,000-candidate clustering cap yields ARI 0.628–0.728 against a 5,000-row subset reference. Neither result establishes valid unknown-family discovery over the full stream. Development and revalidation are prerequisites for a headline discovery experiment.

The audit records the state inspected on 5 October 2026 and does not claim that planned repairs have been applied.

### Implementation acceptance gates

| Gate | Required evidence before final comparisons |
|---|---|
| Data integrity | Versioned schema; finite inputs; source/content IDs; overlap exclusions; supported-family counts |
| Temporal/input isolation | Frozen training-only scaler; explicit order proxy; no future/held-out supervision access |
| Model parity | Same current head order/dimensions; common optimizer reset; central/federated alpha/beta forwarding; ID-unique reservoir and teacher-capture audit |
| Defense parity | Common clean E1; frozen stage checkpoint; deterministic ties; client-level quota/weight parity; mask isolation |
| Federation parity | Persistent ownership; actual active submissions; valid aggregation parameters; weighting disclosure |
| Result integrity | Complete required paired seeds; atomic completion; locked hashes; validated matrices and claim ledger |

Only this documentation is revised. Runtime code, experiment configurations and the existing analysis specification remain unchanged.

## Appendix B: Evidence and Qualification Notes

### Evidence interpretation

| Evidence | Establishes | Does not establish |
|---|---|---|
| Publisher record / official program | Publication identity and year | Code reproducibility or deployment validity |
| Named JCR release/category | That edition's Q1/Q2 classification | A current 2026 or SJR ranking |
| Complete public manuscript | Free readable access and methodological detail | Success of every automated download or identical revisions |
| Published results table | Authors' reported outcome | Reproduction by this project |
| Existing source | Implemented mechanics | Validated aggregate findings |
| Proposed protocol | Intended concrete experiment | Completed implementation or registered/supported hypotheses |

Evidence routes are recorded in Section 1.2. P5 is a peer-reviewed publisher journal pre-proof available online in July 2026, distinct from an unreviewed arXiv posting. Its publisher OA statement takes precedence over a conflicting secondary closed-access index label. P3/P4 author versions are linked to separately verified peer-reviewed publications.

P8's relevance is the implemented clustering component; claiming all nine papers experimentally evaluate network traffic would be inaccurate. The main focus comparison uses three intrusion-detection studies.

P9 was added during self-review after verifying its accepted/publication dates, CC BY publisher record, complete 29-page PDF and Q2 engineering category in the same JCR edition. Its threshold ambiguity remains a reproduction limitation; journal rank does not remove that limitation.

### Limitations retained

The targeted review does not prove exhaustive novelty. Automated download success and free-access evidence remain separate. Static captures do not reproduce every deployment drift. Optional perfect-label review is a simulation assumption, not measured analyst behavior. Seeds do not supply independent deployments. Local admission assumes the training agent follows the defense under the primary data-poisoning model.

The primary FCIL study remains complete and testable within these boundaries.

## Appendix C: Self-Review and Revision Decisions

**Assessment before revision: major revision.** The proposal had a useful implementation foundation but needed clearer identification of what each comparison could establish. This is a self-review, not an independent peer-review verdict.

| Severity | Critique of the earlier report | Revision and remaining boundary |
|---|---|---|
| Major | The selected focus papers could make the intersection of streaming federation and poisoning appear less studied than it is. | Added P9 as qualifying counterevidence; narrowed the gap to expanding family outputs, partial poisoning and measured retention. No priority claim. |
| Major | Final “old” classes included the E2 family attacked during first acquisition, confounding failed learning with forgetting. | Primary retention now uses E1 attack families fixed before poison; target acquisition and post-withdrawal error remain separate. |
| Major | “Chronological grouped 60/20/20” did not specify whether a whole capture or a session could be split, or whether required labels remained supported. | Defined atomic sessions, approximate chronological cutoffs, content-overlap exclusions and feasibility gates. Reliable grouping metadata must still be reconstructed. |
| Major | A total sample-volume match did not guarantee identical client influence or a common learned defense starting point. | Match volume per client and admitted-row FedAvg weights; disable filters during clean E1 initialization. Subsequent states are allowed to diverge because selection is the intervention. |
| Major | Current DER++ memory could be mistaken for uniform historical rehearsal, despite recency bias and duplicate insertion. | Primary planned reservoir inserts each admitted ID once; identical memory/head conventions across defense arms; legacy compatibility reported separately. |
| Moderate | Shared seeds, undefined poisoned-client selection and “current/past validation” left pairing and future-information access ambiguous. | Named RNG streams; source-access-conditioned client selection; separated offline development from final-run training visibility. |
| Moderate | The proposed rule and nonadaptive attack could be read as a general robustness contribution. | Declared the protection threshold heuristic, label-only attacker knowledge and compliant-agent boundary. Adaptive/model-poisoning claims require separate experiments. |

**Remaining implementation risk:** this revision improves the design, not its experimental evidence. Metadata reconstruction, coordinated head/optimizer handling, admission controls, ID-aware reservoir/teacher capture, replay-logit masking and the prospective analysis-plan amendment remain acceptance gates. A pilot may reveal infeasible source support or poor clean learning; any redesign must precede final evaluation. Report null effects, adverse rare-family tradeoffs and incomplete comparisons honestly.

**Document organization:** retain one authoritative submission for Deliverables 1–3, with these appendices as its engineering/evidence audit. Separate result/config artifacts are generated by later experiments; they are not competing versions of the literature review. Deliverable 4 remains omitted as requested.
