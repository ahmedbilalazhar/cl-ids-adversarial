# Implementation and experimental evaluation: second audit

24 October 2026. This review extends the earlier 31-item source audit through G64. It combines source inspection, primary research, full public-data acquisition, conditional preprocessing/split/ownership audits, statistical design arithmetic and repeated protocol review. It contains no trained-model results.

**Final source review and later adoption:** [feature-semantics-and-final-recommendation.md](feature-semantics-and-final-recommendation.md) supersedes the earlier 76-feature candidate with the user-adopted 74-feature omission amendment and scenario-class claim boundary. Positive header inconsistencies and benign-annotation provenance are explicit. Historical candidate tables below keep their original scope; final tuning/grid remain gated.

## Overall assessment

The research question is implementable, but the current legacy runner is not a conforming implementation of the revised Phase 2. The most valuable next step is an adopted data contract and one correct reference trajectory. Additional GPU accounts or a larger run grid cannot substitute for those two milestones.

The plan is now more precise about data provenance, calibration, component identity, client allocation, filtering, memory, evaluation banks, uncertainty, recovery and publication claims. These are concrete planning improvements and new data-feasibility evidence. They are not proof that the proposed defense works or that all implementation defects are fixed.

## 1. Highest-priority gaps and remedies

| Priority | Gap that can change the conclusion | Required remedy |
|---|---|---|
| P0 | Legacy data/scaler/splits and fixed future head differ from the revised methodology | Build the separate Phase 3 engine and typed data/evaluator packages; retain old results as historical |
| P0 | Dataset variants change labels, timestamps, components and eligible acquisition families | Adopt one explicit profile before development; preserve rare classes without inventing support |
| P0 | Future reference conflicts can decide calibration eligibility | Choose Monday-only own-row-valid fit IDs first; never refit after cross-day conflicts |
| P0 | Finite source features include invalid negative values and extreme scaler minima | Select the named domain-screening amendment or justify an alternative prospectively; retain sentinel semantics |
| P0 | Split reproducibility depends on canonical component IDs and a fixed SGKF implementation | Use minimum immutable provenance IDs, a version containing the 1.8 shuffle fix, and actual role-support evidence |
| P0 | Whole mixed-component row retention can overwhelm the intended benign budget | Select whole benign bundles by component while preserving split/owner boundaries; publish realized counts |
| P0 | Replay/importance timing and optimizer resets are materially wrong in the legacy runner | Implement pre-update targets, first-pass Algorithm R, per-example stage-end importance and broadcast-reset semantics |
| P1 | Source dose can be mistaken for global contamination or actual admitted poison | Publish per-seed source, local/global fractions, admitted counts, quota bounds and aggregation weights |
| P1 | Low persistence harm can coexist with poor absolute detection | Report clean and poisoned errors, Hulk recall, FAR, confusion destinations and benign-cohort behavior |
| P1 | Twelve seeds and 29 tests do not guarantee useful power | Preserve the declared family; report resolution/effect sizes and avoid equivalence claims from non-rejection |
| P1 | Controls and ablations do not automatically isolate the claimed mechanism | Use matched volume/composition controls, scoped interventions and explicit exploratory status |
| P1 | Publication/deployment generalization exceeds one historical capture and synthetic sites | Narrow the contribution, compare closest work fairly and obtain independent evidence for broader claims |

P0 means a blocker for the relevant data/implementation lock; it does not imply every concern is a newly discovered software defect. The detailed [second-audit-gap-register.md](second-audit-gap-register.md) separates the issues and required evidence.

## 2. New data evidence

Both full archives are now local and integrity-audited. The original metadata-bearing mirror is pinned to a commit and its Git-LFS object digest; provider authentication remains separate. Its eight CSV members contain 2,830,743 nonempty records plus 288,602 all-empty trailing records. Treating blank CSV records as flows inflates the dataset census.

The original timestamp strings lack AM/PM. Most are minute-resolution; Monday also needs the explicit afternoon interpretation. The corrected source supplies UTC microsecond timestamps and 2,099,976 records, but it is a distinct extractor/annotation contract. Never borrow timestamps across releases by row position or similar features.

