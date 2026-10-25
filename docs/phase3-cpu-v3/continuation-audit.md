# Continuation audit — 25 October 2026

## Verdict

CPU v3 is independently verified within its delivered development scope.
The final study is **not ready for authorization**. The Kaggle default-settings
integration defect is corrected in candidate v4, outside the frozen engine.
Actual CUDA semantic qualification, runtime adoption, final scope and durable
Kaggle handoff remain unresolved. No final features/outcomes were accessed and
no final matrix was launched. No claim of publication readiness follows.

Baseline local HEAD and remote HEAD/main were independently checked at
`b77a7bbf11c1e4ae7cc06f79e5d7d7d452dbf932`. Only ignored/local scratch `tmp/`
was untracked. No applicable AGENTS.md was found in the repository or ancestors.
Work uses branch `codex/phase3-continuation-readiness`; no default-branch push.

## CPU evidence and preservation

The fresh [delivery audit](../../results/phase3-continuation-v1/cpu-delivery-audit.json)
revalidated 22 frozen scientific modules, source identity
`38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c`, parent
identity, protocol/decisions, 32 controller-bound files, nine completed steps,
81 logical rows, 7,200 artifact payloads, and the 287-file CPU source bundle.
It also traced 559 compatibility, 1,080 matched-control, 104 recovery checks
and eight malformed count rejections. This was a fresh hash/arithmetic audit
of historical tests, not 1,743 newly executed model checks.

The first audit invocation finished verification but could not publish into a
missing output directory. Its [failure record](../../results/phase3-continuation-v1/audit-attempt1-failure.txt)
is retained. The successful retry took 41.06 seconds and ran no model.

The existing [report](report.md), [requirements map](requirements-to-evidence.json),
[artifact index](evidence/artifact-index.json), and historical attempts remain.
The audit preceded intentional roadmap/README updates. Original bytes of every
updated baseline document are [archived with hashes](../../results/phase3-continuation-v1/baseline-documents/manifest.json).
The historical CPU source ZIP is still its original snapshot; it does not claim
to contain this continuation's updated documentation or candidate worker.

Selection is 12 rounds × 1 epoch, no class weighting, LR .001 for all learners.
EI uses lambda_E=100; DR uses lambda_y=1 and lambda_z=.1. Mean development scores
are FT .31082626545, EI .34836255931, DR .66758478517. FTP recalls are [1,1,0]
for seeds101–103 in every selected learner. The mean .6667 passes the declared
.5 gate; the zero seed is retained. This reveals acquisition variability,
not grounds for deleting a seed or changing to a per-seed gate retrospectively.

The three paired FT p=.5 persistent Hulk-error differences are .1246450432,
.00001577586 and −.000441724. They are development diagnostics, not final defense
effects. DC/DM/DQ are matched clean engineering controls on seed101: equal counts,
weights and named-stream positions, not equal retained IDs or learned models.
The full poisoned EI/DR/filter matrix has not run. Both timing corrections
preserve exact state/ledger parity and changed no selected winner. CPU profiles
are 263.81/312.47/346.38 seconds end-to-end for FT/EI/DR, excluding installation
and network transfer. They cannot predict Kaggle GPU cost.

## Findings, corrections and acceptance

| Severity | Exact evidence | Consequence | Correction / acceptance | Status |
|---|---|---|---|---|
| High | Baseline `kaggle_worker.worker.main` defaults EI=10, DR z=.5; `notebook.generate` passed neither coefficient | Representative jobs did not use the selected settings | `selection.selected_settings` reads hash-bound selection; notebook bundles it; CLI rejects silent overrides; regression tests inspect actual CLI dispatch | Fixed locally, target runtime pending |
| High | `accelerator.initialize_clients/train_client` owns CUDA dropout separately; `checks.run` CUDA branch checks forward/importance, not paired training | Same seeds are not proof of CPU/GPU trajectory equivalence | Target-runtime primitive, state, admission and development comparison under prospective contract | Open; GPU unavailable |
| High | `experiment-manifest.json` scope_selected remains unset; `protocol.Settings` supports FT/EI/DR and NONE/DM/DC/DQ only | Complete/course menus are not executable adopted studies | Condition-by-condition [scope reconciliation](../phase3-plan/continuation-scope.json); final dispatch remains disabled | Open scope decision |
| High | FIFO/class-balanced/oracle adapters absent; NoY/NoZ are generic zero coefficients without adopted role-specific RNG convention | Component claims would exceed qualified methods | Implement and qualify only after prospective scope/semantics disposition; do not represent zero coefficients as a qualified ablation package | Open |
| High | Baseline handoff inspector does not provide a cross-worker analysis registry; endpoint reconstruction omitted validation of reported R matrix | Malformed/duplicate analysis inputs could be miscounted by a downstream consumer | New fail-closed count import checks expected bindings, hashes, full matrix and duplicate condition identity; synthetic rejection fixtures | Local boundary fixed; persistent final catalog pending |
| Medium | Runtime package inventory lacked an explicit sklearn requirement decision; no preflight free-space/session record | Notebook setup could be mistaken for execution readiness | `preflight.inspect` records resources, sklearn not-required, declared session bound and false durability/provider-verification flags | Implemented/tested locally |
| Medium | Planning research-status still said implementation pending | Roadmap contradicted completed CPU evidence | Archive baseline and add continuation status/15 gates; historical entries retain their scope | Corrected |
| External | Main CI runs40169262324/40169262326 completed with failure before steps began | No hosted CI qualification | Re-query job annotations; repair account billing through owner, then rerun exact workflows | Blocked externally |

