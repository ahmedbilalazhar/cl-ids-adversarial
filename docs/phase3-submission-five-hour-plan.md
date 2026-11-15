Phase 3: five-hour submission plan

Assessment based on the pulled Phase 3 implementation, submitted `submissions/phase2-with-claude.tex`, notebook, and saved results. Planning only: no new training or revised statistical analysis has been executed.

The best use of the deadline is to correct interpretation, complete the report, and add at most one controlled mechanism experiment. The existing grid already contains 696 run JSONs: 58 settings for each of 3 ownership partitions x 4 training replicates. All 696 archived JSONs match the committed SHA-256 ledger. This establishes archive integrity, not scientific correctness or independent replication.

Evidence that changes the priorities:

| Finding | Required action |
|---|---|
| The README links to `submissions/phase3-report/`, which is absent in the checkout | Finish one authoritative report and export a readable PDF before spending the whole deadline on compute. |
| Phase 2 H is mean E3/E4 Hulk-to-benign ASR increase; notebook H is final Hulk recall loss | Recover the Phase 2 endpoint from saved stage outputs. Preserve current results under an explicit name such as final recall damage. Explain the amendment and distinguish targeted evasion from wrong-attack-family predictions. |
| Immediate recall change also has the opposite sign from Phase 2 | Use one stated sign convention consistently in equations, tables, and captions. |
| Phase 2 specifies one 29-test Holm family; the new grid has 30 C1 and 17 C2 tests corrected separately | Remove “exactly as planned” and unqualified confirmatory claims. Present the changed study as amended/exploratory; show combined correction across all 47 performed comparisons as a sensitivity analysis. Do not retrospectively select the most favorable 29. |
| Four training replicates share each ownership partition and the development bank | State 3 partitions x 4 replicates, not 12 independent seeds/sites. Show all partition-level paired effects. Average replicates within partition for a conservative sensitivity analysis; with three independent partition units, exact two-sided signed-rank tests cannot reach .05. Any bootstrap interval based on three partitions is unstable and conditional on the fixed capture/split. |
| Clean final macro-F1: FT .0308, EI .0461, DR .4907; FT/EI final Hulk recall is zero even without poisoning | Report clean failure and stage trajectories. Zero additional final recall damage cannot establish security. Restore targeted ASR and show absolute errors as well as clean-matched changes. |
| At k5/dose .5, existing final-recall damage is NONE .7846, DC .4946, DM .6235, DQ .3410 | The statement that no rule reduces persistent damage is too broad. At this arm DQ also has final macro-F1 .4508 versus DC .3249. Examine paired effects and all arms; describe uncertainty and trade-offs. These numbers use the current recall metric, not the Phase 2 H. |
| One-client and three-client arms change attack distribution as well as total flipped rows | Show attacker count and realized global source-row corruption separately. The single-client arm averages about 25.7% of Hulk rows in the final grid, despite the brief describing an earlier ~6% run. Do not merge these accounts or fit one universal dose-response trend. |
| The literature CSV maps components to references; the repository cross-check compares internal implementations | Add an actual paper comparison with datasets, metrics, learning/attack assumptions, published findings, and explicit comparability limits. |
| The brief still says runs remain incomplete, but the final archive is complete | Update stale status text. Describe code/config changes between internal implementations; batch size alone differs (128 in the older protocol, 256 here), so .655 versus .434 is not a controlled GPU/CPU comparison. |

Five-hour schedule, measured from starting execution:

| Time | Work | Concrete output / stopping rule |
|---|---|---|
| 0:00-0:35 | Freeze scope; document Phase 2 deviations; begin report | Scope-change table; final list of figures/tables; honest study status. Include actual class feedback only if available. |
| 0:35-1:20 | Reanalyse archived JSONs | Corrected H and signed recall change; absolute E2/E3/E4 source recall and ASR; partition-level paired effects; consistent multiplicity disclosure. No retraining required. |
| 1:20-2:10 | Explain strongest existing ablations and DQ; optional memory intervention | Mechanism table with clean twin, poisoned result, acquisition, FAR, memory contamination and final recall. Spend at most 50 minutes preparing/running the optional intervention; if its parity checks fail, stop and use existing ablations. |
| 2:10-3:40 | Complete paper comparison and report | Full report with all seven assignment requirements and 4-5 discussed figures. If two people are available, one can write while the other performs the bounded experiment/reanalysis. |
| 3:40-4:30 | Reproduce analysis and verify submission | Regenerate selected tables/plots from archived runs; check every headline number against its source; run a short implementation smoke check if runtime is available; export and inspect PDF. |
| 4:30-5:00 | Package and submit | Report PDF, notebook/code, dependency/runtime information, result archives and concise reproduction README. Reserve time for upload failure and opening the uploaded files. |

If a sixth hour really exists, use it only after a complete submission package exists: expand a validated small intervention across the remaining training replicates or improve reproducibility and presentation. Do not rely on that hour to finish the report.

