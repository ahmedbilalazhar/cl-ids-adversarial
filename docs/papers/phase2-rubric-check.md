# Phase 2 Paper Rubric Check

**Date:** 20 Oct 2026 · **Checked against:** *Phase 02 – Extended Literature – Research Methodology* §1 "Paper Selection Requirements"
**Scope:** the 7 additional papers already in the repo (`docs/papers/paper-4` … `paper-10`) plus the 3 newly collected (`docs/papers/paper-11` … `paper-13`). Papers 1–3 are the Phase 1 papers and do **not** count toward the 8–10 additional papers.

## Result

| | Count |
|---|---|
| Additional papers before | 7 ❌ (below the 8 minimum) |
| Newly collected | 3 |
| **Additional papers now** | **10 ✅ (top of the 8–10 range)** |
| Papers with a risk flag | 1 (P6, conference paper; allowed by the rubric). **P10 (Prasad, CMES) was replaced on 20 Oct 2026** by a stronger 2026 journal paper (see §5) |

## 1. Rubric matrix: all 10 additional papers

Rubric criteria: **R1** published 2025–2026 · **R2** research article (not editorial/opinion/news) · **R3** Q1–Q2 journal, conference paper or book chapter · **R4** directly relevant to our topic · **R5** identifiable methodology / experimental setup · **R6** enough dataset, method and evaluation detail for critical analysis · **R7** reputable publisher (preferred).

| # | Paper (short) | R1 | R2 | R3 | R4 | R5 | R6 | R7 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| P4 | Carillo et al. — FCIL NIDS for IoT (IEEE TNSM) | ✅ 2026 | ✅ | ✅ Q1 | ✅ High: federated + class-incremental IDS | ✅ | ✅ | ✅ IEEE | Keep |
| P5 | Lavaur et al. — Label-flipping vs FL-IDS (Computers & Security) | ✅ 2025 | ✅ | ✅ Q1 | ✅ High: label poisoning in FL-IDS | ✅ | ✅ 10,670 runs | ✅ Elsevier | Keep |
| P6 | Fuhrman et al. — CND-IDS (ACM/IEEE DAC) | ✅ 2025 | ✅ | ✅ Conference paper (allowed by the Phase 2 rubric) | ✅ Medium: continual novelty IDS | ✅ | ⚠️ Short (7 pp.) but has data, method, metrics | ✅ ACM/IEEE | Keep; label as a conference paper |
| P7 | Sameera et al. — WeiDetect (JISA) | ✅ 2025 | ✅ | ✅ Q2 (JCR) | ✅ High: poisoning defence for FL-IDS | ✅ | ✅ | ✅ Elsevier | Keep |
| P8 | Cerasuolo et al. — CIL NIDS for IoT (Computer Networks) | ✅ 2025 | ✅ | ✅ Q1 | ✅ High: class-incremental IDS, EWC/replay | ✅ | ✅ | ✅ Elsevier | Keep |
| P9 | Guo et al. — CL for IDS (Future Internet) | ✅ 2025 | ✅ | ✅ Q2 (JCR) / Q1 (SJR) | ✅ High: replay memory selection | ✅ | ✅ | ✅ MDPI | Keep |
| P10 | **Latif & Djenouri — AMM-HFL (Sensors)**, *replaces* Prasad et al. (CMES) | ✅ 2026 | ✅ | ✅ Q2 (expected) | ✅ **High**: FL-IDS under model poisoning + label-manipulation backdoor | ✅ | ✅ | ✅ MDPI | **Replaced** (§5) |
| **P11** | **Banbhrani et al. — FLZT-IDS (Electronics)** | ✅ 2026 | ✅ | ✅ Q2 (expected) | ✅ **High** | ✅ | ✅ | ✅ MDPI | **Add** |
| **P12** | **Abhijit et al. — FL + transfer learning for rare attack classes (Scientific Reports)** | ✅ 2025 | ✅ | ✅ Q1 (expected) | ✅ **High** | ✅ | ✅ | ✅ Nature Portfolio | **Add** |
| **P13** | **Nguyen & Park — EL-GNN (Electronics)** | ✅ 2025 | ✅ | ✅ Q2 (expected) | ✅ **Medium–High** | ✅ | ✅ | ✅ MDPI | **Add** |

⚠️ **Quartile confirmation still needed.** SCImago (scimagojr.com) and ScienceDirect block automated access with a bot check. Before submission, look up *Electronics*, *Scientific Reports* and *Sensors* on scimagojr.com (use SJR, as Phase 1 did) and write the category + quartile into Table 1 of the report.

