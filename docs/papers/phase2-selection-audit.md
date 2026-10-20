# Phase 2: Seven Additional Papers and Architectural Audit

**Verified:** 8 October 2026. **Scope:** repository diagnosis, seven-paper acquisition, and critical comparative synthesis. This audit supports the literature selection. A separate standalone `submissions/phase2.tex` develops Deliverables 1–3; no architecture diagram is produced. Papers 4–10 below extend the existing papers 1–3. They are seven additional articles, bringing the local collection to ten; the course's requirement for 8–10 *additional* articles would still require at least one further addition if interpreted literally.

## Task 1: Research Direction & Codebase Diagnosis

### Evidence from Phase 1

The source is [phase1.tex](../../submissions/phase1.tex). Its objectives and assumptions are expressed through a topic and gap table rather than a formal hypothesis section:

> “Proposed Topic: Continual Learning for Network Security” — line 39.

> “If clustering goes wrong, every later step is affected” — line 85.

> “they assume the coordinating server and all clients are honest” — line 100.

> “These methods are tested for detection or authentication accuracy, but not for how well they resist an attacker who specifically targets the continual-learning mechanism” — line 221.

> “Design evaluation protocols and defenses that test continual-learning security systems against attackers who specifically target the adaptation mechanism itself” — line 225.

The report additionally identifies older/synthetic validation data and missing hardware-cost measurements in its Gap 1 and Gap 3 rows (lines 215–219 and 227–231). These are limitations of the three selected Phase 1 studies, not evidence that the entire field lacks adversarial continual IDS research. The new literature supplies important counterevidence to any broad novelty claim.

### Core research trajectory

The implemented project is an **offline experimental study of poisoning and knowledge retention in continual network intrusion detection**, primarily simulated federated learning on tabular network flows. The primary question in [proposal.md](../proposal.md) compares fine-tuning, EWC and DER++ under malicious-client data poisoning and asks whether lightweight filtering recovers lost attack knowledge. A separate branch studies attacks on an autoencoder–HDBSCAN discovery pipeline. There is no implemented RF-fingerprint authentication pipeline.

The most defensible Phase 2 direction is to measure **security versus adaptation**: whether an admission or update rule rejects poison without suppressing legitimate new or rare attack evidence, and whether a poisoned training stage causes later error after attacker withdrawal. This is a controlled research opportunity, not a demonstrated novel algorithm or a proven robustness guarantee.

### Architectural mechanics: implemented versus proposed

