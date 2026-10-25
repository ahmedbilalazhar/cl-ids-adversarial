# Data and implementation interface contract

Proposed implementation specification, 24 October 2026. Names below are future interfaces, not commands already present in the repository. The authoritative scientific source remains the revised Phase 2 document plus any prospective amendment.

## 1. Resolve acquisition before writing a large trainer

The local MachineLearningCSV files contain the numeric schema but lack the endpoint/timestamp metadata required by the proposed session grouping. Begin by obtaining the corresponding metadata-bearing flow release through the [official CICIDS2017 provider](https://www.unb.ca/cic/datasets/ids-2017.html). Record the download/release route and hashes; do not infer provenance from a familiar filename.

Suggested time box: one half-day to locate/access the release and inspect representative headers, then one day for a full schema/coverage/support census. These are planning allocations, not a guarantee of access or processing speed. If metadata cannot be recovered reliably, resolve an alternative or amendment before implementing the complete experiment.

Corrected releases are available from research authors who document construction and labeling defects. They are an alternative benchmark or sensitivity using the same historical capture, **not an independent external dataset**. A replacement changes feature extraction, annotation and possibly family mapping and requires a revised data contract. Do not reconstruct labels from coarse attack windows alone or mix original/corrected rows silently. [Liu et al., CNS 2022](https://intrusion-detection.distrinet-research.be/CNS2022/).

The initial bounded header probe is preserved in [data-acquisition-evidence.json](data-acquisition-evidence.json). The second audit subsequently downloaded and integrity-checked the complete corrected archive and a commit-pinned original mirror, then produced full source censuses and conditional grouping evidence. No form was submitted. See [data-release-decision.md](data-release-decision.md) for the material E3 support, taxonomy, clock and isolation consequences. Download integrity is not canonical experiment approval.

This is a concrete fallback route, not evidence of compatibility with the original 76-feature projection. In particular, `Attempted Category` is an annotation field and must never enter the feature vector. The authors document how attempted flows should be handled; freeze that label policy explicitly if adopting this release. Source IDs, flow IDs, addresses, ports and timestamps also stay outside the declared numeric predictor schema. [Author download/label guidance](https://intrusion-detection.distrinet-research.be/CNS2022/Dataset_Download.html).

The recommended corrected-release default follows the authors' conservative guidance: map attempted flows (`Attempted Category != -1`) to benign before the annotation/conflict audit; do not create separate “Attempted” model classes. Missing/invalid annotation metadata requires a declared quarantine rule. This is a release-specific prospective choice, not a relabeling silently applied to the original primary data.

## 2. Canonical row contract

Keep two aligned views with a stable immutable row ID:

| Builder/evaluator view | Learner view |
|---|---|
| Source release/file/row, endpoint metadata, protocol, timestamps, session/component IDs, reference annotation, provenance links, quarantine reason | Ordered FP32 feature vector, supplied training label, opaque immutable row ID |

Reference labels are available to the controlled corruption builder and evaluator, not to admission or training. A row ID must not encode a target label or poison status. A deterministic `(source_file_index << 32) | original_row_index` scheme is suitable when its bounds are validated and the ordered source-file manifest is pinned. Preserve the original row index before cleaning. It is an identifier, not a secret or proof of authenticity.

Suggested canonical storage:

```text
data/phase3/<data_hash>/
  source-manifest.json
  schema.json                 # exact ordered columns, dtypes, units, aliases
  exclusions.parquet          # builder-only reasons and provenance
  rows.parquet                # builder-only metadata/reference annotations
  features.npy                # contiguous canonical FP32 model inputs
  labels-reference.npy        # restricted builder/evaluator annotation view
  components.parquet
  splits.json                 # immutable component/row assignments
  scaler.json                 # T0 fitting IDs/hash, min/range, zero-range handling
  banks.json                  # fixed supports and row order; evaluator package
  seed-<seed>-ownership.json
  seed-<seed>-corruption.json  # evaluator/audit side; not mounted in learner jobs
```

The train/development worker bundle contains only the necessary index/label arrays. It must not accidentally include the complete builder directory or final-test arrays. One shared numeric array is an efficient local build format, but the exported worker package must physically omit held-out feature rows if claiming that training cannot access them.

## 3. Parsing and session construction

1. Validate required columns in every source file before concatenation. Distinguish duplicate header names from genuinely duplicated feature definitions.
2. Preserve string endpoint fields and numeric ports/protocol as metadata. Sort each unordered endpoint-pair/protocol group by start time and then immutable row ID.
3. Verify timestamp format against capture dates and source documentation. Ambiguous day/month parsing must fail rather than silently move July captures to other months. Record the supplied local time convention; do not invent a timezone.
4. Verify flow-duration units for the selected release before adding them to timestamps. Reject or quarantine negative/invalid intervals under the frozen rule. A current extractor repository is not proof that an old release used identical units or formatting.
5. Merge intervals into one session while `next_start - running_max_end <= 120 seconds`. Update the running maximum end after every record. This handles overlapping/nested intervals correctly.
6. Sessionize across all canonical files before splitting, rather than restarting IDs at every file boundary. File boundaries must not hide a continuing session.
7. Report support/overlap sensitivity for 60/300 seconds without selecting a gap from model test performance.

This defines reproducible operational sessions. The resulting groups are not certified application sessions or independent organizational sites.

## 4. Content components and T0

Use union-find or an equivalent graph method to combine session links and identical-model-input links. Feature keys exclude labels and metadata. Full canonical-byte equality confirms a fast candidate hash before merging. Normalize signed zero, dtype, endianness and feature order; do not collapse approximately similar inputs under a tolerance unless separately amended.

Retain all provenance links before removing same-label duplicate copies. Conflicting annotations for an identical canonical input are quarantined, with counts by affected family. Select the deterministic survivor by declared timestamp/file/row order, not whichever chunk happened to be read first.

Keep **T0 fitting IDs** distinct from the **exclusion closure** of components touching T0. Once the predeclared Monday-benign fitting pool is fixed, only those IDs fit the scaler. Rows linked to that pool are excluded from other splits; adding a linked row to the exclusion closure must not silently add it to scaler fitting.

T0 eligibility must depend on Monday-only source validity/reference benign annotation, not on another day's labels. Cross-day conflicts quarantine learning/evaluation and extend exclusion closure without refitting or removing fitting IDs. Record any calibration-only rows with ambiguous final-input annotations. This closes a circularity found in the first conditional data audit; see [protocol-closure-spec.md](protocol-closure-spec.md).

Apply the frozen transform and FP32 conversion, rebuild any exact-input links introduced by projection/rounding, and finalize component allocation afterwards. Do not repeatedly refit the transform in response to new links. Final leakage checks operate on actual model-visible inputs.

## 5. Split, support and ownership contracts

`SplitManifest` records target 60/20/20 proportions, fixed allocator/seed, realized per-family rows/components and every excluded component. The allocator is deterministic and outcome-independent. Indivisible mixed-label components can make the target or support floors impossible; the correct response is a documented feasibility decision, not row-level splitting.

The builder may use reference annotations to stratify and pre-audit support. That is benchmark construction information, not evidence of a label-free online learner. Report it explicitly. A public class inventory is also distinct from creating active classifier rows before arrival.

Use one component owner per training seed, including components spanning classes. A deterministic allocator can greedily assign whole components to minimize a documented weighted deviation from the sampled Dirichlet per-family target counts. Specify component ordering, tie-breaking and class weights. Report realized allocation and deviations rather than claiming rows were independently Dirichlet sampled.

Sampling roughly 3,500 benign rows must select whole components; it is not a hard exact-row cap. Do not reuse fresh IDs across stages. Maintain distinct canonical rows and test-component cohorts for the declared continual-learning metrics.

The earlier all-rows interpretation makes E4's mandatory benign count 17,960 on the conditional original candidate. The recommended prospective clarification instead selects **all benign members of a component as one bundle**, while retaining prescribed attack records independently. Unselected benign members remain excluded in the train role; no member moves to a held-out role. Components spanning periods contribute a vector of stage counts and remain one split/owner. See [benign-component-selection-amendment.md](benign-component-selection-amendment.md) for the exact algorithm and evidence. If the stricter all-rows interpretation is required, report/amend its unavoidable overshoot explicitly.

For a simple initial allocator, the proposed defaults use five group-stratified folds, assigning folds 2/3/4 to training, 1 to development and 0 to test with a fixed seed. This is an implementation recommendation, not a guarantee of the required per-class component floors. Failed floors require a pre-model-outcome allocator/protocol decision. The exact proposed seeds and conventions are in [proposed-defaults.json](proposed-defaults.json).

Freeze family eligibility from the canonical pre-corruption, pre-admission data audit. Do not recompute it after a dose reduces supplied Hulk labels or a filter rejects a family. A method that admits zero examples of an eligible class still faces that class in the common bank; its failure to acquire it is a result. Register supplied current labels before filtering even when a filter later rejects all rows of one label.

Ownership and attacked-site eligibility are also fixed before corruption/admission. Do not repartition by corrupted labels or select a different attacked site after a defense removes its source rows.

## 6. Minimal typed interfaces

```text
ProtocolSpec
  protocol_version, stage_schema, active_label_policy, rng_policy
  learner_settings, admission_policy, optimizer_reset_policy
  dataset_hash, split_hash, ownership_hash, analysis_hash

StageInput
  stage_id, client_id, x_fp32, supplied_y_int64, immutable_ids
  # no reference_y, poison_mask or final-test rows

Registry
  append_only_label_to_slot, active_width, newly_registered_labels
  # new means globally new, not merely absent at one client

AdmissionResult
  accepted_ids, supplied_class_counts, per_class_quota
  distinct_admitted_count, scoring_snapshot_hash

ClientState
  replay_or_importance_state, named_rng_states, completed_cursor

RoundResult
  local_model_update, distinct_admitted_count, resource_counters

Checkpoint
  shared_model, registry, all_client_states, next_transition
  protocol/data/source/runtime/parent hashes

EvaluationRecord
  run_id, checkpoint_hash, bank_hash, class_map_hash
  predicted_slots, optional_binary_margin, count_tables
```

Prefer simple dataclasses/validated JSON plus NumPy/torch tensors. A new workflow orchestrator, database server, distributed FL framework or configuration metaprogramming system is unnecessary for five simulated clients and a small experiment matrix.

## 7. State-machine boundaries

```text
CREATED -> INPUT_VERIFIED -> REGISTRY_EXPANDED -> ADMISSION_LOCKED
        -> ROUND_STARTED -> CLIENTS_TRAINED -> AGGREGATED
        -> next round OR FINAL_BROADCAST
        -> EI_IMPORTANCE_COMMITTED (EI only)
        -> STAGE_CHECKPOINT_COMMITTED -> next stage OR TRAINING_COMPLETE
        -> EVALUATED -> ANALYSIS_ACCEPTED
```

Only legal next transitions are resumable. Never mark a stage complete before aggregation, final broadcast and required importance commitment finish. An incomplete temporary file is not a recovery boundary.

All client updates in a round start from the same immutable broadcast. Sequential simulation must not mutate the server model after training client 1 and then give that partially updated model to client 2. Aggregate in fixed client order with distinct admitted-row weights. An inactive client has no update or aggregation weight; all inactive clients invalidate the stage.

A client with no admitted current rows does not run a replay-only local update. It preserves retained state; an inactive EI client still receives the final shared anchor while preserving its prior importance. Poisoned records can remain in an inactive client's buffer without being replayed. Log that case separately from an empty/clean buffer when interpreting a zero intervention effect.

The first active E1 head initialization requires an explicit convention. Resolve whether all initial active rows use the same Xavier/zero-bias rule as appended rows or the recorded framework initializer, and freeze it before development. Do not let a helper constructor silently decide it. New-row initialization must have its own RNG context, including any constructor initialization that is overwritten later.

## 8. Acceptance evidence to produce during implementation

| Artifact | Required evidence |
|---|---|
| Data audit | Source hashes, schema/units, quarantine counts, session/content overlap, supports and date ranges |
| Allocation audit | Whole-component ownership, Dirichlet targets versus realized counts, eligible attacker population |
| Corruption audit | Floor/source denominator, nested ID prefixes, no feature mutation, E2-only fresh corruption |
| Admission audit | Stable ties, global-new/small-class rules, exact DM/DC counts, rejected IDs absent from replay |
| Learner semantics | Per-example squared-gradient reference, fixed stage anchor, pre-update logits, first-pass reservoir, separate replay size |
| State recovery | Complete state hashes and deterministic small-run continuation agreement under a fixed runtime |
| Evaluation audit | Fixed bank order, full active head, integer confusion counts, denominators and no outcome-dependent exclusions |
| Import audit | Compatible identities, complete expected stages, duplicate/conflict handling, no stale result promotion |

These are specifications for future implementation acceptance. No tests or training were executed to produce this planning document.

## 9. External dataset decision

CICIoT2023 remains the original exploratory target. Before allocating its 72 runs, verify the exact CSV release, unit of observation, overlap of extraction windows, metadata/grouping support, original versus grouped labels, split provenance and license. The existing community mirror and legacy capped task files do not establish that contract.

Use a manageable **prospectively declared component/sample budget** if needed, reporting the induced class proportions and limits. Do not download and repeatedly parse all tens of millions of rows in GPU sessions. A cap must not break groups or be chosen after seeing favorable model scores. Test banks also need an explicit fixed sampling rule if the complete bank is too large.

If the chosen release cannot support a fair independent audit, omit it with explanation or formally substitute a metadata-bearing source such as TON_IoT before final testing. A newer year or larger row count alone does not improve validity. No learned weights or pooled estimates transfer; only declared method/network settings transfer to independently trained external models.
