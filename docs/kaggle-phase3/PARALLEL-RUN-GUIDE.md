# Parallel Phase 3 execution: operator guide

26 October 2026. Start with [QUICKSTART](QUICKSTART.md) for the prepared files.
This guide explains parallel qualification now and scheduling the final study
after its release gates pass. **The current notebook cannot run final seeds.**

## 1. Choose the account arrangement

Kaggle's [terms](https://www.kaggle.com/terms) allow each person one active
account and prohibit sharing account credentials. Therefore:

* **One researcher:** use their own account and the concurrent sessions actually
  permitted by its current session manager, or additional approved compute.
* **Several researchers:** each person operates their own account and assigned
  notebooks. The eight-worker example below means eight distinct contributors.

Do not plan eight personal accounts as eight independent entitlements for one
operator. Collaboration shares project artifacts and assignments, not logins.
This guide performs no invitations, uploads, account operations or dispatch.

Check current quotas and available concurrency in each account's actual UI.
Do not assume an old advertised weekly allowance or session count applies.
Kaggle's [GPU guidance](https://www.kaggle.com/docs/efficient-gpu-usage) describes
monitoring usage and stopping unnecessary sessions. Concurrent work within one
account consumes that account's available allowance; it creates no new quota.
Measure charging for the chosen device/session configuration.

## 2. Understand the work being parallelized

One trajectory runs one learner, admission policy, dose and seed through E1–E4.
That job already simulates **all five federated clients** inside one process.

A **paired seed block** contains every selected learner/policy/dose condition for
one training seed, including its matching clean references. Assign whole blocks
initially. This preserves pairing and avoids assigning one learner exclusively
to one hardware type. It is job-level parallelism, not cross-account FedAvg or
distributed training of a single MLP.

The twelve final seed labels are `[1,2,3,4,5,6,7,8,9,10,11,42]`.
The frozen planning manifest currently contains these alternative menus:

| Planning menu | Final full trajectories | Full conditions per seed |
|---|---:|---:|
| Core | 240 | 20 |
| Course | 312 | 26 |
| Focused | 360 | 30 |
| Focused plus external | 432 | 36 |
| Original complete | 552 | 46 |
| Strengthened | 648 | 54 |

These exclude the 81 logical development rows and separately budgeted new oracle
suffixes. Some menus require unimplemented or unqualified interventions and
additional data audits. **No menu is adopted by generating an assignment.**
Core alone does not fulfill the ablation rubric. See the
[scope reconciliation](../phase3-plan/continuation-scope.json).

## 3. Share one immutable private input release

The coordinator prepares the exact reviewed private `.b64` bundle, matching
notebook and hash receipt from QUICKSTART. Upload the `.b64` file as a private
Dataset. Give contributors viewing access through the Dataset's sharing
controls; they do not need permission to replace its contents.

