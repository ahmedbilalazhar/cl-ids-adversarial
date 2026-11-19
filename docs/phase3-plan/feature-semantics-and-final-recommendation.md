# Final adversarial review: feature semantics and the preferred candidate

This review supersedes the earlier **recommendation** of the 76-feature negative-screened corrected candidate. Its counts remain historical candidate evidence. On 24 October 2026, the user-adopted data amendment selected the corrected 74-feature profile and resolved the taxonomy as new annotated-class acquisition; the corresponding reference trajectory passed 174 acceptance checks. The separate lambda_z=.5 implementation reference remains untuned and n=1. A later 240-run CPU development extension used the historical selection DR lambda_z=.1; see `submissions/phase3-overnight/appendix.md` and `docs/phase3-plan/phase3-overnight-independent-audit.json`. Final held-out evaluation remains gated. See `docs/phase3-reference/adoption.json` and `configs/phase3/reference74-v1.json`.

## 1. Positive values can still be corrupted

The authors' labeling notebook at commit `f0ce502818e59e6cd062720ab2286c5ff6f2bdec` casts forward/backward header totals to signed 16-bit integers. The related Java implementation accumulates header totals in long fields. This is a plausible lossy conversion mechanism, not proof that the pinned current commit uniquely produced the downloaded archive. [Primary labeling source](https://github.com/GintsEngelen/CNS2022_Code/blob/f0ce502818e59e6cd062720ab2286c5ff6f2bdec/Labelling/CICIDS2017_labelling_fixed_CICFlowMeter.ipynb).

The observed forward fields also violate their own minimum bound: total header bytes must be at least packet count times minimum header bytes, under the documented field semantics. There are 123 violations with nonnegative finite triplets in the corrected source. Sixty-five pass the earlier full domain/metadata screen, including nine fitting records and 56 unique survivors. The original candidate has zero violations of this particular relation among its nonnegative finite triplets. That does not certify its other fields.

Example: 3,462 forward packets with minimum header 20 imply at least 69,240 header bytes, but the stored total is 10,496. Merely rejecting negative values cannot remove this problem. Unsigned reinterpretation recovers at most a residue and cannot recover totals after multiple wraps. The screen is incomplete even when no obvious negative remains.

See [source-code-review-evidence.json](source-code-review-evidence.json) and [header-consistency-feasibility.json](header-consistency-feasibility.json). No third-party code was executed or copied into the learner.

## 2. Preferred prospective route: omit the two affected header fields

Use the corrected archive with its declared attempted-to-benign annotation rule and omit **Fwd Header Length** and **Bwd Header Length** before calibration, exact-input grouping and model input construction. Keep the remaining 74 ordered features and the stated domain/sentinel checks. This is A31, an explicit schema amendment to the submitted 76-feature proposal. A repaired pre-cast export is another option if its provenance and alignment can be established; full PCAP re-extraction is not the efficient default.

This choice is motivated by source/field consistency before learner outcomes. It does not certify all remaining positive values or resolve taxonomy/generalization limitations. Revisit source units and semantics whenever the extractor changes.

The 74-feature graph audit preserves exactly the earlier as-published corrected candidate's selected rows, reference labels, calibration fitting IDs, survivors, T0 closure and canonical components. Its retained-feature scaler statistics also match. The fixed group allocator only consumes those labels/components, so its existing split can be reused after exact identity proof. This is **split reuse only**: changing input width invalidates any model initialization, learned prefix, tuned settings or weights from a 76-feature learner.

Evidence: [corrected-no-headers-74-component-feasibility.json](corrected-no-headers-74-component-feasibility.json), [corrected-no-headers-74-candidate-split-feasibility.json](corrected-no-headers-74-candidate-split-feasibility.json) and [corrected-no-headers-74-candidate-ownership-dose-audit-benign-subset.json](corrected-no-headers-74-candidate-ownership-dose-audit-benign-subset.json). The split report records every reuse check and the parent hash; it does not pretend a new allocator was run.

## 3. Exact candidate inventory

| Property | Preferred 74-feature candidate | Earlier negative-screened 76-feature candidate |
|---|---:|---:|
| Unique survivors, 120-second gap | 1,362,527 | 1,362,039 |
| Survivor components | 1,130,292 | 1,130,077 |
| Train / development / test before training benign selection | 817,516 / 272,506 / 272,505 | 817,226 / 272,407 / 272,406 |
| Cross-role component intersections | 0 | 0 |
| Selected fresh training rows | 183,045 | 183,039 |
| Benign rows per stage | 3,500 each | 3,500 each |
| Active output widths E1/E2/E3/E4 | 3 / 8 / 13 / 16 | 3 / 7 / 12 / 15 |
| Heartbleed role support | 11 train, 0 development/test | 0 train/development, 8 test |

The 74-feature stage totals are 7,658 / 106,239 / 7,178 / 61,970. All required anchor/source and stage count floors pass through Infiltration-Portscan. Web families and ordinary Infiltration remain below the confirmatory floor. Heartbleed is registered from training but has no held-out positives: retain its active output, report coverage, and report recall as unavailable and show false positives; do not claim measured held-out family detection without positives. This profile was not selected to rescue Heartbleed, and no alternate split seed was searched.

