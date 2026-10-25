# Code weakness review and optimization delivery

25 October 2026. Scope: the active Phase 3 numerical path and its separately
versioned Kaggle worker. The frozen numerical source and the running CPU grid
are preserved. The initial Kaggle package and its evidence remain under
`results/kaggle-readiness-v1/`; this revision is under
`results/kaggle-readiness-v2/`.

## Findings and corrections

| Priority | Weakness and consequence | Implemented correction |
|---|---|---|
| P1 | A process could finish every checkpoint and crash before writing its completion receipt. The next invocation skipped training but left the notebook unable to recognize completion. | Reconcile verified committed state with receipts, publish a recovered completion receipt, and preserve every existing segment. Fault injection proves zero model re-executions and unchanged checkpoint bytes. |
| P1 | Pinning Python/Torch/NumPy alone allowed transitive packages and bootstrap tooling to drift. Re-running setup also invoked installers unnecessarily. | Pin uv 0.12.18, resolve Linux x86_64 CPU/CUDA environments with complete version/hash locks, use `uv pip sync --require-hashes --only-binary :all:`, record installed packages, and verify an existing environment before reusing it without installation/network operations. Drift fails explicitly. |
| P2 | Development evaluation retained every round's full replay/importance arrays even though inference needs four stage-end models. | Stream integrity validation in canonical stage/round order and retain only four FP32 model snapshots. Check complete cursors, admission stages, finite FP32 payloads and contiguous history. |
| P2 | Label mapping used a Python dictionary lookup per record; the device adapter copied an already fresh target array twice. | Use a fixed 16-entry integer lookup vector, preserve immutable internal cache/fresh public arrays, reject unregistered labels and remove the redundant copy. |
| P2 | Completed-job deduplication verified checkpoints but could ignore changed auxiliary artifacts. | Check the exact saved segment-file inventory and every receipt payload digest before skipping work. |

The implementation uses bounded caches, vectorized array operations, streaming
I/O, transactional receipts, exact recovery, fault injection, dependency locks
and explicit environment identities. The environment strategy follows
[uv's lock/sync guidance](https://docs.astral.sh/uv/pip/compile/). The candidate
uses an independent versioned execution identity; old runs are not relabeled.

## Measured results

The fixed nine-pair synthetic benchmark uses 183,045 supplied-label integers,
with no research feature rows. The final revision measured median target-mapping
time **81.45 ms → 1.38 ms**, approximately **59× faster for that mapping kernel**.
The earlier preliminary benchmark measured about 50× and is retained. Timings
were collected alongside the background CPU study and synthetic acceptance
checks; they are not an isolated machine benchmark or a full-training speedup.
The previous candidate already cached mappings, so this optimization mainly
reduces cache-construction cost there.

For an exact 12-checkpoint synthetic DR collection, retained NumPy payloads fell
from **12,505,392 bytes to 291,936 bytes**, a **97.7% reduction**. Traced peak
allocations fell from **22,072,443 to 10,052,643 bytes**, about **54.5% lower**.
This measures traced Python/NumPy allocations, not whole-process RSS or GPU
memory. All retained model arrays match the prior full-retention reader exactly.

The fault-injection regression recovered the completion receipt with **30
segment files unchanged**, **zero new training executions**, and one original
segment. Changing a saved settings artifact was rejected even though its model
checkpoints still passed integrity validation.

The CPU dependency lock resolves 11 packages; the CUDA lock resolves 26.
Resolution used actual package metadata and distribution hashes for Python
3.12.14/Linux x86_64. No large GPU wheel installation or actual CUDA run was
performed locally. Linux bootstrap install/reuse/drift control flow was tested
with explicitly mocked subprocesses; real installation remains a Kaggle check.

## Code and evidence

| Behavior | Source | Evidence |
|---|---|---|
| Vectorized target cache | `kaggle_worker/data.py` | [Final regression/benchmark report](../../results/kaggle-readiness-v2/review-final.json) |
| Completion reconciliation and immutable receipts | `kaggle_worker/worker.py` | Same report: crash-before-receipt and artifact-drift tests |
| Streaming stage model collection | `kaggle_worker/evaluate.py` | Same report: exact model arrays and measured allocation reduction |
| Locked setup and runtime fingerprint | `bootstrap.py`, `runtime.py`, `locks/cpu.txt`, `locks/cuda.txt` | Resolved hash locks and mocked install/reuse/drift tests |
| Numerical semantics and recovery | Existing frozen engine plus `kaggle_worker` candidate | [30-group acceptance](../../results/kaggle-readiness-v2/acceptance.json), including exact checkpoint arrays/ledgers, poison fixtures and fresh-process recovery |
| Bundle and notebook integrity | `bundle.py`, `notebook.py` | [Bundle receipt](../../results/kaggle-readiness-v2/bundle/acceptance.json), [offline notebook QA](../../results/kaggle-readiness-v2/notebook-acceptance.json) |
| Existing CPU delivery unchanged | Frozen source and controller procedure | [Preservation check](../../results/kaggle-readiness-v2/preservation.json) |

The full candidate source identity binds both Python source and dependency-lock
assets. Notebook v2 uses separate source, environment and output directories to
preserve the original delivery. Use the [updated setup instructions](README.md)
and [v2 notebook](../../results/kaggle-readiness-v2/notebook/phase3-qualification.ipynb).

## Remaining weaknesses and practical limits

Actual Kaggle GPU throughput, CPU/GPU numerical behavior, driver compatibility
and full job cost remain unmeasured. CUDA may spend substantial time on small
kernel launches, host checks and replay transfers. A tiny MLP is not guaranteed
to benefit from CUDA. Use the notebook's complete subprocess costs and, when
needed, [PyTorch profiling](https://docs.pytorch.org/tutorials/beginner/profiler.html)
on the target worker before choosing another optimization.

The broader repository still contains historical runners and broad dependency
ranges. The qualified notebook uses the isolated Phase 3 entry point and its
locks. Historical code is not promoted into current research evidence. No AMP,
TF32, larger batches, fused optimizers, changed quotas or skipped finite checks
were introduced to produce a speed claim.

Final-study ablations/oracle variants, actual target-runtime confirmations and
clean feasibility remain release gates. Scope selection and the complete
twelve-seed dispatch remain sealed pending those gates. The current CPU
controller continues independently; routine monitoring remains active.
