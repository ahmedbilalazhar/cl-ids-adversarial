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