# Fair comparison with existing research

Use this structure for Phase 3 requirement 5. Populate own metric values only after validated evaluation; no new performance results exist yet.

## 1. Direct within-protocol table

Every included method uses the same canonical release/split, features, stage schedule, ownership/poison IDs, model family, declared current-data budget, paired seeds and evaluator. DR-based admission variants inherit the selected DR settings. This is the table that supports direct quantitative comparisons.

| Method | Clean/poisoned absolute source error | H / immediate source damage | Acquisition A / per-family recall | Clean/poisoned benign FAR | ACC/BWT/forgetting | Actual cost |
|---|---|---|---|---|---|---|
| FT | Pending validated runs | Pending | Pending | Pending | Pending | Pending |
| EI | Pending validated runs | Pending | Pending | Pending | Pending | Pending |
| DR | Pending validated runs | Pending | Pending | Pending | Pending | Pending |
| DM | Pending validated runs | Pending | Pending | Pending | Pending | Pending |
| DC | Pending validated runs | Pending | Pending | Pending | Pending | Pending |
| DQ, if selected | Pending validated runs | Exploratory comparison | Pending | Pending | Pending | Pending |

Report means/dispersion and raw paired effects with support/denominator references. Do not place an unimplemented method in this table with a number copied from another paper.

## 2. Contextual primary-paper comparison

| Primary work | Data / learning setting | Attack or method overlap | Important incompatibility | Appropriate use |
|---|---|---|---|---|
| [Lavaur et al., 2025](https://orbilu.uni.lu/handle/10993/65906) | NF-v2 CSE-CIC-IDS2018 and UNSW-NB15; fixed binary FIDS | Label-only attacks; clean references; timing/redemption and recovery | No new-family shared-head stream; aggregate accuracy/relative ASR and source-data availability differ | Closest static-FIDS motivation; no direct percentage superiority claim |
| [Ariffin et al., 2026 preprint](https://arxiv.org/abs/2608.04602) | CICIDS2017 continual IDS with benign recurrence and replay | Poisoning stored exemplars | Buffer access, budget denominator, class subset and model differ | Compare replay attack surface; distinguish reported/corrected/reproduced artifacts |
| [SacFL, 2025](https://arxiv.org/abs/2505.00365) | Image/text FCL | Adversarial tasks and later historical behavior | Encoder/decoder, proxy-history defense, data and endpoints differ | Refutes generic first-adversarial-FCL positioning; contextual defense comparison |
| [FIL-ZTA, 2026](https://www.mdpi.com/1999-5903/18/3/154) | Network/authentication plus synthetic identity attributes; incremental FL | Label/model/backdoor robustness | Different features, adversary capability and authentication metrics | Network-context prior art; no cross-paper F1/EER ranking |
| [EdgeFedCIL, 2026](https://www.mdpi.com/1424-8220/26/14/4630) | ToN-IoT / X-IIoTID federated CIL | Replay/distillation and communication efficiency | Different learner/balancing/compression and evaluation contract | Context for continual IDS and resource claims |
| [Neurotoxin, 2022](https://proceedings.mlr.press/v162/zhang22w.html) | FL on language/vision tasks | Persistence after limited adversarial participation | Stronger model-update backdoor threat and trigger-conditioned success | Durability prior art and precise threat distinction |
| [Single-task poisoning, CoLLAs/PMLR](https://proceedings.mlr.press/v330/pawlak26a.html) | Exemplar-free vision CL | Weak one-stage attacker; stability/plasticity harm | Input corruption, exemplar-free learning and no IDS federation | Restricted attacker is not itself novel |
| [AER/ABS, 2024](https://bmva-archive.org.uk/bmvc/2024/papers/Paper_680/paper.pdf) | Multi-epoch noisy-label CIL | Loss separation and contaminated replay | Epoch alternation/restoration and different data/budget | Candidate declared adapter if competitive robustness is claimed |
| [PuriDivER, 2022](https://openaccess.thecvf.com/content/CVPR2022/papers/Bang_Online_Continual_Learning_on_a_Contaminated_Data_Stream_With_Blurry_CVPR_2022_paper.pdf) | Online blurry noisy streams | Memory purity/diversity and robust replay | Sampling/training scheme and label-noise setting differ | Robust continual-learning context; adapter requires its own specification |

For manuscript submission, shorten this table to the material closest papers and verify full experimental settings again. This planning table records relevance, not a completed systematic review or replication.

## 3. What “reproduction” would require

A faithful reproduction uses the original source commit, input/release, split, features, label map, task schedule, capacity, optimizer/budget, seed convention, threat and metric implementation. A method adapted to our MLP/five-client/label-feed setting belongs in a direct adapted-method comparison with its changes documented.

A published-noise-aware adapter should not be added by merely copying default hyperparameters into the 1-round/3-epoch or 3-round/1-epoch budget. Some methods' alternating/consolidation phases require a different schedule. Count their own clean development work and disclose any unequal resources. Avoid a “state of the art” claim when the study deliberately compares a small set of retention mechanisms.

## 4. Numbers copied from papers

If reporting a published value, retain its original metric definition, unit, dataset version, positive class, averaging, split, support and uncertainty. Separate the paper-reported value from a local reproduced/corrected result. Do not average them into this study's twelve-seed estimates.

No comparison can establish superiority from a higher headline accuracy on another dataset or a smaller ASR with a different denominator. State the exact scope of each numerical claim.
