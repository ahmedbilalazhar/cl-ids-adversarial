# DG baseline: audited exploratory comparison

This analysis uses the pinned CPU runtime and the development bank. It does not replace the frozen study or belong to the original confirmatory test family.

- Verified DG trajectories: 48 (all 12 seeds × 4 doses).
- Verified DG stage checkpoints: 192; DM/DC matched controls: 96.
- E1 admission IDs, scorer hashes and checkpoint model hashes match DM and DC; input/attack identities match for each paired cell.
- DG keeps `floor(0.75 × client rows + 0.5)` from E2 onward without class protection; E1 is passed through unchanged.

## Paired outcomes

See `paired-comparisons.csv` for all dose-specific seed pairs and descriptive whole-seed bootstrap intervals. Positive H means more Hulk-to-benign error than the same admission method’s clean trajectory; negative Δrec means lower E2 Hulk recall than its clean twin. A is the equal-stage/equal-new-family F1 average for E2–E4, excluding Hulk.

## Limits

- No per-example admission score vectors or accepted ID lists were stored; the audit verifies source-score hashes, policy metadata and counts, but cannot independently rerank every row.
- The 12 seeds vary synthetic ownership and training randomness on one fixed CICIDS2017-derived capture; they are not independent sites or captures.
- No sealed final-test or qualified external-method outcomes were accessed.
- Confidence intervals are descriptive whole-seed bootstrap intervals; no confirmatory significance claim is made.