Other notes:
- P4–P8 are **author manuscripts** of the published articles (green open access). Cite the journal version (DOI, volume, year) and not the manuscript header (e.g. P4's template says "XXXX 2025", but the published year is 2026).
- P6 is a conference paper. The Phase 2 rubric allows these (Phase 1 did not), but label it clearly as one.

## 2. How the 3 new papers were selected

1. **Search:** Crossref bibliographic search, restricted to journal articles published 2025-01-01 to 2026-12-31. Queries: *federated continual learning intrusion detection*; *federated incremental learning intrusion detection IoT*; *poisoning attack federated intrusion detection defense*; *continual learning network intrusion detection catastrophic forgetting*; *label flipping intrusion detection federated*; *class incremental intrusion detection replay*. About 75 hits were kept after title filtering.
2. **Full-text access:** Unpaywall API. Closed-access papers were rejected, because R6 needs the full text. Publishers that block automated download (ScienceDirect, IEEE Xplore) were also set aside.
3. **Relevance and quality:** abstracts and then full texts were read; each paper had to add new evidence to one of our gaps G1–G3.

**Strong but not collected** (relevant, but we could not get the full text; they could replace a paper if you download them manually):

| Paper | Why not |
|---|---|
| FedPromptZero — *Internet of Things* 2026, [10.1016/j.iot.2026.102122](https://doi.org/10.1016/j.iot.2026.102122) | Open access, but ScienceDirect shows a CAPTCHA to automation |
| FedDBC — *Computer Networks* 2026, [10.1016/j.comnet.2026.112497](https://doi.org/10.1016/j.comnet.2026.112497) | Same |
| Delgado et al. — *Applied Soft Computing* 2026, [10.1016/j.asoc.2026.116022](https://doi.org/10.1016/j.asoc.2026.116022) | Same |
| Drift-Aware Federated Continual Learning — *IEEE Access* 2026, [10.1109/ACCESS.2026.3732173](https://doi.org/10.1109/ACCESS.2026.3732173) | IEEE Xplore blocks automation (error 418); also Android malware rather than network flows |
| XDFC-IDS — *ESWA* 2026 | Closed access |
| arXiv 2608.04602 (replay-buffer poisoning in continual IDS) | Not peer-reviewed; cite only as background |

**Rejected after reading the full text:** DS-FedIDS (Youm & Kim, *Applied Sciences* 2025; screened out; not added to the repo). It is formally eligible, but its dataset is a synthetic UNSW-NB15 derivative that is not shared (§3.3, p.6). It reports only accuracy, from a single run with no repeats (§3.8), and its comparison table uses one federated round (Table 5, p.13). It also names classes "Theft" and "R2L" (p.10), which do not exist in UNSW-NB15. This would not survive the "allow critical analysis" test.

## 3. The 3 new papers: critical summaries (ready for Deliverable 1)

All page numbers are **PDF pages** (`### PDF page N` in `paper-N.md` = `assets/page-00N.png`).

### P11 — FLZT-IDS: Trust-Aware Federated Learning for Privacy-Preserving IoT Intrusion Detection
*Banbhrani, Wei, Asad. Electronics 15(20):4584, 2026. https://doi.org/10.3390/electronics15204584*

- **Problem:** federated IDS must resist malicious clients, protect shared updates and limit communication.
- **Method:** GNN + attention BiLSTM detector (binary benign/attack, pp.11–12). Each client gets a **dynamic trust score** (recent activity, protocol compliance, anomaly confidence); clients with τ ≤ 0.6 are excluded, and gradient-deviation screening runs before aggregation (§3.5.3, p.13; Algorithm 1, p.14). Updates are protected with local differential privacy + homomorphic secure aggregation, and sent only when the change exceeds a threshold.
- **Data and setup:** **CICIDS2017** and Edge-IIoTset. Session-grouped 80/10/10 split; min–max fitted on train only; **10 clients, Dirichlet α = 0.5**; SMOTE inside each client after partitioning; 100 rounds, 2 clients sampled per round; single seed 42 (§4.1–4.2, pp.16–17).
- **Results:** 97.8% accuracy / 97.8% F1 on CICIDS2017 (Table 6, p.19). Under **sign-flipping model poisoning** with 30% malicious clients: 89.3% vs 72.3% for plain FL-IDS (§5.4, pp.21–22). At the chosen trust threshold, **4.6% of benign clients were wrongly excluded** on CICIDS2017 (5.1% on Edge-IIoTset) (§5.5, p.22).
- **Author-stated limitations (§6.2, p.24):** fixed simulated clients; trust uses predefined indicators; poisoning evaluation is limited to one scenario and 10 clients, so it is "not … a general guarantee"; no comparison with Krum, Trimmed-Mean or FLTrust.
- **Our critique:** binary output and a **static class set**, so it never tests whether trust filtering rejects an honest client that has just seen a *new* attack family. Only *untargeted model* poisoning is tested, not *targeted label* poisoning. Single seed, no repeated runs or significance tests.
- **Relevance:** the strongest new evidence for **G2**. A modern defence already wrongly excludes ~5% of honest clients on a fixed class set, and this cost is likely to grow when honest clients carry new-family data. It also validates our design choices: CICIDS2017, Dirichlet(0.5), session-grouped splits and a train-only scaler.

### P12 — Federated transfer learning for rare attack class detection in NIDS
*Abhijit, Jerusha, Syed Ibrahim, Varadharajan. Scientific Reports 15:33797, 2025. https://doi.org/10.1038/s41598-025-02068-x*

- **Problem:** in federated IDS, rare and unseen (zero-day) attack classes are missed, because they are scarce and unevenly spread across clients.
- **Method:** personalized FL (shared layers aggregated; class-specific last layer stays local). **New-class detection**: a client flags a "new class" when per-class precision changes by more than a threshold every N = 3 rounds, then **sends that class's data, encrypted, to the server** (pp.9–10, 12). The server keeps per-class exemplars and mean embeddings, labels a sample as a new class if its distance exceeds a threshold, and retrains the global model by transfer learning (Algorithm 2, p.9).
- **Data and setup:** CSE-CIC-IDS2018, UNSW-NB15, Edge-IIoT. Min–max scaling, NaN removal, correlation-based feature selection (p.11). Small dense networks (23→20→10→5→softmax, Table 4). 4 clients (6 for Edge-IIoT), with attack types deliberately withheld from some clients (p.12). Single CPU laptop.
- **Results:** accuracy 98.90% (IDS2018), 98.70% (UNSW-NB15), 97.92% (Edge-IIoT). Rare classes improve sharply, e.g. DDoS-HOIC F1 0 → 98.08% (p.12). The baseline comparison (mislabelled "ablation", Tables 9–11, pp.15–18) puts FedAvg F1 at only 68.50% on IDS2018, despite 98.57% accuracy.
- **Author-stated limitations / future work (p.20):** privacy of the split/personalized design needs stronger encryption or differential privacy; aggregation via embeddings could be explored.
- **Our critique:** **honest clients are assumed throughout.** The new-class trigger (a client-reported performance drop plus client-uploaded class data) is an obvious **poisoning entry point**: a malicious client could fake a "new class" or upload mislabelled data that the server learns from. Uploading raw class data to the server partly defeats FL's privacy goal. Reported numbers are inconsistent: the UNSW-NB15 F1/precision/recall values are swapped between the list items on p.17. There are no repeated runs or variance.
- **Relevance:** the main new evidence for **G1**. It shows federated IDS *already* acquire new and rare classes at the server, with no adversary in the threat model. It also motivates our class-aware admission: rare and new classes need protection (P12's whole point), but that same protection is what an attacker can abuse.

### P13 — EL-GNN: Continual-Learning GNN for Task-Incremental IDS
*Nguyen, Park. Electronics 14(14):2756, 2025. https://doi.org/10.3390/electronics14142756*

- **Problem:** GNN-based IDS forget earlier attacks when retrained on new ones (catastrophic forgetting).
- **Method:** GCN over flow graphs (nodes = flows, edges built from shared source/destination **IP addresses**, p.29). Continual learning uses **EWC**: a Fisher-information penalty with tunable λ added to a binary cross-entropy loss (Algorithm and Eq. 9, pp.16–17). No replay ("we do not revisit old data", p.24).
- **Data and setup:** **CICIDS2017** (Task A) followed by UNSW-NB15 (Task B), i.e. **two tasks**, both binary (§5.2, pp.17–19). Pearson-correlation feature selection; label encoding. Compared with PAPA, SPIDER, EWC, MAS, ECBRS, GEM and GNN IDS models (Tables 6–7, pp.27–28).
- **Results:** single-task accuracy 96.72% (CICIDS2017) / 98.44% (UNSW-NB15) (p.23). After sequential training, other GNNs collapse (FN-GNN 94.9% → 49.9%; E-GraphSAGE 95.2% → 55.2%), while EL-GNN reaches about 85% incremental accuracy (p.24; Table 7, p.28).
- **Author-stated limitations (pp.20, 29):** only two datasets as tasks; future work will add more datasets or real-world streams and evolving threat patterns.
- **Our critique:** only two coarse "tasks" (dataset-incremental, binary), so it is not *class*-incremental and never shows how a new attack family is learned. **Headline numbers disagree across the paper:** 99.76/98.65% (p.21), 96.72/98.44% (p.23) and 95.9/96.4% (p.29); incremental 84.5% (Table 7) vs 85.7% (p.29). Graph edges use IP addresses, which can let the model recognise the testbed's specific hosts rather than attack behaviour (our methodology deliberately excludes IPs and ports). Clean data only; no poisoning.
- **Relevance:** supports our **learner choice** (EWC as a standard continual-learning IDS baseline, alongside P8) and **G1**: even EWC-based continual IDS are evaluated only on clean, honest data. It also gives a concrete example for our preprocessing rule against identifier leakage (Step 3).

## 4. What changes in the Phase 2 report

| Section | Change |
|---|---|
| §2.1 Table 1 | 7 → 10 rows; add P11–P13 with venue, year, SJR category/quartile and open-access status |
| §2.2 Taxonomy | Add 3 rows. P11: FL, model poisoning, trust filtering, no memory. P12: personalized FL, honest clients, new-class detection, server exemplars. P13: centralized task-incremental, clean, EWC, no replay |
| §2.3 Comparison table | Include all 10 papers (see `submissions/review-phase2/phase2-improvement-plan.md` §2.3) |
| Gap matrix (Table 4) | **G1** add P12 (new classes learned with honest clients assumed) and P13 (EWC continual IDS on clean data only). **G2** add P11 (trust filter wrongly excludes 4.6–5.1% of benign clients on a fixed class set) |
| Common patterns | CICIDS2017 now appears in P6, P9, P11, P13 (plus our study); Dirichlet(0.5) in P11 (plus P7); EWC in P8, P13 |
| References | Add the 3 DOIs above |

## 5. Replacement of P10 (20 Oct 2026)

**Why the old P10 was replaced.** Prasad et al. (*CMES*, Tech Science Press, 2026) passes the hard rules: JCR 2024 Q2 in "Engineering, Multidisciplinary" (Q1 in "Mathematics, Interdisciplinary Applications"). It was still the weakest of the ten: its quartile comes only from a category outside computer science, the publisher is less established (the rubric prefers "reputable" publishers), and the study is binary-only, using linear streaming models. It is archived, not deleted, at `docs/papers/_archive/2026-10-20-rubric-replacement/prasad-cmes/`.

### New P10 — AMM-HFL: Adaptive Multi-Model Hierarchical Federated Learning for Robust IoT Intrusion Detection
*Latif, Djenouri. Sensors 26(10):3198, 2026 (published 19 May 2026). https://doi.org/10.3390/s26103198 · open access, CC BY 4.0 · 20 pp. · SHA-256 `9a19a7b57fc7b43cd336dd0e5028122844abeb200126600a9d3b587c9da0e3ee`*

- **Problem:** single-model FedAvg fails under extreme non-IID data and malicious clients in IoT intrusion detection.
- **Method:** three tiers (client → edge → cloud). Edge servers cluster client updates by cosine similarity to isolate anomalous contributions. The cloud keeps **multiple global models** (meta-aggregation), and each client picks the model with the lowest local loss. Updates are encrypted in transit (pp.7–10).
- **Data and setup:** IDSIoT2024 (multi-class: DoS, MITM, Malware, Routing, Injection, Normal …); MLP; standard scaling, label encoding, class weights; **50 clients in 5 edge groups**; 50 rounds × 3 local epochs; IID vs extreme non-IID (≤ 3 classes per client) (§4.1, pp.9–11).
- **Threat model:** 5%, 15% or 30% malicious clients, each attacking with probability 0.3 per round. Two attacks: **(a)** Gaussian-noise model poisoning and **(b)** a stealthy **label-manipulation backdoor "forcing the model to misclassify specific malicious traffic as normal"** (pp.10–11; Table 1).
- **Results:** at 30% malicious clients, 96.83% (IID) and 95.92% (non-IID) accuracy (p.12). It beats FedAvg, Krum and Trimmed-Mean under non-IID + 30% malicious (§4.6, p.15). Client training takes about 1.2 s per round (p.13).
- **Author-stated limitation / future work (p.17):** extend the framework to "real-time streaming data and evolving attack patterns", i.e. it is **not continual** yet.
- **Our critique:** static class set; accuracy-centred reporting with no repeated runs or significance tests. Its own results show **the defence harming legitimate rare evidence**: under non-IID, the rare *Injection* class is "occasionally being misclassified as Normal" because aggregation "outvotes specialized clusters when a specific attack pattern is extremely rare" (p.12). It also reports that Krum "frequently misidentifies highly specialized, legitimate" clients (p.15).
- **Relevance:** the closest threat model among the new papers (targeted relabelling of attack traffic as Normal, like our Hulk→benign E2 poisoning). It is direct evidence for **G2** (defences sacrifice rare/new legitimate classes) and, through its future-work statement, for **G1** (no continual adaptation under poisoning).
