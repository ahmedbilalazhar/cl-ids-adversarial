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
