# Executed v3 CPU implementation report — 2026-10-25

The budget revision is implemented and verified. Clean development feasibility: True. Selected common budget: [12, 1] (rounds,epochs).

78 logical clean rows, 69 physical clean conditions, 69 actual clean attempts and 9 exact aliases across three development seeds. Completed selected-condition FT poison diagnostics: 3/3. No final-test inference or GPU dispatch occurred.

## Selected clean settings and acquisition gates

| Learner | Settings | Feasible candidates | Mean E1 FTP | Mean E1 SSH | Mean E2 Hulk | Selected mean four-stage macro-F1 |
|---|---|---:|---:|---:|---:|---:|
| DR | LR=0.001, lambda_z=0.1, lambda_y=1.0 | 6/12 | 0.6667 | 0.9983 | 0.9998 | 0.6676 |
| EI | LR=0.001, lambda_E=100.0 | 3/6 | 0.6667 | 0.9972 | 0.9997 | 0.3484 |
| FT | LR=0.001 | 1/2 | 0.6667 | 0.9972 | 0.9997 | 0.3108 |

All per-seed counts, failed/infeasible settings and stage outcomes remain in the indexed evidence. Mean gates were not changed into per-seed exclusions. Exact score ties use the documented infrastructure-cost disposition and then the original numeric order.

## Controlled corruption diagnostic

- Seed101, poisoned-minus-clean Hulk-to-benign error: E2: +0.0001, E3: +0.2493, E4: +0.0000.
- Seed102, poisoned-minus-clean Hulk-to-benign error: E2: +0.0000, E3: +0.0000, E4: +0.0000.
- Seed103, poisoned-minus-clean Hulk-to-benign error: E2: +0.0000, E3: -0.0009, E4: +0.0000.

| Seed | Persistent excess Hulk-to-benign H | E2 source-recall change |
|---|---:|---:|
| 101 | +0.1246 | -0.0001 |
| 102 | +0.0000 | +0.0000 |
| 103 | -0.0004 | +0.0000 |

These are paired maximum-dose development diagnostics, not final security estimates or a trigger-conditioned backdoor test. Weak/negative effects are retained. The full poisoned EI/DR/filter grid has not been executed.

## Matched clean controls

| Arm | E1 macro-F1 | E2 | E3 | E4 | E4 benign FAR |
|---|---:|---:|---:|---:|---:|
| DC | 0.7037 | 0.6535 | 0.5870 | 0.5268 | 20.27% |
| DM | 0.7037 | 0.8019 | 0.6231 | 0.6353 | 12.66% |
| DQ | 0.7037 | 0.7662 | 0.6450 | 0.5717 | 13.64% |

One paired engineering seed101; settings source: selected_feasible_DR. All adverse outcomes remain valid. Matched current counts, aggregation weights and named-stream positions do not imply identical retained IDs or later learned models.

## CPU worker costs

| Learner | Process total s | Training loop s | Eval s | Peak process MiB | Batch1 median ms | Batch256 median ms | Local bundle MiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| FT | 263.81 | 228.26 | 7.93 | 368.0 | 0.3484 | 0.7727 | 10.62 |
| EI | 312.47 | 261.04 | 10.35 | 375.2 | 0.3735 | 0.8587 | 39.44 |
| DR | 346.38 | 307.11 | 9.03 | 373.7 | 0.1511 | 0.4442 | 30.60 |

Fresh CPU processes include imports, validation, training/checkpointing, independent development evaluation, state verification, latency/serialization probes and local export. Process peaks include native-library allocations and verification. These are measured local worker jobs, not GPU forecasts; dependency installation and remote transfers are unmeasured. Communication tables distinguish raw parameters and concrete model-template serialization from actual network transport, which the sequential simulator does not implement.

## Verification and disposition

Passed 9 v3 test groups, 3 extended-poison groups, 559 full-data compatibility checks, 1080 full-data matched-control checks, and 104 fresh-process recovery/prediction checks. The separate fixed29 analysis implementation passed 11 synthetic fixtures; it read no final endpoint.

Infrastructure timing remeasurements: 2. Original wall-clock records remain immutable. Exact replay state/ledger checks qualify replacement logical costs; the derived selector records whether any exact-score tie changed. Profiling repetitions, recovered suffixes and cached aliases add no independent research replicate.

An independent count-only audit reconstructed endpoints for 81 valid logical development rows and the three matched engineering controls, retaining registered rare prediction columns and the fixed full-seen FAR bank. Eight deliberately corrupted count artifacts were rejected. This checks count arithmetic and lineage; it does not repeat model inference.

V1/v2 source/evidence and the E1 diagnostic remain preserved. The original v2 clean failure and all v3 outcomes are part of development history. The revised budget meets all clean development gates. These results do not establish a poisoning defense, novel attack-technique acquisition, deployment validity or publication acceptance.

Remaining gates: Actual pinned/confirmed GPU runtime and full worker costs; Final scope/code/data/analysis freeze; Complete validated final matrix before final analysis. Instructor feedback is still unavailable. All registered rare outputs stay active, binary/full-seen and eligible multiclass banks remain separate, and the fixed cross-period benign union is not a deployment prevalence forecast.

[Commands](README.md), [decisions](decisions-2026-10-24.md), [amendments](defects-and-amendments.md), [timing disposition](cost-amendment-2026-10-24.md), [requirements map](requirements-to-evidence.json) and [evidence index](evidence/artifact-index.json).
