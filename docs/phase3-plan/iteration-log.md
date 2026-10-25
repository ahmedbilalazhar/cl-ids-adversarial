# Iteration log

## Iteration 1 — initial research and scope correction

Date: 23 October 2026 (client date). Status: ongoing.

### Findings that materially change the plan

1. **Current implementation is not the revised proposal.** The EWC code still squares mini-batch mean gradients; DER++ stores post-update logits, repeatedly inserts observations and randomly prunes an overflowing list; the data builder uses older splits and scaling. Implementation reconciliation comes before any large run.
2. **GPU use must be measured.** The proposed MLP has only 19,087 maximum parameters. Launch/synchronisation overhead may dominate. Benchmark the complete representative workload on CPU and available GPUs before choosing the execution device; no speedup is assumed.
3. **Ablations are mandatory in Phase 3.** The Phase 2 core-only fallback omitted ablations. A viable course-submission fallback must preserve a small, meaningful ablation package, even if DG and the external dataset are deferred.
4. **Account capacity clarified.** The user clarified that eight accounts would belong to eight different people. Model this as individually operated contributor accounts, with separate worker assignments and no credential sharing.
5. **Use paired seed blocks as the scheduling unit.** Assigning methods to different hardware would confound the comparison. Keep the methods and doses for each paired seed on the same recorded hardware environment where feasible.
6. **Prefix reuse is useful but not a universal 20% speedup.** E1 can be shared only when the complete prefix semantics match. Stage sizes differ greatly, so stage-count reductions must not be presented as runtime savings.
7. **New prior art needs attention.** SacFL (2025) already studies adversarial tasks in federated continual learning on image/text data. The contribution must be narrower than a general claim to first combine poisoning with FCL.
8. **The paper should prioritize a controlled empirical finding.** DC is a simple new-label-protection rule in this schedule. Treat it as a falsifiable comparison and avoid presenting it as a demonstrated general defence.

### Scope

The work is a plan and evidence audit. It does not change the runtime implementation, execute tests/training, publish datasets, consume Kaggle GPU quota or report invented performance results.

## Iteration 2 — attribution, prior art and execution accounting

Date: 24 October 2026 (Asia/Karachi). Completed review pass; broader research continues.

1. **Eight workers still simulate five clients.** Each contributor runs whole paired blocks locally. Cross-account distributed training would add complexity without serving the methodology.
2. **Stronger prior-art overlap found.** Neurotoxin addresses durability after an FL attacker stops; single-task poisoning addresses weak one-stage adversaries; FIL-ZTA combines network-context federated incremental learning with poisoning. AER/ABS and PuriDivER already address noisy replay. The publication plan now centers on a narrowly identified empirical finding.
3. **Quota creates a poison-retention floor.** For local honest benign count b, poison count q and benign quota K, at least `max(0,K-b)` poisoned rows must be admitted. DM shares the same total rejection limit. The new diagnostics distinguish ranking limitations from limited rejection capacity.
4. **Continuation forks have a different estimand.** Removing a term from E3 onward can save E1/E2 training but does not replace removing it from the beginning. A separate optional fork package includes clean controls and explicit physical-versus-logical counts.
5. **Development reuse can save nine full executions.** Selected-budget pilot defaults appear in the tuning grid. When complete identity matches, 81 logical development rows require 72 distinct full executions. No code repair may be hidden behind reuse.
6. **Oracle controls can be aliases.** Original diagnostic pairs have 24 logical rows but can require only 12 new suffix executions. Controls do not add independent replicates.
7. **Prefix reuse is specified concretely.** Core/complete E1 prefix counts can shrink to 3/8 per final seed under the documented compatibility conditions, without changing the logical run matrix.
8. **Machine-readable plans saved.** The largest candidate has 729 logical full trajectories; package memberships and worker assignments are explicit. The 29-test family is separately enumerated. Neither file is runnable before protocol lock.
9. **Numerical and statistical details tightened.** The plan distinguishes eval/no-grad/inference mode, independent replay sizes, signed-rank tie arithmetic, sign-symmetry assumptions and one-time application of quota reserve.
10. **Canonical release remains a gate.** Local raw files lack the required endpoint/time metadata. Corrected CICIDS2017 releases are contextual alternatives/sensitivities, not interchangeable replacements or independent captures.

The source ledger now contains 35 primary references. A newly located author repository discloses historical evaluation limitations; the comparison plan keeps paper-reported and corrected reproduction evidence separate.

## Iteration 3 — concrete data, interfaces and operational feasibility

Date: 24 October 2026. Completed review pass.

1. A bounded public-archive inspection verified consistent 91-column metadata-bearing headers in five corrected CICIDS2017 day files. The all-header probe transferred 21,174 bytes; an earlier probe transferred 8,760. No full archive, row/support census or file CRC was verified.
2. The corrected source is a fallback requiring an explicit release/label/feature amendment. `Attempted Category` is annotation metadata, not a predictor. A provider form's returned error text is not proof that its actual download route is unavailable.
3. The data contract now separates T0 fitting IDs from linked exclusion closure, preserves provenance before deduplication and checks actual FP32 inputs before final allocation.
4. The implementation breakdown has two-author ownership, typed interfaces, legal state transitions and concrete acceptance evidence. Initial-head initialization, DG rounding and rational quota arithmetic are explicit pre-development decisions.
5. The quota review distinguishes aggregate capacity from per-person packing. A balanced hypothetical allocation is provided; no account quota or runtime has been measured.
6. The current Phase 2 diagrams were rendered and visually reviewed. The Phase 3 diagrams clarify next-stage transitions, client-local scoring, logical server versus experiment archive, and eight compute workers versus five simulated clients.

