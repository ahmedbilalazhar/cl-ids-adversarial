# CPU milestone v2 decisions — 24 October 2026

Authority: the user's implementation request; adopted v1 data/taxonomy decisions;
unchanged Phase 2 equations. No instructor feedback has been supplied. These
choices authorize development implementation only. The final GPU grid and
final-test inference remain disabled. The previously observed seed-101 filtered
DR+DC outcomes are known; no v2 development model outcomes are known at this record.

1. **Version boundary.** Preserve every `src/phase3/*.py` byte and every v1
   artifact. Its code hash enumerates that directory. Use sibling
   `src/phase3_v2`; hash its complete module set plus the unchanged v1 dependency
   files, protocol, training manifest and pinned runtime. No v1 run is an
   unfiltered pilot or an independent replicate of v2.
2. **Development selection ambiguity (A-V2-01).** Use the recommended
   feasibility-first interpretation in numerical-and-state-decisions section 9.
   Require all three seeds 101–103 to complete validly for each candidate.
   For each unfiltered learner separately require mean E1 FTP recall >=1/2,
   mean E1 SSH recall >=1/2 and mean E2 Hulk recall >=7/10. These are three
   distinct required cells per learner. Filter tuning candidates by these gates,
   then maximize equal-stage, equal-seed eligible macro-F1. Do not apply this
   gate to filtered arms or exclude their adverse outcomes.
3. **Synchronization.** Execute the 18 unfiltered clean pilot cells in the
   original two budgets, three learners, three seeds, with declared defaults.
   Require all nine cells per budget valid; maximize the exact mean of the
   count-derived rational stage macro-F1s across all learners/seeds/stages.
   Exact ties choose fewer rounds. Acquisition gates apply to tuning selection;
   pilot gate failures are reported and do not prune the predeclared tuning grid.
4. **Tuning order and ties.** Numeric lexicographic order: learning rate
   0.0001,0.001; EI lambda_E 1,10,100; DR lambda_z 0.1,0.5,1 then lambda_y
   0.1,1. Learner order FT,EI,DR; seed order 101,102,103; pilot budget order
   (1,3),(3,1). For exact score ties use the mean measured complete logical
   training-loop seconds (including scoring/importance/checkpoints, excluding
   inference/startup/preparation), then the numeric configuration order. Cached
   aliases carry their original logical measured cost; never zero. No rounding
   tolerance defines a metric tie. Infrastructure failures may retry the same
   identity; invalid numerical candidates stay invalid, with no favorable-seed
   averaging. All-infeasible learner grids stop progression; a second-budget
   revision needs a new dated record. Maximum-dose FT diagnostics are gated on
   all three learners passing clean feasibility.
5. **EI numerical convention (A-V2-02).** Model, gradients, per-example squares,
   chunk reductions, accumulation and penalty are FP32. Eval-mode supplied-label
   CE gradient has the opposite sign of log likelihood; its square is identical.
   Process selected records in saved RNG selection order, chunks of 64; sum
   per-example squares within chunks then in chunk order, divide once by n.
   Accumulate importance with decay one. Penalty is lambda_E/2 times the sum
   over all coordinates; no layer normalization. The independent tiny reference
   loops single records. Before comparison set rtol=2e-5, atol=2e-7 for FP32
   reduction-order differences; exact integers, RNG states and same-engine CPU
   recovered trajectories require equality. No CPU/CUDA equivalence is claimed.
6. **Streams and admission.** Retain v1 namespaces 1,4–8,10; add predeclared
   2 attacker selection(seed), 3 source prefix(seed,client), 9 importance
   (seed,client,stage), 11 DQ(seed,client,stage). DQ assigns a random permutation
   of canonical-ID-sorted records within each supplied class, visiting classes
   in increasing source-code order. The saved admission locks all three controls
   to independently calculated DC quotas. E1 filters are off for every arm.
   One persistent client dropout stream covers both CE forwards, as v1.
7. **Data path.** Reuse and rehash the audited v1 preparation and its original
   source/cache evidence; independently rebuild seed ownership using unchanged
   allocation. This is not fresh CSV/session reconstruction. Export private
   supplied-label-only training directories; keep clean annotations, component
   maps, corruption prefixes and exposure joins in separate audit directories.
   Development uses the existing pinned bank, all registered outputs, no test
   rows. Freeze eligibility before dose/admission.
8. **Recovery.** Commit the complete next transition only after all clients,
   aggregation and (at final stage round) EI importance/anchor commit. Save
   strict schema, all retained arrays, dropout bytes, decimal PCG64 state,
   counters, sample IDs, locked admissions and ledger. Optimizers reset at each
   broadcast, so no optimizer survives a commit. A process crash re-executes the
   uncommitted round. Suffix outputs are the same logical run and are not
   separately evaluated as a complete trajectory.

Scientific clarifications above implement the supplied contracts prospectively;
they are not instructor approval or a freeze of the final study. Twelve final
seeds and the single 29-contrast analysis family are unchanged. Optional eviction
ablations, oracle interventions, CUDA and final inference are outside this CPU
milestone. Any verified software correction and affected reruns are logged in
`defects-and-amendments.md`.