The strongest additional experiment, if the pipeline is already running:

Question: does continued replay of mislabeled stored records contribute to post-withdrawal damage, beyond damage already present in the E2 model?

Use DR, no admission, five attackers, 50% within-attacker Hulk corruption. This is an existing arm with substantial damage and avoids the near-total saturation at 90%. At the end of E2 compare three continuations:

1. Ordinary replay, using the existing baseline or a parity-verified reproduction.
2. Oracle removal of poisoned replay records using evaluator-only provenance.
3. Random removal of exactly the same number of records per client, using a separate intervention RNG.

Keep the E2 model, head mapping, ordinary RNG states, E3/E4 data and training schedule identical before the intervention. Audit E2 prediction/config equality, deletion counts, and zero poison in the oracle-purged memory immediately after deletion. Compact every buffer field together and define subsequent insertion behavior; an intervention that corrupts buffer state is not evidence. Never give oracle masks to ordinary admission or training.

Start with seeds 101/102/103, replicate 0: two added continuation variants per partition, six additional runs if normal baselines can be reused after parity verification. A rerun from the start with the intervention only at the E2 boundary is acceptable. Expand to all four replicates only after the pilot is correct and time remains. Record the added setting in output identity so the resumable runner cannot reuse an old file.

Measure E3/E4 targeted ASR, Hulk recall, eligible macro-F1, acquisition, benign FAR, and replay occupancy/poison counts. Plot all three partition-level paired changes. Better recovery after oracle deletion than count-matched random deletion supports a contribution of continuing poisoned replay; residual failure can reflect the poisoned E2 weights. A null difference does not establish that memory played no role. This is an explanatory oracle ablation, not a deployable defense. Deletion changes memory composition and later draws, so keep causal claims specific to this intervention.

The existing `lam_z=0` arm already provides a replay-label-only baseline; do not spend time implementing the same ER comparison again. Existing FIFO and `lam_y=0` outcomes show that low damage can accompany catastrophic loss of clean capability. Use these as evidence of a security/retention trade-off, not successful defenses. Existing nmin variants barely change results; check whether the protected class counts actually cross the thresholds before claiming a threshold is irrelevant.

Report contents:

- Problem, research questions and reduced scope; a Phase 2-to-Phase 3 change table covering dataset/features, attacker strength, repetitions, endpoints, statistical plan and omitted transfer/discovery work.
- Method with expanding head, persistent five-client ownership, FedAvg weighting, EWC-style variant, DER++ losses and buffer rules, and frozen-model admission selection.
- Data source/release, 74 features, exact cleaning/scaler and grouped split, per-class counts/support exclusions, train/development separation, and development-only evaluation status.
- Baselines with mean/dispersion, precision/recall/F1, accuracy, FAR, source ASR, acquisition and continual-learning metrics. Recompute additional metrics directly from saved confusion matrices.
- Results figures: clean stage trajectories; E2-E4 Hulk recall and targeted ASR; DC/DM/DQ trade-offs at moderate and severe corruption; ablations with matched clean capability; one full-inventory confusion/error view if space allows.
- Primary-paper comparison and limitations. A published method reproduced/adapted locally is a quantitative baseline; a paper with different data or protocol is contextual evidence.
- Critical discussion, failure cases, uncertainty, resource accounting and reproduction instructions. Communication is an analytical float32 parameter-byte estimate, not measured network traffic; run timings under concurrent GPU workers are not isolated inference benchmarks.

Useful primary sources for the comparison:

- Lavaur, Busnel and Autrel (2025), label-flipping in federated IDS: https://orbilu.uni.lu/handle/10993/65906 . The paper finds strong setting dependence; compare threat/heterogeneity and recovery assumptions rather than declaring a cross-paper accuracy winner.
- Carillo et al. (2026), federated and incremental IDS: https://domenicociuonzo.wordpress.com/wp-content/uploads/2026/03/early_access_tnsm26_fedcil_ids.pdf . Compare federation, class growth and retention; its datasets and setup differ.
- Buzzega et al. (2020), DER/DER++: https://arxiv.org/abs/2004.07211 . Explain adaptation to the five-client expanding-head IDS and the differences from a faithful reproduction.
- Reuse other verified Phase 2 primary papers where they directly address defense or rare-class trade-offs. Verify any published number in its original table and record the metric, split and dataset version. No headline percentage ranking across incompatible settings.

Recommended framing: an empirical study of poisoning persistence and legitimate adaptation under a restricted federated continual-IDS protocol. Replay retains useful and corrupted information; class protection preserves admitted rows without guaranteeing learned discrimination; random selection is a serious control. The negative defense results can answer the research questions when reported accurately. Do not promise a beneficial defense, general EWC failure, unseen-attack discovery, state-of-the-art performance, or final-test generalization.
