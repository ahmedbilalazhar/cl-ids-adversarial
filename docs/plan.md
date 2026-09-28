Act as a principal engineer, research scientist, software architect, and critical reviewer preparing this project for a strong security journal submission and, separately, a possible production deployment.

**Repository:** `https://github.com/ahmedbilalazhar/cl-ids-adversarial`

**Reference commit:** `9e635aef56c2a48d0c2937d172069a621eb753df`. Check the current `main` commit first. If it has changed, inspect the new code and results and adapt this plan. Base every decision on the files currently in the repository.

**Your assignment:** Implement the improvement program below in phases. Do not stop after producing another audit or a list of suggestions. Make reviewable code, test, configuration, and documentation changes; run feasible verification; identify experiments that require unavailable data or compute; and give exact resumable commands for those experiments. Never fabricate results or call an unexecuted experiment complete.

**Available compute:** Google Colab Pro with roughly 15 GB RAM and a CPU-only laptop. Use synthetic tests and small diagnostic runs before expensive grids. Preserve the project’s 12 paired seeds for selected final comparisons. Do not assume a persistent GPU, load the full CICIoT2023 pools into pandas at once, or blindly rerun every configuration.

## 1. Understand and inventory the project before changing scientific behavior

Read the current versions of `README.md`; `docs/proposal.md`, `threat_model.md`, `decisions_log.md` **in full**, `results_overview.md`, `positioning_memo.md`, `paper_draft.md`, `search_protocol.md`, `ai_disclosure_log.md`, and `HANDOVER.md`; every module under `src/`; relevant scripts, the Colab notebook, CI, tests, Dockerfile, requirements, all YAML configs, and the checked-in per-seed and aggregate results.

Create an inventory with one row per config: dataset/task artifact, preprocessing protocol, CL method, architecture, attack, defense, runner, expected seeds, existing seeds, valid seeds, device, thread count, and result status. Separate these states: **planned, implemented, executed, validated, paper-ready**. The reference commit contains 211 configs and many incomplete grids; recount rather than assuming the old counts still apply.

Before editing scientific code, write an **artifact-impact matrix**. For every proposed change, identify which existing per-seed results, tables, figures, and written claims remain comparable and which must be archived and rerun. Retain invalidated artifacts with checksums and a reason; exclude them from current summaries. Never silently overwrite or intermingle protocols.

Create a project roadmap document that tracks the phases, dependencies, evidence, and remaining commands. Then implement the plan below.

## 2. Priority order and dependencies

| Priority                           | Work                                                                                                                                                                           | Must happen before                               |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| **P0 — Critical correctness**      | Result persistence/resume, valid data labels and schemas, backdoor training/evaluation parity, valid ASR, test-isolated discovery, broken entry points, secure dataset loading | Any new numerical claims or large reruns         |
| **P1 — Publication evidence**      | Attack-specific metrics, complete statistical families, clean aggregator controls, client/rounds sensitivity, corrected mirror replication, claim reconciliation               | Final abstract, discussion, or robustness claims |
| **P2 — Maintainability and scale** | Memory-bounded IoT ingestion, replay and kNN efficiency, config validation, CI, dependency locking, measured resources                                                         | Reproducibility release                          |
| **P3 — Future production path**    | Trained-model inference contract, monitoring, authenticated federation design, real packet/device validation                                                                   | Any production or edge-deployment claim          |

Complete each phase’s tests and exit gate before starting its expensive experiments. A failed or null attack is a valid finding; selecting another endpoint afterward to manufacture significance is not.

## 3. Phase A — Make execution and results trustworthy

### Problems to fix

