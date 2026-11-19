# Severity-ranked evidence register

A implementation defect; B experimental/analysis defect; C unsupported claim; D amendment; E incomplete experiment; F legitimate limitation; G unresolved evidence concern.

Historical defects are scoped to their engine. A verified later implementation does not repair historical outputs retrospectively.

## R04 - critical / B

**Commitment:** Independent complete seeded trajectories and one 29-test family.

**Implementation and evidence:** original report Statistics and Limits; phase3-implementation/src/p3lib.py: Cfg.rep; historical-run-inventory.json

**Actual behavior:** 696 distinct configurations share three ownership partitions; submitted inference treats 12 training units as independent and uses separate 30/17 families.

**Report claim:** Confirmatory significant learner/defence contrasts.

**Consequence:** RQ1/RQ2: nominal p-values do not support original inferential claims.

**Invalidates:** Invalidates original confirmatory significance claims; not raw confusion counts.

**Smallest fix:** Withdraw original significance claims; latest 12 ownership seeds analyzed separately with single Holm family.

**Required reruns and acceptance:** 29 exact rational contrasts plus paired sign-test sensitivity; whole-seed intervals.

**Status:** Recomputed; latest inference explicitly development-only exploratory.

## R01 - major / C

**Commitment:** Weak effects must not trigger extra attackers or doses (Phase2 Step7).

**Implementation and evidence:** submissions/phase2-with-claude.tex: Step7 clean gates; original report subsection What changed from Phase2

**Actual behavior:** Historical submission escalated to 3/5 attackers and calls it a predeclared fallback.

**Report claim:** Pre-declared fallback and implementation of Phase2.

**Consequence:** RQ1: stronger capability answers a different question.

**Invalidates:** Invalidates predeclared-status claim, not descriptive measurements of the stronger attack.

**Smallest fix:** Remove fallback claim; label escalation retrospective exploratory; lead with single-attacker results.

**Required reruns and acceptance:** No training; revised abstract, methods and conclusion must agree.

**Status:** Corrected in audited report; original preserved.

## R02 - major / A

**Commitment:** Client-local accumulated empirical Fisher, never FedAvg averaged.

**Implementation and evidence:** phase3-implementation/src/p3lib.py: run, lines386-391; src/phase3_v2/learning.py: commit_importance

**Actual behavior:** Historical engine forms weighted global importance and shares one penalty; newer engine retains local importance.

**Report claim:** Faithful Phase2 EI baseline.

**Consequence:** RQ1: EI is a different algorithm in historical study.

**Invalidates:** Historical EI cannot establish behavior of proposed local-EI; latest EI audited separately.

**Smallest fix:** Retain historical source; use local-EI engine for proposed-method comparisons.

**Required reruns and acceptance:** Latest primary matrix already complete; require semantic checks and exact representative replay, not redundant historical reruns.

**Status:** Implementation corrected in later engine; historical discrepancy disclosed.

## R03 - major / A

**Commitment:** Xavier initialization of appended head rows.

**Implementation and evidence:** phase3-implementation/src/p3lib.py: Net.grow lines127-135; src/phase3/model.py: initialize_rows

**Actual behavior:** Historical growth uses Gaussian standard deviation .01; latest growth uses Xavier uniform.

**Report claim:** Faithfulness to Phase2 head initialization.

**Consequence:** RQ1/RQ2: acquisition/scoring can depend on untrained rows.

**Invalidates:** Historical results remain valid only for their implemented initializer.

**Smallest fix:** Use latest Xavier engine; name the historical amendment explicitly.

**Required reruns and acceptance:** No new grid if current primary weights and replay verify.

**Status:** Disclosed; latest engine implements prescribed initialization.

## R05 - major / B

**Commitment:** H is mean E3/E4 Hulk-to-benign poisoned-minus-clean error; eligible rows with all prediction columns.

**Implementation and evidence:** original report Metrics; phase3-implementation/src/p3lib.py: stage_metrics/summarize; audit trajectory-metrics.json

