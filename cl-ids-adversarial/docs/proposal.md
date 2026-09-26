# Proposal — Poisoning of Federated Class-Incremental Network Intrusion Detection

**Students:** Saneedullah (23I-2568), Ahmed Bilal (23I-2581)  
**Status:** post-audit revision for supervisor sign-off · primary result F2
(federated finetune vs EWC vs DER++ × 0/1/5/10%, n=7) + centralized ablation
+ one defense (small-loss) + E5/E7 complete; full numbers in
`docs/results_overview.md` · pre-fix drafts archived, never cited  
**Date:** 26 September 2026

---

## 1. Research question

**Primary RQ (federated poisoning of a class-incremental IDS):**

> When a class-incremental IDS is trained federated across network segments
> with one malicious client, which continual-learning method (naive
> fine-tuning vs. EWC vs. DER++) best retains past attack knowledge under
> data poisoning — and does a lightweight small-loss filter recover the loss?

**Secondary RQ (discovery-stage attacks — related but distinct threat model):**

> Can stream poisoning manipulate the novelty-detection-and-clustering stage
> (AE threshold → HDBSCAN) into manufacturing fictitious attack classes? This
> tests unknown-class DISCOVERY (Paper 1's domain), explicitly NOT spoofing
> drift against a fixed re-authenticated identity set (Paper 3's
> RF-fingerprint domain) — the two are separated everywhere, and the
> drift-authentication system is scoped out (see §10).

---

## 2. Hypotheses (pre-registered)

- **H1 (as originally pre-registered, now reported as NOT reproduced)** — A replay-based class-incremental IDS loses most clean accuracy under label-flipping poisoning of its memory at budgets ≤ 1%, reproducing the single-node finding of arXiv:2608.04602 (collapse to 0.0053 accuracy at a 1% poison budget on CICIDS2017). **Observed (n=7):** under our stream and buffer protocols, targeted 1% flipping gives ACC 0.317 ± 0.028 vs clean ER 0.336 ± 0.027 (Wilcoxon **p=0.031** — the drop is statistically real but *small*, not a collapse; random 0.5% is worse: 0.278). Their figure is tied to their specific buffer-poisoning setup — we report H1 as a *partial/non-reproduction* and compare protocols explicitly (`results_overview.md` E2, `docs/threat_model.md` budget section). Pre-committed fallback: this is a protocol-comparison finding, not a project failure.
- **H2 (restated after nopois control + anchor-variant attack, n=7)** — Poisoning the *novelty-discovery* stage (benign-only AE → threshold → HDBSCAN) is more dangerous per unit of attacker effort than poisoning the classifier: crafted "novel" samples (a) create fictitious discovered classes that absorb future benign traffic or real attack families, or (b) suppress discovery of a real attack family. **Observed:** (b) *closed by design* — with a benign-only AE and a threshold fit on clean scores before poisoning, stream poison cannot move the threshold; discovery miss rate (~0.64) is identical across all four configs. (a) *reachable*: `n_fictitious` = 5–12 vs 0 (nopois), benign absorption up to 1.0%, and — with poison **anchored to the attack manifold** (`mode: anchor`) — **14% of novel real attacks are absorbed into poison-dominated fictitious clusters** (0% for recon-max poison; 0 for nopois), at a significant classifier cost (ACC 0.275 vs nopois 0.307, **p=0.047**). **Restated claim:** *low-budget novelty poisoning cannot suppress which attacks are detected under benign-only discovery, but can misfile detected attacks and benign traffic into manufactured classes; attack-manifold anchoring raises attack absorption from 0 to ~14% at ρ=1%.*
- **H3 (now tested with two defences, n=7)** — At least one defence that works against classifier poisoning (small-loss buffer purification, gradient auditing, or frequency filtering) performs worse in the continual setting because the drift it must distinguish from poisoning is legitimate. Quantifying this "drift vs. poison" confusion is a contribution in itself. **Observed:** small-loss helps under attack (ACC 0.317→0.367, forgetting 0.672→0.550, **p=0.016**) but retains some flipped samples (ASR 7e-5→0.031). A **kNN label-consistency filter** — a static label-noise detector — *hurts*: ACC 0.278 vs undefended 0.317 (**p=0.047**), with **zero benefit** (ASR unchanged), because it discards legitimate rare/new-class samples (Heartbleed and Infiltration retention **0%** on clean, unpoisoned streams). Drift looks like poison; the confusion is real and quantified.

**Fallback if H2 is rejected:** "the discovery stage is robust to crafted-novelty poisoning at budgets up to X%" is a publishable assurance result; the paper becomes a robustness characterisation instead of an attack paper. Decided now so a negative result cannot derail the project. *(This is now the partially-taken branch — see H2 above.)*

---

## 3. Contribution statement (draft)

1. We evaluate **poisoned federated class-incremental IDS** — 5 clients,
   Dirichlet(0.5) non-IID shards, 1 malicious client injecting targeted
   label-flip into its local shard — comparing finetune vs EWC vs DER++ at
   four budgets, n=7, answering the poisoning + non-IID future-work call of
   Su 2025 (see `docs/results_overview.md` §Phase 5).
2. We show federation itself is the dominant effect (finetune/DER++ drop
   significantly, EWC transfers intact), and that a small-loss filter
   significantly recovers EWC under attack — while proving by probe that it
   does so *without* removing flips (recall 0.000), a mechanism warning.
3. We separately characterize discovery-stage poisoning (recon-max vs
   attack-anchored novelty poison + nopois control) and benchmark both
   defences, with the kNN filter's drift-vs-poison confusion quantified
   (0.000 retention of rare classes on clean streams).

*Hedging note (updated after `docs/search_protocol.md`, filled 2026-09-24):* claim of "first" is contingent on the reproducible search protocol returning no prior art in the exact intersection (discovery-stage poisoning × continual IDS). Nearest prior art found and **must be cited**:
- **Sonic** (doi:10.1016/j.ins.2026.123140) — HDBSCAN poisoning; nearest threat to Option 2-A, but *not* inside a continual-learning IDS.
- **Amnesia** (arXiv:2606.12655) — attacks the replay sampler of a CL system (different object: sampler, not discovery pipeline).
- arXiv:2002.02741 — AE poisoning for ICS (static, not continual).

Any of these found in full-text search must be cited and the claim narrowed further before submission. We position our contribution as the *intersection* (open-world discovery stage inside a continual IDS, with a nopois control), not as the first work on any single component.

---

## 4. Dataset and task sequence

**Primary dataset: CICIDS2017** — comparable to arXiv:2608.04602; natural day-based ordering; field-standard.

| Task | Day | Content | Labels introduced |
|------|-----|---------|-------------------|
| T0 | Monday | Benign only | Benign |
| T1 | Tuesday | FTP-Patator, SSH-Patator | 2 brute-force |
| T2 | Wednesday | DoS Slowloris, DoS Slowhttptest, DoS Hulk, DoS GoldenEye, Heartbleed | 5 |
| T3 | Thursday | Web Attack (Brute Force, XSS, SQL Injection), Infiltration | 4 |
| T4 | Friday | Bot, PortScan, DDoS | 3 |

**Design decisions (must state and justify):**

- **Scenario:** Class-Instance Incremental (CII) — benign reappears in every task — citing arXiv:2608.04602. Classic class-IL reported as ablation (A2).
- **Cleaning protocol:** drop duplicate rows; drop `inf`/`NaN` in rate features; normalise label strings (whitespace/case variants); report rows removed per class in the report (credibility marker).
- **Class imbalance:** handled by NO re-weighting — plain unweighted
  cross-entropy throughout (an earlier draft's "class-weighted loss" line was
  a documentation error; the code never weighted). Buffers inherit stream
  imbalance (disclosed on every table/figure). SMOTE is *not* used.
- **No train/test leakage:** never mix datasets for train and test; never split flows from the same capture across both.
- **Optional carrier validation:** CICDDoS2019 (answers Paper 1's own DDoS complaint); CICIoT2023 if time allows.

---

## 5. Baselines (all re-run on our sequence)

| # | Baseline | Family | Why |
|---|----------|--------|-----|
| 1 | Sequential fine-tuning | none | lower bound; pure forgetting |
| 2 | EWC | regularisation | universal CL baseline |
| 3 | LwF | regularisation/distillation | used in Papers 1 and 3; no data storage |
| 4 | Experience Replay (ER) | replay | simplest replay |
| 5 | DER++ | replay | strong simple baseline (if time) |
| 6 | Joint / Oracle | upper bound | always report |
| 7 | [defended variant] | — | baseline + defence |

Optional (Option 2-B only): FedAvg, FedProx, + Krum / Trimmed Mean / FreqFed.

**Software:** this repo implements lightweight PyTorch baselines for portability. Where Avalanche (`avalanche-lib`) or Mammoth is installed, their EWC/LwF/ER/DER++ may be swapped in as cross-checks. Flower (`flwr`) only if Option 2-B is activated.

---

## 6. Threat model (fill-in table — primary deliverable before coding attacks)

| Question | Answer |
|----------|--------|
| **Adversary goal** | Availability (suppress a real attack family) *and/or* integrity (manufacture a fictitious class / make attack traffic look benign) |
| **What can they control** | (a) a fraction ρ of labelled training samples entering the stream (poisoner); (b) optionally, a fraction of federated clients (Byzantine); (c) the traffic itself (evader, for trigger design). **Primary: (a).** |
| **How much** | Budget ρ ∈ {0.5%, 1%, 5%} of samples per task; unit = flows |
| **Knowledge** | White-box for attack design; black-box for defence evaluation (conservative, accepted default) |
| **When** | Persistent — acts at every task (the case that makes CL different from static poisoning) |
| **Assumed NOT to do** | Cannot modify the server, cannot alter the aggregation algorithm, cannot change benign traffic statistics globally |

**One-sentence framing for the report:**

> We assume a white-box, persistent, low-budget poisoner who cannot influence the server, and we evaluate whether defences that succeed in the static setting succeed when the data distribution is itself drifting.

---

## 7. Attack implementations (tabular flow data)

1. **Feature-space trigger (easiest):** e.g. `dst_port = 6666` AND unusual TCP flag AND `fwd_pkt_len_mean > 800`. Cheap; examiner may question realism — argue reachability.
2. **Physically grounded trigger (recommended):** derive from a reproducible traffic characteristic (packet-size sequence, legal TCP flag combo, inter-arrival pattern) generatable with Scapy/hping3. Costs ~1 extra week; much more defensible.
3. **Novelty-poisoning trigger (Option 2-A, headline):** no trigger. Send traffic designed to maximise autoencoder reconstruction error; let the pipeline cluster and learn it. Measure whether the resulting fictitious class (a) captures future benign traffic (→ false alarms) or (b) absorbs a real attack family (→ missed detections).

**Label flipping:** flip labels of ρ of samples; report both random and *targeted* (single-class) — targeted is far more damaging and realistic.

**Byzantine (Option 2-B only):** sign-flip, update scaling ("little is enough", Baruch et al.), model replacement (Bagdasaryan et al.). Test whether EdgeFedCIL-style compression attenuates or masks the attack.

---

## 8. Experiment matrix

| ID | Experiment | Attacks | Budgets | Baselines | Question |
|----|------------|---------|---------|-----------|----------|
| **F2** | Federated poisoning (headline) | targeted flip, 1-of-5 malicious | 0 / 1 / 5 / 10% (of malicious shard) | finetune, EWC, DER++ | which method survives federation + poison |
| **F4** | Federated defence | best of F2 | 5 / 10% | +small-loss filter | H3 under federation |
| **E1** | Clean protocol reproduction | none | — | 1–6 | validates baselines, feeds ablation |
| **E2** | Label-flip buffer/stream | random + targeted | 0.5 / 1 / 5% | 1–4 | H1 |
| **E3** | Backdoor (feature + physical) | static vs persistent | 1 / 5% | 1–4 | trigger persistence |
| **E4** | Novelty-poisoning of discovery | suppression + fake-class | 0.5 / 1 / 5% | 1–4 | **H2 (headline)** |
| **E5** | Evasion of novelty detector | crafted-novel benign | — | 1, 4 | can discovery be prevented |
| **E6** | Defences | best of E2–E4 | fixed | +purification, +auditing, +freq-filter | H3 |
| **E7** | *(bonus)* Deployment cost | clean | — | 4, 6 | latency, peak RSS, params, FLOPs |
| **A1** | Ablation: buffer size | best attack | fixed | 4 | bigger buffer help/hurt attacker? |
| **A2** | Ablation: class-IL vs CII | best attack | fixed | 4 | is CII harder? |
| **A3** | Ablation: task order | best attack | fixed | 4 | ≥3 orderings |

**Cut order if short on time:** A3 → A2 → E7 → E5 → E3. **Never cut:** E1–E4 + E6.

---

## 9. Evaluation protocol and statistical honesty

1. Full task-accuracy matrix for every experiment.
2. Report ACC, BWT, FWT, Forgetting (definitions from arXiv:1810.13166).
3. For Gap 2: always report clean accuracy *and* ASR together. A backdoor with 0.97 clean accuracy and 95% ASR is *worse* than a model that dropped to 0.80 — nobody notices. Make this argument explicitly.
4. Seven seeds (1,2,3,4,5,6,42), mean ± std, Wilcoxon signed-rank vs each baseline. No p-values on single runs. Random-mode ASR is N/A (undefined), never 0; buffer imbalance disclosed everywhere (both enforced in `scripts/stats_summary.py` and `scripts/make_figures.py`).
5. Fix and report: buffer size (500 or 1000), epochs/task, LR, batch size, optimiser; tune hyperparameters on a validation split of the *current task only* (never future data).
6. Repeat the task sequence with ≥2 orderings (order-sensitive).
7. Report compute: GPU hours, wall-clock time.

---

## 10. Threats to validity (write this section — earns marks)

- **Construct validity:** CICIDS2017 itself criticised (duplication, unidirectional artefacts, inf/NaN); attack success does not automatically transfer to production traffic.
- **Internal validity:** single dataset; hyperparameters may favour one method; Thursday raw labels arrived as U+FFFD mojibake (repaired by substring fallback — verified by class counts, but the raw bytes are unrecoverable in principle).
- **External validity:** no real federated deployment (5-client simulation, 1 round/task); no real attacker traffic (simulated); random within-day train/test splits, not time-ordered; single malicious client at ≤10% shard budget; no edge-device measurements.
- **Scoped out (stated, not hidden):** an RF-fingerprint drift re-authentication system (claim #2's second half) — out of budget; our discovery work tests unknown-class discovery (Paper 1's domain), a different threat model, kept separate.
- **Ethical:** all work offline on public data; no live systems targeted; attack code disclosed with the paper.

---

## 11. 12-week timeline (two students, part-time)

| Week | Deliverable |
|------|-------------|
| 1 | This proposal finalised + search-protocol table + 10 new references |
| 2 | Repo stood up: loader, cleaning, sequence builder, metrics, logging (no models yet) |
| 3 | E1: ER end-to-end; task-accuracy matrix + BWT print correctly |
| 4 | Baselines 1–6 complete; `results/baseline_table.csv` |
| 5 | E2: label flipping × 3 budgets; first real result (H1) |
| 6 | E3: backdoor with feature trigger; trigger-realism discussion written |
| 7 | E4: novelty poisoning (**headline**) — budget 2 weeks mentally |
| 8 | E5 + E6: evasion and defences |
| 9 | A1–A3 ablations; E7 bonus table if hardware available |
| 10 | Statistics: 3 seeds, mean±std, Wilcoxon; regenerate all figures |
| 11 | Write-up: reuse Phase 1 summaries as related work |
| 12 | Buffer: reproducibility run on clean checkout, code release, polish |

**Division of labour:** one owns data + protocol + baselines (E1, E2, E7, statistics); the other owns attack implementation + defence (E3, E4, E5, E6). Both write.

**Status vs timeline (2026-09-26):** data + correctness audit complete
(T3 coverage bug found and fixed, EWC/LwF corrected, archives kept);
single-node grid re-run at n=7 (126 runs); federated wrapper built and
smoke-validated (1-client reproduces single-node range); F2 headline grid
(84 runs, n=7) + F4 defense grid (42 runs, n=7) complete; novelty search
done (Su-2025 gap confirmed). Remaining: write-up and clean-checkout
reproducibility run.

---

## 12. Pre-empting supervisor questions

1. **"Isn't this just applying known attacks to a known model?"** — Generic backdoor-on-CL is studied; single-node buffer poisoning on CICIDS2017 exists (arXiv:2608.04602). The untested object is the *open-world discovery pipeline* (and optionally federated aggregation of a continual learner) — where the attacker influences *what the model decides to learn*. Search protocol in `docs/search_protocol.md` documents the novelty check.

2. **"What if the attacks fail?"** — Then we publish a robustness characterisation: "the discovery stage resisted crafted-novelty poisoning at budgets up to X%." Assurance result for a mechanism currently deployed without any such guarantee. Pre-committed in §2.

3. **"Why not just use a public dataset as-is?"** — SoK arXiv:2607.10914 lists artificial splits and trivial benchmarks as field-wide pitfalls; CICIDS2017 has documented defects. We derive sequences from real capture days and report cleaning decisions explicitly.