- `src/reporting.py::save_results` calls `np.array2string` without importing NumPy. It can create a summary and matrix before raising an exception.
- `scripts/run_grid.py` skips an experiment whenever a summary filename exists, regardless of whether the command succeeded or the matrix and summary match.
- The master CSV can be appended repeatedly or become stale; result readers accept files without establishing their runner, input, or protocol identity.
- `scripts/grid_status.py` obtains group definitions by executing a textual portion of `run_grid.py`, and a previous federated dispatch bug produced invalid results under federated config names.
- `scripts/e5_evasion.py` imports `load_tasks` and `train_autoencoder` from `src.run_experiment`, which does not expose them.
- The Colab notebook looks for architecture YAMLs at `configs/ar_*.yaml`; they currently live under `configs/arch/`. Check the GPU importer against the current `results/runs/` layout.

### Implementation

Fix the immediate exceptions. Introduce an import-safe shared group/config registry. Validate all 211 configs, including method, attack mode, budget, malicious-client IDs, aggregator assumptions, dataset path, config name, and expected runner, **before** running a grid.

Write each new seed result transactionally: validate shape and values; write the `R` matrix and summary to temporary files; atomically replace their destinations; publish a completion manifest **last**. The manifest must include config hash, task-file hash, source commit, seed, protocol/scaler, label-map version, dataset, runner type, device, Python/torch/scikit-learn versions, `CL_THREADS`, and output hashes. Resume, status, aggregation, and table rebuilding must accept only a coherent result set. A federated config with a summary lacking `fed` is invalid.

Existing checked-in results lack these manifests. Preserve them as explicitly labeled **legacy, provenance-limited** evidence after structural checks; do not retrospectively claim their environment or task hashes were verified. Provide an intentional migration or exclusion policy. Rebuild aggregate tables deterministically from eligible seeds rather than trusting concurrent direct appends.

Fix E5 imports, notebook paths, GPU import placement, and their tests.

### Acceptance tests and exit gate

Use tiny synthetic tasks to run a single-node and a federated experiment. Simulate interruption between output writes and verify resume reruns the incomplete seed. Reject a wrong-seed, wrong-config, wrong-runner, corrupted-matrix, or mismatched-hash artifact. Verify E5 imports and Colab config discovery. Rebuild a table twice and get identical output without duplicate rows.

**Exit gate:** A fresh run succeeds end to end; partial files cannot count as completed; old and new evidence are distinguishable.

## 4. Phase B — Repair dataset semantics, preprocessing, and input security

### Problems to fix

`src/data/unsw.py` and `src/data/iot.py` construct benign-first label lists with a set expression that can include the benign class twice. Current UNSW configs rely on `Normal=7`; other code assumes benign is zero. Correcting the map changes task files and makes affected mirror results incompatible.

`src/data/sequence.py::fit_scaler_frozen` fits on T0 **and T1 training rows before T0 training**. This excludes held-out test rows but is not strictly future-blind at T0. The default sequence CLI and Make target still generate the superseded random/per-task protocol. `flow_order` is a per-file capture-order proxy, not a verified global timestamp.

`src/data/clean.py` should be audited for cross-file duplicates, split overlap, label repair, and treatment of metadata columns before numeric coercion. `scripts/download_cicids.py` disables TLS verification and falls back to HTTP. Legacy task loading uses `np.load(..., allow_pickle=True)`.

### Implementation

Build a unique class list with benign ID zero; assert label uniqueness and mapping invariants. Resolve attack targets from class names and the stored label map rather than fixed integers. Version and archive old UNSW/IoT task artifacts and results, then regenerate them.

Give every new task artifact a schema describing dataset source and checksum, source file and row identity, feature order and units, label map, split definition, sampled row IDs, imputer/scaler fit set and state, and protocol version. Save numeric arrays and JSON metadata without requiring object pickle for new artifacts. Authenticate and explicitly migrate trusted legacy task files.

Preserve existing T0+T1 results as an accurately labeled **offline-initialization** protocol. Add a T0-only frozen-scaler sensitivity arm. Make the documented primary data command generate the intended primary protocol; name random/per-task arms explicitly. Audit train/test overlap and cross-file duplicates. Describe chronology only to the resolution the data actually support.

