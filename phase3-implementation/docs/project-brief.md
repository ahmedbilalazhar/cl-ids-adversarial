# Project brief: Poisoning, Retention and Legitimate Adaptation in Federated Continual Intrusion Detection

Course: Computer Networks research project. Authors: Saneedullah (23I-2568) and Ahmed Bilal (23I-2581).
Use this page to explain the whole project to someone who has never heard of it.

---

## 1. One-minute version
Network attacks keep changing, so an intrusion detection system (IDS) must keep learning new attack families without forgetting the old ones. Organisations also want to train such systems together without sharing raw traffic. We study what happens when this *shared, continually learning* detector is attacked through its **training labels**: one participant relabels a real attack as "benign" while a new attack family is being learned. We measure how much damage that does, whether the damage stays after the attacker stops, and whether a defence that filters training data can protect the model without blocking legitimate new attack families.

## 2. Background in plain words
- **Intrusion detection system (IDS):** a model that labels network flows as benign or as one of several attack types.
- **Continual learning (CL):** the model learns attack families one stage after another. The danger is *catastrophic forgetting*: after learning stage 4 it can forget stage 1. Common fixes are
  - **regularisation** (EWC-style: protect weights that mattered earlier), and
  - **replay** (keep a small memory of old examples and mix them into training; DER++ also stores old outputs).
- **Federated learning (FL):** several clients (organisations) each train on their own data and send only model updates; a server averages them (FedAvg). Raw traffic never leaves the client.
- **Label poisoning:** a client's training labels are wrong, for example because an automated labelling feed is fooled or compromised.

## 3. The problem
Each field has its own answer, but nobody tests them together:
- Continual-learning IDS papers assume **honest participants with clean labels**.
- Federated poisoning defences are tested with a **fixed set of classes**, and often just single runs.
- Those defences can throw away **honest but rare or new** evidence together with the poison.

So it is unknown: (a) how bad a poisoned stage is for a learner that is acquiring a new attack family, (b) whether replay memory keeps the error alive after the attacker withdraws, and (c) how much legitimate new-class data a protective filter discards.

## 4. What the literature says (Phase 2 review, ten extra 2025-2026 studies plus the three from Phase 1)
- Federated class-incremental IDS exist but trust all clients (e.g. the studies tagged P2, P4, P12).
- Centralised continual-IDS benchmarks compare replay, distillation and EWC on clean data (P8, P9, P13). P9 itself notes its replay could be exploited by attackers.
- Poisoning work in federated IDS uses a fixed class set (P5, P7, P10, P11). Defences wrongly exclude honest clients (P11 reports 4.6% on CICIDS2017), absorb rare classes into normal traffic (P10), or need a large trusted dataset (P7).
- The only study poisoning a continual IDS's replay buffer is a single-machine preprint.
- Many studies report single runs, and some tune thresholds on labelled test batches (P6, P11-P13).

## 5. The research gaps and questions
| Gap | Research question | Hypothesis family |
|---|---|---|
| G1: poisoned labels during class acquisition are untested in federated continual IDS | **RQ1:** How do fine-tuning (FT), an EWC-style regulariser (EI) and DER++ replay (DR) differ in damage to the poisoned attack family, both immediately and after the attacker withdraws? | C1 (learner differences, confirmatory) |
| G2: defences can reject legitimate new evidence together with poison | **RQ2:** Compared with a global filter admitting the same number of samples, how does a class-aware admission rule change the trade-off between poisoning damage and learning new attack families? | C2 (DC versus DM, confirmatory) |
| G3: the responsible mechanism and its cost are not identified | **RQ3:** Which memory and selection mechanisms explain the differences, and what do they cost in computation and communication? | Exploratory (ablations, cost) |

## 6. The study design (what we do)
- **Data:** CICIDS2017 (corrected labels), 74 header-free flow features, repository-audited split. Development bank only; no final-test data is touched.
- **Federation:** five clients; whole network "components" belong to one client (no row leaks between clients). Four stages E1-E4 introduce new attack families; the model's output head grows 3, 8, 13, 16 classes. FedAvg, 12 rounds per stage.
- **Learners:** FT (plain fine-tuning), EI (EWC-style with a per-example Fisher estimate), DR (DER++ replay, 500 records per client).
- **Attack:** in stage E2 one or more clients relabel a share of their DoS-Hulk rows as benign. The attacker is withdrawn in E3 and E4.
- **Defences (applied on top of DR):** DC (class-aware admission: keeps a quota per class and keeps new classes whole), DM (a global ranking admitting the same number of rows), DQ (random control with the same quota).
- **Measures:** macro-F1 on eligible classes, benign false-alarm rate, Hulk recall, attack success rate, **H** (persistent damage = Hulk recall lost at the end, compared with the same learner without attack), acquisition **A** (how well new classes are learned), backward transfer and forgetting, and cost (time, communication bytes, memory bytes).
- **Statistics:** results are paired by run. Confirmatory tests are two-sided Wilcoxon signed-rank tests with Holm correction inside each family, plus bootstrap confidence intervals and rank-biserial effect sizes.

