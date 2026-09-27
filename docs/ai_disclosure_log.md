# Generative-AI disclosure log (per claude's plan.txt §"How to actually work
with the LLM" — the running log of generated-vs-verified)

Honesty note: entries before 2026-09-25 are reconstructed from repo state,
not witnessed; anything reconstructed is marked (reconstructed).

- Pre-Phase-0 (reconstructed): most code in `src/` + configs written by an AI
  coding agent without line-by-line human verification. No surviving log of
  which lines were human-written.
- 2026-09-25 Phase 0 audit: every file in `src/data/clean.py`,
  `src/data/sequence.py`, `src/cl/`, `src/attacks/`, `src/defenses/`,
  `src/discovery/pipeline.py`, `src/run_experiment.py` and every config was
  read and numerically checked; three bugs fixed with before/after numeric
  verification (Thursday label coverage, EWC Fisher, LwF KL width).
  Fixes are AI-written, human-specification-driven, numerically verified.
- Gates A–D + Phases 1–6 (this log, witnessed): `src/federated/` (new),
  all `f2_*`/`f4_*` configs, `scripts/run_grid.py`, Gate-D script rules —
  AI-written to specification, verified by smoke runs, 1-client equivalence
  test (0.317 vs single-node 0.2817 range), and full n=7 grids. All п-values
  recomputed from checked-in result JSONs by `scripts/stats_summary.py`.
- Human-owned (not AI-generated): research questions, locked claims, venue
  strategy, all go/no-go and scoping decisions, the eventual paper prose
  argument and interpretation (per plan: "write the actual argument and
  interpretation yourself").
- 2026-09-26 Phase 0 journal track (witnessed): `fit_scaler_frozen` in
  `src/data/sequence.py`, `configs/e1_finetune_frozen.yaml`, `scaler_abl`
  group in `scripts/run_grid.py`, scaler WILCOXON_PAIR, `data/processed/
  tasks_frozen.npz` — AI-written to specification, verified by finite-value
  check + identical task sizes/labels vs `tasks.npz` + full n=7 grid.
  proposal.md §2/§3/§4/§6–§11 rewrites and threat_model.md rewrite —
  AI-drafted, human-decision-driven (journal pick, H-verdicts, primary/
  secondary framings are supervisor/student decisions); every number
  re-checked against `results/wilcoxon.csv` + `results/stats_summary.csv`.
  Journal-scope evidence: web-surveyed 2026-09-26 (Lavaur C&S 2025,
  Mao IoT-J 2024, FedSecure 2026, WeiDetect 2025, JKSU-CIS 2026, SSF
  INFOCOM 2025);   TOPS/JNCA queries rate-limited on first pass — re-run
  logged as outstanding, journal pick does not depend on them.
- 2026-09-26 Phase 1 (witnessed): 5 arXiv-API queries run directly by the
  agent (URLs + hit counts in search_protocol.md #11–16); neighbour
  descriptions for 2608.04602/Su-2025/Korba/BRFID verified against API
  records or indexed full text, NOT invented; Scholar/Xplore/Scopus rows
  honestly marked proxy/outstanding. positioning_memo.md AI-drafted from
  the verified landscape; the headline LOCK is a human decision.
- 2026-09-26 Phase 2 (witnessed): flow_order emission (clean.py),
  chrono-split + frozen-scaler options (sequence.py), WILCOXON_FAMILIES +
  Holm + rank-biserial + bootstrap (stats_summary.py), grow_head flag
  (run_experiment.py), 54 generated configs — AI-written, verified by
  row-count identity (2,572,640), chrono-ordering proof, locked-row exact
  reproduction, and seed-42 smoke R-matrices. Power/seed analysis is
  agent-computed, human-decision-locked (n=12).
- 2026-09-26 Phase 3 code (witnessed): src/attacks/byzantine.py,
  src/federated/robust.py, persistent/adaptive flip modes,
  GROUNDED_TRIGGER + scripts/gen_grounded_trigger.py,
  src/models/tabular_attention.py + build_model factory, fedavg.py
  aggregator/update_attack/malicious_ids wiring — AI-written, verified by
  exact-formula probes (LIE == mean-z·std; sign-flip negation; Krum-member
  property; outlier-resistance magnitudes) + interface parity probes.
  docs/ewc_immunity_note.md AI-drafted; P1/P2 predictions are locked test
  criteria, not claims.
- 2026-09-26 Phase 4 code (witnessed): src/data/unsw.py, src/data/iot.py,
  UNSW/IoT task files — AI-written, verified by canonical count match
  (175,341/82,332), schema parity with tasks.npz, finite-value asserts, and
  a seed-1 ER smoke run (UNSW acc 0.5296, sane R-matrix). Mirror-swap
  finding (filenames vs canonical sizes) verified from the CSVs themselves.
- 2026-09-26 Phase 5/6 (witnessed): scripts/e8_deployment.py, Dockerfile,
  scripts/reproduce.sh, docs/zenodo_prep.md — AI-written; E8 executed on
  the laptop (numbers + platform block in results/e8_deployment.json).

- 2026-09-27 infra hardening (witnessed): `src/cl/base.py::limit_threads`,
  `n_jobs=1` in `src/defenses/consistency.py` + `src/attacks/flip.py`,
  `CL_THREADS` exports in `scripts/run_groups.py` / `reproduce.sh` /
  `Dockerfile`, `scripts/grid_status.py`, `scripts/run_groups.py`,
  `docs/HANDOVER.md` — AI-written; thread cap verified by timing (57 s capped
  vs 4.3 h thrashing) and a reproducibility caveat measured and logged
  (0.496423 @8 threads vs 0.5043 @2). HANDOVER.md drafted by the agent; the
  scientific judgements it records (which claims survived, which priority
  order) were derived from the checked-in result files, not invented.
- 2026-09-27 dispatch audit (witnessed): AI identified duplicate
  `FED_GROUPS` assignments in `scripts/run_grid.py`, checked all 209 grid
  configs against their runner, then checked every federated result for the
  wrapper's `fed` metadata. The 165 mismatched runs were archived with their
  task matrices and SHA-256 hashes, not deleted. AI fixed the mapping, added
  a fail-fast invariant, and restarted affected groups; scientific claims
  from these groups remain pending corrected reruns.
- 2026-09-27 architecture GPU handoff (witnessed): AI wrote the bundle
  builder, Colab notebook, and GPU-result importer; it verified Python and
  notebook syntax and generated the 28.7 MB bundle. The owner executed all 144
  experiments on a Colab T4 GPU and returned the archive. AI validated the
  manifest, seeds, config hashes, task hash, CUDA provenance, and exact file
  set; imported the outputs; archived the replaced CPU run; and regenerated
  the aggregate table, statistics, and architecture figure.
- 2026-09-27 n=12 finetune recheck (witnessed): AI paired p0/p10 by seed,
  regenerated `stats_summary.csv` and `wilcoxon.csv` from the current result
  files, and corrected the earlier partial-grid breaking-point language.
  The low seed-11 ACC is shared by p0 and p10; no poison-specific collapse
  claim is retained. Broader grid and thread-provenance checks remain open.
