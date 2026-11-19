# Phase 3 submission evidence map

This map points reviewers to the evidence in the roll-number submission ZIP and separates completed experiments from gated work. The primary report and follow-up addendum must be read together.

| Phase 3 requirement | Evidence in submission | Status and scope |
|---|---|---|
| Implement proposed method | `01_FINAL_REPORT/phase3-report.pdf`, Sections 1 and 3-4; source under `03_REPRODUCIBLE_PROJECT/src/` and `scripts/` | Implemented and evaluated on the adopted corrected CICIDS2017 development protocol. |
| Incorporate prior feedback and document methodology changes | Main report, Section 1.1, “Phase 2 to Phase 3 changes” | Documents scope reduction, attack-grid expansion, replication structure, and metric interpretation. |
| Dataset, preprocessing, split, reproducibility | Main report, Sections 2 and 10; frozen configs, manifests and scripts under `03_REPRODUCIBLE_PROJECT/` | Corrected CICIDS2017 source and component-based roles are documented. Follow-up discovery uses development-only component partitions. |
| Baselines and essential metrics | Main report, Sections 4-5 | Clean FT/EI/DR baselines and precision/recall/F1, FAR, and targeted-persistence metrics are reported for their stated populations. |
| Graphical results | Main report, Sections 5-9; addendum figures; SVGs under `03_REPRODUCIBLE_PROJECT/docs/phase3-plan/figures/` | Figures cover the completed experiments; do not interpret exploratory discovery as confirmatory evidence. |
| Comparison with existing research | Main report, Section 8 and References | Literature comparison and cited sources are in the primary report. External discovery results are not presented as full-method literature replication. |
| Ablations | Main report, Section 6; addendum assignment-rule and threshold/cap analyses | Primary component ablations and exploratory discovery ablations are reported separately. |
| Analysis, limitations and research-gap response | Main report, Sections 9-10; addendum final page | Claims are restricted to the corrected CICIDS2017 split. External submodule metrics are adverse/exploratory; no independent-site defense claim is made. |
| External independent data | Addendum; `docs/phase3-plan/external-dataset-readiness.md`; `docs/phase3-plan/external-method-training-pilot-results.md`; per-arm artifacts under `results/phase3-followup/external-method-training-pilot-v1/` | Three-seed discovery-submodule refits plus a one-seed, 16-arm full-method train-only adapter pilot exist. The latter verifies execution only; no test metrics or effectiveness claims. Faithful replication remains blocked by ownership, grouping, taxonomy, schema and units limitations. |
| Cross-dataset transfer | Compatibility audit and external readiness note | Not established. Feature schemas have zero shared names, units are undocumented, and no defensible semantic bridge is frozen. |
| Sealed final-test readiness | Addendum; `docs/phase3-plan/final-test-readiness.md`; `results/phase3-followup/followup-preflight-v1.json`; synthetic-only evaluator tests | Final-test evaluation is not ready: zero rows are exported, the reference settings remain untuned, the development evaluator is role-pinned, and the separate final evaluator has only synthetic contract coverage. Protocol and freeze gates remain open. Test data are excluded from the ZIP. |

## Reproduction entry points

- `03_REPRODUCIBLE_PROJECT/scripts/phase3_followup_preflight.py` records current readiness without loading feature/label arrays.
- `03_REPRODUCIBLE_PROJECT/scripts/audit_phase3_external_compatibility.py` writes the machine-readable external interface audit without accessing final-test data.
- `03_REPRODUCIBLE_PROJECT/scripts/run_phase3_external_method_trainpilot.py` runs the external training-only adapter; `summarize_phase3_external_method_pilot.py` verifies the saved arm and checkpoint inventory.
- Discovery and external runner/config pairs are listed in the follow-up results notes.

The current evidence does not satisfy the gated full-method external replication or final-test evaluation. Completing either requires resolving its documented protocol and data prerequisites before executing that study.
