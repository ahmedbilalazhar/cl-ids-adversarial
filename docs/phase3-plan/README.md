# Phase 3 implementation and evaluation planning

Status: second audit complete; implementation remains pending. Started 23 October 2026 (Asia/Karachi client date).

**Begin with [START-HERE.md](START-HERE.md).** It gives the recommended 441-row research starter and conditional 513-row external extension. The printable plan is generated under `output/pdf/phase3-research-implementation-plan.pdf`; the detailed contracts below remain the implementation reference.

**New evidence and corrections:** [second-audit-gap-register.md](second-audit-gap-register.md), [data-release-decision.md](data-release-decision.md), [protocol-closure-spec.md](protocol-closure-spec.md), [evaluation-strengthening.md](evaluation-strengthening.md), [component-and-control-spec.md](component-and-control-spec.md) and [resource-and-message-contract.md](resource-and-message-contract.md). Full candidate source censuses and conditional component/split audits are data-preparation evidence, not model-performance results. The earlier PDF/delivery hashes are historical until the new audit release is rebuilt and reviewed.

Begin with [audit-executive-summary.md](audit-executive-summary.md) for the three-hour second audit, then [rubric-and-readiness.md](rubric-and-readiness.md) for completion evidence.

This planning package concerns the revised `submissions/phase2-with-claude.tex` protocol and the seven Phase 3 course requirements supplied in this chat. It does not report executed Phase 3 experiments.

## Working assumptions

- Two implementation authors.
- Eight distinct people may contribute compute using their own individually operated Kaggle accounts. The two-account fallback remains necessary because available quotas and access are not guaranteed.
- Deadline and instructor feedback have not yet been supplied.
- Preserve the revised research question, the 12 paired final seeds and the original analysis unless a prospective, documented amendment is justified before final testing.
- Existing legacy configurations and archived results are not automatically compatible with the revised protocol.

## Current working deliverables

| Read | Purpose |
|---|---|
| [plan.md](plan.md) | Main implementation, seven-item rubric, team and milestone plan |
| [implementation-work-breakdown.md](implementation-work-breakdown.md) | Two-author task ownership, dependencies and contributor handoff |
| [data-and-interface-contract.md](data-and-interface-contract.md) | Canonical data, components, splits and state-machine interfaces |
| [proposed-defaults.json](proposed-defaults.json) | Explicit proposed seeds/numerical conventions; not dispatchable |
| [implementation-gap-audit.md](implementation-gap-audit.md) | 31 source-grounded changes needed before the revised experiment |
| [efficiency-and-recovery.md](efficiency-and-recovery.md) | CPU/GPU profiling, RNG, quota, checkpoint and recovery decisions |
| [prefix-reuse.md](prefix-reuse.md) | Exact conditions for safe reuse and conditional execution savings |
| [methodological-risk-review.md](methodological-risk-review.md) | Poison-retention floor, exposure, mechanism forks and statistical risks |
| [metrics-and-analysis-contract.md](metrics-and-analysis-contract.md) | Exact banks, endpoint/continual metrics, signed rank and missingness |
| [numerical-and-state-decisions.md](numerical-and-state-decisions.md) | Initialization, rational quotas, RNG, loss arithmetic and tuning decisions |
| [methodology-diagram-review.md](methodology-diagram-review.md) | Visual audit and editable Phase 3 diagrams |
| [figures-and-reporting-spec.md](figures-and-reporting-spec.md) | Scientific figures, uncertainty, captions and report tables |
| [compute-budget-and-scheduling.md](compute-budget-and-scheduling.md) | Per-person capacity, balanced scenarios and scheduling constraints |
| [failure-and-amendment-policy.md](failure-and-amendment-policy.md) | Instability, interruption, invalidation and unavailable-result handling |
| [amendment-register.md](amendment-register.md) | Prospective methodology decisions; no invented instructor feedback |
| [novelty-and-publication.md](novelty-and-publication.md) | Closest prior art, defensible contribution and claim-to-evidence contract |
| [literature-comparison-template.md](literature-comparison-template.md) | Direct and contextual comparison structures for the report |
| [experiment-manifest.json](experiment-manifest.json) | 729 planning-only logical full trajectories, package membership and assignments |
| [analysis-contrasts.json](analysis-contrasts.json) | Explicit list of the 29 confirmatory contrasts |
| [optional-controls.json](optional-controls.json) | Conditional controls excluded from base package counts |
| [data-acquisition-evidence.json](data-acquisition-evidence.json) | Bounded corrected-archive header evidence; not a support audit |
| [sources.json](sources.json) | Primary-source evidence ledger and verification limits |
| [iteration-log.md](iteration-log.md) | Material changes made through repeated critique |
| [planning-validation.json](planning-validation.json) | Document/manifest consistency audit; not model test results |

No experiments, Kaggle uploads or account changes have been performed for this planning task. Future commands are labelled as existing verified interfaces or proposed interfaces that still need implementation. The manifest is not dispatchable until data, selected settings and code/runtime identities are locked.

## Planning utilities that actually exist

`validate_planning_package.py` checks document/manifest consistency using the standard library. `build_plan_pdf.py` renders the printable plan with ReportLab and the inspected Windows fonts. `tools/inspect_corrected_archive.py` performs the bounded public archive/header probe; it does not download/audit the complete dataset or train a model. The Phase 3 learner/worker interfaces described in the plan are still future implementation work.

## Full-source data-audit utilities

See [tools/README.md](tools/README.md) for the actual commands, environment, candidate profiles, evidence files and limitations. Full archives/derived arrays are local Git-ignored working data, not included in the delivery ZIP. The older bounded-header probe remains a historical snapshot; it is superseded for acquisition by the full-source reports.

## Second audit additions

Read [realized-dose-and-quota-limits.md](realized-dose-and-quota-limits.md), [capture-context-and-generalization.md](capture-context-and-generalization.md), [feature-domain-and-precision-review.md](feature-domain-and-precision-review.md), [protocol-closure-spec.md](protocol-closure-spec.md), [evaluation-strengthening.md](evaluation-strengthening.md), [component-and-control-spec.md](component-and-control-spec.md) and [resource-and-message-contract.md](resource-and-message-contract.md). The full data evidence remains conditional; the study has not passed learner/final-result gates.

## Rebuild the review artifacts

From the project root, use the recorded document runtime to run `python docs/phase3-plan/build_plan_pdf.py` and `python docs/phase3-plan/build_audit_pdf.py`. Render and visually review changed PDFs before recording delivery. Then run `python docs/phase3-plan/validate_planning_package.py` and `python docs/phase3-plan/package_plan.py`. The packager includes both PDFs, planning sources and PNG/SVG audit figures, verifies archived member digests, and excludes raw datasets/working arrays. Document checks are not learner tests.

**Final source review:** [feature-semantics-and-final-recommendation.md](feature-semantics-and-final-recommendation.md) describes A31/A32, the preferred prospective 74-feature candidate, exact split reuse, annotation provenance and remaining taxonomy gate. Earlier 76-feature evidence remains separately identified.