**Actual behavior:** Historical scores mix full-bank false positives with eligible macro averaging and describe retention damage differently from prescribed H.

**Report claim:** Phase2 endpoints and whole-dataset performance.

**Consequence:** RQ1/RQ2: estimands differ; signs and magnitudes cannot be interchanged.

**Invalidates:** Original labels/interpretation require correction; saved confusion matrices can be rescored.

**Smallest fix:** Use independent count-derived endpoints; keep eligible and full-inventory populations separately named.

**Required reruns and acceptance:** No training; rational endpoints, denominators, rare-class support and excluded-column fixtures.

**Status:** Latest primary and follow-up endpoints independently recomputed.

## R06 - major / B

**Commitment:** ACC/BWT/forgetting use fixed stage cohorts including disjoint benign cohorts.

**Implementation and evidence:** phase3-implementation/src/p3lib.py: summarize lines302-312; scripts/verify_phase3_cohort_metrics.py

**Actual behavior:** Historical continual metrics average attack-class recalls and omit required benign cohorts.

**Report claim:** ACC/BWT/forgetting as prescribed in Phase2.

**Consequence:** RQ1/rubric: different retention metric.

**Invalidates:** Historical named metrics do not estimate prescribed quantities.

**Smallest fix:** Label historical recall-based measures; reconstruct fixed-cohort metrics from clean latest checkpoints.

**Required reruns and acceptance:** 60 clean trajectories, four checkpoints each; compare regenerated confusion matrices exactly.

**Status:** Checkpoint reevaluation executed separately; see cohort-metrics.json.

## R07 - major / G

**Commitment:** Immutable source identities must match executed source.

**Implementation and evidence:** results/phase3-overnight/identity.json; source-verification.json; recovered executed-source/scripts/run_phase3_overnight.py

**Actual behavior:** Current runner changed reserve from 1.5h to .75h; exact old bytes recovered by SHA256.

**Report claim:** Current source directly reproduces frozen identity.

**Consequence:** All RQs: hash drift breaks ordinary reproduction even when scheduling-only.

**Invalidates:** Does not by itself invalidate learning outputs; difference inspected and representative execution checked.

**Smallest fix:** Preserve frozen source; record explicit diff; verify every source/input before replay.

**Required reruns and acceptance:** Exact stage/model/memory/ledger/oracle reproduction in pinned environment.

**Status:** Recovered; no frozen identity rewritten.

## R09 - major / E

**Commitment:** Separate qualified sealed final-test evaluator after full freeze.

**Implementation and evidence:** data/processed/phase3-reference74-v1/development/manifest.json; docs/phase3-plan/final-test-readiness.md

**Actual behavior:** Zero final-test rows exported; latest results use same historical development bank.

**Report claim:** Any independent final-test or confirmatory effectiveness claim.

**Consequence:** All RQs: repeated development exposure limits generalization/inference.

**Invalidates:** Development evidence valid conditionally; independent final effectiveness unestablished.

**Smallest fix:** Label all current outcomes development-only; freeze then qualify isolated evaluator before any test extraction.

**Required reruns and acceptance:** Deferred: role-enforced evaluator, source/split/checkpoint/analysis freeze and one-shot predictions.

**Status:** Not executed; sealed outcomes remain untouched.

## R11 - major / F

**Commitment:** Honest clean acquisition and operational false alarms.

**Implementation and evidence:** core-summary.json; comparisons-29.json; clean-gates.json

**Actual behavior:** DC has lower mean A at all four doses and higher clean FAR than DM. Clean FTP recall is zero for pilot103 despite passing prescribed mean gate.

**Report claim:** Retention of every new-label row establishes improved acquisition or operational safety.

**Consequence:** RQ2: retention count is construction, not learning; high FAR undermines operational utility.

**Invalidates:** No implementation invalidation; invalidates broad superiority/safety interpretation.

