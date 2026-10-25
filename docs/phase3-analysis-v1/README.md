# Paired analysis software qualification

This sibling package implements the Phase2 appendix and fixed29-contrast
contract against synthetic fixtures. It has no model, prediction-bank or
final-test reader. A statistical release remains gated on complete validated
final inputs and scientific/runtime/cost freeze. Synthetic qualification is not
a research result.

The [dated decisions](decisions-2026-10-24.md) pin exact rational ordering,
bootstrap stream namespace12/seed20261024/contrast index, NumPy2.3.5,10000
whole-seed resamples and linear quantiles. Original hypotheses,12 final seeds
and one Holm family of29 are preserved.

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $py -m scripts.accept_phase3_analysis --output results/phase3-analysis-v1-reproduce
ruff check src/phase3_analysis tests/test_phase3_analysis.py scripts/accept_phase3_analysis.py
```

Use a fresh output directory. Machine-readable `acceptance.json` binds the source,
tests, count/contrast specification and decisions. `synthetic-family-example.json`
is explicitly labeled synthetic and includes a deliberately unavailable row.
Its `artifact-index.json` hashes the generated evidence, excluding itself.

Pure APIs derive signed Hulk H and immediate recall change from complete integer
partitions, acquisition from fixed per-stage/per-family TP/FP/FN groups, and
benign FAR from its positive fixed denominator. `contrast_differences` performs
the declared left-minus-right comparison; H/recall change are not clean-subtracted
again. `analyze_family` requires all29 IDs and all12 seed positions. Exact zeros
are dropped only for signed ranking and sign-test sensitivity, not for means,
medians or bootstrap sampling.

Unavailable endpoints retain null raw/adjusted inferential p, null effects and
intervals, and the missing-seed list. Their separately named p1 bookkeeping
preserves the29-test Holm family without pretending that a no-effect test ran.
Results preserve exact rational numerator/denominator strings alongside floats.
Rank assumptions and descriptive interval limitations are emitted in the output.

Initial nine-fixture acceptance is preserved as attempt1; final qualification
adds explicit FAR-count rejection and a nonconstant bootstrap fixture verifying
that zero paired differences remain in all twelve-pair resamples. Neither
implementation attempt used a real final endpoint.
