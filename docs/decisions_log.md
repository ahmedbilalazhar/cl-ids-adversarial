# Decision log (mandatory per repo Decision-Making Policy)

Standing settings (2026-09-26, user-stated — recorded here as project memory):
no deadline rush; ~7 weeks available; target bar is award-worthy / Q1-journal,
not workshop-minimum. Prefer rigor over speed everywhere below.

One line each: chose / alternative / why. Newest last.

1. Phase 0 label repair via substring fallback (not re-exporting raw CSVs): chose
   fallback mapping in `clean.py`+`sequence.py` / alternative was re-decoding raw
   bytes / raw bytes are literally U+FFFD, so no encoding recovers them.
2. EWC fix accumulates Fisher + 1/2 factor + expansion guard: chose full
   Kirkpatrick form / alternative was documenting the deviation / penalty must
   mean what the citation says it means.
3. LwF KL-width slice on head growth: chose slice-new-to-old-width / alternative
   was crashing or dropping LwF / slicing is the published LwF practice.
4. Archived `*_prefix0` instead of deleting: chose rename+README / alternative
   was delete-and-regenerate / policy and reproducibility demand provenance.
5. Regenerated all three `tasks*.npz` (not just `tasks.npz`): chose full regen /
   alternative was patching T3 only / CI file had silently lost a whole day.
6. LwF kept in reporting: chose keep-with-mechanism / alternative was silent
   exclusion / buffer-size diagnostic (500→4000 closes ~60% of gap) proved a
   real effect, and unexplained exclusion hides information.
7. `a1`/`a3` ablations not re-run: chose cut-with-statement / alternative was
   spending ~1h compute / locked scope already deprioritized them.
8. Anchor ACC-cost claim softened (p=0.078): chose "suggestive, n.s." wording /
   alternative was claiming p<0.05 / the number is the number.
9. Federated partition = per-task Dirichlet(0.5) label skew, 5 clients: chose
   this / alternative was day-sharding clients / per-task skew keeps the CL
   day-sequence intact while giving standard FL non-IID semantics.
10. Poison budget rho defined per malicious shard: chose shard fraction /
    alternative was global-stream fraction / matches single-node E2 semantics
    where rho is fraction of the poisoned training pool.
11. `local_epochs=3` (= single-node epochs): chose parity / alternative was
    fewer epochs for speed / Phase-3 ablation needs matched compute.
12. Reverted Adam-refresh-on-broadcast: chose pure `load_state_dict` / alternative
    was fresh optimizer per round / 1-client test: refresh scored 0.247 vs 0.317
    without it (single-node 0.282), so refresh broke fidelity.
13. Phase-2 attack = targeted label-flip (Hulk→Benign), not backdoor: chose flip
    / alternative was backdoor or both / flip is the direct comparator to
    single-node E2 that Phase 3's centralized-vs-federated ablation requires;
    backdoor-federated stays a possible extension, not run now.
14. `requirements.txt`: added pyarrow+psutil, dropped seaborn+tqdm: chose
    accurate deps / alternative was leaving it / an unreproducible env is a
    correctness bug.
15. Archived `run_remaining.py`, renamed grid driver to `run_grid.py` with
    relative ROOT: chose archive+rename / alternative was leaving both /
    in-place config rewriting is lossy and absolute paths break portability.
16. Extended stats_summary WILCOXON_PAIRS with f2 method-ranking, dose-response,
    and fed-vs-single-node pairs: chose automatic-in-script / alternative was
    ad-hoc analysis / headline and ablation tests must regenerate with one command.
17. Phase-4 defense scope = small-loss × 3 methods × {p5,p10} (42 runs): chose
    this / alternative was full 3×4 grid or single-method probe / p0/p10
    baselines already exist in f2, so p5+p10 completes the comparison at half
    the cost; knn needs no federated re-proof after significant single-node harm.
18. Defense choice = small-loss, knn to future work: chose small-loss /
    alternative was knn-consistency / numeric probe on new data: knn retains
    0.000 of Heartbleed/Sql-Injection/Infiltration on CLEAN streams and drops
    21% of clean T2 while small-loss alone improves ACC under attack (n=7
    p=0.0156); small-loss flip-removal recall is 0.000, so it is reported as
    "helps ACC without removing flips (ASR rises)", not as a purifier.
19. Phase-5 novelty verdict: gap is real but one paper deep: chose "first,
    citing Su-2025 future-work call" framing / alternative was unqualified
    "first" / Su 2025 explicitly defers poisoning+non-IID to future work and
    we answer exactly that; unqualified novelty would not survive review.
20. F4 scope and write-up order under the Decision-Making Policy: chose to
    execute Phases 2–6 without further confirmation gates / alternative was
    stopping after each phase / policy escalates only on claim changes,
    destruction, >1-day extra cost, or rigor-for-speed trades — none applied.
21. Q1 push (7 weeks, no deadline): chose dataset #2 (UNSW-NB15) + persistent
    multi-task attack + malicious-fraction sweep as the strengthening program /
    alternative was polishing the CICIDS-only story / single dataset and
    single-task attack exposure are the two credibility killers a Q1 reviewer
    will name first.
22. Matched-memory DER++ arm (buffer 100/client federated vs 500 single-node):
    chose to run it / alternative was leaving Phase-3 comparison confounded /
    I introduced the 5x-memory confound; owning the control is correctness.
23. b100 outcome softens Phase-3 DER++ claim: chose "partly memory artifact"
    wording / alternative was keeping "federation hurts DER++ (p=0.031)" /
    matched-memory gap vs single-node is n.s. (p=0.375) while finetune gap
    (no memory confound) stands — report both, overclaim neither.