## 7. The three phases
**Phase 1: literature review.** Three 2026 papers on continual learning for network security were reviewed. They revealed three gaps: evaluation data is old or synthetic, nobody attacks the adaptation mechanism itself, and deployment cost is not measured.

**Phase 2: extended literature review and methodology (done).** Ten more 2025-2026 studies were added and checked against the rubric. The Phase 1 gaps were narrowed into G1-G3, with research questions, hypotheses, the experimental design, metrics and the statistical plan. The deliverable is the LaTeX report `phase2_with_claude.tex` (our improved version), based on the repository `ahmedbilalazhar/cl-ids-adversarial`. It contains a design only; no numbers of our own.

**Phase 3: implementation and experiments (in progress).** The university asks for seven things:
1. implementation of the proposed methodology,
2. dataset and preprocessing,
3. baseline evaluation,
4. graphical results,
5. comparison with existing research,
6. ablation studies,
7. results analysis and discussion.

How we did it:
- All compute runs on Kaggle (a free T4 GPU), in a single notebook, `phase3_kaggle_final.ipynb`, with three parts whose results are saved separately:
  - **Part A:** download and verify the data, rebuild it, check every pinned hash, build one training package per allowed seed.
  - **Part B:** our own implementation (`p3lib.py`, run in parallel by `p3parallel.py`) runs the experiment grid, one result file per run, resumable.
  - **Part C:** tables, figures, statistics, comparison with literature and an auto-written discussion with its limits.
- The repository only allows development seeds 101-103 (higher seeds are sealed for the final evaluation). We use those three ownership partitions times four training replicates, giving 12 paired units.

## 8. What we have found so far
- **First run (3 seeds, a single weak attacker):** the attack did almost nothing. One attacker holds only about 6% of the Hulk rows and the other four clients outvote it. Hulk recall stayed about 0.99-1.00. So the defences showed no benefit and only cost accuracy. We reported this as a finding, then strengthened the threat model: 1, 3 or 5 attacking clients and different poisoning shares.
- **Second run (stronger attack, RQ1 complete with 12 units):**
  - DR keeps what it learned (clean macro-F1 0.49); FT and EI collapse (0.03-0.05) and raise false alarms on about 93-98% of benign traffic.
  - Immediate damage grows with attack strength: DR loses 0.61 of its Hulk recall when 50% of Hulk rows are poisoned, 0.88 at 71%, and all of it at 90%.
  - The damage persists after the attacker withdraws: persistent damage H is about 0.79 (50%) to 0.99 (90%) for DR.
  - FT and EI show H = 0 only because they have already forgotten Hulk without any attack; their damage shows in the immediate recall loss.
  - Six of 30 confirmatory C1 tests are significant after Holm correction (DR versus FT/EI on H in the stronger arms).
- **RQ2 and RQ3:** only partly run so far, so no conclusion yet. The early partial data suggest that class-aware admission (DC) lowers macro-F1 without reducing persistent damage, but this is not final.
- **Known difference from the repository's own result:** our DR scores 0.434 where the repository's committed run scores 0.655 (the ranking agrees); this must be reported honestly.

## 9. Honest limits
- One dataset, one attack pattern (Hulk relabelled benign in one stage), development bank only.
- The 12 units are 3 ownership partitions times 4 training replicates, so replicates within a partition are not fully independent.
- FT and EI collapse even without attack, so their poisoning damage is bounded by what is left to lose.
- CPU and GPU runs are not bit-identical; all comparisons use one device type.

## 10. What remains
1. Finish the Kaggle run (`QUICK = False`): the defence grid (about 108 runs missing) and the ablations (about 258 runs missing), then re-run Part C. About 1.2 hours.
2. Write the Phase 3 report using the generated tables, figures and discussion, covering the seven requirements.
3. Explain the gap to the repository's DR result and the weak FT/EI baselines.
4. Push the final files to the repository.

## 11. Glossary
| Term | Meaning |
|---|---|
| E1-E4 | the four learning stages, each introducing new attack families |
| FedAvg | the server averages client model updates, weighted by how much data each client used |
| H | persistent damage: Hulk recall lost at the end, compared with the same learner with no attack |
| A | acquisition: how well newly arrived classes are learned |
| BWT / forgetting | how much earlier classes are lost after later stages |
| DC / DM / DQ | admission rules: class-aware quota / matched global ranking / random control |
| Unit | one ownership partition times one training replicate; the unit of pairing in the statistics |