With attempted traffic mapped to benign under the correction authors' guidance, confirmed corrected web-brute/XSS/SQL counts are 73/18/13 before isolation. Ordinary Infiltration has 36. No split can make these satisfy 50 train, 50 development and 50 test examples. The additional Infiltration-Portscan label must remain distinct unless a semantic amendment is justified. A distinct scenario annotation is not proof of a new attack technique relative to Friday PortScan. Count feasibility supports a new annotated-class experiment; behavioral novelty requires separate semantic justification.

At the conditional 120-second gap, the domain-screened original/corrected candidates retain 1,407,514/1,362,039 unique survivors. Hulk support is 1,247/158,468 respectively. These populations differ through multiple source/curation mechanisms; the audit does not attribute the difference to one cause. Components are operational session/content units, not independent attack campaigns.

See [data-release-decision.md](data-release-decision.md), [feature-domain-and-precision-review.md](feature-domain-and-precision-review.md) and the machine-readable evidence. The fixed screened-corrected split passes the required source/anchor and stage support checks through Infiltration-Portscan, with zero component overlap. Heartbleed is test-only and must not be added as a learned output. All retained Hulk and FTP records each share one endpoint pair across roles, so this is not host-disjoint evaluation. The final profile remains unselected.

## 3. Sampling and exposure are part of the scientific design

The earlier strict original-candidate sampling rule forces 17,960 E4 benign rows, defeating the roughly 3,500 target. The proposed benign-bundle amendment selects all benign members of a training component together across stages while retaining prescribed attacks separately. All retained component members keep one role and owner; excluded benign remains reserved to train.

On the original as-published candidate, the amendment produces 3,504/3,505/3,544/3,500 benign examples over E1-E4, versus 3,508/3,515/3,501/17,960 under strict all-row retention. Neither policy has been selected using model outcomes.

For that amended original candidate, a 50% attacked-site source dose becomes only approximately 0.0834%-1.7266% of global raw E2 examples across the twelve prescribed ownership seeds. The maximum-dose flipped count ranges from 14 to 290. Do not describe this as 50% global label corruption. Actual admitted poison still requires scorer outputs; this audit provides only quota bounds and DQ expectations.

The screened-corrected bundle candidate selects 3,500 benign examples at each stage and 183,039 fresh training records overall. At maximum source dose its global raw E2 flip fraction ranges from 0.209% to 34.642%. In ten of twelve seed inventories DC must retain some poison even with perfect ranking; the largest forced retained fraction is 74.7%. See [realized-dose-and-quota-limits.md](realized-dose-and-quota-limits.md). These are counting bounds, not downstream harm.

The exact component allocator, integer quotas, RNG namespaces and class-balanced optional buffer are now specified. Approximate prose such as "Dirichlet non-IID" or "class-balanced replay" is insufficient to reproduce these choices.

## 4. Evaluation must answer the question actually measured

Report H beside absolute clean/poisoned Hulk-to-benign error. An always-benign classifier has maximum attack success and zero incremental harm; this shows why small H alone cannot establish security.

Keep untargeted-new F1 accompanied by precision/recall and confusion sources: Hulk false positives can affect that F1. Include supported rare attacks in the descriptive full-seen binary bank, name the eligible-family bank separately, and report the fixed cross-period benign-bank mixture. At E1 that benign bank is not a contemporaneous future-free deployment estimate.

Twelve seeds capture variability from initialization, synthetic ownership, attacker and sampling on a fixed capture/split. They are not twelve captures or organizations. Bootstrap whole seed blocks for the declared seed-level summaries; treat any component uncertainty as a different descriptive question. The hypothetical signed-rank calculation is resolution planning, not a power guarantee.

The 29-test Holm family remains fixed. DQ, ablations, oracle repair, source/curation sensitivities and external studies remain exploratory unless prospectively redesigned. A significant acquisition difference and non-significant security difference do not demonstrate equal security or a superior trade-off. Non-inferiority/equivalence requires justified margins and a compatible design.

