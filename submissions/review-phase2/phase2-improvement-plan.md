# Phase 2 Improvement Plan

**Project:** Continual Learning for Network Security: Poisoning, Retention and Legitimate Adaptation in Federated Continual Intrusion Detection
**Authors:** Saneedullah (23I-2568), Ahmed Bilal (23I-2581)
**Reviewed document:** `submissions/phase2.tex` (compiled Phase 2 PDF dated 8 Oct 2026)
**Checked against:** the course Phase 2 brief
**Evidence base:** the 10 articles in `docs/papers/` of `ahmedbilalazhar/cl-ids-adversarial`
**Plan date:** 20 Oct 2026

---

## 0. Bottom line

The research design is strong and has already been through several methodology reviews. Its weaknesses are in **rubric coverage** and **presentation**:

1. It reviews **7** new papers, but the rubric requires **8–10**.
2. Only **3 of 7** new papers appear in the comparison table, and **none** gets its own critical summary.
3. The gap justification does not answer the rubric's **six questions**.
4. Design choices are rarely **justified from the literature**, even though the papers support almost every choice.
5. The text is **very hard to read**: a 30-row notation table, unexplained acronyms, statistics jargon and `[MEASURE]` placeholders.
6. Quartile evidence **contradicts Phase 1** and openly calls itself "unverified".

**Overall strategy:** keep the science, fix the coverage, make every claim traceable to an article, and rewrite for a reader who has not seen the repo.

Article references below use the folder numbers in `docs/papers/`. "p." means the **PDF page** (the `### PDF page N` marker in each `paper-N.md`, which matches `assets/page-00N.png`).

| # | Paper | Venue | Year |
|---|---|---|---|
| P1 | Ge et al. — Stage-wise CIL for unknown DoS | Future Internet | 2026 (Phase 1) |
| P2 | Wu et al. — EdgeFedCIL | Sensors | 2026 (Phase 1) |
| P3 | Luo et al. — RF fingerprint drift | Future Internet | 2026 (Phase 1) |
| P4 | Carillo et al. — Federated + incremental NIDS for IoT | IEEE TNSM | 2026 |
| P5 | Lavaur et al. — Label-flipping vs FL collaborative IDS | Computers & Security | 2025 |
| P6 | Fuhrman et al. — CND-IDS continual novelty detection | ACM/IEEE DAC | 2025 |
| P7 | Sameera et al. — WeiDetect | J. Inf. Security & Applications | 2025 |
| P8 | Cerasuolo et al. — Attack-adaptive NIDS via CIL | Computer Networks | 2025 |
| P9 | Guo et al. — CL for IDS under evolving threats | Future Internet | 2025 |
| P10 | Latif & Djenouri — AMM-HFL: adaptive multi-model hierarchical FL for robust IoT IDS (**replaces** Prasad et al., CMES, on 20 Oct 2026) | Sensors | 2026 |

---

## 1. Weakness register

Severity: **Critical** = directly loses rubric marks; **Major** = weakens the argument or how it reads; **Minor** = polish.

