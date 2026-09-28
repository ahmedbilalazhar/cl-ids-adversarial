# Results Overview (post-fix, 2026-09-26 — SUPERSEDES all pre-2026-09-25 numbers)

> **READ FIRST — 2026-09-27 protocol-correction banner.** The Phase-2 rebuild
> (time-ordered splits + frozen-scaler + n=12) changed the protocol under the
> locked 7-seed numbers below. Three locked claims did **not** survive: (i) LwF's
> top rank was a per-task-scaler artifact, (ii) "federation hurts finetune
> (p=0.031)" is now n.s., (iii) clean single-node CL methods are mutually
> indistinguishable (~0.51). The old numbers are kept for provenance below but
> **must not be cited as current**. See §PHASE-2 (corrected protocol) for the
> numbers that supersede them. Decisions 48–51 in `docs/decisions_log.md`.

> **2026-09-28 validation reset:** All numerical claims below are historical
> executed observations, not currently manifest-validated. The rebuilt main
> `baseline_table.csv`, `stats_summary.csv`, and `wilcoxon.csv` have no result
> rows. UNSW/IoT label corrections and the class-IL filter repair invalidate
> affected prior outputs, archived with hashes. CICIDS legacy tasks expose
> substantial exact train/test feature overlap, especially Friday; see
> `docs/task_audit.md`. No old number should be used for a paper claim until
> the selected protocol is rebuilt and rerun with 12 paired seeds.

> **2026-09-27 federated dispatch correction.** A duplicate runner mapping
> sent 165 Byzantine, UNSW F2, and persistent-federated runs through the
> single-node code path. Their summaries and task matrices are preserved in
> `results_prefix0/dispatch_bug_20260927/` and excluded from current results.
> These groups, and any aggregate CSV derived from them, require regeneration
> before federated claims are made. See decision 54.

**Data:** CICIDS2017 · 2,572,640 cleaned rows · day-based CII sequence (T0–T4) ·
`data/processed/tasks.npz` (T3 repaired: 5 classes incl. 3 Web-attack families).
**Paper spine (locked):** PRIMARY = federated class-incremental IDS
(finetune vs EWC vs DER++, 1 malicious of 5 clients, budgets 0/1/5/10%, n=7);
SECONDARY = centralized-vs-federated ablation; ONE defense (small-loss);
deployment-cost paragraph; discovery-evasion reframed (see §E4/E5).
**Conventions:** n=7 seeds (1,2,3,4,5,6,42) everywhere cited; Wilcoxon
two-sided paired; random-mode ASR is N/A (never 0); ER/DER++ buffers are
NOT class-balanced (note travels in `stats_summary.csv:replay_note`).
Pre-fix numbers live in `data/processed_prefix0/` + `results_prefix0/` — never cite.
**Loss used throughout: plain unweighted cross-entropy** (the proposal's old
"class-weighted loss" line was a doc error, corrected here).

## F2 — PRIMARY: federated poisoning (ACC mean±std, n=7)

| Method | 0% | 1% | 5% | 10% |
|---|---|---|---|---|
| FineTune | 0.224±0.030 | 0.224±0.030 | 0.223±0.029 | 0.223±0.029 |
| **EWC** | **0.308±0.071** | 0.306±0.069 | 0.302±0.068 | 0.301±0.067 |
| DER++ | 0.224±0.022 | 0.223±0.021 | 0.223±0.021 | 0.222±0.021 |

Wilcoxon: EWC vs finetune p=0.0156 (EWC better); DER++ vs finetune p=0.94
(identical). **No poison dose-response is significant for any method**
(p=0.16–0.81). Targeted-flip ASR ≈ 1e-5 throughout (same definitional
near-zero as single-node). Poison bites only T2 (Hulk lives only there):
malicious-shard poison means track budgets exactly (0.002/0.01/0.02).
`results/figures/fig_f2_federated.png`.

## Phase 3 — Centralized vs federated ablation (clean, same seeds)

| Method | Single-node | Federated | p |
|---|---|---|---|
| FineTune | 0.299 | 0.224 | **0.031 (federation hurts)** |
| EWC | 0.307 | 0.308 | 0.94 (immune) |
| DER++ | 0.274 | 0.224 | **0.031 (federation hurts)** |