**Smallest fix:** Report adverse trade-off, per-seed gates and absolute errors; do not silently discard or retune weak seeds.

**Required reruns and acceptance:** No training; paired A/FAR effects, sign-test sensitivity and raw seed values.

**Status:** Adverse results retained.

## R12 - major / F

**Commitment:** Weak attacks are valid; poison survival alone does not identify causation.

**Implementation and evidence:** core-summary.json; oracle-repair.json; 24 exact E2 clone controls

**Actual behavior:** Replay has small average single-attacker immediate damage; repair effects are conditional on retained labels and earlier poisoned state.

**Report claim:** Strong general persistence or replay-causes-all-damage claim.

**Consequence:** RQ1/RQ3: forgetting, remaining headroom and earlier damage matter.

**Invalidates:** No; limits claim strength.

**Smallest fix:** Report absolute clean/attacked errors and conditional intervention effects; keep original threat.

**Required reruns and acceptance:** No escalation; retain zero-effect repairs; report sign/size without causal overreach.

**Status:** Claims narrowed; repair results recomputed.

## R16 - major / G

**Commitment:** Independent source-session/content construction and release authentication.

**Implementation and evidence:** data-audit.json; source/input hashes; src/phase3/prepare.py docstring; corrected input manifest

**Actual behavior:** Independent standard-library source audits reconstruct all 2,099,976 corrected-release rows and match row IDs, labels, timestamps/endpoints/protocol metadata, 74 transformed FP32 inputs, numeric/domain/metadata validity, T0 fit, raw/final label-conflict quarantine, survivor choices and retained split membership (zero mismatches). A separate full-SHA256/SciPy connectivity pass exactly reproduces the frozen 120-second components and T0 closure; 60/120/300-second sensitivity is recorded. The frozen SGKF allocator was reused from the pinned split after exact input/component identity checks, not rerun. Archive hashes verify byte identity to the recorded downloads, not provider authentication.

**Report claim:** Fully independent raw-capture/session validation.

**Consequence:** All RQs: upstream session semantics/provenance not proven by downstream hash checks.

**Invalidates:** No demonstrated source-row, exclusion, retained-split or 120-second component-identity defect; provider authentication and equivalence to true application sessions remain unresolved.

**Smallest fix:** Preserve row-level, mask, graph and split-membership parity evidence; bound the claims to the archived source identity and declared operational session rule.

**Required reruns and acceptance:** Source-row, exclusion/quarantine, graph/T0 closure and retained role-membership parity pass for the frozen split. No further data rerun is indicated unless a methodology or source change occurs. Provider-side provenance and true-session semantics remain separately bounded.

**Status:** Source-row/model-input, exclusion/quarantine and frozen split-membership parity closed for the adopted 120-second operational rule; provider authentication and true-session semantics remain explicit limitations. SGKF was identity-preserving reuse, not an independent re-execution.

## R17 - major / E

**Commitment:** External replication needs independent data/schema/taxonomy/isolation and full method.

**Implementation and evidence:** results/phase3-followup/external-method-training-pilot-summary-v1.json; external-id-isolation-audit-v1.json

**Actual behavior:** 16 train-only pilot arms on two datasets, one seed, differing feature schemas; discovery is a submodule.

**Report claim:** External full-method effectiveness or deployment generalization.

**Consequence:** All RQs/external validity: no qualified external outcome evidence.

**Invalidates:** Only efficacy extrapolation invalid; execution pilot remains evidence of running.

**Smallest fix:** Describe train-only pilot and discovery separately; do not pool or infer effectiveness.

**Required reruns and acceptance:** Separate verified external evaluator, paired repeated seeds, support and semantic-map audit before held-out scoring.

**Status:** Deferred; no external held-out outcomes opened.

## R20 - major / A

**Commitment:** Importing one engine must not change another engine admission contract.

**Implementation and evidence:** scripts/run_phase3_overnight.py: module-level L.choose_admission assignment; pinned-tests.log eight failures

