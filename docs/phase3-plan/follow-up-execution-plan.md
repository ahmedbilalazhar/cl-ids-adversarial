# Phase 3 follow-up execution plan

Status: the label-free discovery submodule has completed three exploratory component partitions, threshold/cap sensitivity, and a paired assignment-rule ablation. A native-input external full-method adapter has completed a one-seed train-only pilot. Held-out external scoring and final-test evaluation remain gated.

## A. External-data validation

**Question.** Does the proposed behavior recur on an independently sourced IDS dataset?

1. First run a source and schema audit. Lock label mappings, preprocessing, task order, clean/poison eligibility, split roles, metrics, and seed pairing before training. The source audit is summarized in [external-dataset-readiness.md](external-dataset-readiness.md).
2. Treat UNSW-NB15 and CICIoT2023 as independent replications with separately fitted models and within-dataset evaluation. A three-seed external replication of the **discovery submodule only** is complete; see [external-dataset-readiness.md](external-dataset-readiness.md). Do not pool their metrics.
3. Direct cross-dataset transfer is currently blocked: the checked schemas have 194 and 39 features, zero shared feature names, and undocumented units. A transfer study requires a reviewed semantic feature map with units, transformations, missingness policy, and a frozen mapping before outcomes.
4. A one-seed paired train-only adapter pilot is complete for FT, EI, DR, and DR+DC, clean/attacked, on both datasets. Its execution-only inventory is in `external-method-training-pilot-results.md`. Before external scoring, build and qualify an isolated evaluator and account for provider-pool ID limitations. Report per-dataset paired effects, uncertainty, support, preprocessing differences, and failed/unsupported task arms. A replication is not evidence of cross-site deployment. Do not cite the archived pre-v2 mirror runs: their archive manifest says they used incorrect benign IDs and were superseded.

**Gate:** do not access external held-out rows until the evaluator, analysis, and row-isolation limitations are documented and frozen. Current training-only pilot outcomes cannot select settings.

## B. Label-free anomaly candidate clustering

The detector may use a benign-only fit/calibration partition, as a one-class detector. Candidate clustering, subsampling, centroid/radius fitting, and out-of-sample assignment must use features only. Labels and trigger masks may be joined only after freezing clusters, for held-out metrics and explicitly marked post-hoc cluster interpretation.

1. Create component-disjoint fit, calibration, and development-evaluation partitions inside permitted roles. Never split related flows randomly across these partitions. The initial implementation verified that all 272,506 development IDs map to the audited source graph, all have development role, and no test-role rows are present.
2. Freeze AE training, calibration quantile, HDBSCAN settings, candidate cap, seed policy, frozen assignment rule, and metrics before inspecting evaluation labels.
3. Report attack detection, benign false-alert rate, candidate/cluster coverage, noise rate, cluster purity/ARI (evaluation-only), runtime, and uncertainty across independent seeds/components.
4. Ablate threshold quantile, candidate cap, and frozen centroid/radius assignment. Keep the existing primary settings identifiable; mark all new contrasts exploratory unless prospectively registered.

**Gate:** use development data only until the full method, split, and analysis are locked. Existing label-dependent poison-cluster summaries are optional diagnostics, never inputs to cluster fitting.

## C. Sealed final-test evaluation

The current reference74 package reports zero exported test rows. Final-test scoring is therefore not runnable from the current prepared package.

1. Finish and freeze implementation, scope, selected checkpoints, hyperparameters, analysis, seed matrix, and artifact hashes using training/development evidence.
2. Build a physically separate test package from the audited source/component manifest. Verify role disjointness and feature/label hashes without putting test rows into training workers.
3. Run the frozen evaluator once; preserve raw predictions and denominators. No tuning, scope selection, or metric changes may follow test inspection.

**Gate:** no test extraction/evaluation until steps 1–2 pass. If support or provenance fails, report that limitation rather than weakening the split after seeing outcomes.

## Execution order and deliverables

1. Run `scripts/phase3_followup_preflight.py`; archive its JSON output.
2. Preserve adverse discovery-submodule results as exploratory evidence; preserve the train-only full-method adapter as execution evidence with no efficacy claim.
3. Run discovery on component-disjoint development partitions and save immutable configs, assignments, metrics, and figures.
4. Extend the external training pilot to the preregistered paired seeds only after recording its one-seed limitations; then freeze a test evaluator and analysis before any external scoring.
5. Complete the CICIDS final-test freeze and package audit before any one-shot inference.
6. Update the report with actual results and explicit limitations. Discovery and external-method execution pilots are documented separately; neither is a final-test or confirmatory result.
