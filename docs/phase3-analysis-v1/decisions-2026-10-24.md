# Analysis implementation decisions — 24 October 2026, 16:07 UTC

Implement the existing Phase2 appendix and the fixed 29-row contrast contract
against transparent synthetic fixtures. The completed v2 grid/E1 probes and the
first v3 pilot are visible. No final predictions or final seed outcomes exist.
This is software qualification, not a final statistical release or an amendment
of endpoints, final seeds, multiplicity or hypotheses.

Use integer counts and exact rational endpoints/differences for zero detection,
absolute-rank ordering, tied average ranks, exact sign enumeration, rank-biserial
effects, means/medians and Holm bookkeeping. Include observed-or-more-extreme
sign assignments for the two-sided statistic. All-zero differences give p1 and
effect0. Retain exact numerator/denominator strings alongside displayed floats.

Use one Holm family of29 at alpha1/20. An unavailable required endpoint keeps
its planned row, missing-seed list, raw p=null and effect/interval=null. Assign1
only as internal fixed-family bookkeeping, clearly named separately; do not
report it as a computed no-effect result or average the available subset.

Bootstrap the mean paired difference with10000 twelve-pair whole-seed resamples.
Include zero differences. Pin NumPy2.3.5, FP64 conversion/reduction and quantile
method='linear', probabilities0.025/0.975. Use existing version1 PCG64 seed-key
construction with new namespace12, master seed20261024 and the contrast's
zero-based frozen index. Record initial/final stream state and draw-array hash.
This namespace is independent of every training stream and changes no model.
Intervals are descriptive, not simultaneous or signed-rank test inversions.

H and source recall change are clean-subtracted once inside each pipeline before
the learner/control contrast. A and E4 benign FAR use their specified raw
contrasts. Preserve negative changes. Synthetic fixtures must distinguish those
cases and independently verify arithmetic and exact small-sign probabilities.

Keep this implementation in a sibling package outside the frozen v1/v2/v3
learner identity. It cannot open a model, prediction bank, final-test feature
file or run a learner. Its qualification CLI emits only explicitly labeled
synthetic evidence. Real analysis ingestion/release still requires validated
complete final inputs and all existing runtime/cost/scientific release gates.