Kaggle documents that
[private Dataset and Notebook permissions are separate](https://www.kaggle.com/docs/datasets).
Sharing a notebook alone does not grant access to its inputs. Each contributor
should import their own copy of the reviewed notebook and attach the same
release-specific Dataset version. Check the expected hashes inside the notebook;
an unchanged Dataset name does not prove unchanged bytes.

For the **current qualification**, the bundle contains clean **seed101 only**.
Copying it to eight notebooks does not create eight different training seeds.
Final execution will need separately prepared, reviewed seed/dose-specific data
packages and a frozen release manifest. Those are not supplied by this guide.

## 4. Qualify one allocation before expanding

On the first contributor's notebook:

1. Attach the private Dataset and enable Internet for dependency installation.
2. Set `ENCODED_BUNDLE` to its actual mounted `.b64` file path.
3. In the existing configuration cell, set `DEVICE='cpu'`,
   `RUN_FULL_DATA=False`, and the actual remaining session allowance in
   `SESSION_REMAINING_SECONDS`.
4. Run the notebook. Retain the fixture acceptance and output export receipt.
5. Start a separate GPU allocation. Enable GPU through the notebook's settings,
   change `DEVICE='cuda:0'`, keep `RUN_FULL_DATA=False`, and run again.
6. Verify actual CUDA fixture success, then run the authorized clean seed101
   FT/EI/DR development confirmations with `RUN_FULL_DATA=True`.
7. Download the output ZIP and adjacent receipt; verify their hashes locally.
8. Complete the interrupted-save/download/end-session/restore/resume comparison
   in K03 of the [execution contract](../phase3-plan/kaggle-execution-contract.md).

Other contributors then qualify their own target environments. Keep the same
source, precision policy and a scientifically adopted compatible runtime pool.
Record actual GPU model, driver, package fingerprint and fixture receipts for
each worker. Shared filenames or the same random seed do not establish runtime
equivalence. Full confirmations are allocated by the qualification protocol;
do not duplicate all research conditions on every contributor.

The current v5 CLI deliberately accepts development seeds101–103 only, and this
bundle supplies 101. Do not edit validation, rename 101 data as another seed, or
paste final seed labels into the qualification notebook. The current
`RUN_FULL_DATA` switch enables development confirmations, not a final grid.

## 5. Measure costs and check every worker's capacity

For each relevant condition category, record complete job wall time, charged
quota, setup, admission, importance, checkpoints, CPU evaluation and export.
Also record current quota, session allowance, free storage and availability.
The [tracker template](../../results/phase3-parallel-guide-v1/tracker-template.json)
has empty fields for these measurements; `null` means unknown.

Use:

```text
usable quota = displayed remaining quota × (1 − operational reserve fraction)
required quota = sum of measured charged costs of assigned jobs and overhead
feasible only if required quota ≤ usable quota for EACH worker
```

A 20% reserve is an illustrative operational choice, not a measured guarantee.
Do not subtract a reserve twice. A sufficient fleet total can still leave a
worker with two blocks over quota. Each session also needs a separate saving
margin and enough storage; a seed block may span several saved sessions.

Retain the same runtime within a paired block. If GPUs differ, qualify and
prospectively adopt compatible pools before assignment. Do not put all FT on
one GPU type and all DR on another, or splice CPU and CUDA checkpoints together.
Exact checkpoint-runtime compatibility must be checked before any transfer;
matching GPU marketing names alone is insufficient.

## 6. Freeze and release before final assignments execute

The authors must adopt scope, complete its missing adapters and data packages,
qualify runtime/recovery, freeze source/settings/data/analysis, and explicitly
authorize final execution. Preserve the single `all_29` comparison family.

After that release, give each contributor a manifest listing exact assigned
job IDs, input hashes, settings, dependencies and expected artifacts. Include
every selected condition and all twelve paired seeds. Do not choose optional
conditions or replace seeds after viewing final outcomes.

**Current status: this release does not exist.** The files linked below are
planning metadata; they cannot make missing methods or a final dispatcher work.

## 7. Use this initial eight-contributor assignment

| Worker | First block | Second block |
|---|---:|---:|
| A | Seed 1 | Seed 9 |
| B | Seed 2 | Seed 10 |
| C | Seed 3 | Seed 11 |
| D | Seed 4 | Seed 42 |
| E | Seed 5 | — |
| F | Seed 6 | — |
| G | Seed 7 | — |
| H | Seed 8 | — |

A–H run their first blocks simultaneously. A–D then run the second wave, provided
their measured quotas and session margins permit it. All methods/doses for a
given seed belong to that block; they are not eight copies of one job.

The [plan summary](../../results/phase3-parallel-guide-v1/plan-summary.json)
lists eight-contributor job plans for all six menus. One-contributor comparisons
are stored alongside them. The
existing planner can regenerate a scenario without training or dispatch:

```powershell
python -m kaggle_worker.planner --package complete --contributors 8 --output results/fresh-parallel-plan.json
```

Here `complete` is an example menu, not an adopted scope. Use a fresh output
file. The planner retains `planning_only=true`, `final_dispatchable=false`,
unknown GPU hours and unverified quotas. Its CPU-loop proxy is not a GPU ETA.

For a later measured scheduler, rebalance **unstarted** jobs using expected
remaining costs and compatible capacity. Finer job fragments can reduce idle
time only after their state/paired-runtime semantics and importer are qualified.
Keep completed outputs, failures and parent lineage; retries add no replicates.

## 8. Launch without paying twice for the same work

Choose one execution route for each assigned job:

* **Interactive:** run it once, execute the notebook's export cell, download
  the ZIP and receipt, then explicitly stop the session.
* **Saved batch:** configure the notebook first, then use **Save & Run All** to
  run it in a clean session. Wait for the saved version, then download outputs.

Kaggle's [notebook documentation](https://www.kaggle.com/docs/notebooks) explains
that Save & Run All starts fresh and reruns cells. Pressing it after a completed
interactive experiment can execute the same workload again. Quick Save stores
the notebook snapshot; do not treat it as a verified checkpoint backup. Cancel
unneeded sessions, and verify ownership/runtime charging in the actual UI.

Start with one training process per allocation. A two-GPU allocation does not
automatically accelerate this small model: the current notebook uses one device.
Independent processes on device 0/device 1 are a later measured option requiring
separate outputs, budgets and resource checks. No DDP or multi-GPU launcher is
provided by this guide.

## 9. Save, recover and collect results centrally

Before starting another expensive transition, allow time for checkpointing and
export. Stop at committed boundaries when necessary. An unfinished job remains
unfinished even if the notebook itself exits successfully.

For each handoff retain:

* Worker/contributor ID, assigned job ID and attempt ID;
* Exact export ZIP and its independently retained SHA256 receipt;
* Job/settings/source/runtime/input bindings;
* Every checkpoint segment, commit marker, invocation receipt and command log;
* Committed evaluation, integer counts and prediction artifacts when applicable;
* Failure description and last verified commit for interrupted jobs.

Use unique return folders such as `returns/A/JOB_ID/attempt-001/`. Preserve prior
attempts. Do not run two processes against the same job directory or sync an
open SQLite database between contributors. Contributors return immutable files;
the coordinator verifies and imports into the central catalog.

For **v5 development exports**, the verified importer is
`python -m phase3_delivery.worker_import`; it requires a reviewed registry,
archive pin and explicit mapping. See the
[registry contract](../phase3-plan/result-registry-contract.md) for its actual CLI.
It does not support final results. The final collector must be qualified against
the adopted release before the final grid starts.

Resume only after verifying the exact source/runtime/data identity and last
committed state. If a fresh allocation is incompatible, preserve the attempt
and resolve the runtime mismatch; do not silently alter its identity to resume.

## 10. Count completion correctly

The coordinator marks a job verified only after artifact checks pass. A seed
block is complete only when every selected condition/reference is accounted for.
Count each physical trajectory once; an alias, retry, prefix or re-evaluation
does not create an independent seed. Preserve missing/invalid outcomes rather
than excluding unfavorable runs. Final analysis requires the validated paired
matrix and the frozen missingness/family rules.

## Expected time reduction

Let `B` be the **measured total time of one complete paired seed block**, including
its selected conditions. With equal blocks and one block at a time per worker:

| Qualified simultaneous workers | Waves for 12 blocks | Ideal experiment wall time | Ideal speedup over serial |
|---:|---:|---:|---:|
| 1 | 12 | 12B | 1× |
| 2 | 6 | 6B | 2× |
| 4 | 3 | 3B | 4× |
| 8 | 2 | 2B | 6× |

For example, **if** a block measured two hours, serial execution would take
24 hours and eight-worker whole-block execution roughly four hours, before
additional startup/coordination/diagnostic costs. This is a hypothetical example,
not the measured runtime of this study. Unequal costs, allocation delays and
saving can reduce speedup. Finer qualified job scheduling may approach the
ideal work bound `total measured work / workers`, but is not implemented here.

Parallelism reduces waiting time. It does not reduce the statistical study to
fewer than twelve seeds or automatically reduce total charged compute.

**Do now:** run one actual Kaggle qualification using QUICKSTART, return its
export and receipt for verification, and measure costs. Expand to a qualified
contributor pool before releasing the final twelve-seed assignments.
