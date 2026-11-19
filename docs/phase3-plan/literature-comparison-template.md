# Fair comparison with existing research

This template records the comparison protocol. A validated 74-feature development comparison now exists in `submissions/phase3-overnight/appendix.md`; it is development-bank evidence, not held-out confirmation. See the populated contextual comparison in `docs/phase3-reference/research-comparability.md`.

## 1. Direct within-protocol table

Every included method uses the same canonical release/split, features, stage schedule, ownership/poison IDs, model family, declared current-data budget, paired seeds and evaluator. DR-based admission variants inherit the selected DR settings. This is the table that supports direct quantitative comparisons.

| Method | Clean/poisoned absolute source error | H / immediate source damage | Acquisition A / per-family recall | Clean/poisoned benign FAR | ACC/BWT/forgetting | Actual cost |
|---|---|---|---|---|---|---|
| FT | See adopted-profile CPU extension report; development only | See report | See report | See report | See report | Observed run/checkpoint costs only |
| EI | See adopted-profile CPU extension report; development only | See report | See report | See report | See report | Observed run/checkpoint costs only |
| DR | See adopted-profile CPU extension report; development only | See report | See report | See report | See report | Observed run/checkpoint costs only |
| DM | See adopted-profile CPU extension report; development only | See report | See report | See report | See report | Observed run/checkpoint costs only |
| DC | See adopted-profile CPU extension report; development only | See report | See report | See report | See report | Observed run/checkpoint costs only |
| DQ | See matched-random adopted-profile CPU extension; development only | Exploratory comparison | See report | See report | See report | Observed run/checkpoint costs only |

Report means/dispersion and raw paired effects with support/denominator references. DG and the adopted-profile loss/quota/eviction controls remain absent; historical 76-feature ablation results do not transfer.

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

For manuscript submission, shorten this table to the material closest papers and verify full experimental settings again. A web check on 17 November 2026 confirmed the bibliographic record and abstract for Lavaur et al. (2025) and the PMLR record for Neurotoxin; the remaining recent papers and preprints still need primary-source verification. This is a scoped comparison, not a systematic review or replication.

## 3. What “reproduction” would require

A faithful reproduction uses the original source commit, input/release, split, features, label map, task schedule, capacity, optimizer/budget, seed convention, threat and metric implementation. A method adapted to our MLP/five-client/label-feed setting belongs in a direct adapted-method comparison with its changes documented.

A published-noise-aware adapter should not be added by merely copying default hyperparameters into the 1-round/3-epoch or 3-round/1-epoch budget. Some methods' alternating/consolidation phases require a different schedule. Count their own clean development work and disclose any unequal resources. Avoid a “state of the art” claim when the study deliberately compares a small set of retention mechanisms.

## 4. Numbers copied from papers

If reporting a published value, retain its original metric definition, unit, dataset version, positive class, averaging, split, support and uncertainty. Separate the paper-reported value from a local reproduced/corrected result. Do not average them into this study's twelve-seed estimates.

No comparison can establish superiority from a higher headline accuracy on another dataset or a smaller ASR with a different denominator. State the exact scope of each numerical claim.
