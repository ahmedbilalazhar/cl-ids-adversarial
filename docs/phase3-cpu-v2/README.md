# Phase 3 CPU development milestone v2

This version adds FT, EI, unfiltered DR, matched DM/DC/DQ, builder-only E2
Hulk-to-Benign corruption, complete round-boundary recovery and independent
development evaluation. It preserves the runnable v1 reference byte-for-byte.
Final-test inference and GPU-grid dispatch are disabled. No instructor feedback
has been supplied.

Read [the dated decisions](decisions-2026-10-24.md),
[defects and amendments](defects-and-amendments.md) and the executed
`results/phase3-cpu-v2` evidence alongside this implementation. Poor development
performance and filtered-arm harm are valid outcomes. Acceptance does not imply
clean feasibility or a successful defense.

## Commands

Run from the repository root in PowerShell. The existing environment is pinned
Windows CPython 3.12.14, PyTorch 2.7.0+cpu and NumPy 2.3.5. Its complete dependency
lock is `configs/phase3/requirements-reference-cpu.lock`; v2 uses the same CPU
runtime. These commands use fresh destinations because artifacts refuse overwrite.

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'

# Focused semantic/integration fixtures, strict machine-readable report.
& $py -m scripts.accept_phase3_v2 --output results/phase3-cpu-v2-reproduce/acceptance.json

# Prepared package: rehash audited source/cache, rebuild whole-component ownership,
# write supplied labels into train/ and reference annotations only into audit/.
& $py -m src.phase3_v2.prepare --seed 101 --dose 0 1 --output data/processed/phase3-cpu-v2-reproduce/s101-p000
$train = 'data/processed/phase3-cpu-v2-reproduce/s101-p000/train'
$sha = (Get-FileHash -LiteralPath "$train/manifest.json" -Algorithm SHA256).Hash.ToLowerInvariant()

# Unfiltered learner: choose FT, EI or DR. Coefficients are explicit CLI settings.
& $py -m src.phase3_v2.train --train-package $train --train-manifest-sha256 $sha --learner EI --lambda-E 10 --output results/phase3-cpu-v2-reproduce/EI

# Fresh-process exact recovery, including importance/anchors/sample IDs/RNGs.
& $py -m src.phase3_v2.train --train-package $train --train-manifest-sha256 $sha --learner EI --lambda-E 10 --resume results/phase3-cpu-v2-reproduce/EI/E1-R2.npz --output results/phase3-cpu-v2-reproduce/EI-recovered

# Full trajectory only; suffix directories cannot masquerade as complete runs.
& $py -m src.phase3_v2.evaluate --run results/phase3-cpu-v2-reproduce/EI --output results/phase3-cpu-v2-reproduce/EI-development

# Join validated prefix/suffix transactions to evaluate a recovered trajectory.
# This copies committed states and preserves explicit recovery lineage.
& $py -m scripts.assemble_phase3_v2_recovery --prefix results/phase3-cpu-v2-reproduce/EI --suffix results/phase3-cpu-v2-reproduce/EI-recovered --train-package $train --train-manifest-sha256 $sha --output results/phase3-cpu-v2-reproduce/EI-recovery-collection
& $py -m src.phase3_v2.evaluate --run results/phase3-cpu-v2-reproduce/EI-recovery-collection --output results/phase3-cpu-v2-reproduce/EI-recovery-development

# Full-data v1 parity, exact suffix recovery and matched clean DC/DM/DQ.
& $py -m scripts.verify_phase3_v2 --package data/processed/phase3-cpu-v2-reproduce/s101-p000 --acceptance results/phase3-cpu-v2-reproduce/acceptance.json --output results/phase3-cpu-v2-reproduce/integration

