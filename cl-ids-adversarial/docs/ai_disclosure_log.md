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

For the paper: adapt the above into the venue's GenAI-disclosure paragraph;
Computers & Security follows Elsevier's GenAI policy (declare tools used,
human responsibility for content).
