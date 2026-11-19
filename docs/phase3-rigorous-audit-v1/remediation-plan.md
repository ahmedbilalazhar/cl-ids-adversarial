# Prioritized remediation and experiment cards

## Completed priorities

1. Preserved original ZIP, uncommitted work and exact source/configuration identities.
2. Audited primary data exports, split graph, T0, duplicates, counts, paired controls and checkpoints.
3. Recomputed primary/follow-up metrics and the original29 contrast slots independently; reconstructed fixed-cohort metrics from clean checkpoints.
4. Scoped the overnight quota adapter so imports do not alter other engines. Fixed all-zero rank-biserial effect to0.0. Historical training source is unchanged in the frozen snapshot.
5. Regenerated the original-report-based revision, figures and bounded claims; supplied independent audit/replay/package commands.

## Execution rule

New training is CPU-only, one worker. The user authorized the required DG completion with a two-day wall-clock window; the DG runner still enforces its dedicated 5.25-hour execution ceiling and requires the conservative full-block estimate plus20% reserve to fit. Stop selection uses cost, never observed efficacy. Representative replays do not add scientific replicates. Existing valid primary/loss/quota/DQ results are not rerun as new evidence. No incomplete matched block supports comparative claims.

## Phase 2 logic reconciliation - DG E1 prefix (corrected prospectively)

The earlier DG card incorrectly said to filter in E1, even though Phase 2 Step 6 says all admission filters are disabled in E1 and Step 7 requires the same stage schedule across arms. A later audit also found the selector used `ceil(0.75n)` instead of the stated `floor(0.75n + 0.5)`, which differs when a client has `n mod 4 = 3`. The prospective selector now bypasses admission in E1 and uses the exact Phase 2 rounding rule from E2 onward. Existing 417-trajectory results are untouched. The pinned runtime exists at `tmp/phase3-reference-env`. The pinned v2 attempt wrote ten complete cells before storage pressure; v3 wrote thirteen complete cells under the incorrect rounding rule; corrected v4 wrote ten complete cells before C: filled during checkpoint writing. All attempts are hash-inventoried, retained as incomplete, and excluded from scientific analysis. The user has since restored disk headroom; restart the full 48-cell block in fresh `results/phase3-dg-baseline-v5`. Keep the added DG comparison exploratory and outside the frozen confirmatory family.

## Ordered closure plan for remaining weaknesses

| Order | Weakness type | Current evidence / limit | Action and acceptance gate |
|---|---|---|---|
| 1 | Method logic / paired design | DG was absent; its first prospective selector filtered E1 despite Phase 2 requiring filters off. | Corrected selector bypasses E1. Before execution, demonstrate exact E1 selected-ID and checkpoint parity with DM/DC for every seed; use a new source identity/output. |
| 2 | Experimental completeness | The 417 adopted-profile trajectories contain no DG outcomes, so Phase 2's full admission baseline comparison is incomplete. | Run the complete 48 DG cells only if the remaining compute allowance permits the whole block plus reserve. Audit hashes, attack/input parity, per-class admission and recomputed endpoints before interpreting; report exploratory paired effects. |
| 3 | Generalization / outcome leakage | Outcomes use a repeatedly inspected development bank; no final-test rows have been released. | Freeze source, data, checkpoints, endpoint code and analysis; qualify a role-enforced sealed evaluator, then perform one-shot scoring. Until then label all effectiveness as development-only. |
| 4 | External validity | Existing external work is a one-seed train-only pilot with different feature schemas; it is not efficacy evidence. | Qualify independent source/schema/taxonomy/ID isolation and held-out support first; then run a paired full-method matrix with its own dataset-specific results. Otherwise keep external claims withdrawn. |
| 5 | Mechanism attribution | Replay/oracle interventions are conditional; memory occupancy, poison survival and importance magnitude alone do not establish causation. FIFO/class-balanced controls are deferred. | Keep mechanism conclusions conditional. If making eviction claims, preregister and run the complete 48-trajectory matched block; log per-example replay exposure and poison/class occupancy. |
| 6 | Resource validity | Representative replay timings exist, but full repeated cost components, allocations and actual serialized communication are incomplete. | Instrument admission, training, importance and evaluation separately; measure allocated and serialized state/messages. Label analytic payloads and local timings as estimates; make no edge, network, energy or deployment claim. |
| 7 | Inference / claim scope | Twelve ownership seeds are not independent captures or organizations; non-significance does not imply equivalence. | Preserve the one declared 29-test family for its original contrasts; report raw seed values, effects and whole-seed intervals. Keep later DG/ablations/external checks exploratory unless separately preregistered. |
| 8 | Data semantics / construct validity | The adopted corrected 74-feature profile and 120-second operational components are conditional choices; provider authenticity, true-session semantics and independent-site generalization remain unresolved. | Preserve row/graph/support audit evidence and amendment register; state the scenario-level label scope and keep the session-gap sensitivity visible. Any changed source, taxonomy, gap, or feature contract requires a new split and complete matched study. |

Do not treat a source patch, synthetic path, or report regeneration as closure of an evidence gap. Each action above needs the stated acceptance evidence; where the budget, evaluator, or data gate is unavailable, preserve the limitation and narrow the claim.

## E1 - Archived execution verification (executed)