| Component | Current source and mechanics | Relation to Phase 1 / boundary |
|---|---|---|
| Data preparation | [clean.py](../../src/data/clean.py), [sequence.py](../../src/data/sequence.py), [unsw.py](../../src/data/unsw.py), [iot.py](../../src/data/iot.py): numeric flow features, label canonicalization, invalid-row removal, ordered tasks, source/content identifiers, scaling and overlap controls | Extends beyond NSL-KDD to CICIDS2017, UNSW-NB15 and CICIoT2023 adapters. Capture-day order and per-class capture-order splitting are not a globally timestamped deployment stream. Dataset-specific overlap audits remain necessary. |
| Classifier / representation | [mlp.py](../../src/models/mlp.py): default 128/64 MLP, dropout 0.1, expandable classification head; autoencoder with latent width 16 | Implements flow classification and novelty representation, not Phase 1's RF CNN. [tabular_attention.py](../../src/models/tabular_attention.py) processes one token per whole flow; it does not implement feature-to-feature attention. |
| Continual learners | [src/cl](../../src/cl): fine-tuning, EWC, LwF, ER and DER++; EWC accumulates squared *batch* gradients around the newest parameter anchor | These are implementable retention baselines. Describe EWC as an online importance approximation rather than an exact per-example Fisher implementation. |
| Replay mechanics | [er.py](../../src/cl/er.py) and [derpp.py](../../src/cl/derpp.py): append observed records, randomly discard overflow; DER++ also stores logits and uses label and logit replay losses | Random overflow deletion is not uniform reservoir sampling over the entire historical stream. Repeated epochs can insert the same underlying record repeatedly. Current DER++ already masks unavailable teacher coordinates and captures stored logits in evaluation mode; those repairs must not be described as missing. |
| Federation | [fedavg.py](../../src/federated/fedavg.py): persistent client learner state, configurable rounds, sample-weighted FedAvg, robust aggregators and per-client poisoning/accounting | Simulated clients, without measured network transport or physical devices. Default Dirichlet partitions are regenerated by task; stable-ID hashing exists but produces approximately IID ownership rather than controlled persistent non-IID sites. |
| Strict class expansion | [runner.py](../../src/runner.py) has a single-node `grow_head` option; [BaseCLMethod](../../src/cl/base.py) refreshes the optimizer when the head grows | Federated setup initially allocates the full `label_map` width. An expanding family stream alone does not establish strict future-class-blind FCIL; synchronized server/client head expansion is still a bridge. |
| Poisoning / evasion | [src/attacks](../../src/attacks): targeted/random/adaptive label flips, replay-label attacks, feature-trigger backdoors, novelty poison, and Byzantine submitted-update attacks | Directly operationalizes Phase 1 Gap 2. Data poisoning under a compliant local training agent and arbitrary Byzantine clients require different trust boundaries. |
| Defenses | [purification.py](../../src/defenses/purification.py): global cross-entropy small-loss ranking; [consistency.py](../../src/defenses/consistency.py): nearest-neighbor supplied-label agreement | No implemented class-aware admission guarantee. New or rare attack samples can be difficult/high-loss or locally unsupported, motivating matched-volume collateral-damage comparisons. |
| Discovery | [pipeline.py](../../src/discovery/pipeline.py): benign AE scores, clean calibration quantile, training-only HDBSCAN capped at 4,000 candidates, centroid/radius assignment and provisional class IDs | Out-of-sample assignment is an explicit approximation, not HDBSCAN prediction. Unassigned training rows retain supplied labels, so the current branch is hybrid supervised discovery. Cluster IDs are task-unique rather than persistent verified attack identities. |
| Evaluation / provenance | [metrics.py](../../src/metrics.py), [reporting.py](../../src/reporting.py), [stats_summary.py](../../scripts/stats_summary.py), [bench_trained_bundle.py](../../scripts/bench_trained_bundle.py): performance matrices, attack diagnostics, completion manifests, paired analyses and trained-bundle cost instrumentation | Implemented instrumentation is distinct from validated final experiments. Consult the [claim ledger](../claim_ledger.md) before using historical numbers. Serialization bytes do not measure network latency, and host latency does not establish edge-device energy cost. |

Both runners currently obtain continual-method arguments through `learner_kwargs`; the older draft's centralized/federated DER++ parameter-forwarding discrepancy should therefore not be repeated as an unchanged current defect.

### Methodological needs for Phase 2

1. **Lock the learning problem and attacker.** Use multiclass attack-family prediction for FCIL; report binary novelty and fixed-label streaming detection separately. Specify source/target labels, eligible-poison denominators, malicious-client fraction, local-training compliance and attacker withdrawal.
2. **Complete input and ownership isolation.** Use frozen training-only scaling, content-disjoint evaluation, retained capture/session metadata, and persistent ownership with separately controlled class skew. Static benchmarks and simulated partitions constrain deployment claims.
3. **Control the learning mechanism.** Synchronize expanding heads, keep learner/loss parameters identical across central and federated comparisons, and compare ID-unique reservoir, class-balanced memory and current overflow memory under equal capacity. Current teacher-mask/evaluation-mode repairs provide a useful foundation.
4. **Test defenses against matched controls.** Compare class-aware versus global admission with the same admitted count per client; distinguish trusted-validation server filtering from local supplied-label filtering. Measure honest new/rare-class retention and benign false alarms alongside targeted error.
5. **Separate forgetting, failed acquisition and attack persistence.** Freeze a pre-attack old-class set; measure target-family acquisition during the attack and clean-matched source-to-target error after withdrawal. Buffer contamination is a mechanism diagnostic, not alone proof of causation.
6. **Gate discovery on clean viability.** The [detector audit](../e4_detector_cap_audit.md) reports T1 AUC 0.120–0.128 and 5 flagged attacks out of 2,745 at q0.95 across three exploratory seeds. Validate the detector before interpreting a poisoning effect; quantify candidate-cap sensitivity and unresolved samples. This is audited historical diagnostic evidence, not a newly run experiment.
7. **Require manifest-valid repeated results.** Use paired complete seeded runs, per-family macro-F1, recall, ASR relative to clean targeted error, forgetting/BWT, confidence intervals and appropriate multiplicity control. Measure trained-model inference/adaptation time, replay/Fisher/optimizer memory and update bytes on named hardware.