24. Target journal = Elsevier Computers & Security (Q1), fallback JNCA: chose
    C&S / alternative was TIFS/TDSC/TOPS or staying workshop-shaped / Lavaur
    et al. C&S 2025 (systematic label-flip x FL IDS) is our paper's shape twin
    AND the adjacent work we must distinguish (they lack the continual
    dimension); C&S owns the empirical adversarial-evaluation lineage
    (Apruzzese driftxperturbation, AIS-NIDS 2024). AISec/ACM-sigconf refs void.
25. Proposal H1/H2/H3 rewritten to exact wilcoxon.csv values: chose
    0.3070v0.3187 p=0.4688 (H1 non-reproduction), 0.2742v0.3010 p=0.0781
    (H2 suggestive), 0.3637v0.3070 p=0.0156 + 0.2612v0.3070 p=0.0313 (H3) /
    alternative was leaving stale pre-fix numbers (p=0.031/0.047/0.016 drafts)
    / no claim may lack a trace to wilcoxon.csv; stale numbers are never cited.
26. CICIDS2017-over-UNSW reason (backfill): chose comparability with
    arXiv:2608.04602 (H1 target) + Paper-1 future-work naming (CIC-IDS2017
    first of three) / alternative was the EdgeFedCIL rationale in an old note /
    the old note was wrong about our own reason; comparability is checkable in
    proposal.md S4. UNSW-NB15 + CICIoT2023 join as datasets #2/#3 (Phase 4).
27. Scaler = frozen T0+T1-fit primary, per-task secondary: chose frozen /
    alternative was keeping per-task primary / same-seed n=7 finetune ablation:
    frozen 0.5439+-0.0083 vs per-task 0.2991+-0.0162, p=0.0156 — per-task
    re-standardization injects cross-task shift dominating all method effects;
    frozen leaks nothing from the future (T0+T1 train only) and matches the
    plan's no-backward-leakage rule plus Paper-1's single-transform practice.
    Benefit: principled geometry; cost: locked pre-2026-09-26 numbers become
    conservative lower bounds (stated, not hidden).
