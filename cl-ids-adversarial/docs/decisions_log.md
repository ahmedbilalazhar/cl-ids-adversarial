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