- **Question:** Do frozen source, inputs, weights and recorded outcomes agree?
- **Falsifiable hypothesis:** Re-execution matches every stage confusion/model hash, memory summary, admission/importance ledger and oracle continuation exactly.
- **Reference:** Recorded core FT, EI and DR+DC at seed1, dose.5, q.75 and original coefficients/runtime.
- **Endpoints/analysis:** Exact equality; disagreement is a reproducibility failure, not a statistical test. Observational timing wrappers do not change scientific return values or RNG.
- **Compute:** Three full trajectories plus the DC oracle suffix; measured per-run values in `reproduction-attempt2/verification.json`.
- **Stopping:** First mismatch halts and writes failure; hard six-hour watchdog. Failed attempts are retained.
- **Interpretation:** Supports these representative trajectories, not proof of all historical executions or independent final-test effectiveness.

## E2 - Eviction mechanism controls (authorized; revised isolation design)

- **Question:** Does eviction alter the conditional single-attacker result when capacity/insertion eligibility are held fixed?
- **Hypothesis:** FIFO and prescribed class-balanced eviction change replay poison exposure and H relative to the reservoir under the same supplied labels; a null change remains valid.
- **Reference:** Existing unfiltered (NONE) reservoir runs, 500 slots, same clean/.5 dose, seeds 1--11/42, initializer, training and RNG namespaces; no retuning.
- **Design:** 48 full trajectories: two eviction policies x two doses x twelve seeds. Use NONE admission in all arms so every stage input row is eligible in every policy; this prevents model-dependent DC loss scores from changing insertion eligibility after the eviction treatment changes the model. FIFO always inserts an eligible record and evicts oldest. Class-balanced always inserts and evicts oldest within the largest supplied-label occupancy, ties by fixed class ID. Additional bounded insertion-order metadata is counted. Policies are active from E1, so outcomes estimate the full-trajectory policy effect and do not share an E1 model prefix. Do not substitute the later optional class-partitioned reservoir amendment without a separate protocol.
- **Endpoints:** H, A, immediate recall, absolute clean/attacked ASR, FAR, per-family metrics, actual replay exposure and poison/class occupancy.
- **Analysis:** Paired ownership-seed effects with whole-seed intervals; exploratory; reference clean subtraction exactly once. Failure/zero survivors retained.
- **Compute:** Conservative prior estimate is 8.524 hours including 20% reserve, from the FIFO diagnostic; the whole-seed NONE control estimate is 7.422 hours including reserve. The user expanded the available window to two days, authorizing a dedicated 10-hour maximum for this complete block. Recompute the gate immediately before dispatch and require the conservative estimate plus reserve to fit; no partial block and no prefix saving.
- **Stopping:** Dispatch only a complete block that fits. No early stop for null/adverse outcomes. If scientific claims are narrowed to omit eviction attribution, defer rather than spend compute on a conclusion no longer asserted.
- **Interpretation:** A negative result limits this mechanism under this threat; it is not evidence of universal robustness.

## E3 - Complete cost characterization (partially executed)

- **Question/hypothesis:** Replay/importance/admission have separable measurable costs; raw elapsed time is not equivalent to training time.
- **Reference/design:** Observational wrappers during E1 replay, unchanged settings. Existing batch1/256 pilot timings use10 warmups/100 calls; report milliseconds per batch, median and p95. These do not need new training.
- **Endpoints:** Training/admission/Fisher/evaluation seconds, raw allocated and serialized state bytes, actual serialized messages including registry/count metadata.
- **Analysis:** Report representative timings separately from cross-seed distributions; exclude oracle cost from a pure-method comparison or explicitly label it. Analytical byte estimates are not measurements.
- **Compute/stopping:** Instrumented verification already runs inside E1's cap. Additional serialization/latency checks require no research training; do not infer unmeasured network or edge costs.
- **Remaining:** Full matched repeated timings and actual end-to-end transmission/state overhead. Keep deployment claims withdrawn until measured.

## E4 - Raw-data independence and final-test phase (gated, unexecuted)

- **Question/hypothesis:** An independent source reconstruction yields equivalent declared session/content roles and the frozen method's conclusions survive an untouched held-out bank.
- **Reference/design:** Authenticated corrected release, exact74-field projection and annotation policy. Rebuild120s graph plus60/300s sensitivity before outcome access; preserve differences. Freeze code, methods, checkpoints, seeds, analysis and support inventory before a separate role-enforced evaluator.
- **Endpoints/analysis:** Role/component/content/T0 equality first; then original locked endpoints with no tuning after test inspection. The single original29 family applies only if genuinely prospectively qualified; otherwise disclose remaining exploratory status.
- **Compute:** Estimate reconstruction from a fixed source chunk; final inference from measured checkpoint-evaluation timing. No training jobs authorized by this card alone unless an actual defect requires a complete matched rerun that fits the cap.
- **Stopping:** Any isolation/support/source failure blocks outcome access; never weaken split/support rules after viewing performance.
- **Interpretation:** One held-out split from the same capture still does not establish independent-site generalization.

## E5 - External full-method evaluation (gated, unexecuted)

- **Question/hypothesis:** The same declared learning/admission mechanism has a measurable paired effect under a separately verified external protocol; direction need not match CICIDS.
- **Reference/design:** Separate dataset release/schema/taxonomy/scaler, component/ID isolation and sealed evaluator. Methods transfer architecture/settings only. Use the locked twelve-seed clean/.5 DR/DM/DC design (72 full trajectories) if feasible, or declare a new reduced exploratory protocol before outcomes. Do not reuse the one-seed train-only pilot as efficacy evidence.
- **Endpoints/analysis:** Per-dataset H/A/FAR with support checks and paired intervals; no pooled cross-schema estimates. Explicitly account for provider-pool ID limitations and unsupported family mappings.
- **Compute:** Measure one train-only paired seed block; estimate all72 plus reserve. Not dispatched under this audit because the evaluator/data contract is not qualified.
- **Stopping/interpretation:** Gate failures or insufficient support remain limitations; no outcome-driven remapping or claim of deployment generalization.
