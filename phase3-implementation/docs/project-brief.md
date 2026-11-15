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
The reviewed literature motivates testing these mechanisms together under a precisely specified protocol:
- Continual-learning IDS papers assume **honest participants with clean labels**.
- Federated poisoning defences are tested with a **fixed set of classes**, and often just single runs.
- Those defences can throw away **honest but rare or new** evidence together with the poison.

So it is unknown: (a) how bad a poisoned stage is for a learner that is acquiring a new attack family, (b) whether replay memory keeps the error alive after the attacker withdraws, and (c) how much legitimate new-class data a protective filter discards.

## 4. What the literature says (Phase 2 review, ten extra 2025-2026 studies plus the three from Phase 1)
- Federated class-incremental IDS exist but trust all clients (e.g. the studies tagged P2, P4, P12).
- Centralised continual-IDS benchmarks compare replay, distillation and EWC on clean data (P8, P9, P13). P9 itself notes its replay could be exploited by attackers.
- Poisoning work in federated IDS uses a fixed class set (P5, P7, P10, P11). Defences wrongly exclude honest clients (P11 reports 4.6% on CICIDS2017), absorb rare classes into normal traffic (P10), or need a large trusted dataset (P7).
- Prior work on replay poisoning motivates a more specific comparison of federation, acquisition and withdrawal; no exhaustive novelty claim is made.
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

## 7. Implementation and current evidence

Phase 1 reviewed continual IDS research; Phase 2 specified the methodology. Phase 3 implements a reduced, explicitly amended development study using the corrected CICIDS2017 release and five simulated clients. The submitted Phase 2 document remains the historical design, not a claim that every proposed experiment was completed.

The saved GPU grid is complete: 696 trajectories, including learners, admission conditions, and component ablations. The earlier statement that 108 defense and 258 ablation runs remained missing is obsolete. The canonical report is `../../submissions/phase3-report/phase3-report.pdf`.

A local CPU supplement implements clean/ordinary/oracle-purge/random-deletion replay conditions, a DQ check, and offline pooled references. `../../results/phase3-cpu-supplement/completion.json` records its final executed count. The execution protocol and complete state-parity checks are in `../../docs/phase3-cpu-supplement-protocol.md`. Only completed, validated trajectories enter the final report.

## 8. Findings and interpretation

DR retains more earlier-family capability than FT/EI in the original grid, but poisoned training can also produce errors after attacker withdrawal. FT/EI already have weak clean capability, so small additional damage cannot establish security. Initial class acquisition is imperfect as well; the report shows per-family outcomes and an offline learnability reference.

The older summary called final Hulk recall loss H. The corrected report restores Phase 2 H: the mean E3/E4 Hulk-to-benign ASR increase over a matched clean trajectory. Mistaking Hulk for another attack and mistaking it for benign have different operational meanings. Both diagnostics remain available under separate names.

Admission outcomes depend on attack strength. At moderate corruption, random class-aware selection is competitive with loss ranking. Preserving new-labelled rows is a mechanism check, not proof of learning. The report shows acquisition, targeted errors, false alarms and clean capability together.

## 9. Limits and statistical status

The grid uses three ownership partitions times four training/corruption replicates on one fixed development bank. Replicate streams change initialization, minibatches, poison selection and replay while ownership remains fixed. These are not twelve independent captures or deployments.

The expanded attack grid and revised analysis are exploratory. The original separate C1/C2 significance claims are superseded by a combined 47-comparison sensitivity analysis using partition-level effects. Three partition units cannot yield a two-sided exact signed-rank p below .05; absence of significance does not establish equivalence.

The oracle memory intervention uses evaluator knowledge and is not deployable. Its random-deletion control matches volume, not retained class composition. Offline pooled training has future-class and unrestricted historical access and is a sanity reference rather than a matched deployment baseline. Final-test data, adaptive forged updates, live deployment and cross-dataset validation remain outside these executed claims.

## 10. Reproduction and handoff

Run `python scripts/reproduce_phase3_submission.py` from the repository root after the CPU supplement finishes. This verifies evidence, recomputes metrics, regenerates figures and report, renders the PDF, and validates the submission ZIP. `../../submissions/phase3-report/README.md` describes input reconstruction and dependency versions. `defense-notes.md` in the same folder supports the presentation or viva.

## 11. Glossary

| Term | Meaning |
|---|---|
| E1-E4 | Four stages introducing new annotated attack families |
| FedAvg | Current-admitted-row-weighted averaging of local model updates |
| H | Clean-matched targeted Hulk-to-benign error averaged over E3/E4 |
| Final recall damage | Clean-minus-poisoned Hulk recall at E4 |
| A | Mean acquisition F1 on untargeted newly arrived eligible classes |
| DC / DM / DQ | Class-aware loss ranking / matched-volume global ranking / class-aware random selection |
| Oracle purge | Evaluator-only deletion of marked poison; explanatory intervention |
| Partition | One simulated component-ownership assignment, not an independent capture |
