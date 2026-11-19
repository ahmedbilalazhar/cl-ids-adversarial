# Audited report build

From the repository root, run `python scripts/build_phase3_audited_report.py`. The builder regenerates the adopted-profile cost summary and the hash-checked DM/DC admission/memory mechanism analysis, then rebuilds the TeX/vector figures with Tectonic, writes `output/pdf/phase3-audited-report.pdf`, and refreshes the page previews and validation metadata.

The validated local toolchain was Python 3.14 with NumPy 2.4.3, Matplotlib 3.10.8, and PyMuPDF 1.28.2, plus Tectonic 0.17.0. Tectonic emitted a Fontconfig environment warning on this Windows setup but completed successfully; the revised PDF contains nine pages and has no undefined references or overfull boxes. All nine pages were visually inspected, including a full-resolution review of the new mechanism figure; see `pdf-validation.json` and `source-ledger.json` for visual and primary-source checks.

The mechanism outputs are stored at `results/phase3-rigorous-audit-v1/admission-mechanism-v1/`. They verify the completion-manifest hashes of 96 DM/DC primary result files and report class-wise F1 and known-poison memory occupancy. The analysis explicitly does not treat occupancy as replay exposure or identify causal responsibility for the FAR change.