## 5. Controls and baseline fairness

FT/EI/DR are precise separately tuned references. Their differences are pipeline comparisons unless optimization is controlled for a stronger attribution claim. EI uses supplied-label empirical squared-gradient importance; do not call that the strongest or uniquely correct Fisher formulation.

DM and DC match admitted volume and aggregation weights within each condition; DQ matches DC's class quotas with random within-class selection. These answer different questions. Filtering only recurring supplied benign in this schedule limits any broad purification claim. Higher doses can change admitted workload and FedAvg weights.

NoZ/NoY/FIFO begin from the start and measure whole-trajectory component changes. Post-E2 label repair leaves earlier weight/logit damage intact. First E2 pre-update teachers are shared before poisoning has changed the model; a poisoned-bearing record is not automatically a poison-altered dark target. Memory occupancy or importance magnitudes alone cannot establish a causal harmful pathway.

Centralized joint-history retraining, local-only training or further strong methods are useful only if their question matches the intended claim. Joint-history access is an oracle resource advantage, not a guaranteed upper bound. Do not expand every optional control at the expense of correct core implementation and replication.

## 6. Efficient implementation and reproducibility

The MLP is small: 19,087 parameters at 15 outputs, 19,152 at 16. GPU benefit is unmeasured. Profile complete representative CPU/GPU trajectories, including scoring, per-example importance, replay, saving and evaluation. Avoid per-batch host synchronization and reparsing CSVs. Preserve exact prefix reuse only when complete scientific/runtime/state identity permits it.

PCG64 state contains 128-bit integers. Encode them losslessly as decimal strings or typed binary; a file hash cannot restore already rounded JSON numbers. Recovery needs full client/model/replay/importance/RNG/cursor state, not a completed-run skip flag.

Eight distinct contributors provide scheduling capacity, not additional statistical samples or FL clients. Each job simulates five clients. Use real remaining quotas, compatible paired runtimes, bounded saved jobs and complete failure accounting. Nominal quota arithmetic is not a measured feasibility claim.

The audit tools, exact ordered candidate schema, environment record and evidence are included. They remain conditional data utilities rather than a complete canonical learner/builder. Raw archives, trained weights and performance tables are not in the package.

## 7. Recommended next steps

1. **Author A:** adopt a source/domain/taxonomy/benign policy and publish final manifests/support. For a corrected-label research amendment, the corrected screened profile is the preferred candidate to evaluate; accept its narrower E3 claim rather than relabel attempted traffic to manufacture support.
2. **Author B:** build the narrow FT/FedAvg reference state machine, then conforming EI/replay/admission. Follow the concrete contracts and acceptance requirements.
3. **Both:** cross-review data and state ordering, prove durable continuation, measure actual CPU/Kaggle costs, and select development settings/scope.
4. **Freeze before final outcomes:** code/data/runtime/analysis identities, twelve seeds, all primary/exploratory labels, failure dispositions and deviations.
5. **Execute the selected package:** the focused 441-logical-trajectory starter remains the recommendation if measured resources permit; 432 distinct full executions require valid development aliases. Twelve new diagnostic suffixes are conditional on exact control aliases. Optional studies are separate budgets.
6. **Evaluate and write:** produce real figures, fair within-protocol comparisons, count-aware inference, a claim/evidence ledger and a critical discussion. An independent external capture requires a separate audit; original versus corrected CICIDS2017 is not external replication.

See [rubric-and-readiness.md](rubric-and-readiness.md) for all seven course requirements and completion gates. Actual deadline and instructor feedback remain unknown; no feedback or approval has been invented.

## 8. What the audit does and does not establish

It establishes traceable candidate archive identities, observed data defects/support, conditional graph/split/ownership evidence, precise proposed fixes and a stronger evaluation plan. It does not establish predictive accuracy, defense effectiveness, GPU hours, deployment safety, independent reproduction or publication acceptance. The legacy learner has not been silently rewritten, and no final-test model outcome was inspected.
