# Phase 2 research figures

These figures describe the **proposed** methodology. They do not claim completed experiments or deployment.

| Figure | SVG | Vector PDF | Preview | Editable TikZ |
|---|---|---|---|---|
| Methodology overview | `methodology-overview.svg` | `methodology-overview.pdf` | `methodology-overview.png` | `methodology-overview-inline.tex` |
| Proposed framework architecture | `proposed-framework-architecture.svg` | `proposed-framework-architecture.pdf` | `proposed-framework-architecture.png` | `proposed-framework-architecture-inline.tex` |

`build_figures.py` is the shared editable vector source. It produces SVG, native vector PDF, PNG and equivalent inline TikZ from the same coordinate model. It requires Python with ReportLab and PyMuPDF; the bundled Codex runtime supplies both. No model training is performed.

Run from the project root:

```powershell
& 'C:\Users\hp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 'research_figures\build_figures.py'
```

Generation normally touches this directory only. Add `--embed` to replace Deliverable 4 in the existing `submissions/phase2.tex` with these two inline vectors. That option edits the document, never research code. Inline TikZ needs `graphicx` and `tikz`, which the current document already loads.

Use both figures at about seven inches (178 mm) spanning the two columns of a research paper, or at the A4 report's full text width. The 12-point source body text becomes 8.4 points at seven inches; 15-point phase headings become 10.5 points. Do not shrink these versions into a single 3.5-inch column. The framework's 13-point component labels become 9.1 points at the intended width. Colors are supplemented by labeled boundaries and line styles.

SVG contains native shapes and text; PDFs contain no embedded raster images. PNG previews are raster exports for inspection and Word compatibility. The standalone vector PDFs are figure exports, not a separately compiled report PDF. LaTeX uses self-contained inline geometry so its standalone editor does not need external image files.

The reference image informed the server/client/schedule layering. Compression, error feedback, quantization and class-head protection from that reference were not added to this study. Scientific meanings and changes are documented in `CHANGELOG.md`.
