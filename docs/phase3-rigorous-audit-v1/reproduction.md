# Reproduction and interpretation

Run commands from the repository root. Preserve the working tree; do not reset it. The original submission archive SHA-256 is `c219925799b2fe3b1d73e4203e25d1f94987b6c401f0288290f5f0bb67a2311f`.

## Independent evidence audit

```powershell
python scripts/audit_phase3_reliability.py --output results/phase3-rigorous-audit-v1
python scripts/write_phase3_audit_register.py
```

The auditor imports no training runner. It reads original artifacts and writes only its separate audit directory. Data-cache requirements are explicit in `input-verification.json` and `data-audit.json`; full raw graph/source caches are not bundled because of their size. A missing cache is missing evidence, never permission to synthesize a substitute.

The recorded frozen runner is packaged under `results/phase3-rigorous-audit-v1/executed-source/scripts/`. If reproducing in a new checkout, use that snapshot as the source recovery candidate rather than relying on the original `tmp/phase3-portable-check` location. The snapshot SHA-256 must equal the runner hash in the original study identity. The packaged release supplies a fallback for this recovery path.

## Pinned scientific checks and execution verification

Use Python3.12.14, NumPy2.3.5, PyTorch2.7.0+cpu for scientific replay. The existing environment is `tmp/phase3-reference-env/Scripts/python.exe`. Pytest9.1.1 was added for checks; learning-library versions were not changed.

```powershell
& './tmp/phase3-reference-env/Scripts/python.exe' -m pytest tests/test_phase3_v2.py tests/test_phase3_v3.py tests/test_phase3_analysis.py tests/test_phase3_overnight.py tests/test_phase3_reliability_audit.py
& './tmp/phase3-reference-env/Scripts/python.exe' scripts/verify_phase3_archived_execution.py --output results/phase3-audit-replay-new
& './tmp/phase3-reference-env/Scripts/python.exe' scripts/verify_phase3_cohort_metrics.py
python scripts/verify_phase3_component_graph.py
```

The replay checks executed source and all input hashes, uses an exclusive lock, writes a new output directory and limits execution to six hours. It observes existing calls without changing inputs/outputs/RNG. It verifies three archived conditions; they are reproduction checks, not added independent trajectories. Do not reuse a completed output to obtain new timing observations: a cached result does not measure fresh calls.

The cohort verifier reads only the `development_only` package and all clean primary checkpoints; it recreates fixed-cohort metrics and compares prediction confusion matrices exactly. It does not evaluate sealed final-test rows.

## Report and package

### Verify a delivered full-evidence ZIP without project dependencies

The archive carries its own `UPLOAD_INVENTORY.json`. From any directory with Python 3.10+ and the standard library, run:

```powershell
python scripts/verify_phase3_evidence_archive.py submissions/phase3-completed/23I-2568_23I-2581-full-evidence-v28.zip
```

This read-only check streams every member, verifying the exact ZIP member set, CRC and SHA-256 values, the frozen original submission hash, the report digest, and the declared/actual absence of final-test payloads. It does not load CICIDS data or execute model code. The v28 standalone acceptance run checked all inventoried files, preserved the frozen original and report digest, and confirmed no final-test payload. Compare the printed archive SHA-256 with submissions/phase3-completed/full-evidence-v28-validation.json and results/phase3-rigorous-audit-v1/evidence-archive-verification-v28.json.

```powershell
python scripts/summarize_phase3_adopted_costs.py
python scripts/build_phase3_audited_report.py
python scripts/verify_phase3_report_clean_rebuild.py
python scripts/package_phase3_audit.py
python scripts/refresh_rollno_audited_report_v28.py
python scripts/package_phase3_full_evidence_v28.py
```

The clean report verifier uses the preserved v26 full-evidence ZIP (keep it alongside the workspace) as a fresh selective extraction, checks result hashes against its completion manifest, rebuilds the report, and compares report sources plus every page's text and rendered pixels. Its passing record is `results/phase3-rigorous-audit-v1/report-clean-rebuild-v26.json`; this is report reproducibility, not a full scientific re-execution. The cost summarizer checks every completion-manifest result hash, collapses exact duplicate result copies, and emits the adopted-profile CSV, JSON summary, and wall-time figure without training. The report builder reruns that summary before rendering. Report dependencies: Python/NumPy/Matplotlib/PyMuPDF and Tectonic. Generated TeX is native and figures are vector PDF. Inspect rendered page PNGs under `submissions/phase3-audited-report/preview/`. The report builder uses the original submitted TeX foundation, not the most recently named PDF. A fresh build requires the foundation retained under the audit directory.

After extracting the packaged ZIP, first run `python scripts/materialize_phase3_audit_evidence.py` to restore canonical result paths from its deduplicated evidence directory. This restores417 canonical trajectories without recreating546 redundant copies. Historical physical-copy counts remain recorded in the original audit catalog.

The packager preserves the pre-audit roll-number ZIP in the audit directory, includes the untouched original submission under historical evidence, deduplicates newer research results by immutable experiment identity, writes an inventory of every payload and validates the temporary ZIP before atomic installation. No uploads are performed.

## Failures and limitations

The initial general-Python invocation used3.14/NumPy2.4/PyTorch2.14 and failed locked-runtime tests. Those failures are not scientific results. The pinned combined suite then exposed the real runner-import contamination; its before/after logs are retained. The first frozen-source replay attempt failed because relocation changed a relative data root, before research training; attempt2 explicitly binds the verified workspace data root. Both failure records remain.

Not shipped: raw multi-gigabyte caches, sealed test payloads, independently qualified external evaluator, and unsupported deployment assurances. Reconstruct raw data only from authenticated releases and compare exact input identities before scientific reuse. A matching output count or an existing test does not substitute for these checks.