Require verified HTTPS and source checksums for downloads. Fail if a mirror cannot be authenticated. Resolve paths from a declared repository/artifact root and reject ambiguous same-named files in the caller’s working directory.

### Acceptance tests and exit gate

Use small fabricated train/test pools to prove benign maps to zero, labels are unique, test-only categories do not fit encoders, test rows do not fit scalers, and T0-only preprocessing cannot see T1. Test archive/version behavior. Confirm dataset ingestion remains below roughly 15 GB RAM on the selected replication size.

**Exit gate:** Data artifacts have explicit identity and leakage boundaries. Changed-label mirror results are excluded until regenerated.

## 5. Phase C — Make the attacks measure their stated mechanisms

### Backdoor: training, evaluation, and physical validity

Both `src/runner.py` and `src/federated/fedavg.py` currently call `inject_backdoor` without passing the configured `attack.trigger`; evaluation does read the configured trigger. Pass one validated trigger specification through training and evaluation. Transform physically specified raw feature values using the fitted scaler before inserting them into model inputs. Fail when configured features are absent instead of changing an unrelated column.

Verify `scripts/gen_grounded_trigger.py` against the **actual flow-feature extraction process**. A plausible Scapy packet sequence does not by itself establish that the flow extractor will output the three claimed feature values. Until this is measured, label the arm a feature-space approximation.

Calculate ASR only on originally non-target examples of the specified attack class to which the trigger was applied. Persist successes, eligible denominator, per-task ASR, and the clean targeted error rate. If PortScan is absent, report `N/A`; never evaluate all test rows as a fallback. Archive existing backdoor ASR claims, including the reported 1.000, until recomputed.

### Discovery: causal pipeline and held-out isolation

Current `src/discovery/pipeline.py::evaluate_discovery` fits HDBSCAN on training **and held-out test** novel flows. Clustering also happens after classifier training, so its cluster IDs cannot explain the reported classifier ACC change. Redesign the experiment into explicit stages:

1. Fit the AE using eligible benign training flows.
2. Calibrate its threshold on separate eligible benign calibration flows.
3. Identify novel training candidates.
4. Fit discovery clusters on **training candidates only**.
5. Assign provisional class IDs and actually feed those assignments into continual learning.
6. Assign held-out flows using a documented out-of-sample rule, without refitting clusters.
7. Track cluster-to-class mappings across tasks.

Retain a classifier-label-poisoning control so direct poison labels are not mistaken for a discovery-induced effect. Label the existing transductive analysis as legacy, archive incompatible E4 claims, and rerun the causal comparison.

Report baseline attack discovery miss rate, benign false-alert rate, fraction of attacks flagged, attack absorption among **all attacks** and among flagged attacks, cluster assignment quality, downstream attack-family recall, and ACC. The current no-poison discovery miss rate is high; investigate whether the discovery system is useful before interpreting marginal poisoning effects.

### Label flips, adaptive attacks, and metrics

Persist, for each task/client, the source class, eligible candidates, labels actually changed, configured shard budget, realized shard/global dose, defense retention, and attacker knowledge. A configured 1% DoS Hulk flip does not imply that class was available in every task.

The runners initialize the upper triangle of `R` to zero while `src/metrics.py` reads it for FWT. Evaluate future tasks **before** training them and use a declared baseline, or mark FWT unavailable. Treat undefined ASR as `N/A`. Keep the joint model explicitly labeled as a future-data oracle.

### Exit gate

Synthetic tests prove configured backdoor trigger parity, correct raw-to-scaled conversion, ASR eligibility, and `N/A` behavior. Adding or permuting held-out flows cannot alter discovery clusters. A test proves provisional cluster assignments actually affect classifier training. Every attack has a measured actual dose and eligible endpoint.

## 6. Phase D — Strengthen the research architecture and controls

