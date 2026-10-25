# Failure handling and methodology amendments

Proposed policy, 24 October 2026. Freeze it with the final protocol. A weak effect, an unstable method and a broken artifact are different events and require different responses.

## 1. Failure taxonomy

| Event | Classification | Response | Reporting consequence |
|---|---|---|---|
| Runtime ends, quota expires or VM disconnects | Infrastructure interruption | Continue from a compatible complete checkpoint or redo the same assigned execution | Retain interruption/retry cost; not an extra replicate |
| Source/data/runtime hash mismatches | Input/environment incompatibility | Stop before learning or quarantine the incompatible output | No valid performance result from that artifact |
| Output payload is incomplete/corrupt | Artifact failure | Recover/re-export exact state where possible; otherwise rerun the same condition | Never infer completion from a CSV's existence |
| Deterministic non-finite loss/gradient/state under a correct locked method | Scientific training instability | Retain the seed/condition and failure evidence; do not switch to a favorable seed | Failure rate is a result; affected primary endpoints may be unestimable |
| Verified implementation defect | Pipeline invalidation | Document defect/version/affected dependencies; repair and rerun the complete affected matched set | Superseded artifacts remain traceable and cannot support claims |
| Weak/null poisoning effect | Valid experimental outcome | Keep the primary threat and all seeds | Report magnitude/uncertainty and actual exposure |
| Defense harms acquisition or benign FAR | Valid adverse outcome | Analyze the trade-off and retain comparisons | Do not remove the arm or reweight endpoints after testing |
| Rare family below predeclared support | Benchmark eligibility outcome | Train when supported; descriptive scoring only | No silent “whole dataset” performance claim |
| Contributor cannot finish | Scheduling problem | Reassign unstarted/resumable work to a compatible worker | Missing pairs remain visible until completed |

## 2. Numerical instability must not disappear through exclusion

Pre-final development checks should detect obvious scaling or optimizer problems. If a correctly implemented final condition still becomes non-finite, it is not automatically a software bug. Investigate and report whether it is method instability, invalid input or infrastructure failure.

Do not delete the seed, draw a new seed, average only successful repetitions, silently clip gradients or assign a convenient F1/ASR value. A metric from a model that never completed training is undefined unless a failure utility was prospectively specified. The original 29-test analysis may then be incomplete; report this explicitly rather than presenting a complete twelve-seed claim.

A separate conservative sensitivity can bound conclusions under explicit failure outcomes, but must be labeled exploratory. Do not present it as the original metric. If a protocol change is necessary, create a new version with its own analysis scope and disclose that it followed the observed failure.

## 3. Development selection failures

- A tuning configuration is eligible only if all required development trajectories complete validly. Do not average its macro-F1 over a smaller favorable subset.
- A synchronization budget with an invalid required learner cannot be selected from a mean over the remaining learners without a declared amendment.
- If all candidates for a required learner fail clean-learning/numerical gates, stop and revise before final testing.
- A maximum-dose FT diagnostic with little effect is not a failed gate and does not justify attack escalation.

A completed final model with poor clean recall is a valid poor result, even if it falls below a development acquisition threshold. The development gate is not a post-hoc final-seed exclusion rule. Retain its defined counts/endpoints and show absolute source error/clean headroom. Distinguish failure to learn from non-finite training or a corrupt artifact.

The implementation should define invalid/NA handling before reading development results. Development can guide settings within the specified grid; final test outcomes cannot.

## 4. Recovery versus rerunning

Recovery restores the complete next-transition state of the same scientific run. A retry executes the same condition because a recoverable infrastructure artifact is unavailable. Neither creates a new sample.

If two completed retries differ, retain both execution records and explain the cause. Select by a predetermined identity/completeness rule, never by higher performance. Conflicting supposedly deterministic outputs are a reproducibility issue to investigate before promoting one to final analysis.

Resume only from committed checkpoints with matching code/data/config/runtime identities. A round-boundary checkpoint is simpler because the next broadcast resets Adam. Mid-round state requires a client cursor, partial aggregate and local optimizer/batch state; it cannot be reconstructed from weights alone.

## 5. Amendment record

Every change to scientific behavior should record:

```text
amendment_id, date/time, authors
original requirement and reason for change
what evidence was already visible: data census / development / final outcomes
changed data, method, threat, metric, split, seed, precision or scope fields
affected code/config/data/analysis identities
required retuning and matched reruns
which old artifacts are superseded
new confirmatory/exploratory status
```

Examples needing an amendment include a different dataset/release, reduced experiment scope, changing initial-head semantics after development, clipping/refitting the transform, new attack-site selection, post-E2 forks replacing from-start ablations, or new primary statistical tests.

Implementation corrections that restore the already specified behavior still need a defect/provenance record and affected reruns. Documentation-only clarifications can be smaller, but must not hide a behavior change.

## 6. Feedback traceability

Instructor feedback is still unavailable in this chat. Include an explicit placeholder row in the methodology-change table rather than inventing feedback. When supplied, map each item to the revised requirement, code/config location, evidence and paper section.

The user confirmed `submissions/phase2-with-claude.tex` as the source methodology. Preserve the other Phase 2 source and legacy results; their existence does not make them compatible alternatives for filling missing new evidence.

## 7. Release acceptance

The final paper/report should state the selected matrix, expected/completed/invalid counts, all exclusions and the reason for every unavailable primary result. The claim ledger may reference only validated evidence. A clean-looking summary table is insufficient when runs are missing or invalid.
