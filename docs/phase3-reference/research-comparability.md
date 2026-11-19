# Comparison with existing research

This comparison is contextual. It keeps published results separate from local results and does not rank headline metrics across incompatible datasets.

## Protocol alignment

| Study or method | Dataset and task | Overlap with this study | Main incompatibility | Proper use |
|---|---|---|---|---|
| **Adopted 74-feature implementation reference** | Corrected CICIDS2017, 74 numeric inputs, four stages, five simulated clients; one clean DR+DC trajectory with lambda_z=.5 | Confirms one complete reference path | One untuned seed; not the selected primary coefficient | Descriptive implementation reference only |
| **Adopted 74-feature CPU extension** | Same corrected profile; 240 matched core runs over FT/EI/DR/DM/DC × four doses × twelve ownership seeds, plus DQ and oracle controls | Direct local comparison of learner/admission arms and dose response | Development bank was exposed during prior tuning; DR lambda_z=.1 follows historical selection; no independent capture or sealed test | Primary exploratory development evidence; see `submissions/phase3-overnight/appendix.pdf` and the full-evidence archive |
| [Lavaur et al. (2025)](https://orbilu.uni.lu/handle/10993/65906) | NF-v2 CSE-CIC-IDS2018 and UNSW-NB15; fixed binary federated IDS | Label-flipping attacks, clean references and attacker participation | No expanding class head, continual replay, or shared development split; feature sets and endpoints differ | Closest static federated IDS poisoning context; published values are not baselines for this run |
| [DER++ (Buzzega et al., 2020)](https://arxiv.org/abs/2004.07211) | General class-incremental learning | Replay plus distillation objective used by the learner | Not a federated IDS experiment and not a poisoning evaluation | Algorithmic reference for the memory loss; no paper metric is copied as a comparator |
| [EdgeFedCIL (2026)](https://www.mdpi.com/1424-8220/26/14/4630) | ToN-IoT and X-IIoTID federated class-incremental IDS | Continual IDS, replay/distillation and resource concerns | Different data schema, architecture, client construction, balancing and evaluation contract | Related design context; not a numerical leaderboard comparator |
| CICIDS2017 correction authors ([Liu et al., 2022](https://intrusion-detection.distrinet-research.be/CNS2022/index.html)) | CICIDS2017 flow extraction and annotation analysis | Same underlying capture; release quality and label provenance | Data-quality analysis rather than a matched learner comparison; corrected and original releases are not independent samples | Supports the source/schema and annotation limits, not model-effectiveness claims |

The literature records and broader comparison are in [`submissions/phase2-with-claude.tex`](../../submissions/phase2-with-claude.tex), [`docs/phase3-plan/literature-comparison-template.md`](../phase3-plan/literature-comparison-template.md), and the Phase 3 audited report. A paper-reported number may be quoted only with its original task, metric, support, and uncertainty. No published accuracy or F1 is directly subtracted from the current development result.

## Local evidence alignment

| Evidence set | What it compares | Boundary |
|---|---|---|
| Earlier 76-feature development matrix | FT, EI, DR, DM and DC across paired doses/seeds, with corrected endpoints and audited predictions | Different adopted input profile; its results and model weights do not transfer to the current 74-feature study |
| Adopted 74-feature lambda_z=.5 reference | One clean DR+DC seed-101 trajectory | Implementation reference only; not the selected primary coefficient |
| Adopted 74-feature CPU extension (lambda_z=.1 for DR) | FT/EI/DR/DM/DC over 12 seeds and four doses; DQ clean/.5 and exact oracle suffixes | Matched local core, replay-loss (48) and quota (96) ablations are complete; DG has a prospective selector but no matched outcomes, and FIFO/class-balanced eviction remains absent; development-only |
| Existing matched-random DQ work | Random within the same admission quotas | DQ is not Phase 2's global filtering DG control |
| Historical GPU report | Includes DG but uses a different engine/threat and has no saved model weights | Context only; no checkpoint-based re-evaluation or pooling with current evidence |

## What would support a direct comparison

The adopted-profile CPU extension already compares FT, EI, DR, DM and DC under a matched split, seed, attack-ID and metric contract. A direct six-arm Phase 2 comparison still requires 48 DG outcomes under that same profile; the deterministic fixed-75% selector is implemented but unrun, and DQ does not substitute for it. Report absolute clean/attacked outcomes and paired effects with denominators and seed-level uncertainty. Published-paper comparisons remain qualitative because datasets, features, ownership and attack protocols differ; the local matched evidence supports only conditional development-bank contrasts.