One-paragraph interpretation: the single-node vulnerability (small,
non-significant 1%-flip effect) neither strengthens nor weakens under
federation — it stays small and non-significant in both settings. What
federation changes is the *baseline*: per-round averaging of diverged client
models compounds forgetting for finetune/DER++ (−0.05/−0.075, both p=0.031;
IID control α=1000 recovers only to 0.216, so skew is not the driver), while
EWC's penalty term anchors clients near the shared solution and transfers
intact (p=0.94). **Memory-confound control (2026-09-26):** federated DER++
above used 500/client (5× single-node memory). A matched-memory arm
(100/client ≈ 500 total) scores 0.242 vs 0.224 (p=0.47 n.s.) and vs
single-node 0.274 (p=0.375 n.s.) — so the DER++ federated deficit is
partly a memory artifact, while the finetune gap (no memory confound)
stands. Headline consequence: **under federation, EWC is the only
of the three that retains single-node performance, with or without
poisoning** — a method-selection finding, not an attack-amplification one.

## F4 — Defense: small-loss under federation (ACC, n=7)

| Method | p5 undef. | p5 +sl | p10 undef. | p10 +sl |
|---|---|---|---|---|
| FineTune | 0.223 | 0.259 (p=0.11 n.s.) | 0.223 | 0.262 (p=0.078 n.s.) |
| **EWC** | 0.302 | **0.421 (p=0.0156)** | 0.301 | **0.421 (p=0.0156)** |
| DER++ | 0.223 | 0.232 (p=0.22 n.s.) | 0.222 | 0.229 (p=0.30 n.s.) |

Choice rationale (one paragraph): small-loss alone improves ACC under attack
both single-node (0.307→0.364, p=0.0156) and federated (EWC 0.30→0.42,
p=0.0156); kNN-consistency alone harms ACC in both framings (single-node
0.307→0.261, p=0.031) while retaining 0.000 of Heartbleed/Sql-Injection/
Infiltration on *clean* streams and dropping 21% of clean T2 — the
drift-vs-poison confusion quantified. Mechanism honesty: a numeric probe
showed small-loss flip-removal recall = 0.000 (carried-over model assigns low
loss to flipped Hulk→Benign); it helps ACC by reshaping training toward
easy samples while ASR *rises* (single-node 7e-5→0.031; federated ~0.02–0.036).
Report it as "helps ACC without removing flips," never as a purifier.
kNN is future work, stated — not silently dropped.

## E1 — Single-node clean baselines (n=7; reference for ablation)

Joint 0.968±0.001 (oracle; 0.991→0.968 after T3 repair — harder Thursday) ·
LwF 0.575±0.012 (kept with mechanism: buffer-500→4000 closes ~60% of its gap
over ER) · ER 0.319±0.035 · EWC 0.307±0.028 · FineTune 0.299±0.016 ·
DER++ 0.274±0.016 (significantly worse than ER, p=0.031).

## E2/E3 — Single-node poisoning (n=7)

Targeted 1% flip: 0.307 vs clean 0.319, **p=0.47 n.s.** (post-fix verdict:
no detectable ACC effect — H1 non-reproduction stands, strengthened).
Backdoor 5% (historical, invalidated): the prior 0.282 ACC, p=0.031, and
ASR 1.0 on seven seeds came from a path with mismatched training/evaluation
triggers, raw values inserted into scaled features, and an ASR fallback to
unrelated classes. The 38 affected per-seed files are preserved under
`results/_archive/backdoor_protocol_20260928/`; no current backdoor effect
estimate is available. Corrected 12-seed runs are pending.

## E4/E5 — Discovery-stage work: RELATED-BUT-DISTINCT threat model

**Invalidated 2026-09-28:** All E4/E5 numerical values below are historical
and cannot support current claims. E4 fitted HDBSCAN using held-out flows and
computed clusters after classifier training, so the reported cluster effect
could not have caused its classifier ACC. Files and figures were moved to
`results/_archive/discovery_transductive_20260928/` with checksums. The new
train-only pipeline and direct-label-poison control require fresh diagnostics
and paired runs; the main result tree has zero validated E4/E5 seeds.
One version-3 no-poison E4 seed now exists under `results/diagnostics/`; it
is an exploratory baseline only and does not estimate a poisoning effect.

