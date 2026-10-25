# Feature domains, calibration and numerical identity

Data-only audit, 24 October 2026. No learner was fitted. All counts below are conditional on the stated release, schema, clock, conservative graph and calibration rules; they are not experimental performance.

## 1. Finite is an insufficient acceptance rule

The original mirror contains negative flow durations, inter-arrival times, header lengths and minimum segment sizes. The corrected release also has negative forward/backward header lengths: 309/472 records respectively, with overlap. Both releases use -1 in initial-window fields; rejecting every negative value would incorrectly remove these declared missing-window sentinels.

The original as-published Monday calibration minimum for forward-header length is -1,929,349,973. Such values can dominate min-max scaling. A valid frozen transform can produce values outside [0,1] on later days; those values alone are not evidence of an implementation error. Do not silently clip them or refit on development/test data.

## 2. Concrete prospective quarantine candidate

Policy identifier: `nonnegative_flow_features_with_window_sentinel_v1`.

- Require the 76 projected numeric features to be finite.
- Require nonnegative values except the two initial-window fields, which accept -1 or an integer in [0,65535].
- Apply each record's own source/metadata/domain checks before Monday-only calibration eligibility. Preserve excluded records' provenance and conservative graph links.
- Do not repair signed values by unsigned reinterpretation, clip values, drop features, or inspect model accuracy to choose the rule.
- This is a limited declared domain screen. It does not certify every positive value, infer exact original extractor semantics, or prove source labels correct. Feature consistency checks and provenance remain necessary.

The rule is an amendment candidate, not an already implemented production preprocessing change. Existing raw-source reports remain historical evidence, with different populations.

| Candidate | Finite records failing the domain rule | Monday fitting records after rule | Unique survivors at 120-second gap | Survivor components |
|---|---:|---:|---:|---:|
| Original mirror, as published | Not applied | 529,466 | 1,409,081 | 987,432 |
| Original mirror, domain screened | 2,925 | 528,946 | 1,407,514 | 987,389 |
| Corrected, as published | Not applied | 371,621 | 1,362,527 | 1,130,292 |
| Corrected, domain screened | 593 | 371,516 | 1,362,039 | 1,130,077 |

Domain failures overlap other exclusion reasons; do not subtract these columns as disjoint counts. In the original screened candidate, forward/backward header calibration ranges become 0..582324 and 0..568592. In the corrected screened candidate they become 0..32652 and 0..32632. This addresses the observed negative-extreme problem; it does not establish an accuracy improvement.

## 3. Check the actual model representation

The as-published original projection loses 34,219 distinct raw FP64 inputs when transformed and cast to FP32; the corrected projection loses 368. These are cardinality losses, not numbers of distinct physical events or demonstrated meaningful information losses. Examples include tiny decimal differences that may be numerically inconsequential. The original forward-header scale has an FP32 spacing near raw zero of about 115 raw units, but that observation alone does not explain all collisions or Hulk exclusions.

Canonicalize signed zero, retain the ordered schema/dtype/transform identity, and form exact-input links on both raw projected values and final FP32 bytes. Resolve full digest equality with actual byte equality rather than assuming a truncated digest cannot collide. Quarantine conflicting annotations according to the declared reference-label rule. Do not use labels inside the feature key.

After the domain rule, the original final-input distinct count changes from 2,199,080 to 2,199,178. This small increase is evidence against claiming that the domain screen restores the original class population wholesale. Its surviving Hulk count is 1,247, versus 1,249 under the as-published conditional audit. The corrected screened candidate preserves 158,468 Hulk examples. Release changes, timestamp precision, session structure, conflict handling and feature generation all differ; this audit does not isolate their individual causal contributions.

## 4. Calibration must not depend on future labels

Choose fitting IDs solely from Monday's source-valid benign calibration inventory under the adopted domain rule. Freeze fit IDs and statistics before consulting later-day reference conflicts. Later conflict quarantine can remove records from model/evaluation use and extend T0 exclusion closure, but cannot retroactively change the fitting pool.

There are 64 original and 3 corrected fitting records whose final inputs also have conflicting annotations elsewhere. Keep their calibration-only role visible. This does not let their ambiguous copies enter training/test or justify refitting from future information.

## 5. Evidence and remaining decisions

See [feature-domain-census.json](feature-domain-census.json), [fp32-projection-collision-audit.json](fp32-projection-collision-audit.json), [original-domain-checked-component-feasibility.json](original-domain-checked-component-feasibility.json) and [corrected-domain-checked-component-feasibility.json](corrected-domain-checked-component-feasibility.json). These reports contain exact source populations, scaler statistics, family counts and 60/120/300-second sensitivity censuses.

Before a scientific lock, select one source/domain profile, publish the reason-coded exclusion precedence and actual split/support table, cross-review units and aliases, and hash the final feature arrays, fitting IDs and role manifests. A corrected filename or successful parser is insufficient evidence of those properties.
