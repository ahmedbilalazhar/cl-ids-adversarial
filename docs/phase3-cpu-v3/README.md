> Current continuation: [two-hour audit](two-hour-implementation-audit.md), [local acceptance](../../results/phase3-two-hour-audit-v1/acceptance-staged-final.json) and [v5 notebook](../../results/phase3-two-hour-audit-v1/candidate-v5/notebook-final/phase3-qualification.ipynb). Historical CPU delivery below retains its scope.

> Current continuation, 2026-10-25: CPU v3 is verified; Kaggle v4 corrects selected-setting binding. Final scope, actual CUDA equivalence and durable Kaggle recovery remain gated. Historical instructions below retain their original scope. See [continuation audit](continuation-audit.md).

# CPU implementation revision v3

V3 adopts the proposed A-V3-01 budget revision following the user's instruction
to keep implementing. The [dated decisions](decisions-2026-10-24.md) precede v3
development outcomes and retain every v2 scientific rule except the two pilot
budgets: (3 rounds,4 epochs) and(12 rounds,1 epoch). No class weighting is used.
All final-test inference and GPU dispatch remain sealed.

The implementation imports immutable v2 numerical/state primitives rather than
forking their equations. Source identity covers every v1/v2/v3 Python module.
Execution additionally binds the distinct v3 protocol/decisions, parent source,
runtime, consumed settings, taxonomy and exact training manifest. Old schedules
are available for compatibility verification only and excluded from selection.

The checkpoint and run wire schemas remain `phase3-round-v2` and `phase3-run-v2`.
These describe the serialized layout, not the scientific revision. Every v3
execution contains `study_revision=cpu-v3` and separate v3 hashes; v2 checkpoints
cannot be resumed as v3. The independent v3 evaluator enforces that distinction.

## Reproduction commands

Run from the workspace root in PowerShell with fresh output directories:

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $py -m scripts.accept_phase3_v3 --output results/phase3-cpu-v3-reproduce/acceptance.json
& $py -m scripts.verify_phase3_v3 --acceptance results/phase3-cpu-v3-reproduce/acceptance.json --output results/phase3-cpu-v3-reproduce/integration

# Reuse the exact already prepared supplied-label package. The data have not
# changed with this training-budget amendment. The shared v2 builder remains
# available for independent fresh-destination preparation if required.
$train = 'data/processed/phase3-cpu-v2/s101-p000/train'
$sha = (Get-FileHash -LiteralPath "$train/manifest.json" -Algorithm SHA256).Hash.ToLowerInvariant()
& $py -m src.phase3_v3.train --train-package $train --train-manifest-sha256 $sha --learner EI --rounds 3 --epochs 4 --lambda-E 10 --output results/phase3-cpu-v3-reproduce/EI
& $py -m src.phase3_v3.train --train-package $train --train-manifest-sha256 $sha --learner EI --rounds 3 --epochs 4 --lambda-E 10 --resume results/phase3-cpu-v3-reproduce/EI/E1-R2.npz --output results/phase3-cpu-v3-reproduce/EI-recovered
& $py -m src.phase3_v3.evaluate --run results/phase3-cpu-v3-reproduce/EI --output results/phase3-cpu-v3-reproduce/EI-development

# Declared full procedure:18 pilots,60 tuning logical rows, up to9 exact aliases.
# Three FT poison diagnostics run only if all clean learner gates pass.
& $py -m src.phase3_v3.development --acceptance results/phase3-cpu-v3-reproduce/acceptance.json --output results/phase3-cpu-v3-reproduce/development

