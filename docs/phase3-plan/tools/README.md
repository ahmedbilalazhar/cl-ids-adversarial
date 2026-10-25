# Conditional data-audit tools

These scripts produced the data-feasibility evidence in the planning package. They do not implement the Phase 3 learner, train a model, evaluate predictive performance or approve a final data profile. Run from the project root. Preserve the directory layout when extracting the ZIP.

## Environment and storage

The recorded audit environment is CPython 3.12.14, NumPy 2.3.5, pandas 3.0.1, SciPy 1.18.1 and scikit-learn 1.9.1, with the complete package inventory in `../audit-environment.json`. `audit-requirements.txt` pins the audit dependencies; it is not a torch/Kaggle environment lock. In the current workspace the isolated interpreter is `tmp/phase3-research/audit-env/Scripts/python.exe`.

Create a local environment with the recorded Python version and install the requirements if reproducing elsewhere. The scripts use project-root-relative paths, portable NumPy/SciPy/pandas operations and public HTTPS sources. CSVs and derived arrays are stored under Git-ignored `data/raw/phase3-feasibility-original/` and `data/raw/phase3-feasibility-corrected/`. Expect several GB of working arrays and temporary memory, not just the approximately 628 MB combined archives. Back up evidence before rerunning: several tools intentionally replace their candidate report/working outputs.

The packaged `../candidate-feature-schema.json` contains the exact ordered 76-feature list and original file digest. Source aliases are in `census_corrected_feasibility.py`; names alone do not establish extractor-semantic equivalence. The scripts were changed after the census to read the identical packaged list rather than depend on a legacy processed file. No feature/order change was introduced by that packaging edit. Final learner acceptance is still required.

## Reproduction sequence

In the commands below, `python` means the isolated recorded audit interpreter, not an arbitrary system environment. These are existing utility entry points, not future learner commands.

### 1. Acquire and census

```text
python docs/phase3-plan/tools/acquire_original_feasibility.py
python docs/phase3-plan/tools/census_original_feasibility.py
python docs/phase3-plan/tools/audit_original_csv_records.py
python docs/phase3-plan/tools/acquire_corrected_feasibility.py
python docs/phase3-plan/tools/census_corrected_feasibility.py
python docs/phase3-plan/tools/prepare_corrected_component_audit.py
```

Acquisition verifies ZIP structure, complete member reads/CRCs and SHA-256 identities. The original mirror digest is not a provider signature. The corrected acquisition's complete archived digest is recorded in `../corrected-acquisition-full.json`; compare that evidence on reproduction. A successful HTTP status can contain HTML, which is why `probe_original_release.py` records route/content evidence separately. No form submission is automated.

### 2. Conditional graph, calibration and domain evidence

```text
python docs/phase3-plan/tools/audit_original_components.py
python docs/phase3-plan/tools/audit_corrected_components.py
python docs/phase3-plan/tools/audit_feature_domains.py
python docs/phase3-plan/tools/audit_fp32_collisions.py
python docs/phase3-plan/tools/audit_domain_checked_components.py --release original
python docs/phase3-plan/tools/audit_domain_checked_components.py --release corrected
```

The first two retain as-published finite values. The last two create separate `domain-checked/` arrays and reports using the named prospective rule. Do not mix their parent arrays or reports. Each graph audit records 60/120/300-second sensitivity counts; the 120-second state is retained for the proposed split. All features and metadata stay on the same source row.

The original clock is explicitly interpreted from day-first strings with hours below 8 treated as afternoon. This is a conditional capture-specific assumption. The corrected source uses its supplied ISO UTC microsecond times. The domain rule preserves -1 window sentinels and does not clip/repair features. Full metadata/feature semantics are not thereby certified.

### 3. Split and ownership feasibility

```text
python docs/phase3-plan/tools/audit_candidate_split.py --release original
python docs/phase3-plan/tools/audit_candidate_split.py --release corrected
python docs/phase3-plan/tools/audit_candidate_split.py --release corrected --domain-checked
python docs/phase3-plan/tools/audit_candidate_ownership.py --release original --benign-policy mandatory-all-rows
python docs/phase3-plan/tools/audit_candidate_ownership.py --release original --benign-policy benign-subset-by-component
python docs/phase3-plan/tools/audit_candidate_ownership.py --release corrected --domain-checked --benign-policy benign-subset-by-component
```

The fixed group allocator can take tens of minutes on the inspected laptop; these are preprocessing timings, not GPU/model estimates. It requires a scikit-learn version containing the 1.8 SGKF shuffle fix. Component IDs are minimum immutable provenance IDs across the entire component, including excluded members. A union-find internal root is not a stable scientific ID.

Ownership reports use all twelve final seed values solely to audit prescribed synthetic partitions/dose arithmetic before model outcomes. They do not select favorable seeds. Source dose is a fraction of the attacked client's Hulk examples, not all local/global traffic. Poison admitted by DC is only bounded here: actual loss-ranked selection requires the learner/scorer. DQ expectations are arithmetic, not observations.

An original domain-screened split/ownership can be run with `--release original --domain-checked` after its graph audit. It was not necessary to execute every optional candidate to diagnose the source choice; distinguish available commands from actually produced reports.

### 4. Independent graph and statistical arithmetic

```text
python docs/phase3-plan/tools/audit_exclusion_accounting.py
python docs/phase3-plan/tools/audit_graph_independently.py
python docs/phase3-plan/tools/assess_statistical_resolution.py
```

The first two currently target the original as-published candidate. Independent connectivity reconstruction uses full SHA-256 groups and a sparse graph algorithm; it shares parsing/clock assumptions and is not independent human reproduction. The statistical script calculates exact hypothetical signed-rank resolution, not empirical power or learner results.

## Evidence versioning and remaining limits

The retained `*-v1.json` reports are explicitly superseded. One early calibration rule used cross-day raw-conflict eligibility; fitting IDs changed in v2 even though observed scaler statistics did not. One early split used internal union-find roots; v2 uses canonical provenance IDs. Neither change was chosen using model outcomes. Reports retain parent identities and audit versions; never combine a v1 split with v2 ownership.

The new data tools and documentation have not been turned into a canonical production builder. They do not export the final sealed evaluator package, establish rights to redistribute raw data, replace learner acceptance, or measure Kaggle runtime. The delivery includes evidence and scripts, not raw archives, trained weights or completed experimental results.

## Additional completed audit utilities

`audit_profile_accounting.py --release original` and `--release corrected` produce additive ledgers for the separate domain-screened candidates. `audit_capture_context.py` reports screened-corrected endpoint/host concentration and overlap; it does not fit a model or prove causal shortcuts. `build_audit_figures.py` uses pinned Matplotlib to plot observed source/support/workload/dose counts as PNG/SVG, never model performance. These additions do not alter the source arrays.

## Final source-consistency candidate

`audit_header_consistency.py` reproduces the label-independent header relation census. `audit_no_headers_candidate.py` creates a separate 74-feature projection and graph audit; it now derives dimensions from the declared schema. `audit_no_headers_split_reuse.py` proves exact selected-label/component/calibration identity before copying the existing fixed split. Alternatively rerun the allocator with `audit_candidate_split.py --release corrected --profile no-headers-74`. Run ownership with `audit_candidate_ownership.py --release corrected --profile no-headers-74 --benign-policy benign-subset-by-component`, then `audit_annotation_provenance.py` for background/attempted counts. The split alias does not authorize reuse of any model state or hyperparameters across input widths. Earlier figure PNG/SVG files deliberately retain their 76-feature/original-candidate labels.
