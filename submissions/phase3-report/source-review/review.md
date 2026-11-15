# Review of Saneed's earlier Phase 3 report

Source: C_NET_Project (3).pdf, 15 pages, and the TeX pasted by the user. The PDF existed in Downloads at the supplied path but was absent from the GitHub submission folder; the first generated report did not use this source. Both originals are preserved here for provenance.

## Material retained and strengthened

- Original pp. 4-6: consolidated baseline evaluation, binary detection, class support and confusion matrix. Recomputed macro precision/recall and binary accuracy/TPR/FPR/precision/F1 now accompany the corrected eligible-bank macro-F1. The full-inventory confusion heatmap is regenerated from the original 12 clean DR run matrices.
- Original p. 6: acquisition, backward transfer and forgetting. Recreated with partition-level points and clearly descriptive training variation.
- Original pp. 7-11: attack, admission, memory and component views. Retained in corrected plots/tables; all 14 original reference/ablation settings are tabulated using matched clean twins. Attack topology remains explicit instead of fitting one universal corruption curve.
- Original pp. 12-14: published-research context and explicit gap/objective check. Extended with primary-PDF verification and precise limits; no cross-paper superiority or difficulty ranking is asserted.
- New evidence: the completed CPU replay intervention, DQ check and offline pooled reference; source/state/input identities and empirical outcomes are kept separate from GPU results.

## Corrections required before reuse

1. Original pp. 1, 3, 7-13: H changed from the Phase 2 targeted-ASR endpoint to final recall loss. The revised report restores mean E3/E4 clean-matched targeted ASR and names final recall damage separately.
2. Original p. 3 and Tables 8/10: separate C1/C2 corrections and inference over 12 dependent units do not reproduce Phase 2's single family or independent-seed design. Revised contrasts are exploratory, with partition aggregation, exact conditional sign enumeration, explicit tie/zero handling, and combined corrections.
3. Original p. 2: the attack expansion is not presented as an executed prospective registration. The revised report labels outcome-informed threat expansion as exploratory and removes the unsupported implication of identical final seed coverage.
4. Original p. 2: remove the red instructor-feedback placeholder; state only that specific feedback was not provided.
5. Original pp. 1, 8, 13: the blanket no-admission-benefit claim overstates the severe-arm result. The revised report distinguishes moderate corruption and the random quota control.
6. Original Table 9: NONE admits 100% and is not volume-matched to the three filtered conditions. Only DC/DM/DQ share the matched quota volume.
7. Original p. 7: poison remaining in memory alone does not prove why error persists. The new oracle-versus-random CPU intervention provides more specific evidence; class composition and later draws remain interpretation limits.
8. Original pp. 11-12: similar nmin outcomes do not prove global threshold irrelevance. Likewise, lambda sensitivity does not establish that a universally weak EI penalty caused baseline collapse.
9. Original p. 12: do not generalize WeiDetect's auxiliary-data sensitivity experiment to a universal requirement of at least 90% trusted data. Its primary PDF states a server auxiliary labelled validation set and evaluates different volumes.
10. Original pp. 11-12: different datasets, label spaces and attacks do not establish that our problem is categorically harder or that one reported accuracy/F1 dominates another.

## Primary verification of selected comparisons

Guo et al., primary PDF Table 6/12: reported CIC-IDS2017 average accuracy 83.4%, F-score 82.1%, and 76.4% F-score without DP-Means memory. Preserve these as paper-reported values, not local reproductions.

Banbhrani et al., primary PDF Sections 5.4-5.5: ten-client sign-flipping model-update attack, 89.3% binary accuracy with 30% malicious clients, and 4.6% honest-client rejection at the selected trust threshold. Client rejection is distinct from training-row rejection; sign flipping is distinct from supplied-label corruption.

Liu et al., CNS 2022 project page: the actual improved dataset release used here, with documented orchestration, feature and annotation errors. The 2021 troubleshooting paper is historical context rather than the precise 2022 release citation.

The revised bibliography uses a relevant, verified selection rather than copying every Phase 1/2 reference. Native LaTeX citations/bibitems are self-contained for Overleaf.
