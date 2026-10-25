# Kaggle execution contract — current v5 qualification

Status: development qualification only. This contract does not authorize final
seeds, final features, final inference or a GPU grid. It complements the existing
[worker architecture](../kaggle-phase3/architecture-v3.md); v3 remains historical.

## One execution path

Generate the notebook with `python -m kaggle_worker.notebook`. The current v5 candidate is
[phase3-qualification.ipynb](../../results/phase3-two-hour-audit-v1/candidate-v5/notebook-final/phase3-qualification.ipynb).
It invokes `bootstrap`, `preflight`, `checks`, `worker`, and `evaluate` modules;
it contains no training equations. CPU `backends.CPUBackend` delegates frozen
numerical functions. `simulator.execute` is a separately tested transaction
orchestrator, not the original CPU CLI. CUDA `accelerator.Accelerator` remains
a candidate implementation, not an equivalent engine by declaration.

`selection.selected_settings` reads the immutable tuning selection (SHA256
`9f0b1a0e05fa7c329acee199d3236bf53c375e520a76763cf7264d7fc16d4fc4`).
The bundle includes that record. Worker CLI defaults now come from it: 12 rounds,
1 epoch, LR .001, EI coefficient 100, DR label 1/logit .1. Unused coefficients
retain the original selected record values. Explicit coefficient overrides
require `--qualification-overrides`; final seeds remain rejected independently.
Python fixture APIs can still specify development settings and are not final
dispatch APIs. The scientific settings identity excludes unused coefficients.

Job identity binds frozen source, candidate source, protocol, decisions,
taxonomy, consumed settings, runtime and train manifest. The candidate revision
is `kaggle-qualification-v5`; old worker receipts must be evaluated with their
archived matching source. Hash binding does not authorize a run.

## Preflight and target-environment evidence

The notebook verifies the bundle and prepared train/development bytes, installs
the hash-locked Python 3.12.14 environment, and calls `preflight.inspect` before
fixtures. It records PyTorch, CUDA/driver/device, NumPy, all installed packages,
Linux available memory and disk. Scikit-learn is explicitly not required: the
metric engine uses integer counts and NumPy. An installed version is recorded.
The declared session limit must be checked against the actual provider UI;
the preflight does not pretend to query account quotas. Its storage threshold
is a reservation, not a measured full-study storage budget.

Set `RUN_FULL_DATA=True` only after inspecting successful fixture receipts.
Run selected clean FT/EI/DR seed101 jobs and record the whole notebook command
time, component training/admission/importance/checkpoint times, evaluation and
export costs. Extend to the paired clean development seeds101–103 using matching
prepared packages before runtime adoption. The current bundled package contains
seed101 only. Never substitute seed101 data under another seed identity.
No local CPU timing is a CUDA speed estimate.

## Numerical equivalence is not yet established

Initialization, head growth, fixed-order aggregation and reservoir draws remain
CPU-owned; loss/importance tensors and dropout can run on CUDA. Existing CUDA
primitive checks use rtol=2e-5, atol=2e-7 for forward/importance and 2e-7 for
masked replay arithmetic. These are primitive tolerances, not an approved
trajectory equivalence margin. Never expand them after seeing a failure.

`Accelerator.initialize_clients/train_client` uses a CUDA RNG state for dropout;
CPU and CUDA generators do not supply the same masks merely from the same seed.
Actual CUDA checks currently test forward/importance and same-runtime recovery;
they do not establish CPU/GPU whole-training equality. Before adoption, compare
fixed-input, dropout-disabled gradient/update primitives; exact parameter order,
integer quotas, ID tie-breaking and named CPU streams; all committed state and
metrics in controlled fixtures; and paired full development outcomes. Record
any changed admission identities, including near-tie ranking changes. A changed
runtime pipeline needs prospective scientific disposition and clean feasibility
confirmation. A universal final-metric tolerance has not been approved.

PyTorch documents that reproducibility is not guaranteed across CPU and GPU
even with identical seeds: [reproducibility notes](https://docs.pytorch.org/docs/stable/notes/randomness.html).

## Recovery and import

The OS writer lock rejects concurrent writers; transactions have payload and
commit hashes. Incomplete segments and unreceipted commits remain visible.
Resume verifies the source/runtime/settings/data identity and contiguous history.
No retry, prefix, alias, segment or profile adds a statistical replicate.

On Kaggle, interrupt a development fixture at a committed boundary, save the
version, download and hash its export, end the session, restore into a fresh
matching environment, inspect with `kaggle_worker.handoff`, and resume. Compare
full state/predictions to an uninterrupted fixture. Also try changed source,
runtime, settings, damaged payload, duplicate writer and incomplete export.
Retain every failed attempt. Local recovery does not prove provider durability.

`phase3_delivery.import_counts.import_counts` accepts only development/synthetic
count artifacts against caller-supplied settings/execution and payload hashes.
CPU metrics additionally require their separately SHA256-bound complete from-start run manifest; Kaggle metrics embed execution identity. It reconstructs full/eligible confusion, binary/Hulk partitions, acquisition,
cohort endpoints and the complete lower-triangular accuracy matrix. It rejects
duplicate run IDs and repeated condition identities before registry mutation.
The caller must obtain expected bindings from a frozen registry, not from the
incoming result. The continuation v2 [persistent registry and assembler](result-registry-contract.md) now implements development and fabricated synthetic collection. A final-results mode still requires the final scope, target runtime and manifest freeze.

The existing `src.phase3_analysis.statistics` remains the analysis engine.
`phase3_delivery.analysis.seed_summary` adds complete-paired-seed mean and sample
SD without changing its identity or inferential rules. The named Holm family is
still **all_29**, one family, alpha .05, two-sided. C1/C2 are question labels,
not separately corrected families. Exploratory methods must not silently gain
confirmatory status. Missing endpoints retain explicit missingness; no metric
imputation or favorable seed replacement is allowed.


## v5 session and committed-output contract

`session.SessionBudget` starts before extraction. Read the remaining allowance
from the actual provider UI; setup, fixtures, training and evaluation consume
one clock. The 240-second export reserve needs target measurements. Commands
retain argv, log hashes, wall times and failure/timeout receipts. Their owned
process group is stopped before failure export. Provider kills can bypass cleanup.

`evaluate --verify-existing` requires an intact commit with matching job, bank,
runtime, payload inventory and model hashes. Partial attempts are preserved.
Exports hold worker locks, stream files and recheck inventory/hashes; runtime
mutex bytes are explicitly excluded. Local ZIP creation is not provider durability.

Use `phase3_delivery.worker_import` for returned v5 development output with an
externally reviewed registry pin, the exact notebook export SHA256 and an explicit
run mapping. It validates a private archive snapshot, NPZ size/shape envelopes,
complete checkpoint lineage, evaluation/model bindings and counts before writes.
See the [registry contract](result-registry-contract.md). No final import exists.
