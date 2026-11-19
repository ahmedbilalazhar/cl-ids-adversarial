# P0 scope reconciliation and execution contract

Status: repository evidence reconciled; new final-test outcomes remain sealed. This note began as a pre-follow-up reconciliation; the 48 replay-loss and 96 alternative-quota cells have since completed and passed independent audit. A prospective deterministic DG selector and budget-gated execution mode are now implemented, but no adopted-profile DG outcomes exist. The FIFO/class-balanced block also remains unrun. This development evidence does not confer retrospective confirmatory status.

## Canonical scientific evidence

For the audited single-attacker extension, the canonical evidence is the immutable newer engine and its frozen result identities documented in `results/phase3-rigorous-audit-v1/`. The historical `phase3-implementation/src/p3lib.py` GPU study remains a separate historical study. Its global Fisher averaging, Gaussian appended-row initialization, dependent repetitions, altered statistics and majority-attacker escalation are not silently pooled with the newer engine or relabeled as Phase 2 compliant.

The new engine corrects EI to client-local empirical importance and appended-row initialization to Xavier uniform. The audited 417 unique trajectories, 1,668 stage weights, exact representative replays, and 60 clean checkpoint rescoring support the scoped implementation claims recorded in `positive-checks.md`. They do not repair the historical weights or validate held-out performance.

The corrected 74-feature profile has two distinct evidence tracks. The lambda_z=.5 reference engine completed one clean four-stage trajectory and passed 174 recorded acceptance checks (`docs/phase3-reference/adoption.json`); it is an untuned implementation reference with weak acquisition and elevated later benign FAR. A separate frozen CPU extension completed the matched 240-run FT/EI/DR/DM/DC core, 24 DQ cells, 24 paired oracle continuations, and nine fresh clean-gate runs using the historical selected DR lambda_z=.1. Those outcomes are in the development bank, not a new final test.

## Development tuning and clean gates

The pinned tuning manifest is `results/phase3-cpu-v3/development/tuning-selection.json` (`status=clean_feasible`). It selects one configuration per learner using three clean development seeds (101–103). The configured candidates and selection records are:

| Learner | Feasible / candidates | Selected rounds × epochs; LR | Learner settings | Selected records |
|---|---:|---|---|---|
| FT | 1 / 2 | 12 × 1; .001 | — | tune-04..06, seeds 101–103 |
| EI | 3 / 6 | 12 × 1; .001 | lambda_E=100 | tune-22..24, seeds 101–103 |
| DR | 6 / 12 | 12 × 1; .001 | lambda_y=1, lambda_z=.1 | tune-46..48, seeds 101–103 |

The selected row IDs, complete settings, candidate scores and per-seed gate values remain in the machine-readable tuning manifest; abbreviated row ranges above are for navigation only. The status and explicit selected object are the evidence. The overnight clean confirmation reuses clean development seeds 101–103 and applies three class-recall gates per learner: stage-1 FTP ≥.5, stage-1 SSH ≥.5, stage-2 Hulk ≥.7. All nine learner/gate means pass. FTP mean recall is 2/3 for every learner, with per-seed values [1,1,0]; a mean gate therefore passes despite one seed's failure. The report correctly retains this weakness.

**Coefficient reconciliation:** the overnight DR runs use `(lambda_y=1, lambda_z=.1)`, matching the selected DR configuration. EI uses the selected `lambda_E=100`; although the generic run settings record `lambda_z=.1` while the tuning manifest records `.5`, `lambda_z` is only read by the DR objective in `src/phase3_v2/learning.py` and has no effect for EI. FT also does not use replay coefficients. Thus the selected active coefficients match for all methods; the separate one-run lambda_z=.5 DR+DC implementation reference is a distinct, untuned protocol and is not pooled with the CPU extension.

The older Phase 2 design specifies pilot comparison of 1×3 versus 3×1 synchronization, full clean tuning, and a larger prospective matrix. The newer extension uses a fixed 12-round, one-epoch protocol and the already completed development selection/gate artifacts. This is an amended, compute-bounded protocol using a development bank already exposed during selection, not a prospectively untouched confirmatory protocol. The selection and clean gate must not be described as independent validation.

## Baseline and ablation disposition

The independently re-audited 240-trajectory core is FT, EI, DR, DM and DC × four nested doses × twelve ownership seeds. The 24 DQ runs cover clean and .5 only. DR is the replay learner reference; DM is the equal-volume global-loss admission control; DC is class-aware admission. DQ is matched-random selection and is not DG, the global-filtering baseline named in Phase 2. Historical GPU results include DG but have no saved weights and use a different engine/threat/statistics. Thus the prescribed six-arm Phase 2 comparison remains incomplete; the current report labels DG as omitted rather than substituting DQ or historical DG.

