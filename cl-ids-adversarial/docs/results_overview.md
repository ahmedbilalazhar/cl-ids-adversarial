# Results Overview (post-fix, 2026-09-26 — SUPERSEDES all pre-2026-09-25 numbers)

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
Backdoor 5%: 0.282, p=0.031, **ASR 1.0 on all 7 seeds** (stealthy: report
ACC+ASR together).

## E4/E5 — Discovery-stage work: RELATED-BUT-DISTINCT threat model

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
