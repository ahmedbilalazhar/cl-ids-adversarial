# DG global low-loss baseline card

## Status

The original Phase 2 proposal names DG as “DER++ + global 75% low-loss filter.” The adopted-profile runner now has a separate executable DG selector and a `--dg-only` run mode. A pinned-runtime attempt completed 10 of 48 trajectories before storage headroom became unsafe; its hashes and failure status are recorded in `results/phase3-dg-baseline-v2/incomplete-attempt.json`. This incomplete block is excluded from analysis. No complete DG block has been evaluated, and the frozen 417-trajectory evidence is unchanged.

## Operational rule implemented

- At each stage boundary, rank each client's supplied current records together across labels by the frozen-model per-record cross-entropy.
- Retain `floor(0.75 * n + 0.5)` records per client, as specified in Phase 2. Break equal-loss ties by ascending immutable row ID.
- Do not protect newly introduced or rare classes. Bypass admission in E1 for every arm; apply the filter starting in E2.
- Keep the selected IDs fixed for the stage and use the existing admitted-current-count FedAvg aggregation.
- Record client-level selected-ID hashes and pre/post class counts. DG's fixed fraction is distinct from DM, which matches each client's total admitted count to DC.

Ceiling rounding, the row-ID tie break, and client-local filtering (no pooling of client records) make the brief Phase 2 phrase executable. E1 is passed through unchanged, as required by Phase 2. The selector implementation is prospective and does not constitute experimental evidence.

## Experimental question and falsifiable hypothesis

**Question:** Does a fixed global low-loss filter change poison persistence, new-family acquisition, or benign false alarms relative to the class-aware DC rule and volume-matched global DM rule?

**Hypothesis:** The fixed global 75% filter yields lower new-family acquisition than DC on average (`mean(A_DG - A_DC) < 0`) because it does not protect new classes. The directional hypothesis is falsified if the paired mean difference is nonnegative across the registered seed/dose matrix. Poison retention and H remain empirical outcomes; loss ranking is not assumed to detect poisoning.

## Required run matrix and analysis

- 48 full trajectories: DR+DG × four registered doses (0, .1, .3, .5) × twelve ownership seeds (1–11, 42).
- Use the existing pinned environment at `tmp/phase3-reference-env` (Python 3.12.14, PyTorch 2.7.0+cpu, NumPy 2.3.5) and a new output identity. Run the complete 48-cell block with `PHASE3_STUDY_OUT=results/phase3-dg-baseline-v5 tmp/phase3-reference-env/Scripts/python.exe scripts/run_phase3_overnight.py --dg-only --hours 6`. The original frozen output and the three interrupted attempt directories must not be reused.
- First verify the shared E1 prefix: DG, DM, and DC must have identical E1 admitted-ID and checkpoint hashes for each seed. Then pair E2--E4 and outcomes by seed/dose against DR+DM and DR+DC; preserve historical clean-only tuning provenance.
- Report admitted counts and per-class counts, A, H, immediate source recall change, benign FAR, eligible macro-F1 and fixed-cohort retention metrics from raw confusion matrices.
- Treat this added DG analysis as exploratory because its outcome family is being completed after inspection of the existing study. Report paired effects and whole-seed uncertainty; do not append contrasts to the old 29-test confirmatory family or claim significance without a predeclared family and correction.

## Compute and stopping rule

From the 48 matched DR+DC reference run elapsed times, p90 was 199.203 seconds. A conservative 48-run estimate with 20% reserve is 11,474.1 seconds (3.19 hours). The dedicated CLI mode enforces the smaller of the user-supplied hours (minus the existing .75-hour finalization reserve) and a 5.25-hour execution ceiling. Pinned attempts v2/v4 stopped for storage failures and v3 stopped after discovery of the rounding mismatch; all are hash-inventoried and excluded. The corrected formula passed focused synthetic selector and simulator checks. The user restored C: headroom before v5. Execute the complete matrix only if the budget gate passes, preserve failures, and do not claim confirmatory status.

## Acceptance evidence

The corrected E1 pass-through must match DM/DC admitted-ID and checkpoint hashes. The new run writes SHA-256 inventories for results/checkpoints plus actual elapsed-time summaries. Completion requires all 48 data-backed trajectories, input/attack parity, E1 hash parity and independent metric recomputation; no result from development-bank evaluation is final-test evidence. Mark this added DG analysis exploratory; it does not replace the frozen 417 trajectories.