The 24 exact E2 label-repair continuations are interventions, not deployable defenses or independent full trajectories. The subsequent follow-up completed 48 replay-loss and 96 alternative-quota cells; the independent audit verifies these 144 cells. The prescribed 96-cell FIFO/class-balanced eviction block remains unrun; its estimated cost exceeds the six-hour cap. DG's fixed 75% per-client global low-loss selector is now executable, but its 48 matched adopted-profile outcomes remain absent. The full Phase 2 experimental plan is therefore incomplete. The audited report makes only claims supported by the executed matched contrasts.

## Amendments and feedback record

| Phase 2 commitment or original choice | Implemented choice/evidence | Reason and timing | Effect on claims |
|---|---|---|---|
| CICIDS2017 numeric schema described as 76 features and 15 labels | Corrected 74-feature projection and amended taxonomy; 16 source labels, with explicit eligibility/support rules | Source/header and annotation audit; recorded in the adopted reference protocol | Claims concern the amended annotated scenario; no 76-feature replication or certified zero-day novelty |
| Full proposed synchronization/pilot and 633-trajectory plan | Compute-bounded 12-round extension; 417 unique later trajectories and 24 suffixes catalogued | Runtime/feasibility constraints; detailed in overnight plan and completion manifest | Conditional development study; planned cells are not inferred complete from the total trajectory count |
| EI importance stays client-local, appended head rows Xavier | Implemented by newer engine; historical engine differs | Correct implementation amendment and semantic verification | Latest-engine claims only; historical GPU EI/init results remain historical |
| One-attacker weak effects do not trigger escalation | Newer matrix keeps one attacker; historical escalated results are exploratory | Phase 2 threat fidelity | No use of stronger historical attacker results to support the primary threat |
| One family of 29 paired contrasts and fixed-cohort continual metrics | Independently recomputed for newer evidence | Corrected analysis | Development-only; historical significance claims withdrawn |
| FIFO and class-balanced eviction; DG baseline; external check | FIFO/class-balanced have one-seed smoke diagnostics only. DQ is not DG. DG code now implements the fixed 75% per-client global low-loss rule, but its matched outcomes are unrun; external efficacy pilot is train-only | Not executed or not qualified as matched outcomes | These gaps are disclosed; external check is optional under Phase 2 if infeasible, with justification |

**Class feedback:** no genuine instructor comments or dated feedback artifact were found in the audited material. The user confirmed on 17 November 2026 that no specific feedback was given. A historical draft note is not feedback and is explicitly marked unsent/unverified. No feedback-driven change or instructor approval is claimed; the recorded implementation changes respond to Phase 2 commitments and audit findings.

## Run identity and reproducible path

The frozen newer runner identity is in `results/phase3-overnight/identity.json`; its original source snapshot is preserved at `results/phase3-rigorous-audit-v1/executed-source/scripts/run_phase3_overnight.py`. Do not edit that snapshot. Use the exact pinned environment and paths in `docs/phase3-rigorous-audit-v1/reproduction.md` to reproduce the archived audit; use versioned new output paths for amended work. The runner's current validation enforces frozen source/input hashes and exclusive execution locking. Analysis/report/package commands and exact evidence paths are listed in the reproduction guide and package `START_HERE.md`.

For any new result, record an immutable manifest with code/input/runtime hashes, settings, ownership seed, poison IDs, checkpoint hashes, endpoints, failure status and output hashes. The initial overnight extension took 20,415 seconds on one worker. A later 408-run follow-up took 32,655 seconds (9.07 hours), exceeding the earlier six-hour ceiling; the 48 replay-loss and 96 quota arms are now complete. The separate 96-run FIFO/class-balanced block is estimated at 7.30 hours with reserve (8.52 hours conservatively). A 48-run DG block estimates at 3.19 hours with reserve; neither should be launched under the already exceeded allowance.

## Open acceptance gates

1. The selected active coefficients match the overnight core: DR lambda_y=1/lambda_z=.1, EI lambda_E=100; lambda_z is unused for EI and FT. The separate lambda_z=.5 reference is explicitly untuned and not pooled.
2. The 48 replay-loss and 96 alternative-quota cells are complete and independently audited. DG selector code and synthetic checks now exist, but keep its 48 matched data-backed outcomes and the adopted-profile 96-cell FIFO/class-balanced block marked incomplete; DQ does not satisfy DG.
3. P1 source, transform, masks, exclusions, graph/T0, and retained split membership now independently match for all 2,099,976 rows. Zero cross-role component overlap is verified; SGKF output is identity-checked and reused rather than rerun. Provider authentication and true-session equivalence remain bounded.
4. Nine synthetic evaluator tests, including full one-shot synthetic scoring and duplicate-run refusal, pass. A real final package, complete freeze, and held-out run remain unavailable; no test data were opened.
5. Elapsed run time, serialized checkpoint sizes, and limited CPU inference times are measured. Component training times, RSS/allocations, serialized network messages, network delay, and energy remain unmeasured.
6. Instructor feedback is unavailable; retain the external full-method study as train-only execution evidence and optional/incomplete efficacy.

These gates are not administrative wording: until they close or are explicitly accepted as limitations, the full Phase 3 plan is not complete.
