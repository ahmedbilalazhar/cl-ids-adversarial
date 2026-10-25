# Proposed amendment A-V3-01 — larger common training budget

Date: 24 October 2026. Prepared by the implementation agent for author review.
Status: proposed, not adopted; instructor feedback remains unavailable.

## Reason and evidence already visible

The complete v2 clean grid failed the predeclared gates. In the subsequent fixed
E1 diagnostic, original-loss FT at twelve rounds raised mean SSH development
recall from zero to 0.9972. FTP mean recall remained 0.6667; seed103 FTP stayed
zero. Weighting did not remove that weakness and worsened the observed macro-F1
and benign FAR at matched twelve-round exposure. The evidence is exploratory
and development-only. E2 Hulk, EI, DR and later retention were not exercised by
the diagnostic. No final outcomes are visible.

## Exact proposed change

Create a distinct sibling implementation/config identity for v3. Replace the
two common synchronization pilot candidates (1 round,3 epochs) and
(3 rounds,1 epoch) with (3 rounds,4 epochs) and (12 rounds,1 epoch).
Both new candidates expose each admitted current record twelve times, versus
three previously. Keep Adam reset per broadcast, batch128, FP32 and all named
RNG namespaces. Preserve ordinary current CE, EI and DR equations and their
existing coefficient grid. No class weighting is promoted.

This is a training-budget revision, not a correction invalidating the original
v2 runs. Its two schedules jointly compare local work and synchronization/reset
frequency; no claim that one isolated mechanism has been established is made.

Keep the original source data,74 predictors, T0 transform, fixed group split,
whole-component five-client ownership, benign inventory,16-class taxonomy,
eligibility, evaluation banks, supplied-label registration, exact corruption
threat/doses, admission policies, support exceptions, all three development
seeds, twelve final seeds, endpoints and29-contrast analysis family.

## Required verification and complete matched reruns

Before model selection, adopt a new dated v3 decision record that discloses both
the v2 grid and this diagnostic. Freeze pilot order (3,4) then(12,1), all existing
settings/ties/failure handling, and the existing per-learner mean acquisition
gates. Preserve feasibility-first tuning and all-seed validity. Do not replace
the mean gate with an all-seed rule or relax the thresholds after these outcomes;
report individual-seed weaknesses alongside the fixed means.

Qualify v3 separately: exact v2 equivalence on the old three-pass budget, analytic
update/exposure counts for both new budgets, immutable broadcasts/reset Adam,
first-round/first-epoch-only reservoir proposals across four epochs/twelve
rounds, unchanged EI stage-end commit, fixed admissions, inactive clients, strict
complete recovery and independent evaluation. Require exact checkpoint state
continuation on both budgets. Recheck full-data parity where the schedule agrees.

Then execute all eighteen new clean synchronization pilots (two schedules x
three unfiltered learners x three seeds), select one common budget with the
unchanged exact equal-stage/learner/seed macro-F1 rule, and run all sixty tuning
logical rows at that budget. Permit only exact in-version pilot aliases; the
v2 or E1 diagnostic artifacts cannot substitute for any full v3 trajectory.
Count the additional workload explicitly. All admission arms inherit the selected
DR settings if clean learners become feasible. Keep adverse filtered outcomes.

Only if each required learner has a feasible all-seed-valid candidate may the
three maximum-dose FT diagnostics proceed. A weak poisoning effect stays an
outcome. No new seed, threat escalation, optimizer, loss or adaptive budget is
authorized by this proposal. If the new grid also fails, retain the full failure
and decide on a separate prospective revision.

## Artifact and release disposition

Keep every v1/v2 and diagnostic artifact. None is superseded as a software-defect
result by this budget proposal; all remain historical development evidence.
V3 needs its own source/config/runtime/data/settings identities and completion
and failure inventories. Separate physical executions, exact aliases, prefix
verification and three paired development seeds.

Final-test inference and GPU dispatch require full method/control acceptance,
complete clean feasibility including E2 Hulk, pinned and confirmed GPU runtime,
measured complete workload costs, and final scope/code/data/analysis freeze.
An E1 diagnostic or this proposed amendment alone satisfies none of those
remaining release gates.