**Actual behavior:** Import replaced shared v2 chooser with quota adapter requiring settings.q; v2/v3 Settings lack that field.

**Report claim:** Engines can be composed/tested independently without import-order effects.

**Consequence:** Reproducibility: mixed engine use fails; isolated archived overnight worker uses compatible settings.

**Invalidates:** Does not invalidate isolated historical overnight jobs; breaks mixed imports and shared tests.

**Smallest fix:** Scope quota adapter to admission call and restore original function in finally.

**Required reruns and acceptance:** Run combined v2/v3/overnight suite plus import-isolation regression; source amendment recorded, frozen snapshot retained.

**Status:** Patched current runner; archived-source reproduction kept separate.

## R21 - major / F

**Commitment:** Disclose sensitivity of operational session grouping at60/120/300 seconds.

**Implementation and evidence:** scripts/verify_phase3_component_graph.py; component-reconstruction.json

**Actual behavior:** Independent120s graph and T0 closure match exactly. The60s graph has no frozen-split overlap;300s grouping joins8982 train/dev,9056 train/test and3444 dev/test components.

**Report claim:** Session isolation is invariant to plausible session-gap choices.

**Consequence:** Data validity/generalization: isolation is conditional on the declared120s operational grouping.

**Invalidates:** Does not invalidate the predeclared120s contract; invalidates a threshold-invariant isolation claim.

**Smallest fix:** Report sensitivity and distinguish verified source-row metadata from the operational session interpretation; do not choose the gap using model outcomes.

**Required reruns and acceptance:** 60/120/300 metadata-based graph reconstructions executed; any300s study needs new split/support/T0 closure and complete matched retraining.

**Status:** Disclosed; no threshold change or outcome-driven rerun.

## R22 - major / G

**Commitment:** Checkpoint weights, archived source and reported metrics must agree.

**Implementation and evidence:** Original Phase3_Submission ZIP member inventory; historical-run-inventory.json; checkpoint-audit.json

**Actual behavior:** Original archive contains no saved .pt/.pth/.npz weights. Its p3lib.py differs only in line-ending bytes from the inspected historical engine; normalized text is equal. Latest1668 weights are present and verified.

**Report claim:** All696 historical GPU metrics can be independently re-evaluated from saved weights.

**Consequence:** Historical reproducibility: raw696 result records can be checked/rescored, but their prediction/weight linkage cannot be independently replayed from missing checkpoints.

**Invalidates:** No proof of fabricated metrics; limits assurance of the historical GPU study and makes missing weights explicit.

**Smallest fix:** Preserve historical evidence and state this boundary; use qualified latest checkpoints for weight-linked claims.

**Required reruns and acceptance:** Supply original GPU weights/runtime/source bundle to close historical linkage; otherwise do not claim checkpoint re-evaluation of696 GPU runs.

**Status:** Unresolved historical artifact absence; latest primary checkpoints verified.

## R08 - moderate / B

**Commitment:** Unique trajectories, copies and continuations must be counted separately.

**Implementation and evidence:** result-catalog.json; results/phase3-followup-ablation/runs/runs; completion-followup.json

**Actual behavior:** 963 physical files collapse to 417 configurations; 546 identical copies; 24 oracle suffixes are embedded branches.

**Report claim:** Summed directory counts represent experiment replication.

**Consequence:** Rubric and RQ inference: counts inflate apparent independent evidence.

**Invalidates:** Invalidates inflated counts only; no conflicting duplicate payload found.

**Smallest fix:** Catalog by study identity + full settings; reject differing payloads for one identity.

**Required reruns and acceptance:** 417 unique = 9 clean confirmations + 240 primary + 24 DQ + 48 loss + 96 quota; 24 suffixes separately.

**Status:** Corrected catalog, report and package inventory.

## R10 - moderate / D

**Commitment:** Original 76 features/15 labels and source release.