## Iteration 4 — attribution and evidence integrity

Date: 24 October 2026. Completed planning review; final delivery artifacts are checked separately.

1. **Absolute error accompanies H.** A large clean error can conceal susceptibility through a ceiling. Lower H alone cannot establish a safer detector.
2. **Acquisition F1 needs confusion context.** Hulk remains a negative in untargeted-family F1, so new-family precision/recall must accompany A.
3. **Closer prior work narrows the finding.** Lavaur et al. already stop FIDS label-flipping attacks and report accuracy recovery. Our fresh-source availability and class-arrival differences prevent a direct contradiction claim.
4. **Withdrawal means no fresh corruption.** The affected client remains active and retained wrong labels/logits can continue influencing optimization.
5. **Tuned pipelines are not isolated retention effects.** A conditional same-rate FT reference can add at most 24 full trajectories if stronger attribution is intended.
6. **Cache identities now distinguish prefix and full runs.** Future-irrelevant configuration fields can be excluded only through a documented prefix dependency projection; the consumer retains its full run identity.
7. **Telemetry is bounded.** Detailed replay exposure can be reconstructed from exact index/RNG state after reference verification; storing every draw is not the default.
8. **Data treatment stays fixed.** Eligibility/ownership/attacker selection freeze before corruption/admission; rejection of a hard class cannot remove it from evaluation. Mandatory mixed components and cross-stage benign selection need an explicit whole-component rule.
9. **Failures remain visible.** Unrestorable endpoints are unavailable, with p=1 only for fixed-family Holm bookkeeping. Method instability is not automatically a pipeline defect or a reason to replace a seed.
10. **Focused recommendation.** The course package is 393 logical full trajectories; adding DQ gives 441; adding an audited external admission replication gives 513. The 729-row candidate remains an optional menu. Conditional same-rate/cross-runtime work is separate.
11. A document-only audit checked manifest/contrast counts, pairing, aliases, links, source IDs, bounded-header evidence and payload arithmetic. It does not validate the future model implementation or data-support feasibility.

The final broader six-month terminology refresh found STAIN-FL as abstract-verified FL durability context; unrelated watermarking/packet-evasion results were excluded by scope. It did not change the recommended experimental matrix. The evidence ledger contains 47 primary sources with verification limits. A 24-page printable plan was rendered and visually reviewed, including both workflow diagrams. No model tests, training, Kaggle uploads or final experimental results were produced.

## Iteration 5 - source feasibility and exact contracts

Second audit began 24 October 2026 at 03:16:08 UTC. Full archives replaced the earlier bounded-header uncertainty with verified candidate identities and complete censuses. The original CSV blank tail, ambiguous source clock, corrected E3 support/taxonomy, invalid feature domains and actual FP32 collisions were measured. Calibration eligibility was made independent of future labels; canonical component IDs replaced internal union-find roots. Superseded evidence remains labeled and no model outcome selected either change.

## Iteration 6 - feasibility, causal scope and delivery

The screened corrected fixed split has zero component overlap and required anchor/source/stage support through Infiltration-Portscan. Heartbleed is test-only, so sixteen annotations yield fifteen train-supported outputs. Benign bundles reach 3500 examples per stage. Per-seed source exposure ranges widely; quota bounds force retained poison in ten maximum-dose inventories, up to a 74.7% retained fraction even with perfect ranking. These are data arithmetic, not model effects.

Capture-context evidence shows every retained Hulk and FTP example in one endpoint-pair/protocol key shared across roles; component isolation is not host/campaign isolation. The evaluation review adds false-alarm/absolute-error reporting, full-seen versus eligible banks, uncertainty/power limits, scoped controls and reproducibility gates. The combined register now runs G01-G62, with 30 prospective amendment entries and 57 primary sources. Two PDFs and three standalone PNG/SVG figures document the audit. No revised learner, tests, training, Kaggle uploads or model performance were produced. Final delivery/review identities are recorded separately.

## Iteration 7 - source semantics and an explicit schema amendment

The task tracker showed about two hours of active work after the extended wall-clock review, so a further active review was undertaken. Pinned author code casts header totals to int16; observed positive minimum-total violations survive the earlier negative-value screen. A separate 74-feature candidate omits those fields rather than pretending unsigned conversion repairs them. It preserves the as-published corrected candidate's row/label/component/fit identities exactly, allowing proved fixed-split reuse only. Fresh ownership and annotation-provenance audits were executed; no learner state/settings may alias across dimensions.

The 74-feature candidate has 183045 selected fresh records, four exact 3500-row benign pools and sixteen train-supported outputs. Ten maximum-dose seed inventories still force retained poison, with a maximum forced fraction 74.7%. Its benign test inventory contains 214553 original-background annotations and 1605 remapped attempts, motivating separate descriptive errors. The actual notebook/archive Thursday/Friday scan naming differs from the website prose; semantic taxonomy remains an adoption gate. Generic Active/Idle timestamp concerns were not attributed to this archive without supporting values. The register extends through G64 with A31/A32 and 58 primary sources. No model tests, training or predictive outcomes were generated.
