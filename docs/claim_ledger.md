# Claim ledger (2026-09-28) — plan §10

Every research-facing statement in README, proposal, results-overview,
positioning-memo, and paper-draft traced to its evidence. Statuses:
**ESTABLISHED** (audited fact, citable as such), **EXPLORATORY**
(diagnostics only, no inference), **PENDING** (needs manifest-v3 paired
rerun), **SUPERSEDED** (archived, never cite). Central fact: aggregate
CSVs are header-only (`wilcoxon.csv`, `stats_summary.csv`,
`baseline_table.csv`: **0 rows each** — verified 2026-09-28) and
`results/runs/` holds **0 manifests**, so every numeric result below is
executed-only at best until its spec gate clears.

## Proposal H1–H3 (`docs/proposal.md:48-50`)

| Claim | Evidence | Status |
|---|---|---|
| H1: targeted 1% flip 0.3070v0.3187 p=0.4688 n.s., non-reproduction of arXiv:2608.04602 | `e2_labelflip` vs `e1_clean`, random/per-task, seeds 1–6+42, no manifests | PENDING (spec `e_single_node`; chrono-12 rerun; random protocol is secondary anyway) |
| H2: anchor absorption ~12–14%, ACC 0.2742v0.3010 p=0.0781 n.s.; suppression unreachable | pre-2026-09-28 transductive pipeline + per-task scaler | SUPERSEDED twice (archived `discovery_transductive_20260928/`; scaler artifact). New 3-seed means (0.521883/0.530564/0.554113, absorption 0/0.000935) EXPLORATORY; spec `gated-detector` |
| H3: small-loss 0.3637v0.3070 p=0.0156 helps ACC without removing flips (ASR 7e-5→0.031); kNN 0.2612v0.3070 p=0.0313 harms, 0% rare retention | `e6_defense_smallloss/knnconsist` vs `e2_labelflip`, n=7, no manifests | PENDING (spec `e_single_node`/`chrono_single`, `f4_defense*`) |
| CICIDS2017-over-UNSW comparability rationale (proposal.md:87) | locked decision #26, checkable in proposal S4 | ESTABLISHED as rationale (not a result) |

## Positioning headline (`docs/positioning_memo.md:42-50`)

| Claim | Evidence | Status |
|---|---|---|
| Headline: first adversarial evaluation of federated CIL IDS (Su 2025 + EdgeFedCIL calls); EWC transfers, drift/poison confusion, discovery misfiles | hypothesis; memo's own p-values flagged historical-only | PENDING + literature debt: Su 2025 publisher/DOI page, Scholar/Xplore/Scopus manual counts outstanding. "First" only with verified citations, never unqualified |

## Results overview, n=7 sections (`docs/results_overview.md:41-147`)

| Claim | Evidence | Status |
|---|---|---|
| F2: EWC 0.308 p=0.0156, no dose-response p=0.16–0.81 | `f2_*` vs `f2_fed_finetune_p0`, n=7, no manifests | PENDING (spec `f2_headline_c`, 12 seeds) |
| Phase 3: federation hurts FT/DER++ p=0.031, EWC immune p=0.94; DER++ partly memory artifact | same-seed ablation, n=7, no manifests | PENDING (spec `fed_ablation_c`) |
| F4: EWC+small-loss 0.421 p=0.0156; kNN harms | n=7, no manifests | PENDING (spec `f4_defense_c`, same-aggregator controls missing → `gated-controls` for robust pairs) |
| E1 ladder incl. LwF 0.575, joint 0.968 | per-task scaler protocol | SUPERSEDED as ranking (decision #49); joint stays oracle-labeled |
| E3 ASR 1.000, ACC 0.282 p=0.031 | trigger-mismatched path | SUPERSEDED (archived `backdoor_protocol_20260928/`); no current estimate; extractor gate open |
| E4/E5 (miss 0.778, absorption ~0.12, evasion 0.636) | transductive pipeline | SUPERSEDED (archived); E5 has no revised protocol yet |
| E7 params/latency/RSS | random-model proxy | ESTABLISHED AS PROXY ONLY; trained-bundle benchmark pending (Phase G). Dims provenance restored 2026-09-28: E8 now reads (76, 15) from the primary sidecar and reproduces the documented 19,087 params; latency stays host-specific |
| Phase-5 novelty verdict (gap real, one paper deep) | web-search 2026-09-26, protocol re-run pending | PENDING verification (Phase 1 database pass) |

## Results overview, PHASE-2 n=12 (`docs/results_overview.md:173-274`)

All rows (split/scaler decomposition, chrono-single ladder, order
0.448/0.455v0.514, head 0.535v0.511, attacks, c_f2 finetune 0.470v0.511
p=0.569, p10 breaking-point retraction): executed-only, **zero validated
manifests** — read as prose records of unmanifested runs, not estimates.
PENDING across spec families `split_effect` … `architecture`.
EXCEPTION: reverse-order rows additionally contaminated (builder duplicated
Monday-benign rows; archived `order_rev_benign_dup_20260928/`, builder
fixed, spec `gated-rev-rebuild`). Alt-order builder verified clean but its
rows are likewise unmanifested. The preprocessing-pitfall DIRECTION
(per-task inflation, ranking inversion) is an established executed
observation; its POINT VALUES are not validated estimates.

## README status (`README.md:9-29`, current 2026-09-28)

Refreshed: zero-manifest/zero-row facts stated, E1–E5 + federation +
inference rows honestly marked exploratory/pending, N/A and oracle rules
present, 12-seed loops explicitly not launched. No correction needed.

## Paper draft abstract (`docs/paper_draft.md:24-45`)

All quantitative slots marked PENDING in the draft itself — correct state.
Do not fill until spec-gated families complete. Threats-to-validity and
limitations paragraphs (scoped-out RF system, single dataset/client/budget,
no edge numbers, a2 collapse 0.2000) are accurate scoping — ESTABLISHED as
limitations.

## Established audit facts (citable as method, not effects)

Dedup arm 0 exact matches / 0 same-source overlap (`task_audit.md`,
regenerated); cross-file duplicate structure (`cicids_cross_file_audit.md`,
28 nonzero pairs); UNSW 3,723 / IoT 604 cross-pool matches (excluded from
claims); E4 diagnostics (miss 0.755, T1 0.998, cap ARI 0.628–0.728,
resource probes) as measurements of exploratory arms; 36-test suite;
`analysis_spec.json` (27 families/200 pairs); 14 archives + 2 snapshots in
`release_bundle_contents.md`.

## Amendment rule

Append rows here when a spec-gated family completes; never edit a
SUPERSEDED row into a citable one. Corrections to this ledger go through
`docs/decisions_log.md`.