These test evasion/manipulation of unknown-class DISCOVERY (Paper 1's domain:
AE novelty → HDBSCAN clustering of *which traffic deserves a new class*),
NOT spoofing drift against a FIXED re-authenticated identity set (Paper 3's
RF-fingerprint domain). Do not conflate; the paper frames them as a
secondary, clearly-separated result. Findings (n=7): threshold-suppression is
unreachable by design (miss rate invariant 0.778); anchor poison absorbs
~0.12 of novel attacks into fictitious clusters (ACC cost suggestive,
p=0.078 n.s.); nopois control has 0 fictitious clusters. E5 (n=3): detector
evasion 0.636, benign pollution ~0.40.

## E7 — Deployment cost (2–3 numbers, not a section)

19,087 params · ~37.8k FLOPs/sample · batch-1 CPU latency ~0.19ms · process
RSS ~537–634MB (interpreter-inclusive). No edge-device numbers (stated as
limitation, not implied).

## Phase 5 — Novelty check (web search, 2026-09-26; PROTOCOL re-run + database verification pending — Phase 1)

Searched: (a) poisoning × federated class-incremental NIDS, (b) backdoor ×
continual-learning IDS, (c) 2025–26 FL+CL+robustness in netsec. Real matches:
**Su 2025** (Junyan Su; evolutionary replay-driven federated CIL for cyber-attack
detection) — limitations section content-verified 2026-09-26 against indexed
record (honest clients/server + IID assumed; "federated learning poisoning
and non-IID client data" named as future work: this project answers that
call directly; publisher/DOI page confirmation outstanding before citing). **Mao et al. 2024** (hierarchical
federated CIL NIDS, no poisoning). **XDFC-IDS 2026** (federated
class-incremental IDS, no poisoning). **Merzouk et al. 2023** (backdoor
parameter study in FL IDS on UNSW-NB15 — static, not continual).
**PoisonShield-FL-NIDS 2025**, **Neurocomputing 2026 FL-poisoning defense**,
**Zukaib/KBS 2025 backdoor FL IDS** (all FL+poisoning, none continual).
**Lavaur et al., Comput. Secur. 2025, 156:104462** (systematic label-flip ×
static-FL IDS — the adjacent work our continual dimension extends; target-venue
lineage). **arXiv:2608.04602** (single-node CII buffer poisoning — our non-reproduction
target). **Guo et al. 2024 / arXiv:2409.13864** (persistent backdoors in CL —
vision benchmarks, not IDS). Verdict: FL-poisoning-IDS and CL-IDS are each
crowded; the **intersection (malicious-client poisoning × federated
class-incremental IDS × CL-method comparison under attack)** has no exact
prior found yet — but the margin may be one paper deep, so claim "first" only
with the verified-citation attached, never unqualified.

## PHASE-2 — Corrected protocol (chrono splits + frozen scaler, n=12) · PRIMARY from here

All rows below: ACC mean, 12 seeds (1–11, 42), Wilcoxon two-sided paired, with
raw p, **Holm-corrected within family**, and matched rank-biserial r; every p
also has a bootstrap 95% CI of the paired mean difference in
`results/wilcoxon.csv`. Groups: `split_effect`, `scaler_effect`,
`chrono_single`, `order_invariance`, `head_strategy`, `f2_headline_c`,
`byzantine_headline`, `robust_defense`, `mechanism`, `breaking_point`,
`persistent_attack`, `adaptive_attack`, `trigger_realism`, `architecture`,
`unsw_*`, `iot_*`.

### 1. Preprocessing: the split/scaler decomposition (the honest "limitation → contribution")

