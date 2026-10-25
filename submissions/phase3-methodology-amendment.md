# Phase 3 methodology amendment — adopted 24 October 2026

This implementation addendum supersedes the **data, feature dimensions and
taxonomy** in `phase2-with-claude.tex`. That submitted proposal remains the
historical methodology source. The user explicitly authorized adoption of the
data amendments and taxonomy resolution before a reference run. Instructor
feedback has not been supplied; no instructor approval is claimed.

## Adopted changes

| Item | Phase 3 decision | Reason and consequence |
|---|---|---|
| Release | Authors' corrected `CICIDS2017_improved.zip`, SHA-256 `97fdb91d339e2d8cf5627f981b831e5e7e400b981c58181c451a38fd03c48883` | Metadata-bearing, audited release. Original and corrected releases share a historical capture; they are not independent replications. |
| Annotation | `Attempted Category != -1` becomes Benign before the conflict audit | Follow the selected release policy. Annotation/provenance columns never become predictors. |
| Predictors | **74 ordered FP32 inputs**; omit both Fwd/Bwd Header Length | Lossy header totals and positive consistency violations make an unsigned reinterpretation insufficient. Old 76-feature model weights, tuning and resource estimates do not carry over. |
| Validity | Named nonnegative-feature policy, with the declared TCP-window sentinel | Finite values alone do not establish physical validity. This screen does not certify every remaining value. |
| T0 | 371,621 Monday-only source-valid benign fitting records; frozen min/max; zero range denominator 1; no clipping/refit | Later cross-day conflicts affect learning/evaluation exclusion and component closure, never calibration fitting. Three fitting rows have ambiguous final-input annotations and remain calibration-only. |
| Isolation | 120-second interval sessions plus raw/final exact-input links; retain excluded provenance bridges | Canonical component ID is the minimum immutable provenance ID of the entire component. This is session/content isolation, not host/campaign independence. |
| Split | Fixed SGKF5, shuffle, seed 2026; train folds 2/3/4, development 1, final test 0; sklearn 1.9.1 audited implementation | No split search using model outcomes. The 74-feature split reuse has an exact input/component identity proof. |
| Benign training inventory | Whole cross-stage benign bundles, seed-2027 heuristic toward 3,500 per stage | Prescribed attack records are retained independently. Excluded benign records remain reserved to training. |
| Sites | Five simulated clients with persistent whole-component ownership | Exact normalized squared-error greedy allocator with family Dirichlet(.5) targets; no independent row allocations or per-stage redraws. |
| Taxonomy | **16 source annotation classes**, with active widths **3 → 8 → 13 → 16** | Preserve Thursday `Infiltration - Portscan` and Friday `PortScan` as distinct source scenarios. Global annotation codes are separate from append-only classifier slots. |
| Claims | New **annotated-class acquisition** | Scenario labels do not demonstrate previously unseen techniques, zero-day detection or independent network sites. |
| Rare support | Train supported classes and keep all their active logits; use the fixed ≥50 rows and ≥5 components per role scoring floor | Only Infiltration - Portscan is eligible among E3 attacks. Ordinary Infiltration and web classes are descriptive; Heartbleed has no held-out positives. |
| Benign reporting | Combined benchmark FAR plus original-background/remapped-attempted descriptive rates | Fixed subgroup denominators and evaluator-only provenance. No subgroup or threshold selection from outcomes. |

## Resolved arrival schedule

| Stage | Newly registered attack annotations |
|---|---|
| E1, Tuesday | FTP-Patator; SSH-Patator |
| E2, Wednesday | DoS GoldenEye; DoS Hulk; DoS Slowhttptest; DoS Slowloris; Heartbleed |
| E3, Thursday | Infiltration; Infiltration - Portscan; Web Attack Brute Force; Web Attack Sql Injection; Web Attack XSS |
| E4, Friday | Bot; DDoS; PortScan |

Benign is introduced at E1 in classifier slot zero and recurs in every stage.
Class names above preserve the canonical source aliases. Support counts and
eligibility are recorded in [taxonomy-v1.json](../configs/phase3/taxonomy-v1.json).

The 29-contrast analysis family and twelve final seeds remain planned. The
reference is **one clean development seed (101)** with untuned settings and is
not part of those final replicates. A corrected implementation and successful
recovery do not establish clean learning feasibility or a beneficial defense.

## Reference implementation boundary

The adopted reference implements DR+DC, three rounds and one local epoch per
stage, learning rate .001, replay-label coefficient 1 and logit coefficient .5.
These settings were fixed before its first evaluated model outcome. Full-pool
current permutations precede taking admitted subsequences. Adam resets at each
broadcast. Admission is fixed once per stage, after head expansion. Replay uses
pre-update teachers, independent draw/insertion streams and one first-pass
reservoir proposal per distinct admitted record.

Typed, pickle-free round transactions preserve models, admissions, replay,
counters and lossless RNG states. A failed round rolls back all five clients to
the previous commit. Final-test rows are physically absent from the exported
training and development packages. The final test is not evaluated here.

FT/EI/DM/DQ, controlled corruption, intervention/ablation acceptance, GPU runtime
confirmation, development tuning and final scope/analysis freezing remain gates
before a GPU grid. No experimental matrix is made dispatchable by this addendum.

Implementation, commands and executed evidence: [Phase 3 reference](../docs/phase3-reference/README.md).
