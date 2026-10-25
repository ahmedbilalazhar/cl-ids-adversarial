# Executed reference report — 24 October 2026

## Outcome

**Data and taxonomy adopted; one clean DR+DC CPU reference completed; exact
round-boundary recovery passed. The GPU grid remains gated.**

This is implementation/development evidence. It is not a final research result,
a successful defense demonstration, a tuned baseline, or a publication-readiness
certification. The [protocol](../../configs/phase3/reference74-v1.json) was fixed
before evaluated model outcomes. Final-test features were not exported or used.

## Adopted data and taxonomy

The corrected author release uses **74 predictors**, omitting both header-total
fields. Its 16 source annotation classes are retained, with Thursday
Infiltration - Portscan and Friday PortScan treated as distinct **capture
scenarios**. The claim is new annotated-class acquisition. Underlying technique
novelty and zero-day detection are not established by those labels.

The hash-checked audited graph/split has 1,362,527 retained records and 1,130,292
components. The builder independently reproduced benign selection, seed-101
component ownership and every exported training/development FP32 input from the
frozen Monday-only transform. It exported 183,045 training and 272,506
development rows. Component overlap across the three roles is zero; final-test
rows exported: **zero**. The graph itself was reused from the pinned audit,
whose reconstruction and exact split-reuse evidence remain available.

A second complete execution of the final preparation code reproduced **all 26
prepared files byte-for-byte**, including worker/evaluator arrays, manifests,
ownership and scaler files. [Rebuild evidence](evidence/preparation-rebuild.json)
records their hashes. Both builds reused the same pinned upstream audit assets.

See [preparation evidence](evidence/preparation-report.json),
[taxonomy and support](../../configs/phase3/taxonomy-v1.json), and the
[submission amendment](../../submissions/phase3-methodology-amendment.md).

## Executed trajectory

Five simulated clients, development seed 101, clean labels, three rounds per
stage, one local epoch per round, batch 128, replay capacity 500/client,
learning rate .001, lambda_y=1, lambda_z=.5. Settings were untuned and fixed for
this reference. The final model contains 18,896 parameters.

| Stage | Fresh rows before admission | Distinct admitted current rows | Active head |
|---|---:|---:|---:|
| E1 | 7,658 | 7,658 | 3 |
| E2 | 106,239 | 105,366 | 8 |
| E3 | 7,178 | 6,304 | 13 |
| E4 | 61,970 | 61,096 | 16 |
| Total | 183,045 | 180,424 | — |

The run made 4,257 local optimizer updates, 541,272 current-record exposures and
544,256 replay-record exposures. Exactly 180,424 first-pass reservoir proposals
were made; repeated rounds did not reinsert the current stream. Final occupancy
is 500 records on each of five clients. Replay can exceed current exposure
because its batch size stays 128 when the current last batch is shorter.

Measured reference-loop wall time was **79.31 seconds** on the recorded Windows
CPU, single thread, FP32, PyTorch 2.7.0+cpu/NumPy 2.3.5. This includes the loop's
scoring/checkpoint work, excludes preprocessing and environment setup, and is
not a Kaggle GPU-time estimate or a performance benchmark comparison.

## Correctness and recovery evidence

The [acceptance report](evidence/acceptance.json) contains **174 passing bounded
checks**. It checks the observed class widths, quotas, distinct-current FedAvg
weights, first-pass proposal counts, fresh Adam broadcasts, buffer uniqueness
and capacity, lossless PCG64 representation, and replay batches independent of
the current last-batch length.

A fresh process restored E1-R2 and re-executed the remaining ten rounds. At
**every** subsequent checkpoint, model/replay/admission/dropout arrays, cursor,
counters, ledger and complete RNG states matched exactly. The recovered NPZ
payload SHA-256 hashes also matched the uninterrupted files. Recovery is the
same logical trajectory, not an additional research replicate.

The runner checks finite scores, teachers, objectives, gradients, Adam state
and parameters. Client updates start from immutable copies of the same
broadcast. Admission occurs after head expansion and stays locked for the
stage. Teachers are computed before the update; replay is drawn before current
insertion; only the admitted first pass proposes reservoir insertions.

This is bounded evidence on the executed clean DR+DC path. It does not exercise
every edge case, including a zero-current client, corrupted labels, EI
importance, matched DM/DQ, ablations or CUDA behavior. Those remain explicit
acceptance work before a complete experiment grid.

## Development outcomes: clean learning is still weak

All predictions use the full active head, including rare trained outputs.
Eligible multiclass scoring and full-seen descriptive binary scoring use
separate banks. The benign denominator is a fixed cross-period mixture of
216,158 development records at every stage. It is not contemporaneous traffic.

| Stage | Eligible macro-F1 | Benign false-alert rate | Full-seen development rows |
|---|---:|---:|---:|
| E1 | 0.4178 | 1.7945% | 217,545 |
| E2 | 0.4640 | 9.3820% | 251,789 |
| E3 | 0.3945 | 18.2542% | 253,014 |
| E4 | 0.3682 | 24.5196% | 272,506 |

Untargeted new-annotation acquisition A is 0.2031. E1 SSH recall and E4 Bot
recall are zero under these settings. High Hulk recall does not establish good
acquisition across classes or an acceptable benign alert burden.

At E4 the combined benign error comprises 51,569/214,589 original-background
alerts (24.0315%) and 1,432/1,569 remapped-attempted alerts (91.2683%). Both
denominators were fixed by the data policy. Original-background annotations are
not certified benign ground truth; the attempted subgroup also need not match
an operator's definition of a false alarm. The combined FAR remains the
declared benchmark endpoint.

These observations identify a development problem, not its cause. The fixed
3,500-per-stage benign selection creates a training prevalence different from
the development bank, and forgetting/class imbalance are plausible contributors.
No causal attribution or effective remedy has been established. Do not change
the split, feature transform, taxonomy, support floor or benign pool to improve
these observed scores silently. A changed training objective or sampling policy
would require a prospective amendment and matched development work.

Complete confusion counts, rare-class missingness, Hulk error partitions, benign
subgroup counts and continual-learning matrices are in
[development-metrics.json](evidence/development-metrics.json).

## Preserved correction

The first implementation execution permuted the admitted pool directly. The
paired-arm convention calls for a full local-current permutation followed by
the admitted subsequence. It was superseded before development prediction or
final-test inspection, corrected, and rerun from initialization with the same
data/seed/settings. Its [invalidation record](evidence/superseded-attempt.json),
checkpoints and source snapshot remain traceable. Only the corrected reference
is evaluated here.

## Next gate

Implement and accept FT/EI and the matched admission/control/corruption paths;
then run the declared clean development pilots and tuning. Compare the required
anchor/Hulk acquisition cells across all development seeds before selecting
settings. Confirm the eventual GPU runtime and measure complete logical jobs.
Freeze scope, versions and analysis before evaluating the final-test bank.
The current reference cannot dispatch that grid.

Exact commands and state-flow diagram: [README](README.md).