# Complete declared clean procedure: 18 pilots, 60 tuning logical rows;
# up to nine exact aliases. Three FT poison diagnostics run only if all clean
# learner gates pass. The v1 filtered reference is never a pilot alias.
& $py -m src.phase3_v2.development --acceptance results/phase3-cpu-v2-reproduce/acceptance.json --packages data/processed/phase3-cpu-v2-reproduce --output results/phase3-cpu-v2-reproduce/development
```

For controlled-corruption method verification, prepare `--dose 1 10`, `3 10` or
`1 2` in a fresh package, then pass that same rational `--dose` to training.
Matched admission uses `--learner DR --admission DM`, `DC` or `DQ`, with the
same settings/seed/dose and complete local pools. Reference annotations and
poison flags are never passed into training or admission. The full procedure
enforces clean feasibility before its poisoned FT diagnostic.

```powershell
# Evaluator-only exposure accounting; use a complete matching run and package.
& $py -m src.phase3_v2.exposure --package data/processed/phase3-cpu-v2-reproduce/s101-p000 --run results/phase3-cpu-v2-reproduce/integration/DC --output results/phase3-cpu-v2-reproduce/exposure.json
ruff check src/phase3_v2 tests/test_phase3_v2.py scripts/audit_phase3_v2.py scripts/accept_phase3_v2.py scripts/verify_phase3_v2.py
```

## Interfaces and identity

`Settings` is immutable; `StageInput` validates ordered FP32 features, int64
supplied labels, uint64 opaque IDs and five int8 owners, then marks arrays
read-only. `ClientState` retains explicit admissions/dropout and optional replay
or importance/anchor state. `Simulator` runs sequential clients from the same
copied broadcast and commits the whole round transaction. No optimizer survives
the boundary because Adam resets on every broadcast.

The code identity covers every v2 module and all unchanged v1 Python dependencies.
Execution additionally binds the v2 protocol, dated decisions, frozen taxonomy,
exact train manifest, consumed learner settings and pinned CPU runtime. An explicit
expected training-manifest hash is required at the CLI. Features/IDs must match
the pinned train-only v1 arrays. Training packages reject extra/missing files;
evaluation accepts only the exact pinned development manifest. All dataset
derivation is identified as audited-cache reuse, not a new CSV/session rebuild.

Checkpoint NPZ arrays are pickle-free and typed. Commit markers cover payload
and logical-state hashes. Metadata uses strict JSON; PCG64's 128-bit integers
use bounded canonical decimal strings, including its cached uint32 state.
Import validates required keys/arrays/shapes, registry history, next cursor,
ledger counters, locked admissions, sample IDs and shared EI anchors. A failed
round leaves earlier committed boundaries usable. Recovery re-executes that
uncommitted round and is the same logical run, not an additional replicate.
The run field `independent_replicate` distinguishes a from-start execution from
a recovered suffix within its condition. It must not be summed across settings
or retries: independent seed counts require the condition/seed identity, and
verification repetitions of that identity add no independent evidence.

The assembly script validates every transaction, full chronological inventory,
training identity, ledger continuation and frozen admission artifact before
copying the prefix and recovered suffix into a complete collection. Its manifest
uses `artifact_kind=verified_recovered_trajectory_collection_v1`, keeps
`independent_replicate=false`, and stores original resume path, prefix/suffix
hashes and physical costs under `recovery_lineage`. `resumed_from=null` identifies
this full collection for the evaluator; it does not erase the recorded recovery
history. No logical training cost is invented. The collection is suitable for
independent development evaluation and adds no research replicate.

Admission ledger `quotas` entries describe the **DC reference quotas** used to
match control totals. DM applies their sum, DC/DQ apply them within classes,
and NONE bypasses them. They must not be read as DM/NONE's realized per-class
admission counts. Realized selections are the typed `client*.accepted` arrays,
their ID hashes and each client's actual `admitted` total. Round `mean_losses`
contains unweighted means over optimizer batches in the order current CE,
replay CE, dark MSE, EI penalty; these logging summaries are not pooled
record-weighted cross-entropies.

The EI estimator uses per-record gradients at the final aggregate, eval mode,
FP32 square-before-average, min(1024,n) distinct supplied-label records, decay
one and lambda_E/2 penalty. Its reference tolerance was fixed at rtol=2e-5,
atol=2e-7 for FP32 reduction differences. Same-engine recovered states and RNGs
require exact equality. CUDA agreement is untested.

## Evidence boundaries

The original benchmark split, Monday-only calibration, benign inventory,
eligibility and banks are unchanged. All registered rare outputs participate in
argmax. Confirmatory multiclass and descriptive full-seen binary banks remain
separate. The fixed benign union spans capture periods; stage-wise FAR is not a
contemporaneous deployment estimate. The two portscan annotations denote source
scenarios; they do not establish zero-day or underlying-technique novelty.
Ownership uses the full scheduled training inventory to construct synthetic
clients offline; it does not model organizations allocating unknown future
traffic. Reference labels, including the adopted attempted-flow remapping,
are benchmark annotations rather than certified operational ground truth.

Optional FIFO/loss ablations, oracle interventions, external datasets,
confirmatory statistical analysis, CUDA, final-test prediction and the final
12-seed grid are not qualified by this milestone. The twelve final seeds and
single 29-contrast family remain planned and sealed. Eight possible compute
contributors do not change the five simulated clients.