`src/federated/partition.py` redraws client shards each task although clients retain CL state. Implement a stable-client/site variant where identity is available; otherwise describe the existing setup as **resampled simulated clients**. On selected matched configurations compare stable versus resampled assignments. Log per-client class mix, sample counts, empty participation, memory, optimizer steps, and communication bytes.

The system performs one federated round per task. Add a limited one-versus-multiple-round sensitivity study, with optimizer-work accounting. Audit Adam state across broadcasts, EWC Fisher estimation and anchor updates, ER/DER++ buffer behavior, stored DER++ logits, and total memory across clients. Version changed algorithms and rerun their affected arms; do not attach old numbers to changed methods.

For each robust aggregator, run its own **clean same-aggregator control** and an attacked arm. Compare clean-to-attacked within the rule and attacked rule-to-attacked FedAvg. Enforce Krum’s client/malicious-count assumptions in config validation. Investigate why available sign-flip FedAvg results exceed clean FedAvg and why median/Krum can score worse; evaluate the attack’s targeted objective, not ACC alone. Do not claim the aggregators provide defense until the controls support it.

`src/models/tabular_attention.py` uses one token for the entire feature vector. Existing results are therefore a comparison with a **single-token transformer block**, not feature-to-feature attention. Rename its description accordingly. If useful to the paper, implement a true feature-token tabular architecture and compare on a small, parameter/compute-matched subset. Consider a feasible conventional tabular or balanced-replay control only when it resolves a stated confound. Avoid an automatic rerun of all architecture combinations.

**Exit gate:** The main federated interpretation has controls for benign aggregator behavior, client identity, rounds, replay memory, and architecture, or names the unresolved dependence as a limitation.

## 7. Phase E — Prespecify inference and finish selected experiments

Before final grids, create a machine-readable analysis specification with hypotheses, dataset, **primary metric per attack**, comparator, paired seed set, effect direction, minimum important difference, and full Holm comparison family.

`scripts/stats_summary.py` currently corrects over comparisons with available numeric results. Mark adjusted values from unfinished families **provisional**. Finalize family membership and document amendments before final inference. For each selected comparison report per-seed paired differences, interval, effect size, raw and corrected \(p\), realized poison dose, and eligible population. Do not infer “immune,” “equivalent,” or “no effect” from a nonsignificant test. If equivalence matters, define a justified margin and analyze it directly.

Alongside ACC, report attack-family recall/missed detections, benign false-positive rate, ASR with denominator, forgetting, and per-task results. State clearly that 12 random seeds on one captured dataset estimate seed variation, not generalization across network sites.

Run experiments in this order:

1. Synthetic checks and three-seed diagnostic probes for changed mechanisms.
2. Resource measurement and investigation of the anomalous federated seed.
3. Selected primary CICIDS2017 arms using the same 12 paired seeds.
4. Same-aggregator clean/attacked controls, then selected adaptive and persistent attacks.
5. Corrected UNSW and **capped** CICIoT2023 replications.
6. Limited task-order, T0-only scaler, rounds/client-identity, and architecture sensitivity arms.
7. Final statistics, figures, claim ledger, and manuscript tables.

Checkpoint every seed. Never silently mix CPU/GPU, thread settings, task versions, label maps, or different scaler protocols. Incomplete families and one- or three-seed results remain visibly provisional.

**Exit gate:** Each proposed headline has a validated estimate for its stated endpoint. Inconclusive and null findings remain accurately labeled.

## 8. Phase F — Performance and scalability without changing conclusions

Profile first, then implement measured improvements:

- Replace per-sample replay-list growth and repeated full-list reconstruction in `src/cl/er.py` and `derpp.py` with a bounded reservoir and explicit RNG state.
- Batch prediction, small-loss scoring, AE inference, and attack scoring rather than copying whole tasks to GPU where unnecessary.
- Bound brute-force kNN and HDBSCAN memory. If approximate neighbors or capped candidate sets change decisions, quantify the difference against an exact small-case reference.
- Avoid repeated federated model-state copies when parity tests show the change is numerically safe.
- Stream/project parquet columns and seed-sample by label **before** materializing large IoT dataframes. Record source hashes, row IDs, caps, wall time, and peak RSS.
- Apply thread limits before heavy imports and limit simultaneous CPU workers according to measured memory.