| Comparison (n=12) | ACC | raw p | Holm | r |
|---|---|---|---|---|
| per-task → frozen scaler, ER clean | 0.319 → 0.544 | 0.0156 | 0.109 | +1.00 |
| per-task → frozen scaler, finetune | 0.299 → 0.544 | 0.0156 | 0.109 | +1.00 |
| per-task → frozen scaler, EWC | 0.307 → 0.538 | 0.0156 | 0.109 | +1.00 |
| per-task → frozen scaler, DER++ | 0.274 → 0.533 | 0.0156 | 0.109 | +1.00 |
| per-task → frozen scaler, **LwF** | 0.575 → **0.511** | 0.0156 | 0.109 | −1.00 |
| per-task → frozen scaler, **joint** | 0.968 → **0.930** | 0.0156 | 0.109 | −1.00 |
| random → chrono splits, ER | 0.544 → 0.519 | 0.031 | 0.094 | −0.93 |
| random → chrono splits, finetune | 0.544 → 0.511 | 0.0156 | 0.078 | −1.00 |
| random → chrono splits, EWC | 0.538 → 0.514 | 0.0156 | 0.078 | −1.00 |
| random → chrono splits, LwF | 0.511 → 0.509 | 0.938 | 0.938 | −0.07 |
| random → chrono splits, DER++ | 0.533 → 0.515 | 0.219 | 0.438 | −0.57 |

