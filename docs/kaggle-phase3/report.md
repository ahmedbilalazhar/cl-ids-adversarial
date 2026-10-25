# Kaggle preparation delivery — 25 October 2026

The separate notebook candidate is implemented and verified on the local pinned
CPU runtime. It is ready for private upload and actual Kaggle qualification.
No remote account was accessed, no Kaggle job was launched, and no final-study
inference was performed. The current Windows CPU development grid continues.

## Delivered artifacts

- [Importable notebook](../../results/kaggle-readiness-v1/notebook/phase3-qualification.ipynb)
- [Private qualification bundle](../../results/kaggle-readiness-v1/bundle/qualification.zip)
- [Kaggle metadata template](../../results/kaggle-readiness-v1/notebook/kernel-metadata.json)
- [Eight-contributor course planning scenario](../../results/kaggle-readiness-v1/course-eight-contributors.json)
- [One-contributor alternative](../../results/kaggle-readiness-v1/course-one-contributor.json)
- [Setup, commands and limits](README.md)

The 51,725,948-byte archive contains 69 verified files, including seed-101 clean
supplied-label training inputs and the fixed development bank. It contains no
final-test features, raw source archive or credentials. It is ignored by Git
because it contains derived flow data. Its SHA256 is
`1f8bfd38f4b97b1c39e9acb5c22d3bafeadd55b66698923133d86d075d8fdeb5`.

The notebook checks that digest before extracting source, creates an isolated
pinned environment, runs bounded synthetic acceptance, optionally measures full
development jobs, independently evaluates completed collections and exports
saved outputs. It defaults to CPU and leaves full-data jobs disabled. Actual
Kaggle environment installation was not exercised locally.

## Requirement-to-code-to-evidence map

| Requirement | Implementation | Verified evidence and limit |
|---|---|---|
| Avoid repeated stage loading/target mapping | `kaggle_worker/data.py` | Four cached loads per fixture trajectory; exact CPU state/ledger comparisons |
| FP32 device execution | `kaggle_worker/accelerator.py` | CPU emulation exact across FT/EI/DR/DM/DC/DQ, both v3 budgets and compatibility budget; actual CUDA pending |
| Preserve replay/importance/corruption semantics | Original numerical helpers plus candidate device loop | All-arm half-dose fixture parity, nested integer poison prefixes, independent masked-loss/gradient arithmetic |
| Complete retained state and bounded continuation | `checkpoint.py`, `simulator.py`, `worker.py` | Exact FT/EI/DR suffixes, including a new interpreter; corrupted payload rejection; completed jobs skipped |
| Durable verified handoff | `handoff.py` | Complete synthetic collection verified; traversal and corrupted checkpoint archives rejected |
| Preserve final seals | Development-only `Settings` and CLI | Final seeds 1/42 and undeclared budget rejected; all planning/delivery artifacts remain non-dispatchable |
| Pair seeds across contributors | `planner.py` | Eight package/contributor scenarios retain all twelve unique seeds; no method-to-hardware assignment |
| Measure actual full-worker costs | Notebook subprocess wall clocks, logs, setup costs and worker memory peaks | Instrumented; actual Kaggle measurements pending |
| Independent development evaluation | `evaluate.py`, immutable bank identity, original count arithmetic | Implemented; target-runtime full-data validation remains pending |
| Keep existing CPU evidence unchanged | Separate source/package paths | Frozen numerical identity and 32 controller-bound delivery files rechecked unchanged |

## Verification results

[Acceptance](../../results/kaggle-readiness-v1/acceptance.json) passed **30 groups**
in 258.12 seconds. The main equivalence matrix covers **864 checkpoint pairs**
and **36,864 exact typed-array comparisons**. Fresh-process recovery and poison
checks add further suffix/state comparisons. These are transparent synthetic
fixtures and do not count as research trajectories or independent final seeds.

[Notebook QA](../../results/kaggle-readiness-v1/notebook-acceptance.json) compiled
all four code cells, extracted and hash-verified all 69 bundle payloads, exercised
setup/check/export control flow with explicitly mocked subprocesses, and
confirmed zero default full-data dispatches. This does not claim successful
Linux installation or actual-device execution.

[Bundle acceptance](../../results/kaggle-readiness-v1/bundle/acceptance.json) and
[preservation checks](../../results/kaggle-readiness-v1/preservation.json) passed.
Fatal/undefined-name/unused-import Ruff checks and Python compilation passed for
all candidate modules. Earlier passing fixtures and the interrupted harness
correction are retained; see [change log](change-log.md).

Worker source identity:
`b4c0423786c2a64ca487f75277e328fbedc6ce03e2f509d792dcee58b55a5d1f`.
Frozen numerical identity:
`38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c`.

## Scheduling and scope

The course scenario has 312 final full trajectories plus twelve new oracle
continuations when control aliases are valid. The local loop-time proxy is
24.69 aggregate CPU hours; its busiest eight-contributor assignments contain two
seeds and about 4.11 loop hours each. Filtered/ablation costs use DR as an
unmeasured proxy. Setup, importance outside the recorded loop component,
evaluation, saving, failures and confirmations are additional. There is no
measured Kaggle GPU duration or verified per-account quota.

Generating this scenario does not adopt a smaller scientific scope. Unimplemented
ablations and oracle variants are not silently mapped to ordinary DR. Final
dispatch must wait for the CPU delivery, clean feasibility, actual-device
acceptance and profiles, selected-setting confirmations, full workload costs,
remaining scoped methods, exact final training packages and the final
source/data/runtime/settings/analysis lock. The final bank remains separate.