**Implementation and evidence:** configs/phase3/reference74-v1.json; taxonomy-v1.json; docs/phase3-reference/adoption.json; data-audit.json

**Actual behavior:** Corrected source; two header-length fields removed; Infiltration-Portscan added; widths3/8/13/16.

**Report claim:** Unamended original methodology.

**Consequence:** RQ2: E3 acquisition concerns one supported annotated scenario, not certified novel technique.

**Invalidates:** Does not invalidate amended study; prevents drop-in comparison to original release.

**Smallest fix:** Document release/schema/taxonomy amendments and support by class; no retrospective editing of Phase2.

**Required reruns and acceptance:** Independent role/content/T0/transform checks and exact feature list.

**Status:** Documented and exported inputs independently verified.

## R13 - moderate / E

**Commitment:** Meaningful eviction ablations if eviction mechanism claims remain.

**Implementation and evidence:** latest unique_blocks; Phase2 Step10; historical FIFO source/results

**Actual behavior:** Latest single-attacker study has loss/quota/DQ controls but lacks FIFO and specified class-balanced eviction.

**Report claim:** Eviction rule explains latest single-attacker persistence.

**Consequence:** RQ3: mechanism attribution incomplete.

**Invalidates:** Does not invalidate primary comparisons; invalidates unsupported eviction attribution.

**Smallest fix:** Remove eviction attribution from latest conclusions; preregister complete matched controls before running.

**Required reruns and acceptance:** 96 full DC trajectories: 2 eviction variants x 2 doses x12 seeds, original500 slots; run only if conservative estimate plus reserve fits six hours.

**Status:** Unexecuted; exact experiment card in remediation-plan.md.

## R14 - moderate / B

**Commitment:** Costs separate training/admission/importance/evaluation, actual allocations and transmitted bytes.

**Implementation and evidence:** phase3-implementation/src/p3lib.py: Buffer.bytes and run cost; latest elapsed_seconds and latency fields

**Actual behavior:** Historical memory is a formula, communication counts raw weights only; latest elapsed time includes evaluation and, for some runs, oracle continuation.

**Report claim:** Measured end-to-end deployment/communication cost or fair training-only timing.

**Consequence:** RQ3: overhead ratios and absolute budgets otherwise misleading.

**Invalidates:** Invalidates resource interpretation, not accuracy.

**Smallest fix:** Instrument observational replay; distinguish measured stage categories from analytic payload estimates and unmeasured serialization.

**Required reruns and acceptance:** Representative matched runtime rows; batch1/256 warmup10/trials100; no edge/network/energy claim.

**Status:** Representative timings measured in replay; full cross-seed cost characterization remains open.

## R18 - moderate / G

**Commitment:** Incorporate feedback actually received in class and document resulting methodology changes.

**Implementation and evidence:** docs/phase3-rigorous-audit-v1/p0-scope-reconciliation.md; docs/phase3-plan/amendment-register.md; docs/instructor_note.md

**Actual behavior:** The user confirmed on 17 November 2026 that no specific class feedback was given. Audit-driven and Phase 2-driven methodology changes are documented separately; the historical draft note is marked unsent and unverified.

**Report claim:** The revised report says no instructor feedback was supplied and does not claim instructor approval.

**Consequence:** No feedback-driven change can be attributed to the instructor because no comments were given; this is not an unprocessed-feedback defect.

**Invalidates:** No experimental values. Any future claim of instructor approval would be unsupported.

**Smallest fix:** Complete: preserve the no-feedback disclosure and keep methodology-change provenance explicit.

**Required reruns and acceptance:** None while no feedback exists; if comments are later provided, record their source/date and map each point to its disposition.

**Status:** Resolved as an explicit no-feedback condition; no approval is claimed.

## R19 - moderate / A

**Commitment:** Completed evidence must be independently reproducible without overwriting history.

**Implementation and evidence:** scripts/finalize_phase3_overnight.py: main early guard lines60-65; reproduce_phase3_overnight.py: materialize before validation

