# Executed CPU milestone report — 24 October 2026

Implemented v2 and passed 33 focused tests, 594 full-data integration checks, 84 v1 integrity checks and all 174 preserved v1 bounded checks.

Development: clean_gate_failed_final_grid_blocked. Common budget: [3, 1]. 78 logical clean rows, 69 physical clean executions, 9 exact aliases; three independent development seeds. Poisoned FT diagnostic rows completed: 0/3.

Final-test inference and the GPU grid remain sealed. The twelve final seeds and one 29-contrast family are unchanged. These are development outcomes and bounded software evidence, not publication or efficacy certification.

## Clean tuning acquisition gates

| Learner | Feasible configurations | Selected |
|---|---:|---|
| DR | 0/12 | None: clean gate failed |
| EI | 0/6 | None: clean gate failed |
| FT | 0/2 | None: clean gate failed |

Every candidate and its three per-family gate cells are retained in [tuning-selection.json](evidence/tuning-selection.json). Scores, confusion tables, exposure counts and losses remain available for poor candidates. No candidate is silently promoted when all gates fail.

## Untuned filtered controls

| Arm | E1 macro-F1 | E2 | E3 | E4 | E4 benign FAR |
|---|---:|---:|---:|---:|---:|
| DC | 0.4178 | 0.4640 | 0.3945 | 0.3682 | 24.52% |
| DM | 0.4178 | 0.5767 | 0.4254 | 0.4875 | 16.55% |
| DQ | 0.4178 | 0.5547 | 0.4755 | 0.4940 | 17.02% |

These are one-seed default-setting control checks, not separately tuned arms or independent replicates. All registered rare logits remain active. The DC model/replay/dropout/admission state matched v1 at all 12 checkpoints; its independent evaluator reproduced every v1 confusion count. All 10 in-process recovered suffix payloads matched exactly.

Fresh-process DR and EI recovery each reproduced all ten strict metadata records, typed states and the full ledger exactly. Complete recovered collections passed 24 additional checks, including identical development prediction arrays and counts at all four stages and rejection of mismatched lineage/manifest. Collections preserve prefix/suffix lineage and add no independent replicate. See [recovery evidence](evidence/recovery-assembly-acceptance.json).

## Measured CPU work

| Learner | Physical clean jobs | Loop median seconds | Min–max seconds |
|---|---:|---:|---:|
| FT | 9 | 52.89 | 47.27–53.86 |
| EI | 21 | 64.73 | 57.86–69.17 |
| DR | 39 | 81.39 | 35.48–114.18 |

Component timings are in [cpu-profile.json](evidence/cpu-profile.json). These are measured CPU workloads, not GPU-hour forecasts. No training-loop optimization has been promoted on timing alone.

## Interpretation and remaining gates

Observed weak learning is not a demonstrated cause. The immutable training inventory is highly skewed, and the development bank has a different benign prevalence. Controlled learning-rate/synchronization/retention comparisons are preserved in the full grid. Inspect actual confusion sources, stage losses and acquisition/retention curves before proposing an objective or sampling amendment. No split, calibration, taxonomy, benign inventory, eligibility or bank was altered to improve scores.

No CUDA/runtime agreement, optional ablation/intervention acceptance, final-test predictions or final statistical analysis has been exercised. Clean infeasibility requires a prospective scientific revision before final testing. The failure and completion inventories identify missing paths without imputing metrics.

Requirements map: [requirements-to-evidence.json](requirements-to-evidence.json). Commands and identity boundaries: [README](README.md). Corrections and amendments: [log](defects-and-amendments.md).

## E1 training/development diagnostic patterns

These counts summarize physical development executions across settings and schedules; they are not independent research replicates. A high-training/low-development cell uses recall >=0.50 on training and <0.50 on development. Both-low uses recall <0.50 in both banks. These are descriptive diagnostics, not new selection gates.

| Learner | Annotation | Physical checks | High train / low dev | Both low |
|---|---|---:|---:|---:|
| FT | FTP-Patator | 9 | 0 | 5 |
| FT | SSH-Patator | 9 | 0 | 9 |
| EI | FTP-Patator | 21 | 0 | 11 |
| EI | SSH-Patator | 21 | 0 | 21 |
| DR | FTP-Patator | 39 | 0 | 19 |
| DR | SSH-Patator | 39 | 0 | 39 |

Complete training confusion counts, held-out error destinations, round loss/exposure curves, fixed class counts and paired learning-rate comparisons are in [learning-diagnostics.json](evidence/learning-diagnostics.json). These observations can locate acquisition/generalization gaps; they do not by themselves identify why those gaps occur.

The fixed E1 banks contain 1,776 SSH training records and 592 SSH development records. All 69 physical E1 checks had SSH recall below 0.50 on both banks. This documents weak acquisition in the fitted training population as well as the held-out bank; it does not establish a mechanism.
