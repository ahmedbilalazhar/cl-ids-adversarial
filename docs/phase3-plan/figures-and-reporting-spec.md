# Figures and reporting specification

Produce these from validated count/prediction tables after the selected matrix is complete. No experimental charts have been fabricated for this plan.

## Core figures

| Figure | Data and display | Interpretation safeguard |
|---|---|---|
| Study timeline/architecture | E1–E4, E2 fresh corruption, retained state, protocol lock and read-only evaluator | Client participation continues after E2; eight workers are not eight FL clients |
| Absolute source-error trajectories | FT/EI/DR clean and maximum dose at E2–E4; paired seed points and stage summaries | Keep y-axis 0–1; show absolute error before interpreting H |
| Susceptibility contrasts | Fixed learner-pair H and immediate-recall differences by dose, with raw paired points | H is already clean-subtracted; label recall-damage direction explicitly |
| Admission comparison | DM/DC and selected DQ; acquisition, source error/H and benign FAR in separate aligned panels | No single invented utility score; higher F1 is not automatically safer |
| Poison admission/capacity | E2 honest benign b, poison q, quota K, theoretical retention floor and actual retention | Show denominator and local versus global scope; zero-dose poison ratios are NA |
| Retained-state diagnostics | Source/poison occupancy by stage/client and audited replay-exposure summaries | Distinguish no surviving poison from no replay because the site is inactive |
| Component ablations | Clean/poisoned paired differences from the matching DC reference | From-start and post-E2 fork effects have different labels and estimands |
| Full-inventory confusion | True-row normalized percentages plus raw support and family names | Rare/descriptive labels visible; full active output space retained |
| Costs | End-to-end and component times, process/device peaks and actual message bytes | Within compatible hardware blocks; raw payload is not WAN latency or energy |

Keep the main paper focused on the figures needed by the actual finding. Put detailed dose/family/resource tables in an appendix rather than shrinking labels to fit everything into one figure.

## Units and uncertainty

- Display fractions consistently as 0–1 or percentages. A signed change of 0.05 is five percentage points, not automatically a five-percent relative change.
- Label mean/SD and confidence intervals distinctly. Paired bootstrap intervals describe the paired mean and are not simultaneous across the 29 tests.
- Stage-trajectory uncertainty is pointwise descriptive unless otherwise specified. Do not infer equivalence from overlap.
- Retain every expected seed in the inventory. Unavailable endpoints remain unavailable, with the fixed-family bookkeeping described in the analysis contract.
- Inference timing calls are repeated measurements of a runtime, not independent research seeds.

## Rendering

Export scientific plots as vector PDF/SVG plus a high-resolution PNG preview. Use readable fonts at the intended single/two-column print size, accessible colors paired with line styles/labels, direct units and simple 2D panels. Avoid 3D bars, decorative dashboards and color-only significance coding.

Generate every figure from one validated input table and save its input hash, analysis/source/config identities, rendering version and caption. The caption states the bank/condition, metric, number/unit of repeats, uncertainty convention and relevant exclusions. Never use a paper's reported numbers as another seed of this study.

## Report tables

Required tables are: data/support and exclusions; implementation/amendment traceability; selected settings/environment; complete run inventory; clean/poisoned baseline outcomes; 29 contrasts/effects; ablation results; costs; contextual literature comparison; limitations and failed conditions.

The claim ledger should connect each conclusion to those tables/figures and its exact scope. Label a result as descriptive, exploratory or confirmatory according to the frozen analysis, rather than by whether it looks favorable.