Maximum local source dose produces about 0.208%-34.637% global raw E2 contamination across prescribed ownership seeds. Ten of twelve maximum-dose inventories force positive retained poison under DC; the largest forced retained fraction remains 74.7%. These are quota/exposure arithmetic, not observed loss selection or downstream harm. The earlier 76-feature tables/figures must keep their profile labels rather than being relabeled as 74-feature results.

## 4. Architecture and resource amendment

For input width d and active classes C, the declared MLP has `P(d,C)=128*d+8384+65*C` parameters. At d=74 and C=16 this is 18,896 parameters, 75,584 FP32 model bytes. A raw maximum-width replay tuple is `4*74 + 4*16 + 17 = 377` bytes, or 188,500 bytes per 500-slot client. EI anchor plus importance is 151,168 raw bytes per client at that width. Actual runtime/serialization overhead remains unmeasured.

Update initializer shapes, class maps, masks, payload ledgers, manifests, prepared-array checks and evaluator identities together. Retune all selected learner settings on development data after adopting the profile. The existing 441-logical-trajectory recommendation and twelve final seeds do not change automatically; runtimes remain to be profiled.

## 5. Benign is a policy label with two provenances

In this candidate's retained test inventory, benign has 214,553 original-background records and 1,605 remapped-attempted records. Development has 214,589 and 1,569 respectively. Selected benign training records contain 0/75/26/2 remapped attempts in E1-E4. Raw attempted marker/category agreement is complete in the inspected archive; observed categories are -1 and 0-6.

Report the unchanged combined benchmark FAR, plus descriptive original-background and remapped-attempted error rates with their own denominators. The latter may include traffic an operational team would still investigate. Neither annotation provenance certifies benign ground truth. Keep provenance evaluator-side; do not expose `Attempted Category` or original labels to the learner, admission scorer or threshold selection. Empty subgroup denominators remain unavailable.

The combined FAR must also equal the subgroup-denominator-weighted mean when both subgroup rates are defined; preserve additive false-positive counts.

This is an A32 reporting clarification, not a new confirmatory family or a post-hoc threshold. See [annotation-provenance-census.json](annotation-provenance-census.json). Do not transport combined FAR to an operational alert workload without explaining its annotation mixture.

## 6. Independent raw-row reconstruction status

On 17 November 2026 (Asia/Karachi), a separate parser using Python's standard-library `csv` module independently streamed all five corrected archive members. It reconstructed 2,099,976 row identities, 74 projected features, attempted-label mapping and timestamp/endpoint/protocol metadata. All metadata rows matched the candidate cache; independently applying the frozen Monday T0 transform produced zero FP32 model-input cell mismatches across the complete source inventory. Evidence and command are in `corrected-no-headers-74-independent-source-row-audit.json` and `tools/audit_corrected_source_rows_independent.py`.

The independent decimal parser and pandas builder differed in binary64 representation for 229,383 feature cells (201,184 rows). None changed the transformed FP32 inputs. This is a parser-rounding difference, not evidence of a feature or row-alignment defect. The independent mask audit also exactly reproduced numeric/domain/metadata validity, raw/final conflicts, survivor selection, T0 fitting, and retained split membership. Combined with the independent connectivity audit, this matches the frozen 120-second graph/T0 closure and gives zero cross-role component overlap. The SGKF allocator was reused from its pinned output after exact input/component identity checks rather than independently rerun. Provider authentication and equivalence between operational and true application sessions remain unresolved. The profile was adopted separately; this source audit does not select numerical settings or make the existing 76-feature learner transferable to it.

## 7. Adopted taxonomy and claim boundary

The authors' notebook and downloaded files use Thursday Infiltration-Portscan versus Friday Portscan; the public prose uses inconsistent Friday naming. The adopted protocol preserves these source scenario labels and narrows the claim to new annotated-class acquisition. Do not silently merge labels or interpret distinct scenario names as distinct techniques.

For the corrected route, the supported E3 question is learning a newly introduced annotated scenario class. It does not establish independent new attack techniques or behavioral novelty. That claim boundary is resolved in the adoption record; the mismatch between archive/code and public prose remains disclosed as a provenance limitation.

## 8. Negative findings and information boundaries

The inspected Active/Idle source ranges do not demonstrate epoch-sized timestamp values. A generic extractor defect report is not proof that it occurs in this archive. This source review did not optimize a feature subset against final accuracy, search a favorable split, or demonstrate independent reproduction; a separate single reference trajectory exists and passed the recorded acceptance checks.

Development selection uses the declared complete simulated curriculum, including its later families. Describe that as offline algorithm selection, not future-free operational tuning. Published feature-based annotation rules can create benchmark-specific recognition shortcuts; inspect such relationships on training/development only if adding a diagnostic, and do not mine final feature-label associations to choose a favorable schema or story.

## 9. Adoption checklist

The independent exclusion/graph/split parity is now complete for the adopted operational data contract, and a 240-run 74-feature development core plus DQ/oracle controls and a reproducible report have been produced. The exact core/metric/checkpoint audit is `phase3-overnight-independent-audit.json`. Preserve the historical selection and clean-gate provenance; do not call the development bank untouched. Remaining gates are the omitted DG and planned ablations, real sealed-test package/evaluation, remaining cost measurements, and external/instructor evidence limits.

A suitable working paper frame is a controlled study of label-poisoning persistence and admission limits under a fixed federated continual classification benchmark. The quota bound and source audits motivate careful experiments; they are not, by themselves, a demonstrated novel defense or a publication guarantee.