28. Head = pre-sized fixed, uniform, expand dormant (backfill+resolution):
    chose document-and-keep / alternative was silent picking or a hidden
    mixed strategy / run_experiment.py pre-sizes to full label space so
    expand_head never fires; all methods share base.py::_maybe_expand; LwF
    slice-to-seen-width (#3) is consistent with this, not a rival strategy.
    Growing-head ablation scheduled in Phase-2 ablations, not decided silently.
29. Byzantine + robust aggregators + adaptive attacker promoted to PRIMARY:
    chose implement all in Phase 3 / alternative was "Option 2-B only" scope /
    a security journal expects the aggregation attack surface attacked AND the
    defences adaptively evaded; Lavaur 2025 already owns static FL label-flip.
30. A1/A2/A3 CUT void, chrono-primary, Holm families, power-set seeds:
    chose full Phase-2 rebuild / alternative was keeping the cut list /
    nothing is cut for time under the journal bar; order-invariance (A3) and
    the chrono-vs-random delta become first-class findings.
31. Su-2025 citation quarantined: chose "verification pending, do not cite"
    flag / alternative was citing the web-search description / I have not
    seen a DOI or arXiv page; Phase-1 step 6 verifies or the claim is narrowed.
32. Phase-1 arXiv-API pass (5 exact queries, real counts): chose protocol
    table entries 11-16 with verbatim hit counts / alternative was reusing the
    2026-09-24 top-10 proxy / the protocol demands database runs; arXiv API
    is directly queryable so no excuse for proxying it. Scholar/Xplore/Scopus
    logged as outstanding manual debt (paywall/CAPTCHA), owned by student.
33. arXiv:2608.04602 VERIFIED as real entry (Azizi Ariffin et al., cs.CR,
    2026-08-05): chose anchor H1 on the abstract's own numbers / alternative
    was trusting repo lore / abstract confirms CII scenario, 0.0053 collapse
    at 1% flip, 0.97/95% backdoor, CICIDS2017, and baseline ladder
    (finetune 0.0052 / EWC 0.0324 / LwF 0.0699 / iCaRL 0.8770) — the
    protocol-comparison story for H1 now cites a checked source.
34. Su 2025 VERIFIED at content level (Junyan Su, indexed record quoting the
    honest-clients/IID assumptions + poisoning/non-IID future-work call):
    chose content-verified-but-publisher-page-outstanding status / alternative
    was full citation or full quarantine / the quoted limitations text matches
    our gap claim exactly; citing awaits the publisher page at write-up.
35. Headline locked per positioning memo: federated poisoning+Byzantine x
    FCIL x method comparison / alternative was discovery-stage or
    defense-confusion headlines / two independent verified future-work calls
    (Su 2025, EdgeFedCIL S3.1) name exactly this; adjacent FL-IDS poisoning
    is uniformly static; discovery effects are n.s.-adjacent. Secondaries:
    defense-confusion (A), discovery-stage (B).
36. n=12 seeds (1-11 + 42) for all new runs: chose 12 / alternative was
    staying at 7 or jumping to 20 / a priori: exact Wilcoxon min-p at n=7
    (0.0156) CANNOT survive Holm in any family with m>=2 (demonstrated:
    f4 EWC raw 0.0156 -> Holm 0.0938); n=12 min-p 0.00049 survives m~100;
    post-hoc: bootstrap CIs already resolve effects continuously; locked 7
    contained so locked-seed pairings stay valid subsets. rf group stays n=7
    (paired against locked secondaries only).
37. Chrono = per-class 70/30 by flow_order, sampling unchanged: chose this /
    alternative was global 70/30 cut or re-sampling benign / per-class keeps
    test coverage for rare classes (no singletons found) and isolates the
    split effect (same rows as random, only assignment differs); sampling
    unchanged for the same reason. flow_order = raw-file rank (no Timestamp
    in ML-CSV distribution — disclosed, not imputed).
38. Locked FedAvg path bit-identical: chose branch preservation / alternative
    was unifying on the delta path / float summation order differs between
    model-averaging and delta-averaging; locked F2/F4 numbers must never
    shift under a refactor. Robust rules use the delta path (new configs only).
39. LIE = white-box vs benign updates (strong adversary): chose strongest
    variant / alternative was black-box LIE estimate / conservative FOR the
    defense: if robust aggregators hold against white-box LIE, the claim is
    stronger; disclosed in code + paper.
40. Robust rules unweighted (Krum/median/trimmed): chose literature-standard /
    alternative was sample-count-weighted variants / weighting would be a
    novel rule needing its own validation; standard rules keep comparisons
    checkable. dynamic_trust named exactly as what it is (FedRDF-style,
    not FedRDF-proper).
41. EWC-immunity mechanism registered with P1 lambda-sweep test (l0/l1000):
    chose argument-plus-prediction / alternative was curves-only story /
    a journal expects explanation; P1 failure rewrites the note instead of
    being patched. Rounds-sweep (P2) only if P1 inconclusive.
42. Grounded trigger = 3xSYN/window-29200/40B via hping3-or-Scapy: chose
    legal-observable values / alternative was keeping feature-space trigger
    as sole result / every value maps to a documented generatable packet;
    feature-space trigger kept ONLY as realism comparison (E3).
43. UNSW mirror files swapped (their test.csv = canonical 175k train):
    chose 175k-pool-train / 82k-pool-test / alternative was trusting filenames
    / row counts + Moustafa-Slay proportions prove the swap; canonical split
    preserved, never re-split. Normal sliced disjointly across 4 tasks (CII
    spirit); one-hot categories fit on train pool only.
44. UNSW replication scope = E1 + F2 (flip, explicit target Normal=7) + F4:
    chose bounded scope / alternative was full-suite incl. backdoor/novelty /
    E3/E4 code hardcodes CICIDS label names and feature names; generalizing
    is a separate code task, conditional on the F2 replication outcome.
    F2 source class = DoS-in-T2 (mirrors Hulk-in-T2 position).
45. CICIoT2023 = seed-fixed subsample (3k/1k per fine Label, 8k benign per
    task): chose subsampled replication at CICIDS scale / alternative was
    full 8M-row files on laptop CPU or dropping dataset #3 / caps land each
    task at 20-38k train rows (ours: ~180k total) so CPU runs stay minutes;
    every cap recorded in data/processed/tasks_iot.json; GPU full-scale
    logged as follow-up, not a blocker.
46. E8 supersedes E7 numbers with stated method: chose recompute-all-archs /
    alternative was quoting legacy E7 (19,087 params, 0.19ms) / E8 analytic
    count gives 19,343 for the same MLP (legacy figure unexplained, likely
    different in_dim); a stated method beats an inherited number. Paper
    cites E8 + platform block, never bare latency.
47. Zenodo upload = student-owned at submission time: chose prep-file over
    uploading now / alternative was minting DOI mid-project / record must
    match the submission tag; prep file makes it one command later.
48. A2 class-IL was silently identical to CII (identical ACC to 6 dp):
    chose build a true CI task file (tasks_chrono_ci.npz) + archive the 24
    wrong result files to results_prefix0/a2_bugfix/ / alternative was
    leaving the run / load_or_build_tasks' filter_ci only drops UNSEEN
    labels, and CII task t already contains only seen labels, so the filter
    is a no-op; class-IL means benign ABSENT from later tasks, which is a
    sequence-build property. Bug found by exact-ACC collision, not guessed.
49. Phase-2 overturns three locked claims (honest reporting, n=12):
    (a) LwF's 0.575 top rank was a per-task-scaler ARTIFACT — under frozen
    scaler LwF 0.511 vs ER 0.533 (r=-1.00, p=0.0156); joint also drops
    0.968->0.930; (b) federation no longer hurts finetune (0.470 vs 0.511,
    p=0.569 n.s.) — the old p=0.031 was a per-task-scaler/split artifact;
    (c) clean chrono single-node: all CL methods ~0.51, mutually
    indistinguishable (p=0.11-0.47), joint 0.907 p=0.0005 (Holm 0.0063).
    Consequence: the method-ranking story is REPLACED by the protocol
    story + whatever survives under the corrected protocol; old numbers
    stay archived, never cited.
50. Order-dependence is real and large (A3, n=12): default 0.514 vs alt
    0.455 vs reverse 0.448, p=0.0005 (Holm 0.0015, r=-1.00). Reported as
    a first-class finding per instruction 11 — the single-node headline is
    order-SENSITIVE, so the paper must report order-conditioned results
    rather than one ordering.
51. Growing head beats pre-sized (0.535 vs 0.511, p=0.0005, Holm 0.0005):
    chose report BOTH (this ablation + pre-sized everywhere) / alternative
    was silently switching to the better arm / decided by the data, but
    transparently: the head strategy is now a named ablation with the
    pre-sized default retained for comparability with prior CL work.
52. Thread pinning is now part of the reproduction contract
    (CL_THREADS=2 + limit_threads() in run_experiment + n_jobs=1 in the two
    kNN filters): chose pinning / alternative was leaving defaults /
    measured pathology: 5 concurrent workers x 8 default BLAS/torch threads
    on 8 cores -> one federated run took 4.3 h (vs 57-100 s capped) and all
    workers died with 0xC0000135/0x40010004. CAVEAT recorded honestly: the
    thread count changes float reduction order, so a run is bit-reproducible
    ONLY at the pinned value (f2_fed_finetune_p5_c seed7: 0.496423 at
    8 threads vs 0.5043 at 2). reproduce.sh and Dockerfile must export
    CL_THREADS=2; do not compare numbers across thread settings.
53. scripts/grid_status.py added (per-group/per-config completion vs target
    seeds): chose a status tool / alternative was eyeballing file counts /
    the last eyeball check missed that 5 groups had silently died.
54. Federated grid dispatch corrected (2026-09-27): chose one complete
    FED_GROUPS mapping plus a config/runner invariant / alternative was
    accepting the second, truncated FED_GROUPS assignment / it silently ran
    165 federated-config seeds through the single-node path (45 Byzantine,
    96 UNSW F2, 24 persistent federated). Archived all 165 summaries and
    R matrices with SHA-256 manifest in results_prefix0/dispatch_bug_20260927/;
    rerun on the federated path before interpreting these groups. No archived
    result is evidence for a federated claim.
55. Architecture sweep execution: chose a self-contained Colab GPU bundle,
    resumable notebook, and validated import / alternative was waiting for
    144 CPU runs on the laptop / the task file and all 12 configs are packaged
    with SHA-256 hashes, GPU outputs remain separate until all seeds and
    config hashes pass import checks, and earlier CPU architecture results
    are archived before replacement. GPU-vs-CPU bit identity is not assumed.
56. Group-queue failure handling: chose fail-fast on a nonzero grid exit /
    alternative was continuing to later groups / continuing can hide a failed
    early group behind later DONE markers; the per-group exit remains logged.
57. Retired the provisional 10%-flip breaking-point story at n=12: chose
    paired-seed interpretation / alternative was extrapolating the partial
    grid / p10 vs p0 finetune is 0.471±0.098 vs 0.470±0.099 (Wilcoxon
    p=0.791, Holm=1.0), and the ≈0.195 collapse occurs at seed 11 in both
    arms. High seed variance remains for verification, not a poison claim.
58. Architecture GPU result placement (2026-09-27): chose raw Colab transfer
    archives under `artifacts/`, validated per-seed outputs under `results/`,
    and replaced CPU outputs under `results/_archive/architecture_cpu_pre_gpu/`
    / alternative was leaving the only ZIP in Downloads / this follows the
    repository's existing artifact and archive structure while keeping every
    replaced result recoverable.
59. 2026-09-28 result integrity: chose per-seed completion manifests with
    output, config, task, and task-sidecar hashes / alternative was treating
    a summary filename as complete / the old reporting path could write a
    partial seed then fail and the grid would skip it on retry. Historical
    unmanifested files remain executed-only, never validated by inference.
60. 2026-09-28 data audit: chose separate source-row and duplicate-content
    measures / alternative was calling every exact feature match a shared
    source row / UNSW/IoT train and test use separate positional-ID pools,
    whereas CICIDS legacy artifacts lack IDs. Friday has more than 26k
    exact test feature+label matches in each legacy variant; no independent
    generalization claim from those results until a sensitivity comparison.
61. 2026-09-28 CICIDS sensitivity: chose a distinct duplicate-disjoint
    protocol and config / alternative was silently replacing the primary
    tasks/results / global raw feature+label dedup removed 339,476 records
    and final-precision exclusion removed six more test matches. Three
    diagnostic finetune seeds ran separately; selected final comparisons
    still require 12 paired seeds. T0+T1 scaling remains named offline
    initialization, with a distinct T0-only frozen-scaler task artifact.
62. 2026-09-28 E3 repair: chose one task-sidecar-validated, raw-to-model-space
    trigger for training and evaluation plus class-eligible ASR / alternative
    was continuing the legacy E3 path / its training ignored the configured
    trigger, applied raw values to standardized inputs, and substituted all
    test rows when PortScan was absent. Archived 38 historical E3 seed files;
    reruns use the distinct duplicate-disjoint v2 task artifact. No backdoor
    effect claim survives until paired reruns. The packet recipe remains a
    feature-space approximation until the actual flow extractor verifies its
    output; the old hping3 payload option was inconsistent with a bare SYN.
63. 2026-09-28 E4 causal redesign: archived 157 historical E4/E5 files with
    checksums because held-out flows affected HDBSCAN and provisional labels
    were never used in classifier training. The new pipeline fits AE on a
    benign training subset, calibrates on separate benign training rows,
    clusters training candidates only, assigns held-out rows by a fixed
    nearest-centroid/radius rule, and trains on task-unique provisional class
    IDs. Added a matched direct-label-poison control. The HDBSCAN fit is
    capped at a seeded 4,000 training candidates; cap sensitivity is required
    before any headline. Chronological E4 configs now use duplicate-disjoint
    CICIDS tasks. Old absorption and ACC claims are invalid.
64. 2026-09-28 endpoint/provenance repair: FWT is recorded as null because
    no runner measures future-task accuracy before training or a baseline.
    New manifest version 3 hashes all runtime `src/*.py`, including dirty
    worktree contents, and rejects a seed if code changes during its run.
    Earlier manifest-v2 diagnostics are exploratory and explicitly marked
    `pre-code-hash`. One first-pass E4 no-poison diagnostic measured 122 s
    and 864 MB sampled peak RSS on this CPU host, but was archived before
    the v3 rerun because its source revision was not fingerprinted.
65. 2026-09-28 mistake-audit fix (undefined-metric): chose None/N/A for
    clean/joint ASR and E5 empty-denominator endpoints / alternative was
    leaving `0.0` / `src/runner.py` joint path and both runners' clean path
    reported `asr_mean=0.0` with no denominator, and `scripts/e5_evasion.py`
    reported `0.0` for absent attack/benign cohorts; `src/metrics.py` already
    returns None for unmeasured FWT/ASR and `stats_summary.py` renders None
    as blank, so 0.0 was the exact bug class under audit. Verified by
    `tests/test_backdoor.py` + `tests/test_discovery.py` (9 passed) and
    `results/diagnostics/runs/e1_finetune_dedup_summary_seed1.json` showing
    the stale `0.0` pattern.
66. 2026-09-28 mistake-audit fix (buffer-poison target): chose
    `resolve_class_id` in `src/runner.py::poison_buffer` / alternative was
    `label_map.get` / the old lookup returns None for numeric ids (keys are
    names), silently degrading targeted buffer flips to random; stream path
    already validated via `resolve_class_id`. Verified: numeric source 1
    flips 1->0 correctly after fix.
67. 2026-09-28 mistake-audit scope note: `results/diagnostics/` e1_dedup/t0
    summaries carry manifest v2 (`pre-code-hash`) with stale `fwt=0.0`; chose
    to leave files untouched and mark them exploratory / alternative was
    rewriting diagnostics as validated / they predate manifest v3 and the
    12-seed standard, so `docs/inventory.md` "validated" wording for those
    six seeds is overstated until v3 reruns.
68. 2026-09-28 E4 provenance reconciliation: live manifest checks found that
    the nine E4 diagnostics recorded source hash `b8081e8…`, whereas current
    `src` hashed to `94abb157…` after the ASR-null and buffer-poison fixes.
    Archived 37 affected run/log/resource/descriptive files under
    `results/_archive/discovery_pre_commit_asr_20260928/` with SHA-256 hashes.
    Re-ran all nine seeds under current commit `a4558b5` and source hash
    `94abb157…`; all nine now pass live `check_artifact`, and the descriptive
    means match the archived diagnostics. This establishes reproducible
    exploratory diagnostics, not a final effect or a completed Holm family.
69. 2026-09-28 E4 detector/cap decision: chose keep q0.95 primary, E4 stays
    exploratory, no 12-seed headline / alternative was retuning to q0.50 or
    claiming a poison effect from 3 seeds / T1 AUC is 0.120-0.128 (inverted:
    5/2,745 flagged per seed) and 5,000-vs-4,000 cap ARI is 0.628-0.728 on
    all three seeds (`docs/e4_detector_cap_audit.md`); post-hoc retuning
    after seeing outcomes would manufacture significance against the plan's
    failed-attack rule. Gates before any headline: family-level T1 analysis,
    separately specified detector protocol, larger cap reference plus
    downstream sensitivity.
70. 2026-09-28 E3 extractor check: chose blocked-locally, trigger stays a
    feature-space approximation / alternative was claiming groundedness from
    the header-range check / `data/raw/` holds only two Friday flow CSVs, no
    pcaps, no CICFlowMeter, and scapy is not installed, so nothing here can
    prove the extractor emits the three claimed feature values. Resumable
    extractor commands are documented in `docs/e3_extractor_check.md`; E3
    diagnostics stay gated on that measurement.
71. 2026-09-28 pre-Phase-D preservation: chose copy-preserve 39 live E4 files
    to `results/_archive/discovery_prefedcontrols_20260928/` with SHA-256
    manifest before any `src/` edit / alternative was moving them / the live
    set stays checkable against `94abb157...` until the edit lands, and the
    runtime snapshot zip was hash-verified; the archive is the fallback
    record once the fingerprint changes.
72. 2026-09-28 Phase-D federated controls: chose additive per-client logging
    plus active-only unweighted aggregation / alternative was changing
    aggregation semantics or the locked FedAvg path / `run_federated` now
    records pre/post-defense counts, class mix, participation, optimizer
    steps, buffer occupancy/bytes, and comm bytes per client-task, and
    excludes inactive (empty-shard) submissions from trimmed/median/krum/
    multi-krum/dynamic-trust with the exclusion recorded; plain-FedAvg
    weighted averaging is byte-unchanged. `DynamicTrust.__call__` gained an
    optional index map (identical behavior when absent). Verified by 4 new
    synthetic tests in `tests/test_fedcontrols.py`; full suite 28 passed,
    fatal Ruff selection passes, new code adds zero lint issues. Matched
    same-aggregator clean controls and multi-round sensitivity are still
    pending and stay gated in `docs/analysis_spec.json`.
73. 2026-09-28 Phase-E analysis spec: chose generated
    `docs/analysis_spec.json` (27 families, 200 pairs) from
    `WILCOXON_FAMILIES` + group seed protocol / alternative was a hand-written
    list / generation cannot peek at outcomes and stays consistent with the
    stats code by construction. Two-sided Wilcoxon, Holm-within-family,
    prespecified MIDs (0.02 headline, 0.01 ablation, reviewable), gates:
    105 ready-pending-runs, 42 gated-controls, 46 gated-dedup, 6
    gated-detector, 1 gated-extractor. No run may be cited against this spec
    until its gate clears and its 12 (or 7) paired seeds complete.
74. 2026-09-28 reverse-order benign duplication: chose disjoint Monday-benign
    draws via consumed-id tracking + archived 24 `a3_order_rev_c` files /
    alternative was leaving the builder / same-seed sampling of the shared
    Monday pool handed identical benign rows to every task when Monday was
    not first (verified: 10/10 shared in reverse, 0 in default/alt), a
    cross-task train/test contamination in the order-invariance arm. Alt arm
    verified clean and kept. Builder fix proven disjoint and deterministic
    on synthetic pools (`tests/test_data_tasks.py`); `a3_order_rev_c` gated
    as `gated-rev-rebuild` in the regenerated spec. Also hardened the
    empty-task skip (an emptied Monday task crashed the splitter).
75. 2026-09-28 flip-ASR eval consistency: chose score the train-time flipped
    class and carry it in ASR rows / alternative was test-majority scoring /
    persistent-mode eval re-resolved the majority on TEST, which can differ
    from the TRAIN majority actually flipped, and numeric source ids passed
    validation yet scored silent N/A. Single-node reuses `asr_meta`
    source (fallback: pooled train majority); federated uses pooled task
    train majority with per-shard sources already in poison rows; all
    targeted branches resolve names and ids identically to poison time.
    Proven by `tests/test_flip_asr.py` (train/test-majority mismatch,
    numeric source). Joint summaries now carry machine-readable
    `joint_oracle` (True only for the single-node all-at-once path).
76. 2026-09-28 notebook bundle-name restore + aggregation testability: chose
    to restore `architecture_colab_bundle_v2.zip` in the notebook /
    alternative was amending the test / the producer script still writes the
    v2 name, so the notebook dirt (not the test) was inconsistent; the
    removed unused import was left out. Also extracted federated aggregation
    into testable `_aggregate_updates` (locked path byte-identical) with
    direct unit tests for degenerate/inactive-exclusion behavior that no
    public run can reach (dirichlet covers the pool; filters keep >=1 row),
    plus a buffer-target persist-and-validate test proving new summary shapes
    survive `save_results` JSON. Suite now 36 collected, all passing.
77. 2026-09-28 claim ledger + plan typo: chose `docs/claim_ledger.md`
    tracing every README/proposal/overview/memo/draft statement to evidence /
    alternative was leaving prose claims unlinked / plan §10 requires it.
    Findings: aggregates are 0-row and `results/runs/` has 0 manifests, so
    all numeric results (including the PHASE-2 n=12 tables) are
    executed-only; README status (2026-09-25) is stale on E2/E6/Wilcoxon/E4;
    abstract PENDING slots are correct as-is. Also removed a stray "ss" typo
    in `docs/plan.md` (restored to HEAD text).
78. 2026-09-28 v2 artifact reproduction: chose temp rebuild + array compare /
    alternative was trusting builder-version notes / both checked-in v2
    artifacts (`tasks_chrono_dedup`, `tasks_chrono_t0`) reproduce
    bit-identically (all 30 + 30 arrays incl. ids) under the fixed builder,
    proving the Monday-disjoint fix changed nothing for monday-first orders
    and reproducing the 339,476/6 dedup counts. Rebuild outputs stayed in
    system temp, never in `data/processed/`.
79. 2026-09-28 round-sensitivity probe (synthetic, ER, 5 clients): steps 11
    vs 33 (exact 3x), comm 381,520 bytes both arms, buffer capped at 64,
    participation 1.00 / reported as accounting validation, never paper
    evidence / a same-seed 12-run study with work-matched multi-round arms
    remains the gated Phase-D experiment.
80. 2026-09-28 inference contract: chose `src/inference.py` (versioned
    bundle + per-tensor weight hashes, strict schema, median imputation with
    counts, batch bound, explicit abstain threshold, latency metrics) /
    alternative was extending the random-model E8 proxy / E8 never loads a
    trained checkpoint, so no inference claim could attach to it. Corrupt
    files fail closed as ValueError; tampered weights trip the hash gate
    (both observed in tests). 4 tests in `tests/test_inference.py`; suite
    40 passing. Trained-bundle benchmark on real dims still pending.
81. 2026-09-28 IoT chunk-accumulation fix: chose periodic per-group
    consolidation every 20 batches / alternative was accepting 11.3 GB peak /
    per-batch RSS bisect proved ~10k few-row chunks (~1 MB overhead each)
    accumulated monotonically; fix bounds live chunks with identical row
    content and order. Measured: 11,340 → 3,108 MB peak, 122.7 → 107.1 s,
    rebuilt artifact bit-identical (all arrays). Corrected four
    "parquets absent" notes (both IoT pools were present all along).
    Proven by `test_pool_sample_consolidation_preserves_content`.
82. 2026-09-28 T1 family audit: per-family medians + one-vs-benign AUCs,
    seeds 1–3 (`docs/e4_family_analysis.md`, `scripts/audit_family_scores.py`).
    Both T1 families invert every seed (SSH-Patator AUC 0.038–0.060,
    FTP-Patator 0.164–0.168); Bot inverts harder (0.006 all seeds);
    PortScan is chance; T2 detects well. Small-n AUCs (3/6/11) reported
    but barred from citation. Post hoc, exploratory; q0.95 unchanged.
83. 2026-09-28 E8 dims fix: hardcoded `(78, 15)` described a model matching
    no artifact (real: 76 features) / dims now read from the primary task
    sidecar with fallback; added `--output`/`--tasks` args. Temp run gives
    mlp 19,087 params — exactly the documented E7 figure — confirming the
    hardcode was drift. Latency remains host-specific proxy.
84. 2026-09-28 lint safe pass: 79 → 30 errors via behavior-preserving fixes
    only (`int(round())` identity, unused imports/vars, f-strings, import
    sort, `ewc` items loop, sequence single-if); untouched: exception-type
    changes (would break tests), blind-except style (repo convention),
    subprocess-check semantics, structural shadowing. Suite re-verified
    green after. Generator-determinism tests added (`test_determinism.py`):
    spec and bundle inventory regenerate byte-identically modulo timestamps.
85. 2026-09-28 cleaner wipe-guard: string metadata in DROP_COLS now raises
    instead of coercing to NaN and emptying the file (proven: synthetic
    hostile frame raised, numeric frame 2/2 survived); empty output raises.
    First attempt (drop-metadata-first) was REVERTED after a temp rebuild
    showed 2.31M vs 2.57M rows — dedup ran before the metadata drop in the
    audited build, so reordering silently redefined duplicates. Final guards
    proven byte-identical on the full 2.57M-row rebuild (report + parquet).
86. 2026-09-28 fail-closed contracts (SUPERSEDED same day by #87–#88 —
    kept as a pointer, not evidence): this entry's CI-guard, arch-validation,
    and figure-gating claims were re-landed with extensions (novelty+defense
    and keep_ratio/k rules, grid failure accounting, CWD fixes, skipped-seed
    reporting) in #87 and #88. Cite #87/#88, never this entry.
87. 2026-09-28 fail-closed contracts round 2: `load_or_build_tasks` rejects
    benign-after-T0 under scenario "ci" (the exact A2 silent-identical
    class); `validate_config` checks arch/hidden/transformer,
    novelty+defense incompatibility, defense keep_ratio/k ranges (214/214
    still pass). `run_grid` records per-seed failures with tracebacks and
    exits nonzero instead of aborting unattended grids. Proven by new tests
    in `test_data_tasks.py`, `test_backdoor.py`, `test_run_grid.py`.
88. 2026-09-28 figure + script-CWD hardening: `make_figures.py` plots only
    manifest-validated R matrices, fails loudly on missing E5 outputs,
    prefers cpu on device-duplicate stats rows, reports only files it
    actually rewrote (12/12 skip cleanly on empty aggregates), and imports
    off-root. `summarize/compare/audit/run` E4 scripts fixed for the same
    CWD-dependence class (proven by `tests/test_script_cwd.py` from a
    foreign directory); E4 summarizer additionally reports skipped seeds
    instead of silently omitting them.
89. 2026-09-28 GPU import version gate: `import_architecture_gpu` demanded
    manifest v2 while the pipeline now emits v3, so the next Colab export
    would have been unimportable / v2 stays the cross-machine format
    (`pre-code-hash` on import, honestly labeled); v3 additionally accepted
    only when its tree matches this machine (same-machine CUDA), foreign v3
    rejected rather than silently downgraded. Factored into tested
    `check_completion_manifest` (`tests/test_gpu_import.py`, 3 tests).
    Full v3 cross-machine provenance awaits the GPU-protocol redesign.
90. 2026-09-28 minor hardening without behavior change: downloader creates
    `data/raw` in `main()`, not at import (proven by
    `tests/test_download.py` under a fake root); removed stray untracked
    `cl-ids-adversarial/docs/threat_model.md` (old Gap-2 framing, fully
    superseded by locked root `docs/threat_model.md`, nothing unique);
    transformer docstring corrected (squeeze, not mean pool — single-token
    claim verified in code); UNSW `seed` documented as provenance-only.
    Reviewed clean: LwF slicing, EWC, replay determinism, byzantine math,
    run_experiment wiring, paths/models, defenses, grid dispatch.
91. 2026-09-28 comparison-name resolution hardening: a renamed config would
    have silently dropped its prespecified pairs (empty seed maps hit
    `continue`; the spec generator defaulted unknown names to 7 seeds) /
    `write_analysis_spec.py` now raises on unknown pair names and duplicate
    display names (verified: 214 unique, all 200 pairs resolve); `stats_summary.py`
    prints an explicit WARNING per orphaned comparison name (verified: none
    on empty aggregates).
92. 2026-09-28 EWC analytic characterization (no behavior change):
    `tests/test_ewc_semantics.py` proves anchor==post-task weights, Fisher
    non-negative and accumulating across tasks, extra_loss == closed-form
    (λ/2)ΣF(θ−θ*)² (zero at anchor, positive after perturbation), and no
    crash across head growth. Federated anchor-reset semantics and prose
    single-token rename stay pending; paper prose contains no attention
    claims needing the qualifier yet.
93. 2026-09-28 stats-math audit (no behavior change): Holm step-down with
    monotonicity, Kerby rank-biserial, percentile bootstrap, and sample-std
    formulas verified by reading against definitions; dead duplicate
    `wilcoxon_pair` removed (unreferenced; divergent zero-handling was a
    trap for future callers). n=1 std renders ±0.0000 with visible n and
    blank CI — left as-is, documented here.
94. 2026-09-28 build/CI reproducibility: `pytest==9.1.1`/`ruff==0.16.9`
    pinned (tested versions); Makefile `lint` aligned to the gated fatal
    selection with `lint-strict` kept informational (was red); CI runs the
    lint gate (previously absent). `run_groups.py` records group failures
    and continues the queue with nonzero exit instead of aborting
    unattended runs; `snapshot_runtime.py` fixed for off-root invocation.
    Proven by `tests/test_run_groups.py` and the extended CWD entry-point
    test.
95. 2026-09-28 stale-figure archival + quarantine hygiene: 7 tracked
    `results/figures/*.png` renders from unmanifested n=7-era runs archived
    to `results/_archive/figures_prevalidation_20260928/` with manifest
    (E4/E5-figure precedent); `make_figures.py` re-verified 12/12 skip on
    empty aggregates. Reverted `ruff --fix` churn on frozen
    `scripts/archive/run_remaining.py` and excluded `scripts/archive/` from
    lint so future rule changes can't rewrite provenance. Aligned
    `pyproject` dev pins with `requirements.txt` (`pytest==9.1.1`,
    `ruff==0.16.9`).
96. 2026-09-28 stable-partition variant: `stable_partition` assigns by
    splitmix64 of source ids (same row, same client, every task/rerun;
    approximately IID by design, never a non-IID control) / alternative was
    seed-fixed Dirichlet reuse (fragile across label sets) / wired as
    `fed.partition` (default dirichlet, zero behavior change) with
    validation, `fed.partition` in summaries, and an explicit error on
    id-less legacy tasks. Proven by 4 tests (coverage/disjoint/determinism,
    shared-id stability, end-to-end, rejection).
97. 2026-09-28 multi-round federation: `fed.rounds` (default 1) repeats
    broadcast→train→aggregate with poison/defense applied once per task /
    alternative was restructuring the shared loop (would reorder RNG draws
    and shift legacy numbers) / rounds==1 runs the legacy inline path
    untouched (move proven whitespace-only vs HEAD by script); rounds>1
    records per-round work in `fed_round_rows` with dose rows unchanged in
    schema. Caught in testing: per-submission comm is constant, so totals
    scale by participation, not blindly by R — dose rows now sum round rows.
    Proven by matched-work tests (steps/comm exactly 2x on 2 rounds).
98. 2026-09-28 trained-bundle benchmark + rollback: `scripts/bench_trained_bundle.py`
    trains T0 MLP (76 feats, 19,087 params — matches E7), exports via the
    inference contract, and records host latency/throughput/RSS to
    `results/diagnostics/` (exploratory); `save_versioned_bundle` /
    `rollback` add hash-chained versioning with fail-closed restores. The
    T0 sanity ACC 1.0 is vacuous (benign-only task) and labeled as such.
99. 2026-09-28 audit-rendering honesty + archive crash-safety: the task
    audit rendered separate-pool source overlap as 0 ("verified disjoint"
    misreading) — now `n/a (separate pools)` with content matches kept
    visible (re-ran: 0 hard failures, UNSW/IoT counts unchanged).
    `archive_artifacts.py` factored into testable `move_verified` /
    `write_manifest`; a mid-move crash now leaves a `complete: false`
    manifest describing exactly what landed (proven by flaky-move test),
    and the bundle inventory surfaces incomplete archives.
100. 2026-09-28 Colab notebook output completeness: the GPU notebook copied
    only R/summary to Drive (no per-seed manifests), resumed on an
    unchecked `runtime_device` flag, and omitted the `source_commit` its
    importer requires — the next Colab export would have been unimportable /
    cells now copy manifests, resume through manifest validation, and record
    `source_commit` in `run_manifest.json`. All code cells compile; extended
    the notebook regression test. v3 cross-machine tree mismatch stays an
    honest documented limit, not a silent one.
101. 2026-09-28 reproducibility + anchor characterization: rerun-identity
    tests prove same code+seed+process gives bit-identical R and summaries
    (federated + single-node). A federated EWC smoke run exercises the
    post-aggregation anchor-reset lines; anchor==local solution and Fisher
    estimated on it is coherent (matches single-node semantics), so no
    behavior change — the open item stays the cross-condition comparison,
    not the mechanism.
102. 2026-09-28 cross-process determinism: same config+seed in two CLI
    processes and result dirs gives byte-identical R files, equal summaries
    modulo wall time, and equal matrix hashes / proven by
    `test_cli_rerun_across_processes_is_bit_identical`, which also pins
    JSON type stability across runs (int-vs-float would diverge in bytes
    while comparing equal as values). Manifest summary hashes legitimately
    differ by embedded wall time — asserted, not hidden.
103. 2026-09-28 verification sweep (no behavior change): every cited number
    re-checked against its source JSON (descriptive means, cap ARIs,
    score AUCs, resource probes — all match); tracked-file secret scan
    (AWS/key/bearer/connection patterns) finds nothing; randomized
    invariant tests added for both partitioners, overlap counting, and
    dedup idempotence (`tests/test_invariants.py`).
104. 2026-09-28 replay/kNN profiling verdict (no code change): cProfile
    shows buffer ops at ~3 ms/observe at buffer 4000 (~10% of observe;
    model compute dominates), so the planned reservoir rewrite is
    declined — the premise fails measurement. kNN is time-quadratic
    (~190 s projected at 139k rows) but memory-flat (few MB). Fixed two
    stale `results/README.md` lines instead (E4 live-hash claim expired
    with later `src/` edits; layout listed a nonexistent e7 file).
105. 2026-09-28 matched sensitivity configs (unrun): new group `c_f2x`
    (12 seeds) with `f2_fed_finetune_p0_dedup_c` (resampled baseline),
    `f2_fed_finetune_p0_stable_c` (stable partition), and
    `f2_fed_finetune_p0_r2_c` (2 rounds) — all on the v2 dedup artifact,
    since stable partitioning needs source ids that legacy tasks lack.
    All 217 configs validate; `grid_status c_f2x` reads 0/36 TODO. No
    spec family yet (prespecified-comparison step) and no runs launched.
