# Reproduce the acquisition diagnostic

This version runs the fixed exploratory E1 comparison recorded in
[the prior plan](plan-2026-10-24.md). Read [the executed report](report.md) and
[proposed amendment](proposed-amendment.md) for interpretation. It does not edit
or extend the frozen v2 study engine.

From the workspace root in PowerShell, using the existing pinned CPU runtime:

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $py -m scripts.diagnose_phase3_acquisition --output results/phase3-acquisition-diagnostic-v1-reproduce
& $py -m scripts.report_phase3_acquisition --results results/phase3-acquisition-diagnostic-v1-reproduce --docs docs/phase3-acquisition-diagnostic-v1-reproduce
ruff check scripts/diagnose_phase3_acquisition.py scripts/report_phase3_acquisition.py tests/test_phase3_acquisition.py
```

Fresh output directories are required. The diagnostic requires all three
original v2 clean packages and matching FT baselines. It verifies the pinned
data/runtime/parent identity, runs four small acceptance fixtures, reconstructs
all nine FT round states exactly, and executes the locked natural/equal-class
E1 matrix. Baseline parity must pass before intervention outcomes are interpreted.
Development readouts cannot enter learner inputs or objective weights.

The diagnostic scientific identity binds its engine script, tests, config,
prospective plan and frozen parent source. It records exact input manifests,
runtime, full per-round accounting, every seed/cell and E1 model artifact hashes.
The reporting script is separately hashed as a derived-evidence producer.
Its review evidence verifies parent source/delivery preservation and all raw
diagnostic artifact hashes. The original file tree retains all model arrays.

The report generator writes a fresh `evidence/` directory and copies this
version's plan, amendment, log and README when generating a reproduction folder,
so its local documentation links remain usable. No recovery or partial-restart capability is claimed
for exploratory probes: an interrupted probe is an incomplete physical attempt,
and any rerun uses a fresh destination with its cost recorded separately.

Missing qualification: EI/DR under the longer schedule, E2 Hulk and all later
stages, revised-schedule poisoning/filtering controls, GPU runtime/cost and final
release. Final evaluation and GPU dispatch remain blocked.
