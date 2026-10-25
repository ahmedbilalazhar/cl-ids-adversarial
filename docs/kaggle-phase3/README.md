> Current continuation, 2026-10-25: CPU v3 is verified; Kaggle v4 corrects selected-setting binding. Final scope, actual CUDA equivalence and durable Kaggle recovery remain gated. Historical instructions below retain their original scope. See [continuation audit](../phase3-cpu-v3/continuation-audit.md).

# Kaggle notebook preparation — 25 October 2026

This is a separate development qualification candidate. The ongoing Windows CPU
grid, its nine delivery steps, scientific source, protocol and decisions are
unchanged. The numerical source identity must remain
`38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c`.

The project record describes eight distinct contributors, each operating their
own account. The scheduler assigns whole paired seed blocks and never signs into
accounts, shares credentials, rotates accounts or starts remote work. Eight
workers still each simulate five FL clients. Kaggle permits one active account
per person: [terms](https://www.kaggle.com/terms).

## What changed

`kaggle_worker/` is deliberately outside the frozen source and the CPU
controller's bound delivery-script inventory.

- Validate the complete supplied-label training package before numerical work.
- Cache each immutable stage and its supplied-label-to-output mapping. The
  existing engine reloads/revalidates a stage every round and reconstructs targets
  for every client. The candidate avoids that repeated work.
- For CUDA, copy each stage's FP32 feature bank to the selected device once and
  reuse its target tensors. Keep CPU initialization, admission integer quotas,
  reservoir/ordering streams, and fixed-order FP32 CPU aggregation explicit.
- Group gradient and optimizer finite checks at their existing logical
  boundaries. Every checked tensor is retained; fewer separate host/device
  synchronizations are required. Keep teachers before updates, insertion after
  updates, current/replay means separate, and EI's accepted estimator unchanged.
- Persist CPU and CUDA dropout streams separately. Save both in hashed,
  pickle-free round transactions; reject missing/incompatible states and preserve
  interrupted segments. Resume never adds a seed replicate.
- Stop before starting another transition when the planning bound plus save
  reserve exceeds the remaining session budget. This is a planning guard, not a
  hard guarantee against unexpectedly long transitions or VM termination.
- Independently evaluate complete committed collections on the pinned development
  bank using CPU inference and the existing count arithmetic. No final evaluator
  or final-seed switch is provided.

The CUDA implementation is a candidate. Passing its CPU emulation does not
qualify CUDA. CUDA dropout draws and floating-point training need not match CPU
trajectories. Do not splice a CPU checkpoint into a CUDA run. A common backend,
GPU model, driver/build, precision policy and paired settings must be frozen
before final dispatch. AMP, TF32, fused Adam, batch-size changes, torch.compile,
DDP and cross-device client aggregation have not been enabled.

## Private qualification notebook

The latest reviewed candidate, generated files and bundle receipt are under
`results/kaggle-readiness-v3/`. The original v1/v2 deliveries are retained as historical
evidence. See [the architecture review and decision](architecture-v3.md) and
[the earlier performance fixes](review-v2.md). The notebook is intended for manual import into
Kaggle; no account access or upload occurs locally.

1. Upload `bundle/qualification.zip` as a **private** Kaggle dataset. It contains
   exact frozen source, the separate candidate, seed-101 clean training inputs
   and the pinned development bank. It contains no final-test features, builder
   oracle annotations, raw source archive or credentials. Dataset access and
   redistribution rights remain the contributor's responsibility.
2. Import `notebook/phase3-qualification.ipynb`. Attach the private dataset and set
   `BUNDLE` to its mounted path. The notebook enforces the exact archive digest
   before extracting or executing source.
3. Start with `DEVICE='cpu'`. Enable Internet for the isolated environment setup.
   The environment uses Python 3.12.14, NumPy 2.3.5 and Torch 2.7.0+cpu. It does
   not replace packages in Kaggle's notebook interpreter.
   All transitive dependencies and download hashes are locked. A matching,
   fingerprint-verified environment is reused without installing or accessing
   the network. Environment drift requires a fresh environment directory.
4. Run the synthetic checks. Preserve failed evidence. Use a separate environment
   and output directory with `DEVICE='cuda:0'` for CUDA qualification, enabling an
   actual Kaggle GPU. That candidate uses Torch 2.7.0+cu126. The notebook records
   device, driver, CUDA, cuDNN, framework build and deterministic precision policy.
5. After the fixture checks, enable `RUN_FULL_DATA` to measure full FT/EI/DR
   development workers. These pilot-default jobs measure execution; they are
   not selected clean confirmations or final study results. Inspect their
   complete wall costs and development predictions. Do not choose the backend
   based on favorable model outcomes.
6. Save Version / Run All, wait for a successful saved version, download and
   hash-verify its output archive. Save all segments, logs and receipts. A file
   present only in a running VM is not a durable handoff.

The initial notebook uses one device/job at a time. Two T4s do not automatically
accelerate one small model. After measuring full-job throughput and actual quota
charging, independent paired blocks may use separate GPUs/processes. Avoid
running every instance of one learner on a different hardware type.

Kaggle documents session/output limits, which can change; inspect the actual
session options and account quota before assigning work. See
[notebooks](https://www.kaggle.com/docs/notebooks) and
[GPU usage](https://www.kaggle.com/docs/efficient-gpu-usage). GPU availability and
speedup have not been measured for this project.

## Local reproduction commands

These commands run synthetic checks or package existing data. They do not launch
the final study or rerun valid local research conditions.

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $py -m kaggle_worker.architecture_checks --output results/kaggle-readiness-v3/architecture-release-final.json
& $py -m kaggle_worker.checks --device cpu --output results/kaggle-readiness-v3/acceptance-final.json
& $py -m kaggle_worker.review_checks --output results/kaggle-readiness-v3/review-final.json
& $py -m kaggle_worker.planner --package course --contributors 8 --output results/kaggle-readiness-v3/course-eight-contributors.json
& $py -m kaggle_worker.planner --package course --contributors 1 --output results/kaggle-readiness-v3/course-one-contributor.json
& $py -m kaggle_worker.bundle --output results/kaggle-readiness-v3/bundle
& $py -m kaggle_worker.notebook --bundle-receipt results/kaggle-readiness-v3/bundle/acceptance.json --output results/kaggle-readiness-v3/notebook
```

Outputs are immutable. Use a fresh destination for another attempt. Evidence and
paths refer to this working-tree snapshot; untracked source is not a Git commit.

## Workload and time correction

The earlier chat estimate was arithmetically wrong. Twelve seeds times only the
three clean learners is 36 trajectories: using 201.9 + 233.9 + 314.6 seconds per
seed gives **2.50 training-loop hours**. It is not the complete study.

The existing planning manifest specifies 240 final full trajectories for core,
312 for course, 360 for the focused package, and 552 for the complete original
plan. Each also needs twelve new oracle continuations when the primary controls
are valid aliases. Development, failed attempts and runtime confirmations are
additional. The original complete scope remains the target unless a prospective
scope amendment is adopted; generating course assignments does not adopt one.

The scheduler uses measured local unfiltered loop medians as a transparent
planning proxy, with DR's median substituted for unmeasured filtered/ablation
conditions. It does not assume E1 reuse or GPU speedup. It reports aggregate
hours separately from the longest contributor assignment. Eight contributors
receive two seeds each for contributors 1–4 and one each for 5–8. Actual quotas,
availability, complete Kaggle job costs and saving overhead remain unknown.

The generated course scenario is **24.69 aggregate CPU loop hours**, with a
**4.11-hour** longest assignment at eight contributors, or 24.69 hours at one
contributor. These figures exclude the costs listed above and substitute DR
timing for filtered/ablation conditions; they are not Kaggle GPU estimates.

## Downloaded-output verification

The notebook logs each subprocess, includes interpreter import/input/saving time
in its parent wall clock, records environment setup separately, and writes worker
resource high-water values. It exports immutable segments and receipts without
the installed environment or input dataset. Preserve the exact export digest
printed in the notebook.

```powershell
& $py -m kaggle_worker.handoff --archive PATH-TO-DOWNLOADED-OUTPUT.zip --archive-sha256 SHA256-PRINTED-BY-NOTEBOOK --output results/kaggle-readiness-v3/returned-output-integrity.json
```

This verifies the archive, source/runtime identities, receipt payloads,
checkpoint typed-state hashes and contiguous lineage without executing a model.
It reports partial/failed attempts. It does not turn a qualification result into
a final release or an additional final seed.

## Remaining release gates

Finish and independently verify the current CPU grid/delivery. Establish clean
feasibility. Run actual Kaggle CPU/CUDA fixtures, independent estimator checks,
same-runtime fresh-process recovery, complete-worker profiles and selected
settings confirmations on seeds 101–103. Complete target-runtime corruption and
matched-control acceptance. Finish any scoped ablation/oracle implementation.
Choose scope from measured costs before final outcomes, prepare exact final
training packages separately, and freeze code/data/runtime/settings/analysis.
Final-test inference and the final GPU study remain sealed.
