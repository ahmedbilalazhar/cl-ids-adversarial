# Search Protocol — Reproducible Novelty Check

Run every query on **Google Scholar**, **IEEE Xplore**, **Scopus**, and the **arXiv API**.  
Record for each: date run, database, number of hits, how many judged relevant.  
This table is the evidence base for any "first" / "nobody has done X" claim in the paper.

**arXiv API form:** `http://export.arxiv.org/api/query?search_query=...`

**Hedging rule:** if any hit threatens Option 2-A (discovery-stage poisoning), cite it and narrow the contribution statement in `docs/proposal.md` §3 before submission.

---

## Query strings

| # | Query | Date run | DB | Hits | Relevant | Notes |
|---|-------|----------|-----|------|----------|-------|
| 1 | `"continual learning" AND "intrusion detection"` | 2026-09-24 | websearch (top-10) | 10 shown | 9 | Field crowded: SOUL, CND-IDS, ACORN, SPIDER, RepShield, ExBCIL, MDPI'25, NeurIPS'23 CBRS/PAPA — none adversarially evaluate a discovery stage |
| 2 | `"class-incremental" AND ("IDS" OR "intrusion detection")` | 2026-09-24 | websearch (top-10) | 10 shown | 8 | Cerasuolo CIL IoT (comnet'25), hierarchical BNN+QDA, FSCIL edge, few-shot CIL, IL-IDS — closed-world CIL, no poisoning eval |
| 3 | `"continual learning" AND ("poisoning" OR "backdoor" OR "adversarial")` | 2026-09-24 | websearch (top-10) | 10 shown | 9 | USENIX'25 persistent backdoor, BrainWash, PACOL, false-memory (Umer), Li&Ditzler task-targeted, backdoor-on-IL survey (2305.18384), Amnesia — all generic CL / image domain |
| 4 | `("novelty detection" OR "open-world" OR "unknown attack") AND "poisoning"` | 2026-09-24 | websearch (top-10) | 10 shown | 5 | ACORN, CND-IDS, OWCL (2304.10038), SOUL, COUQ — build ND, do not attack it; METANOIA mentions poisoning only in discussion |
| 5 | `"federated" AND "continual learning" AND "poisoning"` | 2026-09-24 | websearch (top-10) | 10 shown | 6 | FL-IDS poisoning defenses, GFCL IoV, PCAP-Backdoor, Fed-CLIDS, 2303.02622 multi-agent CL — Option 2-B territory |
| 6 | `"replay buffer" AND ("poisoning" OR "backdoor" OR "manipulation")` | 2026-09-24 | websearch (top-10) | 10 shown | 7 | Amnesia (2606.12655) sampler-level replay attack; 2602.13062 replay-amplified CCL backdoors; 2606.14987 — buffer well covered; *discovery* stage still open |
| 7 | `"concept drift" AND ("adversarial" OR "poisoning") AND "intrusion detection"` | 2026-09-24 | websearch (top-10) | 10 shown | 7 | Adversarial concept drift (PMC9162121), Apruzzese AISec'24 drift×perturbation, retraining-vs-backdoor, 2608.04602 — drift≠discovery poisoning |
| 8 | `"CICIDS2017" AND ("limitations" OR "pitfalls" OR "data quality")` | 2026-09-24 | websearch (top-10) | 10 shown | 8 | Liu CNS'22 error prevalence, Engelen SPW'21 (>25% artefact flows), Dube'23, Rosay, 2401.16843 — confirms Gap 1 strongly |
| 9 | `"autoencoder" AND "clustering" AND ("poisoning" OR "adversarial") AND "intrusion detection"` | 2026-09-24 | websearch (top-10) | 10 shown | 4 | **Sonic** (Inf. Sci. 2026) poisons HDBSCAN; AE poisoning on ICS (2002.02741); PANDA-style AE *evasion*; NAD contamination — components exist, **no paper combines them as continual-IDS discovery-stage attack** |
| 10 | `"novelty discovery" AND ("continual" OR "incremental") AND ("attack" OR "adversarial" OR "poison")` | 2026-09-24 | websearch (top-10) | 10 shown | 3 | OWL review, dynamic cluster novelty (no adversary), i-DarkVec — **no hit** on adversarial poisoning of a continual novelty-discovery stage |

Hits column = top-N returned by the search backend (not full DB totals); IEEE/Scopus exact counts still require manual runs per §"How to fill".

## 2026-09-26 arXiv-API pass (exact queries, real hit counts — Phase 1 step 5)

| # | Query (arXiv API `search_query`) | Date run | DB | Hits | Relevant | Notes |
|---|-------|----------|-----|------|----------|-------|
| 11 | `all:"federated class-incremental" AND all:intrusion` | 2026-09-26 | arXiv API | 0 | 0 | Exact-phrase intersection empty |
| 12 | `all:federated AND all:"class-incremental" AND all:"intrusion detection"` | 2026-09-26 | arXiv API | 1 | 1 | Korba et al. 2407.15700 (life-long FL IDS, 6G IoV) — claims first CIL×FL for attack detection; NO poisoning eval |
| 13 | `all:"continual learning" AND all:"intrusion detection" AND (all:poisoning OR all:backdoor OR all:adversarial)` | 2026-09-26 | arXiv API | 2 | 1 | 2608.04602 (VERIFIED real entry; our H1 target, numbers match lore) + 1812.00622 (irrelevant UEBA) |
| 14 | `all:"novelty detection" AND all:poisoning` | 2026-09-26 | arXiv API | 3 | 0 | Web3-FL validation (2606.13180, 2312.05459) + DP theory (1911.07116) — none attacks a continual-IDS discovery stage |
| 15 | `all:"replay buffer" AND (all:poisoning OR all:backdoor) AND all:"continual learning"` | 2026-09-26 | arXiv API | 2 | 2 | 2608.04602 + 2606.14987 (continual backdoor IoT/CPS) — neither federated nor discovery-stage |
| 16 | Su-2025 verification (`au:Su_Chunhua AND all:federated` → miss; title-word hunt → hit) | 2026-09-26 | arXiv API + indexed-record search | 1 | 1 | "Evolutionary Replay-Driven Federated Class-Incremental Learning for Cyber-attack Detection", Junyan Su, 2025 — limitations section VERBATIM: honest clients+server assumed, IID assumed, future work = "federated learning poisoning and non-IID client data". Content-verified; publisher/DOI page still outstanding |

## Scholar / Xplore / Scopus status (honest)

Paywalled/CAPTCHA'd databases cannot be queried from this environment. Websearch proxies (site-scoped) were run 2026-09-24/26 covering the same 10 query intents; manual in-browser runs with exact counts remain OUTSTANDING debt (owner: student, ~30 min, run-book in §"How to fill"). No "first" claim enters the paper until those counts are filled.

---

## Known neighbours (pre-verified — must be cited and distinguished)

| ID | What it does | Why not the same as us |
|----|--------------|------------------------|
| arXiv:2608.04602 | Replay-buffer label-flip + backdoor on CICIDS2017, CII scenario | Single-node *buffer*, not open-world *discovery* stage |
| arXiv:2409.13864 | Persistent backdoors in CL (USENIX S&P 2025) | Generic CL, not IDS discovery pipeline |
| arXiv:2609.06346 | CLUBA defence under backdoor in CL | Defence, not discovery-stage attack |
| arXiv:2602.13062 | Backdoors on contrastive CL for IoT | Embedding-level, not AE+HDBSCAN discovery |
| arXiv:2606.14987 | Continual backdoor training IoT/CPS (CIC-IDS-2018) | Anomaly detector SI-regularised, not discovery pipeline |
| Pawlak et al. PMLR v330 (2026) | Single-task poisoning exemplar-free CL | Exemplar-free; image domain |
| arXiv:2502.14094 (CND-IDS) | Continual novelty detection for IDS | Builds ND; no adversarial evaluation of ND stage |
| arXiv:2602.07291 (ACORN-IDS) | Adaptive continual novelty detection | Same — no adversary |
| arXiv:2205.11736 | Federated backdoor defense under continuous training | Federated; leakage defence, not discovery |
| arXiv:2501.00438 (METANOIA) | Incremental provenance IDS avoids learning malice | Graph/provenance, not flow AE+clustering |
| arXiv:2606.12655 (Amnesia) | Replay *sampler* composition attack on ER/DER++ | Manipulates buffer indices; not AE+clustering discovery |
| Sonic, Inf. Sci. 2026 (doi:10.1016/j.ins.2026.123140) | Genetic poisoning of HDBSCAN/FISHDBC clustering | Clustering-only; no continual IDS / novelty pipeline — **must cite as nearest tool-level threat to Option 2-A** |
| arXiv:2002.02741 | Poisoning online-trained AE anomaly detectors (ICS) | AE poisoning exists, but no clustering/discovery or CL setting |
| Su 2025 (Junyan Su; content-verified 2026-09-26, publisher page outstanding) | Evolutionary replay-driven federated CIL cyber-attack detection; honest clients+server, IID; poisoning + non-IID = future work | **Our gap license #1** — we answer the quoted call directly (verify publisher page before citing) |
| Wu et al. 2026 / EdgeFedCIL, Sensors 26:4630 (read in full) | Federated CIL IDS + compression; honest server/clients assumed (§3.1), poisoning/backdoor explicitly out of scope | **Our gap license #2** — poisoning × FCIL-IDS deferred by the closest system |
| Korba et al., arXiv:2407.15700 | Life-long (CIL×FL) IDS for 6G IoV | No poisoning/adversarial eval; we add the attacker |
| Jin et al. 2023, IEEE Network (EIDS) | Federated incremental + open-set DAE zero-day IDS | No poisoning eval; discovery is DAE-threshold, not AE+HDBSCAN pipeline |
| Cerasuolo et al. 2025 (network-agnostic CIL NIDS) | Cross-dataset CIL NIDS; names federated + poisoning-robustness as future work | Single-node CIL; supports our gap from a third angle |
| Lavaur et al., Comput. Secur. 2025, 156:104462 | Systematic label-flip × static-FL IDS | Static FL, no continual dimension — target-venue adjacent work we extend |
| BRFID, arXiv:2609.28599 | Single-Byzantine label-flip on CICIDS2017 FL IDS (ensemble aggregation) | Static FL, no CL, non-FedAvg aggregation — cite + distinguish |
| TSK-FedIDS 2026 / FedSecure 2026 / WeiDetect 2025 / Nowroozi 2025 | FL-IDS poisoning attacks/defences (CIC/UNSW/CICIoT2023) | All static FL; none continual — crowded flank, open continual dimension |

---

## How to fill the table

1. Copy each query exactly into each database on a single recorded date.
2. Count total hits and hits judged relevant after reading title+abstract (threshold: addresses poisoning/backdoor/adversarial evaluation **of** a continual/novelty IDS mechanism, not merely "uses ML for IDS").
3. Save result export (BibTeX/CSV) into `docs/search_exports/` (create folder).
4. If #4 or #9 or #10 returns any paper that attacks an autoencoder+clustering novelty-discovery pipeline in a continual IDS: stop, read in full, re-scope contribution statement.
