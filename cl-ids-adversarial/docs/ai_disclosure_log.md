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

For the paper: adapt the above into the venue's GenAI-disclosure paragraph;
AISec 2026+ explicitly values this transparency.