### CPU boundary assessment

`src/phase3_v2/learning.py` supplies model/client training, admission, aggregation,
importance and zero-current behavior to v3. `tests/test_phase3_v2.py` covers empty
current clients with populated replay, small/new classes, ties, nested poisoning,
importance, registered rare prediction outputs and count behavior. V3 source,
protocol and checkpoint execution identities distinguish v2 from v3 despite
sharing wire schemas. Historical full-data recovery checks establish state and
prediction parity within the pinned CPU runtime. No new frozen numerical defect
was demonstrated in this audit. This does not qualify unimplemented interventions.

Kaggle initialization and aggregation remain CPU-owned; its transaction loop is
separate and tested. Candidate v4 keeps the old source/evidence untouched in Git
and old bundles. Source identity changes prevent incompatible receipt reuse.
The new importer also validated all 72 physical development trajectories and excluded nine aliases, using the CPU metrics' separately hashed run manifests. This checks existing counts without inference. Local duplicate-writer rejection, existing fresh-process recovery and malformed
artifact tests are evidence of local behavior only. Session timeout bounds are
estimates; no code can guarantee a provider will not terminate mid-transition.

## Scientific scope and analysis

The [scope reconciliation](../phase3-plan/continuation-scope.json) derives every
final dataset/arm/dose group from the authoritative planning manifest and retains
all twelve seeds [1–11,42], package membership and oracle parents. It does not
adopt course/core/complete. Core contains 240 final full trajectories; original
complete contains 552, plus conditional oracle suffix accounting. An alias or
retry is never another replicate. Eight contributors change scheduling, not n.

Recommend explicitly resolving the original complete scope versus the minimum
core confirmatory scope before implementing additional intervention adapters.
Core alone does not satisfy the ablation rubric. The current seed101 private
qualification bundle is not a final-matrix data package or a multi-seed runner.

The existing single named Holm family **all_29** already covers 18 C1 and 11 C2
contrasts. Preserve it; no posthoc split into smaller families. The fixed exact
signed-rank, zero/tie rules, rank-biserial effect, paired bootstrap, and missingness
implementation remain unchanged. Added sample SD uses ddof=1 and refuses silently
reduced seed sets. Full final import/analysis must wait for a prospective registry
and scope freeze. Synthetic final-seed labels in unit tests are fabricated counts,
not final data access.

H measures untriggered Hulk-to-benign error change; A uses fixed eligible new
non-Hulk classes. Binary FAR uses the fixed benign union, including cross-period
benign records. Rare registered prediction columns remain active. Valid negative,
weak or adverse outcomes remain in the study. No training instability or missing
pair may become a favorable seed substitution. These are fixed-benchmark claims,
not independent-site generalization or deployment false-alert forecasts.

## Fifteen authorization gates

| # | Gate | Status and evidence required |
|---:|---|---|
| 1 | CPU source/evidence | PASS within delivered scope: fresh delivery audit |
| 2 | Data/taxonomy | PASS reference/development adoption; final package freeze pending |
| 3 | Learner correctness | PASS FT/EI/DR CPU scope; proposed interventions excluded |
| 4 | Admission/poison | PASS implemented CPU fixtures/controls; full final combinations unexecuted |
| 5 | Checkpoint/recovery | PASS pinned local CPU; provider durability belongs to gate12 |
| 6 | Kaggle CPU/GPU equivalence | BLOCKED actual CUDA and dropout/admission disposition |
| 7 | Clean feasibility | PASS CPU mean gates; target-runtime development confirmation pending |
| 8 | Operational metrics | PASS CPU count audit and synthetic importer; final catalog pending |
| 9 | Selected tuning | PASS immutable CPU selection; v4 CLI now consumes it |
| 10 | Final scope/manifest freeze | BLOCKED explicit scope and missing adapter decisions |
| 11 | Statistics/family freeze | Existing all_29 implemented; final-scope binding pending |
| 12 | Kaggle runtime/storage/recovery | BLOCKED actual pinned install, cost and fresh-session handoff |
| 13 | Human final authorization | NOT GRANTED; this mission explicitly excludes final execution |
| 14 | Complete final artifacts | NOT STARTED; requires gates1–13 |
| 15 | Analysis/publication readiness | NOT READY; requires validated final artifacts and interpretation review |

## Verification and immediate next action

See [verification ledger](../../results/phase3-continuation-v1/verification.json)
for commands, local outcomes and preserved failures. Local suites are not hosted
CI. Both main workflows were queried at the baseline SHA; GitHub reported that
the job did not start because the account is locked due to a billing issue.
[Pinned CPU workflow run](https://github.com/ahmedbilalazhar/cl-ids-adversarial/actions/runs/40169262326).
The pinned CPU workflow now includes the continuation importer/preflight regression tests. No CI gate is weakened and no account workaround is attempted.

The highest-priority next action is an **actual Kaggle v4 development
qualification**, starting with synthetic CPU/CUDA fixtures in the generated
notebook, then the selected clean representative jobs and saved-output recovery.
Use the [execution contract](../phase3-plan/kaggle-execution-contract.md).
Collect the runtime fingerprint, primitive/state comparison, admission identities,
component costs and download/restart receipts. A failed or unavailable comparison
leaves gate6/12 blocked; even a pass does not authorize final execution.