**The finding, in one line:** *random-within-day splitting inflates apparent
accuracy by only ~2–3 points, but per-task re-standardization inflates it by
~25 points and — crucially — inverts the method ranking (it manufactured
LwF's "best-in-class" status and a joint ceiling of 0.97).* Both are now
reported as first-class preprocessing-pitfall results; the corrected protocol
(chrono + frozen) is primary and the per-task variant is the explicit
secondary comparison.

### 2. Clean single-node under the corrected protocol (chrono + frozen)

| Method | ACC (n=12) | vs ER, raw p | Holm | r |
|---|---|---|---|---|
| Joint (oracle) | 0.907 | 0.0005 | **0.0063** | +1.00 |
| ER | 0.519 | — | — | — |
| EWC | 0.512 | 0.470 | 1.00 | −0.26 |
| LwF | 0.509 | 0.0269 | 0.242 | −0.72 |
| finetune | 0.511 | 0.380 | 1.00 | −0.31 |
| DER++ | 0.508 | 0.110 | 0.879 | −0.54 |

**Corrected claim:** under a leakage-free, scaler-consistent protocol, no
CL method in our set significantly separates from plain replay on CICIDS2017;
only the joint oracle does (survives Holm). The old ladder (ER 0.319 > EWC
0.307 > finetune 0.299 > DER++ 0.274, with LwF 0.575 on top) was a
per-task-scaler artifact and is retired.

### 3. Order-dependence (A3, first-class) and head strategy

| Comparison | ACC | raw p | Holm | r |
|---|---|---|---|---|
| alt ordering vs default (ER+flip) | 0.455 vs 0.514 | 0.0005 | **0.0015** | −1.00 |
| reverse ordering vs default | 0.448 vs 0.514 | 0.0005 | **0.0015** | −1.00 |
| growing head vs pre-sized (finetune) | 0.535 vs 0.511 | 0.0005 | **0.0005** | +1.00 |
| buffer 1000 vs 500 (A1) | 0.517 vs 0.514 | 0.233 | 0.233 | +0.41 |

**Single-node results are order-SENSITIVE** (−6 points across orderings,
surviving Holm) — so every single-node claim in the paper is reported
order-conditioned, and the federated headline is re-checked per ordering
before any "invariant" language is used. A1 (buffer size) is n.s.

### 4. Attacks under the corrected protocol (single-node, n=12, in progress)

| Comparison | ACC | raw p | Holm | r |
|---|---|---|---|---|
| targeted 1% flip vs clean | 0.514 vs 0.516 | 0.677 | 1.00 | −0.15 |
| backdoor 5% vs clean | 0.514 vs 0.516 | 0.380 | 1.00 | −0.31 |
| discovery poison vs clean | 0.517 vs 0.516 | 0.622 | 1.00 | +0.18 |
| anchor poison vs no-poison | 0.498 vs 0.517 | 0.0005 | **0.0063** | −1.00 |
| persistent multi-task flip vs clean (ER) | 0.520 vs 0.516 | 0.092 | 0.277 | +0.56 |
| small-loss vs undefended (ER+1%) | 0.528 vs 0.514 | 0.0122 | 0.134 | +0.79 |
| kNN-consistency vs undefended | 0.505 vs 0.514 | 0.0210 | 0.210 | −0.74 |

**H2 upgrades:** the anchor-variant discovery poison now *does* cost
classifier accuracy significantly (0.498 vs 0.517, p=0.0005, Holm 0.0063) —
the old p=0.078 "suggestive only" was a per-task-scaler artifact too. H1
(1% flip) remains a non-reproduction (p=0.677), and the persistent
multi-task arm still does not collapse single-node (p=0.092 n.s.).

### 5. Federated headline (c_f2) — in progress, n=12

At n=12, federated finetune p0 = 0.470±0.099 vs single-node 0.511±0.008
(paired p=0.569, **n.s.**); the old "federation hurts finetune p=0.031"
does not replicate. The earlier partial-grid hint of a 10%-flip breaking
point was a seed-matching error: p10 = 0.471±0.098 vs p0 = 0.470±0.099
(paired p=0.791, Holm=1.0, r=+0.103, difference CI [−0.0011, 0.0049]).
Seed 11 collapses in **both** arms (≈0.195), not only under attack. Full
per-seed task-accuracy matrices are in
`results/f2_fed_finetune_p{0,10}_c_R_seed*.csv`; the paired statistics are
in `results/wilcoxon.csv` (family `f2_headline_c`). Treat the broader
federated headline as pending until DER++/ER, Byzantine, and thread-provenance
checks finish.

*(All Phase-3/4 numbers — Byzantine availability/robust aggregation, adaptive
attackers, UNSW/IoT replication, architecture sweep — are pending their
grids; every row will carry raw p, Holm p, r, and bootstrap CI. Nothing in
this section is written from a partial grid without saying so.)*

## Limitations (paper paragraph — includes the scoped-out claim)


RF-fingerprint drift-authentication (the second half of research-gap claim #2)
is explicitly scoped out: building an RF re-authentication system from scratch
exceeded the remaining budget, and our discovery-evasion work tests a different
threat model (unknown-class discovery, Paper 1's domain), which we separate
rather than conflate. Further limits: plain unweighted loss (no class
re-weighting); random within-day train/test splits (not time-ordered);
single dataset (CICIDS2017); single malicious client at ≤10% shard budget
(≤2% global); no edge-device latency; a2 strict-CI collapses to 0.2000
(total recency loss — reported, not hidden).

## Status table (DONE / CUT / FLAGGED)

| Item | State | Note |
|---|---|---|
| Gate A data regen + archives | DONE | T3 5-class; CI file 4→5 tasks |
| Phase-0 code fixes (EWC/LwF/labels) | DONE | verified numerically |
| Gate D labeling rules in scripts | DONE | N/A + buffer note in CSV+figures |
| LwF disposition | DONE | kept with buffer-capacity mechanism |
| F2 federated grid 84 runs n=7 | DONE | headline: EWC immune, no dose-response |
| Phase-3 ablation | DONE | federation hurts FT/DER++, not EWC |
| Phase-4 small-loss eval 42 runs | DONE | significant for EWC only; knn→future work |
| Phase-5 novelty search | DONE | Su-2025 future-work call = our gap |
| E5/E7 | DONE | 0.636/0.40; 19k params, ~0.19ms |
| a1/a3 ablations | REINSTATED (Phase 2 step 11) | prior CUT void under journal bar |
| Scaler | FROZEN PRIMARY (Phase-0 ablation) | frozen 0.544 vs per-task 0.299, p=0.0156 |
| RF drift-auth system | CUT | scoped out; limitations + instructor note |
| Backdoor-federated extension | CUT | noted as future work, not run |
| a2 CI collapse (0.2000) | FLAGGED | mechanistic, reported, secondary |
| Anchor ACC-cost (p=0.078) | FLAGGED | suggestive only; discovery effect stands |
| Time-ordered splits | PHASE-2 PRIMARY | chrono rebuild re-runs full suite; random kept as quantified secondary |

Reproduce: `python scripts/run_grid.py <group>` (e1,e2e3,e4,e6a2,f2_ft,f2_ewc,
f2_derpp,f4_ft,f4_ewc,f4_derpp) → `python -m src.run_experiment
--rebuild-table` → `python scripts/stats_summary.py` →
`python scripts/make_figures.py`. Decisions: `docs/decisions_log.md`.