**Actual behavior:** Existing finalizer refuses completed manifest before reanalysis, and replay assumes current runner hash and mutating materialization.

**Report claim:** Ordinary command reproduces final completed study.

**Consequence:** Reproducibility rubric: completed archive cannot be independently regenerated with stated path.

**Invalidates:** No accuracy invalidation; reproduction instructions broken for frozen evidence.

**Smallest fix:** New read-only catalog/scorer plus strict frozen-source replay into new output, exclusive lock and atomic audit outputs.

**Required reruns and acceptance:** Read-only input hashes unchanged, conflicting duplicate rejection, pinned representative replay and package self-contained source snapshot.

**Status:** New audit/replay commands supplied; original finalizer preserved.

## R15 - minor / A

**Commitment:** All-zero signed-rank effect convention is zero.

**Implementation and evidence:** scripts/phase3_evidence.py: signed_rank_enumeration; tests/test_phase3_cpu_supplement.py

**Actual behavior:** Shared helper returned None for all-zero rank-biserial effect.

**Report claim:** Phase2 all-zero convention.

**Consequence:** Inference/reporting: null effects inconsistently represented.

**Invalidates:** No change to p=1 or any nonzero contrast.

**Smallest fix:** Return0.0; update meaningful zero-case assertion and independent rational fixture.

**Required reruns and acceptance:** Focused helper tests; regenerate audited analyses.

**Status:** Patched and tested; frozen training sources unchanged.

## R23 - major / E

**Commitment:** Phase 2 DG baseline: DER++ plus a global 75% low-loss filter, distinct from DM's DC-volume-matched global ranking and DQ's random selector.

**Implementation and evidence:** `submissions/phase2-with-claude.tex` terms and Step 6; `src/phase3_v2/global_filter.py`; `src/phase3_v2/learning.py:choose_admission`; `scripts/run_phase3_overnight.py:choose` and `--dg-only`; `results/phase3-rigorous-audit-v1/followup-independent-audit.json`.

**Actual behavior:** The frozen 417-trajectory adopted-profile study contains no DG outcomes. The first prospective selector applied global filtering from E1, contradicting Phase 2's explicit all-filters-off E1 condition and breaking the common prefix. The prospective selector now bypasses E1 and retains `ceil(.75*n)` lowest-loss rows per client across classes from E2 onward, breaking ties by immutable row ID and recording ID hashes/class counts. The dedicated block is 48 trajectories (four doses × twelve ownership seeds).

**Report claim:** A full Phase 2 baseline comparison includes DG or that DQ substitutes for DG.

**Consequence:** RQ2 and the baseline/evaluation rubric remain incomplete; existing DC-versus-DM contrasts remain valid on their own matched scope.

**Invalidates:** No existing adopted-profile outcome. The missing arm limits completeness but does not invalidate FT/EI/DR/DM/DC development comparisons.

**Smallest fix:** Keep DQ distinct, preserve the shared E1 prefix, use the corrected fixed DG selector from E2 onward, and report DG outcomes only after the complete matched block and independent identity/metric audit.

**Required reruns and acceptance:** Complete 48 DG full trajectories paired by seed/dose to existing DM/DC arms; verify result hashes, admitted-ID/scoring rules, checkpoint identities, all endpoints, and paired uncertainty. The user authorized this block with a two-day wall-clock window; the runner still requires the full-block estimate plus reserve to fit its dedicated 5.25-hour execution ceiling. Two interrupted attempts are retained separately; launch the clean v3 block only with safe disk headroom.

**Status:** E1 semantic mismatch corrected prospectively; the existing DM/DC E1 parity preflight passed for all 48 seed-dose cells. A pinned-runtime attempt produced 10 complete DG cells then stopped for low disk headroom; hashes/failure disposition are in `results/phase3-dg-baseline-v2/incomplete-attempt.json`. No complete DG evidence exists; full DG-to-control E1 parity and independent outcome audit remain required.