## Task 2 & 3: Discovered Papers & Comparative Synthesis

### Discovery and qualification

Targeted searches addressed FCIL IDS, label-flipping collaborative IDS, server poisoning defenses, continual novelty detection, incremental IoT classification, memory selection and streaming federated robustness. Existing draft references were leads; exact titles/authors/DOIs were checked against publication metadata and primary publisher, author or university records. Full PDFs were then retrieved without institutional credentials and parsed successfully. The selected set contains **exactly seven original experimental papers published in 2025–2026**, all directly studying intrusion detection.

Journal qualification uses **2024 JIF category quartiles in the June 2025 JCR release**, [distributed by UEFISCDI](https://uefiscdi.gov.ro/resource-865584-JCR_2024.iunie2025.pdf). It does not assert a 2026 or SJR quartile. Relevant ranking rows and page locations are retained in [qualification evidence](qualification-evidence.json): Computer Networks p.129 Q1; Computers & Security p.129 Q1; Future Internet p.130 Q2; IEEE TNSM p.131 Q1; JISA p.133 Q2; CMES p.257 Q2. CMES is also Q1 in another category, but its declared qualifying category here is Engineering, Multidisciplinary. DAC qualifies through premier ACM/IEEE peer-reviewed proceedings; its [official research program](https://www.dac.com/Portals/0/62DAC/Program/62DACProgram.pdf?ver=M_DMJU3AU3OMZhX6dDjwsQ%3D%3D) independently lists CND-IDS.

Papers 4–8 are **green OA author versions** linked to published articles/proceedings. Papers 9–10 are **publisher OA versions**. Neither a free URL nor an arXiv identifier was treated as sufficient peer-review evidence. The author TNSM manuscript retains a placeholder “XXXX 2025” header; the registered journal publication is 2026. All outcome figures below are authors' reported results, not results reproduced by this repository.

The highly relevant Applied Soft Computing domain-incremental study (10.1016/j.asoc.2026.116022) was screened but its publisher PDF returned HTTP 403 through this download route. That is an automated-access limitation, not evidence of a paywall. It is not one of the seven delivered papers. The selected streaming ensemble study provides independently verified and successfully downloaded adversarial network evidence instead.

### Relevance reassessment and primary-paper selection

**Primary comparison:** Paper 4 supplies clean federated class-incremental IDS; Paper 5 supplies realistic client label-flipping design; Paper 9 supplies explicit continual-memory selection and its ablations. Together they directly span the project's federation, poisoning and retention mechanisms. Papers 7 and 8 provide the closest defense and clean incremental benchmark extensions. Paper 6 supports the secondary AE/novelty branch. Paper 10 is a lower-priority binary streaming comparator and important counterevidence to a broad claim that federated adaptation under poisoning is unstudied; it is not the anchor for strict multiclass FCIL novelty.

CTWA was replaced by Paper 8 following exact method and experimental-protocol matching. The replacement's complete author manuscript, peer-reviewed publication metadata and Computer Networks Q1 row were verified. The inaccessible domain-incremental article is not substituted using an abstract or a thesis. This targeted review establishes relevance to concrete modules, not exhaustive novelty or guaranteed experimental superiority.

### Seven-paper comparison

The number column follows the existing local folder numbering, so the additions are papers 4–10.

| # | Paper Title | Year | Venue / Publisher | Direct Access Link / Open DOI | Benchmark Dataset | Core Model / Method | Relevance to Our Codebase |
|---|---|---|---|---|---|---|---|
| 4 | A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats | 2026 | IEEE Transactions on Network and Service Management 23, 3865–3880; IEEE; Q1 | [DOI](https://doi.org/10.1109/TNSM.2026.3675031); [free PDF](https://domenicociuonzo.wordpress.com/wp-content/uploads/2026/03/early_access_tnsm26_fedcil_ids.pdf) | TON_IoT, IoT-NID, Edge-IIoTset | Packet CNN; FedAvg/FedProx/FedDyn; BiC+/MEMENTO+ rehearsal, distillation and bias correction | Clean FCIL reference for server/client class handling and old/new F1. Packet features require a separate PCAP adapter. |
| 5 | Investigating the Impact of Label-flipping Attacks against Federated Learning for Collaborative Intrusion Detection | 2025 | Computers & Security 156, 104462; Elsevier; Q1 | [DOI](https://doi.org/10.1016/j.cose.2025.104462); [free PDF](https://orbilu.uni.lu/bitstream/10993/65906/1/Investigating_the_Impact_of_Label_flipping_Attacks_against_Federated_Learning_for_Collaborative_Intrusion_Detection.pdf) | NF-V2 CSE-CIC-IDS2018 and UNSW-NB15 | Binary MLP/FedAvg; targeted/untargeted flips; attack timing and heterogeneous partitions | Direct model for `attacks/flip.py`, eligible budgets, withdrawal and clean-matched attack controls. |
| 6 | CND-IDS: Continual Novelty Detection for Intrusion Detection Systems | 2025 | 62nd ACM/IEEE DAC; premier peer-reviewed proceedings | [publication DOI](https://doi.org/10.1109/DAC63849.2025.11132541); [free PDF](https://arxiv.org/pdf/2502.14094) | X-IIoTID, WUSTL-IIoT, CICIDS2017, UNSW-NB15 | Continual encoder: reconstruction, clustering and historical distillation; benign-fitted PCA novelty score | Replacement novelty-detector arm for the weak AE; separate from attack-family discovery and classification. |
| 7 | WeiDetect: Weibull distribution-based defense against poisoning attacks in federated learning for network intrusion detection systems | 2025 | Journal of Information Security and Applications 95, 104275; Elsevier; Q2 | [DOI](https://doi.org/10.1016/j.jisa.2025.104275); [free PDF](https://arxiv.org/pdf/2504.04367v2) | CIC-Darknet2020, CSE-CIC-IDS2018 | Auxiliary-validation local-model scores; Weibull-based rejection before aggregation | Trusted-validation server-defense comparator to existing robust aggregation and local filters. |
| 8 | Attack-Adaptive Network Intrusion Detection Systems for IoT Networks through Class Incremental Learning | 2025 | Computer Networks 263, 111228; Elsevier; Q1 | [DOI](https://doi.org/10.1016/j.comnet.2025.111228); [free PDF](https://domenicociuonzo.wordpress.com/wp-content/uploads/2025/03/comnet25_cil_ids.pdf) | IoT-23, TON-IoT, IoT-NID, Edge-IIoT | Packet CNN; fine-tuning, replay, LwF, EWC, iCaRL+, EEIL, LUCIR and BiC; memory/few-shot/perturbation sweeps | Direct clean CIL benchmark for our retention baselines, memory budgets and old/new family metrics; packet representation is a separate adapter. |
| 9 | Continual Learning for Intrusion Detection Under Evolving Network Threats | 2025 | Future Internet 17(10), 456; MDPI; Q2 | [DOI](https://doi.org/10.3390/fi17100456); [free PDF](https://mdpi-res.com/d_attachment/futureinternet/futureinternet-17-00456/article_deploy/futureinternet-17-00456.pdf) | UNSW-NB15, CICIDS2017, TON_IoT | DP-Means diversity/high-entropy memory; multi-level distillation; meta-weighted semi-supervised training | Direct alternative to ER/DER++ memory admission; tests rare-class retention and poison attraction. |
| 10 | Resilient Federated Ensemble Learning for IoT Intrusion Detection in Adversarial and Imbalanced Environments | 2026 | Computer Modeling in Engineering & Sciences 147(3), 48; Tech Science Press; Q2 | [DOI](https://doi.org/10.32604/cmes.2026.082021); [free PDF](https://cdn.techscience.cn/files/CMES/2026/TSP_CMES-147-3/TSP_CMES_82021/TSP_CMES_82021.pdf) | CICIoT2023 | Similarity-balanced initialization; Bernoulli-NB/Passive–Aggressive/SGD ensemble; client/server accuracy gates | Streaming federation and label-flip comparator; challenges overly broad claims that adaptation poisoning is unstudied. |

### Assignment-oriented experimental comparison

| # | Preprocessing / experimental construction | Metrics and reported result | Limitations / research opportunity |
|---|---|---|---|
| 4 | Relabel attack hierarchy; majority undersampling; first ten packets/biflow, zero padding; exclude IP/ports; two-/five-client old/new scenarios | Table IV: TON_IoT S2, FedProx–MEMENTO+, 100 rounds: old/new/all F1 **79.05/68.10/74.49%** | Clean short incremental scenarios, not poisoned replay persistence. Translate protocol before comparing packet CNN to CSV MLP. |
| 5 | Common NF-V2/nProbe representation; sampled datasets; ten-client IID and cluster-based heterogeneity arms; varied malicious participation and attack timing | **10,670 runs**. Central reference F1 **0.966** on sampled CSE-CIC-IDS2018 and **0.945** on UNSW-NB15 (§4.2); accuracy, recall, F1, targeted success and clean-relative impact | Fixed binary output, no continual family expansion or replay forgetting. Results depend on class distribution and malicious participation. |
| 6 | Initial normal-only pool; incremental attack experiences; encode stream; PCA fit from available benign representations | Table II: CICIDS2017 versus LwF: AVG **1.93×**, FwdTrans **2.64×**; PR-AUC also evaluated | Best-F chooses test-batch thresholds using labels. Reproduce with development-only thresholds and separately identify original oracle thresholding. |
| 7 | Remove missing/redundant fields; one-hot categorical features, numerical normalization; 80/20 split; Dirichlet non-IID clients; auxiliary server data | Author manuscript §5.4.1: clean F1 **89.791%** (Darknet), **94.184%** (IDS2018). Abstract reports target-recall improvement up to **70%**, F1 improvement **1–14%** | Improvement ranges are not absolute final F1. Trusted validation/class coverage adds information unavailable to unassisted local filters. |
| 8 | Biflow packet matrices; base/expanded fields; initial attack classes followed by added families; 25 exemplars/class baseline and memory sweeps | Table 7: optimized TON-IoT BiC all/old/new F1 **95.30±1.46/96.47±1.18/85.89±7.76%**, 50 records/class, 9 packets; all PAUC **96.79±2.64%** | Centralized clean CIL and inference-time packet perturbations; neither federated poisoning nor replay persistence. Configuration optimization is dataset-specific. |
| 9 | Numerical min–max/categorical one-hot features; five incremental stages; low-label fractions; memory and imbalance sweeps | Table 6: CICIDS2017 average accuracy **83.4%**, F1 **82.1%**; Table 12 removing DP-Means gives F1 **76.4%** | High-entropy admission may prefer crafted outliers; 5,000-sample nominal memory is not the repository's 500-record baseline. No adversarial admission validation. |
| 10 | Binary attack/benign mapping, missing-value handling, min–max features, similarity-balanced warm start, three-client streaming batches | Table 6: proposed initialization aggregate accuracy **0.979596**, FMI **0.979392**; full label inversion rejected; FGSM evaluated | Does not establish multiclass FCIL or poisoned-replay retention. Accuracy gate has additive (§3.3) and multiplicative (§4.7) formulations that must be resolved. |

These outcomes cannot be numerically ranked as if they shared splits, labels, inputs, class counts, supervision or hardware. Their most useful contribution is complementary experimental design.

### Individual technical breakdowns

#### Paper 4: A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats

**Authors:** Raffaele Carillo, Francesco Cerasuolo, Giampaolo Bovenzi, Domenico Ciuonzo, Antonio Pescapè. **Publication:** 2026, IEEE TNSM. [Free manuscript](https://domenicociuonzo.wordpress.com/wp-content/uploads/2026/03/early_access_tnsm26_fedcil_ids.pdf); [local PDF](paper-4/paper-4.pdf).

**Problem and methodology:** decentralized clients acquire new attack classes while preserving prior discrimination. BiC+/MEMENTO+ couple rehearsal, distillation and bias correction with federated optimization. Early detection uses a matrix of packet fields rather than aggregate flow statistics. Two- and five-client settings vary new-class distribution and synchronization rounds.

**Empirical evidence:** Table IV reports TON_IoT S2 FedProx–MEMENTO+ at 100 rounds: 79.05% old-class F1, 68.10% new-class F1 and 74.49% all-class F1. The old/new difference exposes incomplete acquisition concealed by an overall score.

**Integration:** implement synchronized head expansion and separately reported old/new F1 in `fedavg.py`; add FedProx and bias-correction controls after establishing plain FedAvg parity. A CNN reproduction requires packet extraction, not reshaping the current CSV vector into a purported packet sequence. Evaluate the resulting clean baseline before poisoning it.

#### Paper 5: Investigating the Impact of Label-flipping Attacks against Federated Learning for Collaborative Intrusion Detection

**Authors:** Léo Lavaur, Yann Busnel, Fabien Autrel. **Publication:** September 2025, Computers & Security. [Free manuscript](https://orbilu.uni.lu/bitstream/10993/65906/1/Investigating_the_Impact_of_Label_flipping_Attacks_against_Federated_Learning_for_Collaborative_Intrusion_Detection.pdf); [local PDF](paper-5/paper-5.pdf).

**Problem and methodology:** measure targeted/untargeted client-data corruption under FedAvg. A two-hidden-layer binary MLP uses common NetFlow features; systematic sweeps vary corruption rate, collusion, timing, training schedules and partition heterogeneity.

**Empirical evidence:** 10,670 runs establish a broad experimental basis. Section 4.2 reports central reference F1 0.966/0.945 and accuracy 0.992/0.995 on sampled CSE-CIC-IDS2018/UNSW-NB15. These are clean central references, not poisoned federated results. Its central finding is that distribution and target support strongly affect attack impact and similarity-based defenses.

**Integration:** use explicit source-family eligibility and malicious-client versus row-dose accounting in `flip.py`/`fedavg.py`; pair clean and poisoned arms; add late/burst/withdrawal controls. Extend its fixed-output experiments to expanding classes and replay contamination rather than relabeling the original protocol as FCIL. [Author experiment code](https://github.com/leolavaur/cose_2025).

#### Paper 6: CND-IDS: Continual Novelty Detection for Intrusion Detection Systems

**Authors:** Sean Fuhrman, Onat Gungor, Tajana Rosing. **Publication:** 2025, ACM/IEEE DAC; [published DOI](https://doi.org/10.1109/DAC63849.2025.11132541). [Free manuscript](https://arxiv.org/pdf/2502.14094); [local PDF](paper-6/paper-6.pdf).

**Problem and methodology:** binary novelty detection as stream representations evolve without attack labels. The encoder combines reconstruction, cluster structure and previous-encoder distillation. PCA reconstruction of benign embeddings supplies the anomaly score.

**Empirical evidence:** Table II reports CICIDS2017 AVG and forward-transfer ratios of 1.93× and 2.64× over LwF; PR-AUC provides threshold-independent evaluation. Its AVG is not the repository's final-row multiclass accuracy. Best-F uses labeled test-batch outcomes to choose thresholds.

**Integration:** add an encoder/PCA detector beside the current AE in `discovery/pipeline.py`; freeze calibration from development data and evaluate score PR-AUC before clustering. Keep unknown detection, cluster identification and downstream classification as distinct endpoints. [Author code](https://github.com/Sean-Fuhrman/CND-IDS).

#### Paper 7: WeiDetect: Weibull distribution-based defense against poisoning attacks in federated learning for network intrusion detection systems

**Authors:** Sameera K. M., Vinod P., Anderson Rocha, Rafidha Rehiman K. A., Mauro Conti. **Publication:** December 2025, JISA. [Published DOI](https://doi.org/10.1016/j.jisa.2025.104275); [free author version v2](https://arxiv.org/pdf/2504.04367v2); [local PDF](paper-7/paper-7.pdf).

**Problem and methodology:** server-side rejection of poisoned local models under non-IID clients. Auxiliary validation data produce model scores; a Weibull-based decision removes suspicious contributions before aggregation.

**Empirical evidence:** author-version clean baselines report F1 89.791% on CIC-Darknet2020 and 94.184% on IDS2018. Reported defense improvements reach 70% for target recall and 1–14% for global F1 across settings; these ranges do not denote one universal absolute score.

**Integration:** add a trusted-validation aggregation comparator to `federated/robust.py`; declare validation size, family coverage and access timing. Compare with equally informed baselines. In FCIL, poor emerging-family scores may reflect insufficient exposure rather than malice, requiring honest-client rejection and new-family acquisition measurements.

#### Paper 8: Attack-Adaptive Network Intrusion Detection Systems for IoT Networks through Class Incremental Learning

**Authors:** Francesco Cerasuolo, Giampaolo Bovenzi, Domenico Ciuonzo, Antonio Pescapè. **Publication:** May 2025, Computer Networks 263, 111228. [Published DOI](https://doi.org/10.1016/j.comnet.2025.111228); [free author manuscript](https://domenicociuonzo.wordpress.com/wp-content/uploads/2025/03/comnet25_cil_ids.pdf); [local PDF](paper-8/paper-8.pdf).

**Problem and methodology:** append attack families without full historical retraining. The packet-CNN benchmark compares fine-tuning, replay, LwF, EWC, iCaRL+, EEIL, LUCIR and BiC. Explicit old/new/all results, exemplar-size and packet-count sensitivity, SHAP/Integrated Gradients, few-shot acquisition and packet jitter/dropping/flipping expose practical failure mechanisms.

**Empirical evidence:** Table 7 reports optimized TON-IoT BiC all/old/new F1 95.30±1.46%, 96.47±1.18%, 85.89±7.76%, with 50 exemplars/class and nine packets using expanded fields. All-class PAUC is 96.79±2.64%. These are dataset-optimized author results, not a common-protocol comparison with our MLP. Table 8 evaluates packet perturbations, not label-flipping training-data poisoning.

**Integration:** import its old/new/all-family evaluation and memory-capacity sweeps into the existing fine-tuning/EWC/ER/DER++ protocol; add bias correction as a separately controlled baseline. Its per-class capacity must be converted to a matched total-record/byte budget. Packet input requires a distinct PCAP pipeline. The central contribution to our question is the clean retention reference against which staged poisoning can be measured.

**Replacement rationale:** this is more direct than CTWA because it studies the same expanding attack-family learning problem, includes EWC and replay comparators already implemented in our repository, and isolates memory size and few-shot acquisition. CTWA's task-routing/CAE–TCN design is useful but less necessary to the primary research question. The former CTWA package is preserved outside the active seven.

#### Paper 9: Continual Learning for Intrusion Detection Under Evolving Network Threats

**Authors:** Chaoqun Guo, Xihan Li, Jubao Cheng, Shunjie Yang, Huiquan Gong. **Publication:** 4 October 2025, Future Internet. [Published DOI](https://doi.org/10.3390/fi17100456); [free publisher PDF](https://mdpi-res.com/d_attachment/futureinternet/futureinternet-17-00456/article_deploy/futureinternet-17-00456.pdf); [local PDF](paper-9/paper-9.pdf).

**Problem and methodology:** continual classification with scarce labels and class imbalance. DP-Means preserves diverse exemplars while entropy selects informative boundary samples. Logit, feature and attention alignment preserve knowledge; meta-weighting adjusts class contributions.

**Empirical evidence:** CICIDS2017 accuracy/F1 83.4/82.1%; removing DP-Means yields F1 76.4% in Table 12. The nominal memory setting is 5,000 samples, so direct comparison with a 500-record buffer would be unfair.

**Integration:** implement interchangeable admission/eviction policies in ER/DER++, retaining each sample ID once. Compare diversity/entropy selection to reservoir and class-aware admission at equal records and bytes. Quantify contamination, target error and legitimate rare-class retention; an informative outlier can also be adversarial.

#### Paper 10: Resilient Federated Ensemble Learning for IoT Intrusion Detection in Adversarial and Imbalanced Environments

**Authors:** Arvind Prasad, Ibrahim Aljubayri, Mohammad Zubair Khan, Abdulfattah Noorwali. **Publication:** 30 June 2026, CMES. [Publisher record](https://www.techscience.com/CMES/v147n3/67913); [free publisher PDF](https://cdn.techscience.cn/files/CMES/2026/TSP_CMES-147-3/TSP_CMES_82021/TSP_CMES_82021.pdf); [local PDF](paper-10/paper-10.pdf).

**Problem and methodology:** attack-dominant binary streaming IDS with non-IID clients and partial adversarial behavior. Similarity-balanced initialization warm-starts an incremental NB/Passive–Aggressive/SGD ensemble; accuracy gates control local submissions and global acceptance.

**Empirical evidence:** Table 6 reports accuracy 0.979596 and FMI 0.979392 for proposed initialization. Complete label inversion is rejected; FGSM perturbations are additionally examined. These experiments do not establish expanding-family or replay-retention robustness.

**Integration:** add a declared accuracy-gate baseline to the federation experiment; measure rejected honest novel-family updates alongside poison rejection. Resolve the additive versus multiplicative threshold formulations before reproduction. Keep initialization and trusted-evaluation budgets matched; binary ensemble numbers must not be compared directly against multiclass MLP accuracy.

### Research-gap synthesis supported by the selected studies

| Potential gap | Evidence across studies | Proposed bounded research opportunity |
|---|---|---|
| Poison persistence in expanding-family learning | Paper 4 studies clean FCIL; Paper 5 measures fixed-label FL poisoning; Paper 9 measures clean continual memory | Compare fine-tuning/EWC/DER++ with a staged poison burst and withdrawal, separating pre-attack retention from target acquisition. This intersection requires testing; the review does not prove priority. |
| Defense rejection of honest novel/rare evidence | Papers 7/10 gate contributions by validation performance; Paper 9 emphasizes informative low-support/uncertain samples | Compare class-aware local admission to matched-volume global admission, and trusted server gates to equal-information controls; measure collateral loss and benign alarms. |
| End-to-end validity and resource-aware comparisons | Paper 6 includes test-informed thresholding; Paper 8 measures packet waiting time and memory tradeoffs; Paper 4 uses packet rather than CSV inputs | Use development-only calibration, feature-content isolation, matched record/byte budgets and trained-model runtime; gate discovery before propagating pseudo-labels. |

No selected paper demonstrates all of this repository's proposed strict multiclass, persistent-client, partial-poison, memory-policy and post-withdrawal controls together. This motivates the narrowed design; it does not warrant “first ever” or generalized immunity claims.

### Download integrity and local organization

Each new folder contains the complete downloaded `paper-N.pdf`, automatic page-level `paper-N.md`, and `assets/` with original-page PNGs plus publication/source metadata. Page renders preserve charts, tables and equations even when Markdown extraction is imperfect. The PDFs were not replaced with abstracts or locally generated summaries.

| Folder | Version | Pages | PDF bytes |
|---|---|---:|---:|
| paper-4 | Public author early-access manuscript | 17 | 1,656,380 |
| paper-5 | Institutional author manuscript | 34 | 1,339,480 |
| paper-6 | DAC-linked arXiv author version v1 | 7 | 442,271 |
| paper-7 | JISA-linked arXiv author version v2 | 24 | 1,208,964 |
| paper-8 | Public author manuscript, Computer Networks publication verified | 22 | 1,733,201 |
| paper-9 | Publisher version of record | 25 | 682,136 |
| paper-10 | Publisher version of record | 29 | 11,115,059 |

Total: **158 pages in seven active PDFs**. Exact SHA-256 values, URLs, dates and per-paper verification are recorded in [the download manifest](phase2-download-manifest.json). The existing Phase 1 source and existing Phase 2 methodology draft remain separate; this audit does not silently revise either document or implement the proposed code changes.