| ID | Severity | Weakness | Where in current Phase 2 | Strategy (summary) |
|---|---|---|---|---|
| W1 | Critical | Only 7 additional papers; the rubric requires 8–10 | §2.1, Table 1 (the repo's own `docs/papers/README.md` admits this) | Add 1–3 verified 2025–26 Q1/Q2 papers (§2.1 below) |
| W2 | Critical | No per-paper critical review of the new papers; Phase 1 did one per paper | §2.2–2.4 contain only a taxonomy and cryptic paragraphs | Add a short structured critical summary per new paper (§2.2) |
| W3 | Critical | Comparison table covers only P4, P5 and P9 | Table 3 | Full rubric-format table for all new papers (§2.3) |
| W4 | Critical | Gap justification does not answer the rubric's six questions | §3.2 (two dense paragraphs) | Rewrite §3.2 with six labelled answers (§3.2 below) |
| W5 | Critical | Gap matrix evidence is weak: G2/G3 cells describe paper features, not gaps (e.g. "Packet modality and round count condition results") | Table 4 | Replace with the authors' own limitation statements (§3.1 below) |
| W6 | Major | Quartiles undermine themselves and contradict Phase 1. Table 1 caption: "Quartiles require the primary-profile check"; §2.1: "primary journal profiles remain unverified". Phase 1 used SJR (Future Internet = Q1); Phase 2 uses JCR (Future Internet = Q2). | §2.1, Table 1 | One ranking source for both phases, verified and stated plainly (§2.5) |
| W7 | Major | The rubric asks students to "identify common research patterns"; no such synthesis exists | §2.2 | New "Common research patterns" subsection with counts across all papers (§2.4) |
| W8 | Major | Methodology steps are rarely justified from the literature. The rubric asks for a "technically justified" methodology. | §4.1–4.12 | Add a "Why / literature basis" line to each step, using the map in §4 below |
| W9 | Major | Readability: undefined acronyms (FT/EI/DR/DG/DM/DC, E1–E4, T0, ASR, H), a 30-row notation table, compressed sentences ("DC's honest-new admission is one by construction") | Throughout §4 | Plain-language lead per step; move heavy material to appendices (§5) |
| W10 | Major | Baseline step (§4.6) is two sentences | §4.6 | Baseline table: what / why / source article (§4, Step 6) |
| W11 | Major | Unfinished placeholders: the Table 11 "Wall time/run" column is `[MEASURE]` in all 8 rows; "GPU availability is to be confirmed" | §4.7, Table 11 | Replace with estimated ranges or remove the column; state the compute plan |
| W12 | Major | Repo-internal material in a course submission: "Source Verification Record and Folder Mapping" (folder numbers), "frozen Phase 1 course report", "Archived rows support these values", "author template year differs" | App. A, ref [1], §2.1 | Remove; keep a clean reference list |
| W13 | Minor | Phase 1 → Phase 2 link is one sentence; Phase 1 Gaps 1 and 3 are narrowed without clear explanation | §1 | Add a 3-row "Phase 1 gap → Phase 2 status" table |
| W14 | Minor | The diagrams do not show which of the 12 steps each box covers | Fig. 1–2 | Add step-number badges to the boxes |
| W15 | Minor | Abstract is overloaded ("symmetry-qualified permutation intervals", "two declared Holm families") | Abstract | Rewrite as 150–200 plain words: problem → gap → method → expected contribution |
| W16 | Minor (future risk) | Phase 2 narrows to label poisoning + class-aware admission; the repo's paper draft (`docs/paper_draft.md`) headlines Byzantine attacks + robust aggregators | Scope | No change for Phase 2; record so later phases stay consistent |

---

## 2. Deliverable 1: Extended Literature Review

### 2.1 Fix W1: add 1–3 papers

**Strategy:** add papers that strengthen our specific gap, not just to reach the count. Each must be checked for year (2025–26), venue, quartile and full-text access before inclusion.

**Repo check (20 Oct 2026, live GitHub commit `21bc6c3`):** `docs/papers/` holds 10 papers. paper-1 to paper-3 are the Phase 1 papers; **paper-4 to paper-10 are only 7 additions**, below the rubric's 8–10.

**Status: done.** 3 papers were collected, read in full and checked against the rubric. They are in `docs/papers/paper-11` to `paper-13` (pdf + md + page PNGs), giving **10 additional papers**. Full rubric matrix, selection method and critical summaries: **[phase2-rubric-check.md](../../docs/papers/phase2-rubric-check.md)**.

| New | Paper | Venue | Gap it strengthens |
|---|---|---|---|
| paper-11 | FLZT-IDS: trust-aware FL-IDS under model poisoning | *Electronics* 2026 | **G2**: its trust filter wrongly excludes 4.6–5.1% of benign clients even with a fixed class set (§5.5, p.22) |
| paper-12 | Federated transfer learning for rare/new attack classes | *Scientific Reports* 2025 | **G1**: new classes are learned via a client-triggered upload, with honest clients assumed (pp.9–12) |
| paper-13 | EL-GNN: EWC-based continual IDS | *Electronics* 2025 | **G1** + learner justification: EWC continual IDS evaluated only on clean data (pp.16–24) |

Remaining manual step: confirm SJR quartiles on scimagojr.com for *Electronics*, *Scientific Reports* and *Sensors* (automation is blocked).

### 2.2 Fix W2: one critical summary per new paper

**Strategy:** a compact block per paper (~120–150 words, about one-third of a page), using the same headings as Phase 1 so the two phases read as one review:

> **Problem · Method · Data · Key result · Author-stated limitation · Our critique · Relevance to our study**

Evidence for each block, already located in the articles:

| Paper | Key result to quote | Author-stated limitation (with location) | Our critique |
|---|---|---|---|
| P4 Carillo | Table IV, TON_IoT S2, FedProx–MEMENTO+, 100 rounds: old/new/all F1 79.05/68.10/74.49% | §VI p.15: FCIL "face[s] challenges integrating new attacks"; future work (e) "improving robustness against adversarial threats" | Clean clients only; the old–new F1 gap shows new-attack learning is the weak point |
| P5 Lavaur | 10,670 runs; §5.4/Fig. 10: one attacker in ten gives relative success < 0.1; clean F1 0.966/0.945 (§4.2) | §6.2 p.28: only 10 participants; heterogeneity simulation is "caricatural"; "lack of a common benchmark" | Fixed binary output, no continual learning and no replay, so poisoned memory is never tested |
| P6 Fuhrman | Table II: up to 1.93× AVG / 2.64× FwdTrans vs LwF on CICIDS2017; PR-AUC (Fig. 5) | p.3: thresholds chosen with Best-F | Best-F uses labelled test data to pick thresholds, which inflates reported scores; no poisoning test |
| P7 Sameera | §5.4.1: clean F1 89.791% (Darknet) / 94.184% (IDS2018); up to 70% target-recall gain | §6.2 + Table 9 pp.20–21: needs ≥ 90% auxiliary data on CSE-CIC-IDS2018 to detect malicious models | Relies on a large trusted server dataset; a new, not-yet-seen attack family could look "malicious" and be rejected |
| P8 Cerasuolo | Table 7: TON-IoT BiC all/old/new F1 95.30/96.47/85.89%; benchmarks FT, replay, LwF, EWC (p.4) | §7 p.20: future work on generalisation and traffic shift | Centralised and clean; its perturbation tests are at inference time, not training-data poisoning |
| P9 Guo | Table 6: CICIDS2017 AA 83.4 / F1 82.1; Table 12: without DP-Means memory, F1 = 76.4 | §5 p.22: "As our method relies on pseudo-labeling and memory replay, it may be vulnerable to adversarial attacks that exploit these mechanisms" | 5,000-sample memory; selects uncertain/outlier samples, which is exactly what poison looks like |
| P10 Latif (AMM-HFL) | 50 clients, IDSIoT2024, MLP; with 30% malicious clients (noise model-poisoning + label-manipulation backdoor that relabels malicious traffic as Normal): 96.83% IID / 95.92% non-IID accuracy (p.12) | Conclusion p.17: extending to "real-time streaming data and evolving attack patterns" is future work | Static class set; accuracy only, no repeated runs. Its own results show the defence hurting rare classes: *Injection* misclassified as Normal under non-IID (p.12), and Krum "frequently misidentifies highly specialized, legitimate" clients (p.15) |

### 2.3 Fix W3: full comparison table (rubric format)

**Strategy:** one table with the rubric's exact columns: **# · Title · Year · Dataset · Preprocessing · Models/Techniques · Evaluation Metrics · Results · Limitations/Research Gap**. Include **all** new papers (9 rows if W1 is fixed). Typeset landscape, split into two tables (rows 1–5, 6–9) to stay readable. The audit file (`docs/papers/phase2-selection-audit.md`, lines 78–98) already has nearly all cell content; rewrite it in our own words, because the rubric forbids copying sentences.

Make the differences visible: end each Limitations cell with **what it means for our study** (e.g. P5: "→ we add class expansion + replay").

### 2.4 Fix W7: new subsection "Common research patterns"

Replace the current §2.2 paragraphs with patterns counted across P1–P10:

| Pattern | Evidence | Implication for us |
|---|---|---|
| Public benchmark CSV/flow datasets dominate | CICIDS2017: P6, P9 · CSE-CIC-IDS2018: P5, P7 · UNSW-NB15: P5, P6, P9 · TON_IoT: P2, P4, P8, P9 · IDSIoT2024: P10 · only P3 is synthetic | CICIDS2017 is a standard, comparable choice; CICIoT2023 (P10) is a sensible external check |
| Federated clients are simulated by splitting one dataset | Dirichlet: P2, P7 (pp.12–13) · fixed 2/5 clients: P4 · 10 clients: P5 · 50 clients in 5 edge groups: P10 | Our 5-client Dirichlet(0.5) is standard, but we must call it a simulation (P5 §6.2 says so too) |
| Retention relies on replay + distillation | P2, P4, P8, P9 (replay/exemplars + distillation); P8 also EWC | Justifies FT vs EWC vs DER++ as our learner set |
| Small MLP/CNN backbones | P5: MLP, 2 hidden layers of 128 (pp.9–10); P4/P8: packet CNN | Our 128/64 MLP matches P5's scale for flow features |
| Metrics separate old vs new classes | P4, P8: old/new/all F1 · P2, P9: forgetting/BWT · P5: attack success · P7: target-class recall | Supports our split into acquisition (new) vs retention (old) vs attack-damage metrics |
| **Threat model is either "clean CL" or "static FL poisoning", never both** | Clean CL: P1, P2, P4, P6, P8, P9 · Poisoning without CL: P5, P7, P10 | **This is the core gap** (feeds G1) |
| Defences need trusted information | P7: server auxiliary data (≥ 90%) · P10: edge similarity clustering (no trusted data, but outvotes rare classes) | Our admission rule should use only local data; matched controls are needed |

### 2.5 Fix W6: quartiles

**Strategy:** use **SJR 2025** for both phases (Phase 1 already uses it, and it is free to check at scimagojr.com). For each journal state **category + quartile + SJR year**, with no hedging. Mark DAC as "peer-reviewed conference (allowed by the Phase 2 rubric)". Delete "primary profiles remain unverified" and the "Quartiles require the primary-profile check" caption.
⚠ Needs a quick manual check on scimagojr.com for TNSM, Computers & Security, JISA, Computer Networks, Future Internet, Sensors and any added journal.

---

## 3. Deliverable 2: Refined Research Gap

### 3.1 Fix W5: rebuild the gap matrix with stronger evidence

Keep the rubric layout (**Gap · Evidence from Paper A · B · C · Proposed opportunity**) but use the authors' own words wherever possible:

| Gap | Evidence A | Evidence B | Evidence C | Proposed opportunity |
|---|---|---|---|---|
| **G1 — Poisoning is never tested where continual learning happens.** Continual IDS assume clean labels; poisoning studies assume a fixed model. | P2 §3.1: honest server and clients assumed; malicious clients "outside the scope" (Phase 1) | P5: 10,670 poisoning runs, but on a fixed binary model with no new classes or replay | P9 §5 p.22: replay/pseudo-label method "may be vulnerable to adversarial attacks that exploit these mechanisms" | Measure source-family damage when poison arrives mid-sequence, and whether it persists after the attacker leaves (E2 → E3/E4), for FT, EWC and DER++ |
| **G2 — Defences can reject honest new attacks along with poison.** | P7 §6.2/Table 9: needs ≥ 90% trusted auxiliary data, and an unseen family can look malicious | P10 pp.12, 15: its clustering defence misclassifies the rare *Injection* class as Normal under non-IID, and Krum "frequently misidentifies highly specialized, legitimate" clients | P4 §VI p.15: FCIL already struggles to integrate new attacks, so any rejection makes this worse | Compare class-aware admission (DC) with matched-volume global admission (DM); report new-family F1 **and** attack damage together |
| **G3 — It is unclear which mechanism (memory, selection, update rule) causes damage, and at what cost.** | P9 Table 12: removing DP-Means memory drops F1 82.1 → 76.4, so memory choice matters, but only clean data was tested | P8: memory-size and EWC/replay comparisons are clean and centralised | P6 p.3: Best-F uses test labels, mixing calibration with evaluation | Ablations on eviction rule, DER++ terms and keep-fraction under equal memory; measure poison in memory, time and bytes |

### 3.2 Fix W4: rewrite §3.2 to answer the six rubric questions

Use the six questions as bold run-in headings (about 1 paragraph each, ~350 words in total):

1. **What has already been done?** Clean FCIL for IDS (P2, P4); clean centralised CIL benchmarks (P8, P9); novelty detection under drift (P6); label-flipping in static FL-IDS (P5); server-side poisoning defences (P7, P10).
2. **What approaches currently exist?** Replay + distillation + bias correction (P4, P8, P9); regularisation such as EWC (P8); gradient/score similarity defences (P5 §2.3, P7); similarity-clustering aggregation (P10).
3. **What are their limitations?** Quote: P2 honest-client assumption; P9 §5 vulnerability statement; P10 leaves adaptation to evolving attacks as future work (p.17); P7 trusted-data requirement; P5 caricatural heterogeneity.
4. **What remains insufficiently investigated?** (a) partial label poisoning *during* class acquisition; (b) persistence after withdrawal through replay memory; (c) the acquisition cost of defences.
5. **Why is this gap important?** Federated IDS learn from many organisations' labelling pipelines. One corrupted feed can teach the shared model that an attack is benign, and replay memory can keep that error alive after the attacker leaves. A defence that also blocks new attack families defeats the purpose of continual learning.
6. **How will our research address it?** Point to RQ1–RQ3 and the traceability table (current Table 5, kept).

### 3.3 Fix W13: Phase 1 → Phase 2 link table

| Phase 1 gap | Phase 2 status | Reason |
|---|---|---|
| Gap 1: old/synthetic data | **Narrowed**: CICIDS2017 + CICIoT2023 external check; synthetic RF dropped | Real public captures; modern IoT check |
| Gap 2: attacks on the adaptation mechanism | **Retained as the core** (G1, G2) | Directly answered by our poisoning protocol |
| Gap 3: no runtime/hardware cost | **Partly retained**: CPU time, memory bytes, update bytes; physical edge energy deferred | No edge hardware available |

---

## 4. Deliverable 3: Methodology, with literature justification (fixes W8, W10)

**Strategy:** keep all 12 steps and every technical decision. Add to each step (a) a 1–2 sentence plain-language lead ("What this step does") and (b) a "**Why / literature basis**" line. Map:

| Step | Design choice | Literature basis |
|---|---|---|
| 1 Input | Numeric flow features; IPs/ports/times excluded | P4 removes IP/ports (audit l.92); P5 uses common NetFlow features |
| 2 Data | CICIDS2017 primary; CICIoT2023 external | CICIDS2017 in P6, P9; CICIoT2023 is CIC's modern IoT successor dataset [27]; Engelen et al. [28] for known label defects |
| 3 Preprocessing | Session-grouped chronological split; scaler fitted on benign T0 only; dedup | P6's Best-F test leakage shows why calibration must avoid test data; P9 uses min–max (we keep it, train-only) |
| 4 Representation | Same features for all arms; labels are the only thing poisoned | P5 flips labels only (threat realism) |
| 5 Model | 128/64 MLP | P5: MLP, 2 × 128 hidden layers (pp.9–10) |
| 5 Learners | FT, EWC-style, DER++ | P8 benchmarks FT/replay/EWC (p.4); P2, P4, P9 use replay + distillation |
| 5 Federation | FedAvg, 5 clients, Dirichlet(0.5) | P4 uses 2 and 5 clients (p.1); P7 Dirichlet non-IID (pp.12–13); Hsu et al. [22] |
| 6 Baselines | **Expand to a table** (below) | — |
| 7 Attack | One malicious client, partial flips at 10/30/50% | P5 §5.4: one-in-ten attacker is weak, so we test dose; P10 and P11 test 5–30% malicious clients, but only with a fixed class set |
| 7 Withdrawal | E3/E4 contain no poison | Measures persistence, which none of P4–P10 test |
| 8 Metrics | Old/new F1, forgetting/BWT, ASR, benign false alarms | P4/P8 old/new F1; P2/P9 BWT; P5 attack success; P7 target recall |
| 9 Stats | 12 paired seeds, Wilcoxon + Holm | P5's 10,670-run sweep shows high variance across settings, so paired repeats are needed |
| 10 Ablation | Eviction, DER++ terms, keep-fraction | P9 Table 12 ablation style; P8 memory-size sweeps |
| 11 Errors | Failure taxonomy | P4 old/new gap; P6 threshold failure |
| 12 Output | Protocol + report | P5 §6.2 calls for a common benchmark for distributed IDS |

**Step 6 baseline table (replaces the current two-sentence §4.6):**

| Baseline | Full name | What it tests | Source |
|---|---|---|---|
| FT | Fine-tuning | Lower bound: no protection against forgetting | P8 |
| EI | EWC-style importance | Regularisation-based retention | P8; Kirkpatrick [16] |
| DR | DER++ replay, no filter | Replay-based retention, no defence | Buzzega [19]; P4/P9 replay |
| DG | DER++ + global 75% small-loss filter | Common unmatched filter | Co-teaching [13] |
| DM | DER++ + global filter, matched quota | Fair control for DC | — |
| DC | DER++ + class-aware quota (**proposed**) | Our heuristic | — |
| (optional) | Validation-gate / clustering aggregation / trust filter | Server-side defences from the literature | P7, P10, P11 |

---

## 5. Readability and clean-up (fixes W9, W11, W12, W14, W15)

| Action | Detail |
|---|---|
| Acronym box | A small "Key terms" table at the start of §4: FT, EI, DR, DG, DM, DC, T0, E1–E4, ASR, H, A, FAR, FCIL, CIL |
| Move to appendices | Table 6 (notation, 30 rows), Eqs. 17–19 (permutation/bootstrap detail), the "Resolution" paragraph, the memory-byte formula. Keep a 2–3 sentence summary in the main text |
| Rewrite dense sentences | e.g. "DC's honest-new admission is one by construction" → "Under DC, every honest example of a new attack family is always admitted, because new classes are exempt from filtering." |
| Table 11 | Replace `[MEASURE]` with an estimate (e.g. "~1–5 min/run on a 2-thread CPU") or drop the column; replace "GPU availability is to be confirmed" with a definite plan |
| Remove repo artefacts | Delete App. A "folder mapping"; change ref [1] to "Saneedullah & Bilal, Phase 1 report, 2026"; delete "Archived rows…", "author template year differs" |
| Figures | Add step badges (①–⑫) to Fig. 1/2 boxes |
| Abstract | 150–200 words, no statistics jargon |
| Date | Update the 8 Oct date to the actual submission date |

---

## 6. Execution order

| Order | Task | Fixes | Depends on | Effort |
|---|---|---|---|---|
| 1 | Find and verify 1–3 new papers (year, venue, SJR quartile, full text) | W1 | — | Medium |
| 2 | Verify SJR quartiles for all journals | W6 | — | Low |
| 3 | Write per-paper critical summaries | W2 | 1 | Medium |
| 4 | Build the full comparison table | W3 | 1, 3 | Medium |
| 5 | Write "Common research patterns" | W7 | 1 | Low |
| 6 | Rebuild the gap matrix + six-question justification + Phase 1 link table | W4, W5, W13 | 3 | Medium |
| 7 | Add plain-language leads + literature justification to Steps 1–12; baseline table | W8, W10 | 3 | Medium |
| 8 | Readability pass: acronym box, appendices, placeholders, repo artefacts, abstract, figure badges | W9, W11, W12, W14, W15 | 7 | Medium |
| 9 | Final check against the rubric (below) | all | 1–8 | Low |

### Rubric checklist (final self-check)

- [ ] 8–10 additional papers, all 2025–26, Q1/Q2 or conference, each with methodology + data + evaluation
- [ ] Cross-paper comparison table with all rubric columns, synthesised (not copied)
- [ ] ≥ 3 gaps with evidence from papers + proposed opportunity
- [ ] Gap justification answers all 6 questions
- [ ] Steps 1–12 present, each justified
- [ ] Methodology architecture diagram
- [ ] Deliverables 1–4 clearly labelled

---

## 7. Decisions needed from the authors

1. **Output format:** edit `phase2.tex` (compile on Overleaf; no LaTeX compiler on this PC), produce a Word `.docx`, or both.
2. **Which new papers** to add: approve candidates after verification.
3. **Ranking source:** confirm SJR (consistent with Phase 1) rather than JCR.
4. **How much statistical detail** to keep in the main text vs the appendix.
