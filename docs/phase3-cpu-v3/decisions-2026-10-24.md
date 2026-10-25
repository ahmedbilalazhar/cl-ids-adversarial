# Adopted CPU development v3 decisions — 24 October 2026, 15:44 UTC

Authority: the user's instruction to keep implementing and improving after the
completed diagnostic and proposed A-V3-01. Adopt A-V3-01 for this CPU development
revision. Instructor feedback remains unavailable. This is not final-study or
GPU approval.

Evidence already visible: complete failed v2 clean grid, all original filtered
control results, and the six fixed E1 acquisition probes. Natural FT twelve-round
SSH mean recall was0.9972; FTP mean0.6667 with seed103 still zero. Weighted loss
did not resolve that failure. No full four-stage v3 outcome is visible here.

1. Use pilot budgets (3 rounds,4 epochs), then(12 rounds,1 epoch), twelve current
   passes each. Keep original FP32 Adam resets, losses, coefficient grid, batch128,
   replay capacity/draw/teacher/insertion rules and EI estimator/commit unchanged.
   Preserve the exact data, transform, ownership, labels, support and banks.
2. Use seeds101–103, learner order FT,EI,DR, eighteen full clean pilots. Select
   the common budget by the exact equal-stage/learner/seed macro-F1 rule, all nine
   required rows valid; exact ties choose fewer rounds. Then run sixty tuning
   logical rows in the unchanged numeric order: LR0.0001,0.001; EI lambda1,10,100;
   DR lambda_z0.1,0.5,1 then lambda_y0.1,1; seeds increasing.
3. Preserve feasibility-first selection: each unfiltered learner needs three
   valid seeds and separate mean E1 FTP>=0.50, E1 SSH>=0.50, E2 Hulk>=0.70 cells.
   Among feasible settings maximize exact mean macro-F1, then lower mean measured
   logical complete-loop seconds, then numeric configuration order. Aliases carry
   their source logical cost. Keep poor seeds and filtered-arm adverse outcomes.
4. Exact pilot aliases are permitted only within this v3 identity and complete
   data/settings/runtime matches. V2 and E1-only diagnostic states are never pilot
   substitutes. Old budgets remain executable solely for explicit compatibility
   verification and are excluded from v3 selection.
5. First pass DR proposals remain round1/epoch1 even at four epochs or twelve
   rounds. Admission remains stage-locked. EI still commits only once per stage.
   New extended-budget tests and exact recoveries precede development selection.
   Arithmetic tolerances are unchanged; CPU same-engine state equality is exact.
6. Reuse the unchanged v2 numerical engine and typed checkpoint serialization.
   The wire schema remains phase3-round-v2/phase3-run-v2; execution metadata binds
   the separate v3 protocol, decisions, complete v1/v2/v3 source, parent identity,
   runtime, data and settings. A v2 checkpoint is incompatible with a v3 run.
7. Make orchestration resumable without changing condition identity: preserve a
   frozen procedure, row receipts and full immutable output hashes; verify all
   before reuse. Completed valid physical rows retain elapsed logical costs.
   Invalid scientific rows remain invalid; never replace them with favorable
   seeds or average a subset. An unreceipted completed run may be imported only
   after exact identity/whole-output verification. Infrastructure interruptions
   retain partial artifacts. Orchestrator restart reruns that same incomplete
   condition from its start in a new attempt directory, preserving full logical
   cost comparability and counting the additional physical attempt. The train
   CLI separately supports exact round-boundary recovery of that same run.
8. Only after every clean learner has a feasible setting run three FT maximum
   dose diagnostics with the selected FT settings. No effect-based escalation.
   All other cases retain the blocked status. No final feature rows are opened;
   twelve final seeds and the single29-contrast family remain sealed. GPU dispatch
   also requires pinned runtime, full workload costs and final scientific freeze.

This amendment increases development compute. None of the scientifically valid
v1/v2/diagnostic results is invalidated or overwritten. A later failure requires
its own prospective decision; there is no adaptive budget/loss expansion here.
