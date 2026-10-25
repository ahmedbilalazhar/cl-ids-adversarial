# Candidate change and evidence ledger

25 October 2026: the user requested optimization and notebook preparation for the
twelve-seed Kaggle study. Existing project records describe eight distinct
contributors, not eight accounts operated by one person.

This adds a separately identified engineering candidate. It does not amend the
frozen v3 numerical methods, seeds, doses, gates, data, analysis or current grid.
The CPU candidate delegates numerical work to the original learning functions.
Its cache and bounded orchestration require exact typed-state/ledger comparison.
The CUDA candidate has a separate device execution and saved CUDA RNG state;
CPU/CUDA bitwise equivalence is neither assumed nor a release claim.

Before tests, the comparison policy is:

- CPU cached and device-emulated fixture states: exact metadata, ledger, typed
  arrays and logical checkpoint identities. Ignore incidental NPZ ZIP timestamps.
- Same-runtime recovery: exact metadata, retained arrays, RNG, final states and
  ledgers, including a fresh-process continuation.
- CUDA per-example importance against independent single-record autograd and
  small forward comparisons: rtol 2e-5, atol 2e-7, consistent with the accepted
  FP32 estimator's tolerance for small reduction-order differences. These
  tolerances do not license changing sampling, chunks or numerical precision.
- Hand-derived masked dark loss and gradient: rtol/atol 2e-7 for the small FP32
  fixture. No tolerance is used for IDs, quotas, counts, RNG or checkpoint hashes.
- Full-data target-runtime performance and clean feasibility: pending; no metric
  threshold or tolerance is invented here to make a GPU result pass.

The first fixture execution and any subsequent corrections are retained under
`results/kaggle-readiness-v1/`. The original CPU grid/controller and frozen-source
identities are independently checked after candidate delivery. No remote upload,
Kaggle account operation, final inference or actual GPU run has occurred locally.

The first 24 fixture groups passed. A read-only cached target array triggered a
PyTorch input-alias warning, so the public target method now returns a fresh
copy while retaining its immutable internal map. A subsequent extended fixture
attempt was stopped after static checking exposed a local path variable
shadowing the corruption helper; it was renamed. The interruption record and
earlier passing evidence are retained. Neither correction changes the frozen
learner or any research trajectory.
