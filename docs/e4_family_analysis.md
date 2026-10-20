# E4 per-family score audit (2026-09-28)

Post hoc and exploratory: same AE-retraining scheme as the runner and the
threshold audit (benign 80/20 fit/calibration split, seed+task), seeds 1–3
on `tasks_chrono_dedup`. Per-family medians plus one-vs-benign AUCs.
Changes nothing about the q0.95 primary threshold and estimates no
poisoning effect. Source: `results/diagnostics/e4_family_scores.json`,
reproduce with `python scripts/audit_family_scores.py --seeds 1 2 3`.

## Result (stable across all three seeds)

| Task | Family (n) | Median | One-vs-benign AUC, seeds 1/2/3 |
|---|---|---:|---|
| T1 | FTP-Patator (1779) | 0.106–0.113 | 0.165 / 0.164 / 0.168 |
| T1 | SSH-Patator (966) | 0.131–0.150 | 0.038 / 0.060 / 0.053 |
| T1 | Benign (1500) | 0.237–0.260 | — |
| T2 | DoS Slowloris (1613) | 6.3–6.4 | 0.775 / 0.816 / 0.771 |
| T2 | DoS Slowhttptest (1568) | 12.1 | 0.971 / 0.972 / 0.970 |
| T2 | DoS Hulk (51852) | 12.2–12.4 | 0.894 / 0.909 / 0.900 |
| T2 | DoS GoldenEye (3086) | 7.7–7.8 | 0.939 / 0.943 / 0.941 |
| T2 | Heartbleed (3) | ~1700 | 0.999 (n=3: unstable, do not cite) |
| T3 | Web Brute Force (441) | 0.38–0.41 | 0.630 / 0.655 / 0.658 |
| T3 | Web XSS (196) | 0.38–0.42 | 0.637 / 0.666 / 0.670 |
| T3 | Web Sql Injection (6) | 0.63–0.67 | 0.797–0.805 (n=6: unstable) |
| T3 | Infiltration (11) | 4.7–4.9 | 0.952–0.953 (n=11: unstable) |
| T4 | Bot (431) | 0.126–0.135 | 0.006 / 0.006 / 0.006 |
| T4 | PortScan (587) | 0.39–0.41 | 0.473 / 0.499 / 0.472 |
| T4 | DDoS (38404) | 9.2–9.4 | 0.689 / 0.711 / 0.684 |
| T4 | Benign (1500) | 0.328–0.334 | — |

Cross-checks: T1 benign medians (0.237–0.260) match
`e4_detector_cap_audit.md` (0.237–0.260); pooled T1 AUC 0.120–0.128 is the
mixture of 0.165 and 0.038; T4 pooled 0.673–0.700 is Bot dragging against
DDoS lifting.

## Reading

- The detector is not uniformly weak: volumetric DoS reconstructs far above
  benign (AUC up to 0.97); interactive brute-force families (SSH-Patator,
  FTP-Patator, Bot) reconstruct *below* benign — Bot at AUC 0.006 is
  essentially perfectly misranked. PortScan is chance-level.
- Small-n AUCs (Heartbleed 3, Sql Injection 6, Infiltration 11) are reported
  for completeness and must not be cited as family characterizations.
- No mechanism is established. A candidate hypothesis (unproven): brute-force
  flows sit inside the benign manifold in standardized space so the
  benign-trained AE generalizes to them. Testing it needs a separately
  specified protocol (e.g., per-family distance-to-benign-centroid analysis
  on a development split), not more cuts of these outcomes.
- Consequence for the detector gate: any redesigned detector must be judged
  per family, and T1/Bot/PortScan performance — not pooled AUC — is the bar.
  The q0.50 post hoc check from the threshold audit would still miss most
  SSH-Patator/Bot while multiplying benign alerts; it is not a fix.