# Restart orchestration only after the prior controlling process has ended.
& $py -m src.phase3_v3.development --acceptance results/phase3-cpu-v3-reproduce/acceptance.json --output results/phase3-cpu-v3-reproduce/development --resume
```

The preserved v2 preparation commands and manifest descriptions remain in
`docs/phase3-cpu-v2/README.md`. Data reuse is hash-verified audited-cache reuse,
not a fresh CSV/session reconstruction or a new benchmark split.

## Long-run control and costs

A process-level OS lock prevents two live writers to one development output.
Every row receives an immutable receipt covering its identity and all output
file hashes. Resume rechecks the frozen procedure, acceptance, input package
hashes, receipts and alias lineage before reuse. A completed but unreceipted
physical trajectory is verified and independently evaluated before import.
Completed retries must have identical committed scientific states.

An interrupted incomplete active condition is retained under its attempt folder.
Orchestrator resume executes the same condition from its start in a new folder;
it never picks a seed or retry by score. This supplies a measured complete-loop
cost comparable with the other candidates. The added physical attempt is counted
separately. Explicit training CLI recovery remains available for round-boundary
continuation and is not an independent replicate or a complete from-start cost.

Pilot/tuning aliases retain the original logical training seconds. The row's
`physical_attempts` includes interrupted attempts; `physical_execution` identifies
a condition that actually trained rather than an exact alias. Neither field is
an independent seed count. The development procedure has three paired seeds.
Undefined or invalid outputs are retained without favorable imputation.

The filtered controls inherit the selected DR settings. Their adverse outcomes
do not invalidate the unfiltered acquisition gates. E1-only probe artifacts and
all v2 runs remain historical evidence, never aliases for a complete v3 run.

## Qualification boundary

V3 acceptance extends old-budget state parity, update/exposure accounting,
first-pass reservoir proposals, stage-locked admission, once-per-stage EI commit,
exact recovered continuation under both new budgets, orchestration interruption,
immutable receipts and duplicate-writer rejection. Previously qualified numeric
formulas are imported without source changes; they retain their bounded scope.
The full-data compatibility script independently checks all old-budget DC arrays
and four evaluation stages, and reproduces the fixed twelve-round E1 FT probe
models for all three seeds. Actual report/inventory files distinguish these
checks from later development outcomes and remaining GPU/final release gates.

## Sequential post-grid verification

After the complete declared grid, execute the following once, with fresh default
output destinations and the same pinned Python environment:

```powershell
& $py -m scripts.accept_phase3_v3_poison
& $py -m scripts.remeasure_phase3_v3
& $py -m scripts.match_phase3_v3_diagnostic
& $py -m scripts.verify_phase3_v3_controls
& $py -m scripts.recover_phase3_v3
& $py -m scripts.profile_phase3_v3
& $py -m scripts.audit_phase3_endpoints
& $py -m scripts.report_phase3_v3
& $py -m scripts.package_phase3_cpu --output results/phase3-source-bundle-v1/CPU-delivery
```

These default commands audit the actual `results/phase3-cpu-v3` delivery. The
individual verification tools accept explicit output/development/selection
paths for an independently reproduced grid; the delivery reporter binds the
actual default evidence locations. Preserve previous failures before a corrected
attempt. Do not overlap model jobs when collecting comparable CPU timings.

The [prospective timing disposition](cost-amendment-2026-10-24.md) identifies
infrastructure pauses by a fixed within-stage rule. Each flagged condition gets
one complete fresh-process repeat, with every committed state and the full
ledger required to match. A separate derived selector retains original costs
and selections. If its cost tie changes the selected FT condition, the matching
three development poison diagnostics are executed before reporting; original
diagnostics remain preserved. No score or seed is chosen by retry.

The matched controls follow the [control verification plan](control-verification-plan.md).
Fresh-process EI/DR continuation is assembled with validated original prefixes
into explicit recovery collections. Independent evaluation checks predictions
and count tables against their original full trajectories. Collections have no
from-start elapsed cost and add no independent research replicate.

The [CPU worker profile plan](profile-plan.md) covers complete fresh-process
FT/EI/DR jobs, process working-set peaks, fixed-shape inference calls, logical
FP32/model-template bytes and local export. It distinguishes actual CPU costs
from unmeasured remote transport, installation and GPU execution.

`scripts.finish_phase3_v3` runs this exact sequence after an explicitly named
live grid PID ends. It locks its own output, binds delivery source hashes, stores
per-step logs/receipts, verifies completed evidence on resume, and stops at a
failure without automatically rerunning scientific conditions. Its temporary
Windows idle-sleep request lasts only for the controller's lifetime; the display
may turn off and no persistent power policy changes. Example for an active grid:

```powershell
& $py -m scripts.finish_phase3_v3 --grid-pid 26888 --output results/phase3-cpu-v3/post-grid-extended
```

The PID in that example belongs to the recorded actual execution and must be
replaced with the explicitly verified PID of a new run. This is a local batch
controller, not a recurring scheduler or an authorization to access final data.

The first controller was replaced while waiting, before any post-grid model job,
to include the count audit and final source bundle in this sequence. Its original
procedure/status and replacement record remain under `post-grid`; the extended
controller uses `post-grid-extended`. The active grid was not interrupted.

The [independent count audit](../phase3-endpoint-audit-v1/README.md) reconstructs
development endpoints and selected-condition FT H/recall changes without feature
access. The [source snapshot](source-bundle.md) verifies the archived numerical
source identity, deterministic packaging, syntax and invalid-archive rejection.

The separate fixed-29 analysis implementation and its synthetic-only acceptance
are documented in [phase3-analysis-v1](../phase3-analysis-v1/README.md). Final
features/inference and actual GPU dispatch remain sealed throughout these tools.
