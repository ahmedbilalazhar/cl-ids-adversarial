# Proposal — Poisoning of Federated Class-Incremental Network Intrusion Detection

> **2026-09-28 audit note:** All result numbers and hypothesis verdicts below
> are historical, executed-only evidence pending manifest-validated reruns.
> The T0+T1 scaler is an offline-initialization protocol, not future-blind at
> T0. Existing CICIDS test sets have exact duplicate-content exposure;
> `docs/task_audit.md` quantifies it. This proposal is not a deployed IDS claim.
> E4/E5 discovery results were invalidated and archived on 2026-09-28:
> held-out flows affected clusters, and cluster assignments never entered
> classifier training. Historical H2 numbers below are superseded, including
> all absorption rates, ACC differences, and p-values. Corrected runs are pending.

**Students:** Saneedullah (23I-2568), Ahmed Bilal (23I-2581)  
**Status:** post-audit revision for supervisor sign-off · primary result F2
(federated finetune vs EWC vs DER++ × 0/1/5/10%, n=7) + centralized ablation
+ one defense (small-loss) + E5/E7 complete; full numbers in
`docs/results_overview.md` · pre-fix drafts archived, never cited  
**Target venue (locked 2026-09-26, see decisions_log.md #24): Elsevier
Computers & Security (Q1)** — full research article (~20 journal pages,
survey-grade related work), NOT a workshop short paper. All prior
workshop-shaped expectations (short length, thin related work) are void.
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

## 2. Hypotheses (pre-registered; numbers reconciled 2026-09-26 against `results/wilcoxon.csv` — this section now matches the locked results exactly)

- **H1 (as originally pre-registered, now reported as NOT reproduced)** — A replay-based class-incremental IDS loses most clean accuracy under label-flipping poisoning of its memory at budgets ≤ 1%, reproducing the single-node finding of arXiv:2608.04602 (collapse to 0.0053 accuracy at a 1% poison budget on CICIDS2017). **Observed (n=7):** under our stream and buffer protocols, targeted 1% flipping (e2_labelflip) gives ACC **0.3070 ± 0.0251** vs clean (e1_clean) **0.3187 ± 0.0353** (Wilcoxon **p=0.4688, n.s.** — no detectable effect, not a collapse; random 0.5% is descriptively worse at 0.2787 ± 0.0148, no paired test yet; targeted 5% gives 0.2984 ± 0.0354; buffer-targeted flip gives 0.3119 ± 0.0285). Their figure is tied to their specific buffer-poisoning setup — we report H1 as a *non-reproduction* and compare protocols explicitly (`results_overview.md` E2, `docs/threat_model.md` budget section). Pre-committed fallback: this is a protocol-comparison finding, not a project failure. *(An earlier draft of this bullet cited stale pre-fix numbers, 0.317 vs 0.336 at p=0.031 — superseded; never cite.)*
- **H2 (restated after nopois control + anchor-variant attack, n=7)** — Poisoning the *novelty-discovery* stage (benign-only AE → threshold → HDBSCAN) is more dangerous per unit of attacker effort than poisoning the classifier: crafted "novel" samples (a) create fictitious discovered classes that absorb future benign traffic or real attack families, or (b) suppress discovery of a real attack family. **Observed:** (b) *closed by design* — with a benign-only AE and a threshold fit on clean scores before poisoning, stream poison cannot move the threshold; discovery miss rate (~0.64) is identical across all four configs. (a) *reachable*: `n_fictitious` = 5–12 vs 0 (nopois), benign absorption up to 1.0%, and — with poison **anchored to the attack manifold** (`mode: anchor`) — **~12–14% of novel real attacks are absorbed into poison-dominated fictitious clusters** (0% for recon-max poison; 0 for nopois), at a suggestive-but-nonsignificant classifier cost (anchor ACC **0.2742 ± 0.0313** vs nopois **0.3010 ± 0.0244**, **p=0.0781, n.s.**). **Restated claim:** *low-budget novelty poisoning cannot suppress which attacks are detected under benign-only discovery, but can misfile detected attacks and benign traffic into manufactured classes; attack-manifold anchoring raises attack absorption from 0 to ~12–14% at ρ=1%.* *(An earlier draft cited p=0.047 on stale numbers — superseded; never cite.)*
- **H3 (now tested with two defences, n=7)** — At least one defence that works against classifier poisoning (small-loss buffer purification, gradient auditing, or frequency filtering) performs worse in the continual setting because the drift it must distinguish from poisoning is legitimate. Quantifying this "drift vs. poison" confusion is a contribution in itself. **Observed:** small-loss helps under attack (ACC **0.3637 ± 0.0423** vs undefended **0.3070**, forgetting 0.6578→0.5196, **p=0.0156**) but retains some flipped samples (ASR 7e-5→0.031). A **kNN label-consistency filter** — a static label-noise detector — *hurts*: ACC **0.2612 ± 0.0181** vs undefended 0.3070 (**p=0.0313**), with **zero benefit** (ASR unchanged), because it discards legitimate rare/new-class samples (Heartbleed and Infiltration retention **0%** on clean, unpoisoned streams). Drift looks like poison; the confusion is real and quantified. *(An earlier draft cited 0.317→0.367 — superseded by the exact 0.3637 vs 0.3070; never cite the rounded draft.)*

**Fallback if H2 is rejected:** "the discovery stage is robust to crafted-novelty poisoning at budgets up to X%" is a publishable assurance result; the paper becomes a robustness characterisation instead of an attack paper. Decided now so a negative result cannot derail the project. *(This is now the partially-taken branch — see H2 above.)*

---

## 3. Contribution statement (draft)

1. We evaluate **poisoned federated class-incremental IDS** — 5 clients,
   Dirichlet(0.5) non-IID shards, 1 malicious client injecting targeted
   label-flip into its local shard — comparing finetune vs EWC vs DER++ at
   four budgets, n=7, answering the poisoning + non-IID future-work calls of
   Su 2025 (content-verified) and EdgeFedCIL §3.1 (see `docs/results_overview.md`
   §Phase 5, `docs/positioning_memo.md` for the locked headline decision).
2. We show federation itself is the dominant effect (finetune/DER++ drop
   significantly, EWC transfers intact), and that a small-loss filter
   significantly recovers EWC under attack — while proving by probe that it
   does so *without* removing flips (recall 0.000), a mechanism warning.
3. We separately characterize discovery-stage poisoning (recon-max vs
   attack-anchored novelty poison + nopois control) and benchmark both
   defences, with the kNN filter's drift-vs-poison confusion quantified
   (0.000 retention of rare classes on clean streams).

*Hedging note (updated after `docs/search_protocol.md`, filled 2026-09-24; sharpened 2026-09-26):* claim of "first" is contingent on the reproducible search protocol returning no prior art in the exact intersection (discovery-stage poisoning × continual IDS). Nearest prior art found and **must be cited**:
- **Lavaur et al., Computers & Security 2026(2025) 156:104462** — systematic label-flipping × federated IDS (static FL, no continual learning). Direct adjacent work in our TARGET VENUE: our contribution is the continual dimension it lacks (federated × class-incremental × CL-method comparison under poisoning). Cite, distinguish, and mirror its evaluation-recommendation shape.
- **Mao et al. 2024, IEEE IoT-J** — hierarchical federated CIL NIDS, no poisoning.
- **Sonic** (doi:10.1016/j.ins.2026.123140) — HDBSCAN poisoning; nearest threat to Option 2-A, but *not* inside a continual-learning IDS.
- **Amnesia** (arXiv:2606.12655) — attacks the replay sampler of a CL system (different object: sampler, not discovery pipeline).
- arXiv:2002.02741 — AE poisoning for ICS (static, not continual).
- **Su 2025** (Junyan Su; evolutionary replay-driven federated CIL; honest-clients assumption; poisoning + non-IID deferred to future work — **content-verified 2026-09-26 against indexed record quoting the limitations section; publisher/DOI page confirmation outstanding before citing**).

Any of these found in full-text search must be cited and the claim narrowed further before submission. We position our contribution as the *intersection* (open-world discovery stage inside a continual IDS, with a nopois control), not as the first work on any single component.

---

## 4. Dataset and task sequence

**Primary dataset: CICIDS2017** — chosen for direct comparability with arXiv:2608.04602 (our H1 non-reproduction target) and named in Paper 1's (Ge et al. 2026) own future-work call (CIC-IDS2017 alongside CSE-CIC-IDS2018 and UNSW-NB15); natural day-based ordering; field-standard. (An earlier project note justified CICIDS2017 via an EdgeFedCIL rationale — superseded; the comparability reason above is the locked one.)

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
- **Split validity:** no source row is intentionally assigned to both train and test, but legacy CICIDS files lack row IDs and exact duplicate feature records do cross the split. The duplicate-disjoint sensitivity arm excludes these matches; quantify this limitation before any generalization claim.
- **Scaler correction:** the following historical scaling bullet is superseded where it calls T0+T1 fitting future-blind or treats earlier scores as confirmed lower bounds. The frozen T0+T1 scaler is offline initialization; the T0-only arm and duplicate-disjoint arm are separate sensitivity protocols, with paired comparisons pending.
- **Feature scaling (locked 2026-09-26, Phase-0 ablation):** PRIMARY = one StandardScaler fit on T0+T1 train only, applied frozen to all tasks (no backward leakage: no future-task row touches the scaler; `src/data/sequence.py::fit_scaler_frozen`, `data/processed/tasks_frozen.npz`). SECONDARY = per-task scalers kept as an explicit preprocessing-pitfall comparison: same-seed finetune ablation (n=7) scores 0.5439 ± 0.0083 frozen vs 0.2991 ± 0.0162 per-task (p=0.0156) — per-task re-standardization injects artificial cross-task covariate shift that dominates all method effects. All locked pre-2026-09-26 numbers used per-task scaling and are thereby conservative lower bounds; the Phase-2 chrono rebuild adopts frozen scaling throughout.
- **Classification head (resolved 2026-09-26):** pre-sized fixed head over the full label space (Paper-2 §3.2.1 fixed-head protocol), UNIFORM across all methods via `src/cl/base.py::_maybe_expand`; `expand_head` exists but never fires under current configs (class_bound ≤ pre-sized width always); LwF distils sliced to seen width (decisions_log.md #3). A growing-head ablation (T0-width init + live expansion) is scheduled in the Phase-2 ablations family — not silently picked.
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
| **What can they control** | (a) a fraction ρ of labelled training samples entering the stream (poisoner); (b) a fraction of federated clients — data poisoning AND Byzantine update attacks (sign-flip, "little is enough" scaling, model replacement) against the aggregation step (Phase 3 implements all three); (c) the traffic itself (evader, for trigger design). **Primary: (a) + (b).** |
| **How much** | Budget ρ ∈ {0.5%, 1%, 5%} of samples per task for the stream poisoner (unit = flows); federated shard budgets 0/1/5/10% extended PAST 10% to a characterised breaking point, × malicious fractions 1/5, 2/5+ (Phase 3). |
| **Knowledge** | White-box for attack design; black-box for defence evaluation (conservative, accepted default). Adaptive attacker: each defence faces an attack crafted to evade it (Phase 3, mandatory for a journal). |
| **When** | Persistent — acts at every task (the case that makes CL different from static poisoning); persistent multi-task arm (each task's own majority class flipped) added in Phase 3. |
| **Assumed NOT to do** | Cannot modify the server, cannot alter the aggregation algorithm, cannot change benign traffic statistics globally |

**One-sentence framing for the report:**

> We assume a white-box, persistent, low-budget poisoner who cannot influence the server, and we evaluate whether defences that succeed in the static setting succeed when the data distribution is itself drifting.

---

## 7. Attack implementations (tabular flow data)

1. **Feature-space trigger (easiest):** e.g. `dst_port = 6666` AND unusual TCP flag AND `fwd_pkt_len_mean > 800`. Cheap; examiner may question realism — argue reachability.
2. **Physically grounded trigger (recommended):** derive from a reproducible traffic characteristic (packet-size sequence, legal TCP flag combo, inter-arrival pattern) generatable with Scapy/hping3. Costs ~1 extra week; much more defensible.
3. **Novelty-poisoning trigger (Option 2-A, headline):** no trigger. Send traffic designed to maximise autoencoder reconstruction error; let the pipeline cluster and learn it. Measure whether the resulting fictitious class (a) captures future benign traffic (→ false alarms) or (b) absorbs a real attack family (→ missed detections).

**Label flipping:** flip labels of ρ of samples; report both random and *targeted* (single-class) — targeted is far more damaging and realistic.

**Byzantine (PRIMARY from Phase 3 — no longer "Option 2-B only"):** sign-flip, update scaling ("little is enough", Baruch et al.), model replacement (Bagdasaryan et al.) against the federated aggregation step, alongside the label-flip-through-averaging attack. Server-side defences: Krum, Trimmed-Mean, coordinate-wise Median, FedRDF-style dynamic aggregation, evaluated against BOTH attack families plus the client-level defences (small-loss, kNN-consistency). Adaptive attacker per defence (mandatory). Test whether EdgeFedCIL-style compression attenuates or masks the attack.

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

**Reinstatement rule (journal bar, locked 2026-09-26):** A3 → A2 → E7 → E5 → E3 cut order is VOID. Nothing is cut for time — A1 (buffer size), A2 (class-IL vs CII), A3 (≥3 orderings, first-class order-invariance result) are all reinstated in full (Phase 2 step 11). Deprioritisation requires a result in hand making the item unnecessary, logged as such.

---

## 9. Evaluation protocol and statistical honesty

1. Full task-accuracy matrix for every experiment.
2. Report ACC, BWT, FWT, Forgetting (definitions from arXiv:1810.13166).
3. For Gap 2: always report clean accuracy *and* ASR together. A backdoor with 0.97 clean accuracy and 95% ASR is *worse* than a model that dropped to 0.80 — nobody notices. Make this argument explicitly.
4. Seeds ≥3 everywhere (status quo n=7: 1,2,3,4,5,6,42), mean ± std, Wilcoxon signed-rank vs each baseline — EXTENDED in Phase 2: power analysis sets the final seed count, bootstrap CIs sit alongside Wilcoxon everywhere, and WILCOXON_PAIRS is split into Holm-corrected families (f2_headline, byzantine_headline, f4_defense, e_single_node, ablations, adaptive_attack) with raw + corrected p and rank-biserial effect sizes. No p-values on single runs. Random-mode ASR is N/A (undefined), never 0; buffer imbalance disclosed everywhere (both enforced in `scripts/stats_summary.py` and `scripts/make_figures.py`).
5. Fix and report: buffer size (500 or 1000), epochs/task, LR, batch size, optimiser; tune hyperparameters on a validation split of the *current task only* (never future data). Feature scaling: frozen T0+T1-fit primary (see §4); per-task kept as quantified secondary.
6. Repeat the task sequence with ≥3 orderings (A3: order-invariance as a first-class result).
7. Report compute: GPU hours, wall-clock time.
8. **Primary splitting protocol (Phase 2):** chronological (time-ordered) train/test within each day; random-within-day kept as an explicit secondary, with the delta reported as a quantified leakage-pitfall finding.

---

## 10. Threats to validity (write this section — earns marks)

- **Construct validity:** CICIDS2017 itself criticised (duplication, unidirectional artefacts, inf/NaN); attack success does not automatically transfer to production traffic.
- **Internal validity:** single dataset; hyperparameters may favour one method; Thursday raw labels arrived as U+FFFD mojibake (repaired by substring fallback — verified by class counts, but the raw bytes are unrecoverable in principle).
- **External validity:** no real federated deployment (5-client simulation, 1 round/task); no real attacker traffic (simulated); random within-day train/test splits primary until the Phase-2 chrono rebuild (then chrono primary, random kept as quantified secondary); single dataset (CICIDS2017) until Phase-4 replication (UNSW-NB15 + CICIoT2023); single malicious client at ≤10% shard budget until Phase-3 fraction/budget sweeps; no edge-device measurements (cloud free-tier software proxy, honestly labelled — Phase 5).
- **Scoped out (stated, not hidden):** an RF-fingerprint drift re-authentication system (claim #2's second half) — out of budget; our discovery work tests unknown-class discovery (Paper 1's domain), a different threat model, kept separate.
- **Ethical:** all work offline on public data; no live systems targeted; attack code disclosed with the paper.

---

## 11. Work plan (journal bar — replaces the void 12-week workshop timeline)

| Phase | Deliverable |
|------|-------------|
| 0 | Venue locked (C&S) · proposal/threat-model truth fixes · scaler ablation (frozen primary) · head resolution |
| 1 | Protocol-specified novelty search (Scholar/arXiv-API/Xplore/Scopus) + neighbour verification + locked positioning memo |
| 2 | Chrono-primary rebuild + power-set seeds + Holm families + bootstrap CIs + A1/A2/A3 reinstated |
| 3 | ER-federated · Byzantine attacks + robust aggregators · adaptive attacker · persistent/multi-fraction/breaking-point arms · grounded trigger · 3-architecture sweep · EWC-immunity mechanism note |
| 4 | UNSW-NB15 + CICIoT2023 replication of the primary set |
| 5 | Free-tier deployment-cost measurement (honestly labelled proxy) |
| 6 | Docker/conda-lock artifact + one-command repro + Zenodo DOI |
| 7 | Computers & Security full-article draft (~20 pp., survey-grade related work, threats-to-validity with resolved findings) |

**Status (2026-09-26):** data + correctness audit complete
(T3 coverage bug found and fixed, EWC/LwF corrected, archives kept);
single-node grid re-run at n=7 (126 runs); federated wrapper built and
smoke-validated (1-client reproduces single-node range); F2 headline grid
(84 runs, n=7) + F4 defense grid (42 runs, n=7) complete; novelty search
done (Su-2025 gap confirmation **pending database verification**); scaler
ablation done (frozen 0.544 vs per-task 0.299, p=0.0156 — frozen primary
from here on). Remaining: Phases 1–7 above.

---

## 12. Pre-empting supervisor questions

1. **"Isn't this just applying known attacks to a known model?"** — Generic backdoor-on-CL is studied; single-node buffer poisoning on CICIDS2017 exists (arXiv:2608.04602). The untested object is the *open-world discovery pipeline* (and optionally federated aggregation of a continual learner) — where the attacker influences *what the model decides to learn*. Search protocol in `docs/search_protocol.md` documents the novelty check.

2. **"What if the attacks fail?"** — Then we publish a robustness characterisation: "the discovery stage resisted crafted-novelty poisoning at budgets up to X%." Assurance result for a mechanism currently deployed without any such guarantee. Pre-committed in §2.

3. **"Why not just use a public dataset as-is?"** — SoK arXiv:2607.10914 lists artificial splits and trivial benchmarks as field-wide pitfalls; CICIDS2017 has documented defects. We derive sequences from real capture days and report cleaning decisions explicitly.