A full multi-million-row IoT experiment using the current in-memory pandas approach does **not** fit the stated 15 GB constraint reliably. Keep it as future work unless streaming and capacity measurements establish otherwise.

**Exit gate:** Selected primary and replication workloads fit the stated resources and produce results within declared numerical tolerances.

## 9. Phase G — Define a production path without overstating deployment

`scripts/e8_deployment.py` benchmarks random models using hard-coded feature/class counts. Retain its current numbers as a model-only software proxy. Export a **trained** checkpoint with fitted preprocessing, input feature schema and units, label map, model/protocol version, and integrity hashes. Benchmark that loaded bundle end to end: validation, preprocessing, batch-one p50/p95/p99 latency, throughput, update time, and real process peak RSS on the named CPU.

Design a minimal local inference interface with strict schema validation, bounded batches, missing-feature behavior, version compatibility, unknown/abstain policy, health metrics, false-alert/drift monitoring, and rollback. For a future real federation, specify authenticated participants, protected transport, signed model releases, client participation rules, malicious-update handling, and server audit logs. A five-client single-process simulation does not prove privacy, robustness, or physical edge suitability.

**Exit gate:** Documentation distinguishes implemented inference, measured software cost, simulated federation, proposed real deployment, and unperformed packet/device validation.

## 10. Phase H — Reconcile paper claims, CI, and release

Build a **claim ledger** linking each README, proposal, results-overview, positioning-memo, abstract, and paper-draft statement to exact protocol, config, seed set, validated result, endpoint, paired effect/interval, raw/corrected \(p\), and status. Correct legacy seven-seed headlines, incorrectly labeled “n=12” preprocessing comparisons, old EWC-immunity and defense statements, discovery framing, and pending Byzantine/cross-dataset assertions. Keep superseded statements in dated decision history.

Verify novelty language against primary sources on static FL-IDS poisoning, honest-client federated CIL IDS, single-node CII replay poisoning, and AE/clustering attacks. State the contribution as the **validated intersection and analysis actually demonstrated**; do not use an unqualified “first” claim.

Make CI cover the substantive failure modes from every phase. Require strict lint, config validation, synthetic single-node and federated integration, persistence/restart behavior, data leakage invariants, ASR denominators, discovery isolation, federated dispatch and aggregator constraints, E5/notebook paths, and deterministic table regeneration. Pin a tested dependency environment and container digest at the submission tag. Perform a clean-environment reproduction of a representative table and figure.

**Exit gate:** Every current paper claim points to compatible validated evidence; the release artifact contains enough code, config, task provenance, per-seed data, and environment information to reproduce it.

## Required final response from you

Report work phase by phase with statuses **implemented / tested / numerically rerun / pending**. Include:

1. Exact files changed and why, distinguishing macro design decisions from micro fixes.
2. Tests and commands run, with failures and unresolved risks.
3. An archive/invalidation manifest and a list of existing results still valid.
4. Resource measurements against the CPU-laptop and approximately 15 GB Colab limit.
5. Completed and incomplete primary comparisons and Holm families.
6. A claim ledger showing which research claims can now be made.
7. Exact resumable commands, in order, for any experiments blocked by unavailable raw data or long-running compute.
8. Remaining steps toward real deployment, without presenting them as already built.

**Definition of done:** Code, artifacts, statistics, and manuscript language agree. A failed attack, harmful defense, or non-replication is a valid research outcome when measured and reported honestly. Do not fabricate evidence, mark partial grids complete, silently replace old files, or claim production readiness from the simulation.
