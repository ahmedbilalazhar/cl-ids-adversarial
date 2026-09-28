# HANDOVER — cl-ids-adversarial (paste this into the new chat)

> **2026-09-28 correction overrides the historical handover below.** Do not
> relaunch the old grid workers or use summary-file existence as completion.
> The main table has zero manifest-validated seeds after repair; old results
> remain executed-only or are hashed under `results/_archive/`. Three seeds
> each for `e1_finetune_dedup` and `e1_finetune_t0` are isolated diagnostics,
> separate from final comparisons.
> Read `docs/inventory.md`, `docs/invalidation_table.md`, and
> `docs/task_audit.md` before any new experiments. The remainder of this file
> is a historical 2026-09-27 snapshot, not current run instructions.

> **2026-09-27 repo reorg:** the `cl-ids-adversarial/` subdirectory was promoted
> to repo root and `results_prefix0/` moved to `results/_archive/prefix0/`.
> Read old `cl-ids-adversarial/...` paths below as repo-root-relative, and old
> `results_prefix0/...` as `results/_archive/prefix0/...`.

> **Continuation update, 2026-09-27:** Four 2-thread workers were restarted.
> A duplicate `FED_GROUPS` assignment was then found and fixed; 165 invalid
> single-node outputs under federated config names were archived, with hashes,
> in `results_prefix0/dispatch_bug_20260927/`. The affected groups were
> restarted through the federated runner. Check live processes and
> `results/run_groups.log` before launching anything else. A Colab GPU
> architecture notebook and a 28.7 MB upload bundle now exist (see §6).

**Repo:** `C:\Users\hp\Desktop\University\5. C Net\1. Project\cl-ids-adversarial`
**Date:** 2026-09-27 · **Phase:** 2 of 7 · **Grid completion:** run
`python scripts/grid_status.py` (the prior 953 count included 165 invalid runs).
**Source-of-truth docs:** `docs/decisions_log.md` (57 entries, newest last),
`docs/results_overview.md` (has a 2026-09-27 protocol-correction banner — READ IT),
`docs/ai_disclosure_log.md`, `docs/positioning_memo.md`, `docs/paper_draft.md`.

---

## 0. READ FIRST — the one thing that will waste your time if missed

**Grid workers were relaunched after this handover was first written.** First
check their current state:

```powershell
cd "C:\Users\hp\Desktop\University\5. C Net\1. Project\cl-ids-adversarial"
$env:CL_THREADS="2"                    # MANDATORY before any python run
python scripts/grid_status.py          # authoritative per-group completion
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
    Where-Object { $_.CommandLine -match 'run_(groups|grid)' } |
    Select-Object ProcessId,ParentProcessId,CommandLine
```

Only if no grid workers remain, relaunch workers (4 × 2 threads on 8 logical
cores; do NOT run 5):

```powershell
$env:CL_THREADS=2
Start-Process python -ArgumentList "scripts/run_groups.py","c_f2","c_f4" -WorkingDirectory $PWD -RedirectStandardOutput "$env:TEMP\w1.log" -RedirectStandardError "$env:TEMP\w1.err" -WindowStyle Hidden
Start-Process python -ArgumentList "scripts/run_groups.py","bz","f2r" -WorkingDirectory $PWD -RedirectStandardOutput "$env:TEMP\w2.log" -RedirectStandardError "$env:TEMP\w2.err" -WindowStyle Hidden
Start-Process python -ArgumentList "scripts/run_groups.py","u_f2","u_f4","i_e1","i_f2","i_f4" -WorkingDirectory $PWD -RedirectStandardOutput "$env:TEMP\w3.log" -RedirectStandardError "$env:TEMP\w3.err" -WindowStyle Hidden
Start-Process python -ArgumentList "scripts/run_groups.py","mech","brk","perst_fed","adapt","trig","c_e6a2" -WorkingDirectory $PWD -RedirectStandardOutput "$env:TEMP\w4.log" -RedirectStandardError "$env:TEMP\w4.err" -WindowStyle Hidden
```

Every grid is **skip-if-exists** per (config, seed) result file, so relaunching
is safe and resumes. `results/run_groups.log` appends `DONE <config> seed N`
lines and per-group `=== <group> exit=... min ===` markers — use it to verify
liveness (`Select-String -Path results/run_groups.log -Pattern "DONE " | Select -Last 3`).

---

## 1. Project objective and locked conventions

Goal: turn this repo into a **Q1 security/networking journal paper**
(target locked: **Elsevier Computers & Security**, full research article; AISec
workshop framing is void). Standing rules, all still binding:

- seeds ≥ 3 (current: **n=12** = seeds 1–11 + 42; legacy n=7 = 1–6, 42),
  mean ± std, **full task-accuracy matrices**, Wilcoxon + **Holm within named
  families** + bootstrap CIs + matched rank-biserial r, never report average
  accuracy alone, `N/A (undefined)` for undefined metrics, archive-never-delete.
- Every claim must trace to a number in `results/wilcoxon.csv` or
  `results/stats_summary.csv`.
- Every decision logged one-line (chose / alternative / why) in
  `docs/decisions_log.md`; every AI-vs-human boundary in
  `docs/ai_disclosure_log.md`, written as work happens, not batched.
- **Compute/calendar time are NOT constraints.** Never cut an experiment for
  time; deprioritise only if a result makes it unnecessary, logged as such.

## 2. What is DONE (do not redo)

| Phase | State | Notes |
|---|---|---|
| Reading/reconciliation of the 5 source files (Lit Review PDF, Paper-1/2/3 PDFs, `claude's plan.txt`) | done | findings folded into docs below |
| Phase 0 (venue lock, doc-truth fixes, scaler ablation, head resolution) | done | decisions #24–#31 |
| Phase 1 (arXiv-API novelty pass, neighbour verification, positioning memo) | done | #32–#35; **Scholar/Xplore/Scopus manual counts still outstanding (owner action)** |
| Phase 2 protocol code (chrono splits, frozen scaler, n=12, Holm/bootstrap/r families, grow_head flag, 54 configs) | done | #36–#38 |
| Phase 3 code (Byzantine attacks, 5 robust aggregators, persistent/adaptive/knn-adaptive flips, grounded trigger, transformer arch, EWC-immunity note, 70 configs) | done + numerically probed | #39–#42 |
| Phase 4 pipelines (UNSW builder+task file, CICIoT2023 builder+task file, 48 replication configs) | done | #43–#45 |
| Phase 5 (E8 deployment harness + laptop numbers) | done | #46; **Colab rerun = owner action** |
| Phase 6 (Dockerfile, `reproduce.sh`, Zenodo prep) | done | #47; **Zenodo upload = owner action** |
| Phase 7 (paper skeleton drafted, Results/Discussion placeholders) | partial | `docs/paper_draft.md` |

Completed corrected grids include `c_e1`, `c_e2e3`, `c_e4`, `c_a1`,
`c_a3`, `rf_e1`, `gh`, `perst_sn`, and `u_e1` (+ most legacy n=7 runs).
`c_f2`, `bz`, `u_f2`, and `mech` were advancing after the restart; `c_f4`,
`f2r`, `brk`, `perst_fed`, `adapt`, `trig`, `u_f4`, `i_e1`, `i_f2`, `i_f4`,
and corrected `a2_classil_c` are queued. The archived invalid runs do not
count toward grid completion; use `grid_status.py` for current counts.

## 3. The scientifically important part — Phase 2 overturned three locked claims

The corrected protocol (chronological per-class splits + frozen scaler fit on
T0/T1 train only + n=12) **reversed** earlier results. The old numbers are
archived, banner-marked, and must not be cited. Full tables in
`docs/results_overview.md` §PHASE-2. Headline reversals (decisions #49–#51):

1. **LwF's "best-in-class" was an artifact.** Per-task re-standardization
   inflated every CL method by ~0.25 ACC and *inverted* the ranking: LwF
   0.575 → **0.511** under a frozen scaler (r = −1.00), while ER 0.319 → 0.544,
   EWC 0.307 → 0.538, DER++ 0.274 → 0.533. Joint also dropped 0.968 → 0.930.
2. **"Federation hurts fine-tuning (p=0.031)" does not replicate.** Under
   chrono+frozen: federated finetune 0.470 vs single-node 0.511, p = 0.569 n.s.
3. **No CL method separates from plain replay when clean** (all ≈ 0.51,
   p = 0.11–0.47 vs ER); only the joint oracle survives Holm (0.907, raw
   p = 0.0005, Holm 0.0063).
4. **New, strong first-class results:** order-sensitivity is real
   (default 0.514 vs alt 0.455 vs reverse 0.448; p = 0.0005, Holm 0.0015,
   r = −1.00) → every single-node claim must be reported order-conditioned;
   growing head > pre-sized (0.535 vs 0.511, Holm 0.0005); H2's anchor
   discovery poison now *does* cost accuracy significantly (0.498 vs 0.517,
   Holm 0.0063, upgrading the old p = 0.078 "suggestive"); random-vs-chrono
   split delta is only ~2–3 points (p = 0.016–0.031) versus ~25 points for the
   scaler — that contrast is now a contribution ("limitations → findings").
5. **Breaking-point correction (n=12):** the earlier 10%-only collapse hint
   was false. Seed 11 is ≈0.195 in both p0 and p10; p10 vs p0 is 0.471±0.098
   vs 0.470±0.099 (paired p=0.791, Holm=1.0, `results/wilcoxon.csv`). Keep
   high seed variance as a finding to investigate, without attributing it to
   poison dose.

**Implication for the paper:** the method-ranking narrative is retired. The
surviving spine is (a) the protocol/preprocessing decomposition, (b) whatever
the federated + Byzantine headline shows under the corrected protocol, (c)
defence/adaptive-attacker results, (d) order/architecture/dataset
generalisation. Do not write a ranking claim until `c_f2` + `bz` land.

## 4. Bugs found and fixed (do not reintroduce)

- **A2 class-IL was silently identical to CII** (identical ACC to 6 dp).
  `load_or_build_tasks`'s `filter_ci` only drops *unseen* labels, and CII task
  *t* contains only already-seen labels, so it was a no-op. Fix: real CI task
  file `data/processed/tasks_chrono_ci.npz`; `configs/a2_classil_c.yaml` now
  points at it; the 24 wrong result files are archived in
  `results_prefix0/a2_bugfix/`. **`a2_classil_c` must be re-run (12 seeds)** —
  it is currently 0/12.
- **Thread oversubscription (the stall that killed 5 workers).** 5 workers × 8
  default BLAS/torch threads on 8 cores → one federated run took 4.3 h (vs 57 s
  capped); workers exited 0xC0000135 / 0x40010004. Fixed: `CL_THREADS` env +
  `src/cl/base.py::limit_threads()` called at import of `run_experiment`,
  `n_jobs=1` in both kNN filters, `run_groups.py` exports the caps, and
  `reproduce.sh` / `Dockerfile` pin them. **Bit-reproducibility now depends on
  the thread count** (f2_fed_finetune_p5_c seed 7: 0.496423 @8 threads vs
  0.5043 @2) — never compare numbers across thread settings; log this caveat
  in the artifact.
- Two syntax errors in `scripts/stats_summary.py` were introduced by block
  insertions (a `]` and a `}` in the wrong place) — already fixed; if you edit
  that file, run `python -c "import ast; ast.parse(open('scripts/stats_summary.py').read())"`
  before launching grids.
- Locked FedAvg path is deliberately preserved bit-identically (branch in
  `fedavg.py`: robust rules use the delta path, plain FedAvg keeps model
  averaging). Do not "unify" this.

## 5. Environment / data facts

- 8 logical cores, 34 GB RAM, Python 3.14, torch 2.14 CPU, sklearn 1.8.
- CICIDS2017 raw CSVs are in `data/raw/` (8 files). `clean.py` now emits a
  `flow_order` column (raw-file rank, assigned after dedup) — the ML-CSV
  distribution has **no Timestamp column**, so capture order is the disclosed
  chronological proxy.
- UNSW-NB15 from HF mirror `Mireu-Lab/UNSW-NB15` in `data/raw_unsw/`.
  **The mirror's filenames are swapped**: their `test.csv` (175,341 rows) is
  the canonical *training* set; `src/data/unsw.py` uses it that way and never
  re-splits. Disjoint Normal slices across 4 tasks; one-hot from train pool.
- CICIoT2023 from `lacg030175/CIC-IoT-2023-full` in `data/raw_iot/`
  (7.7M + ~14M rows). `src/data/iot.py` builds a **capped** replication
  (3k train / 1k test per fine Label, 8k benign per task → 20–38k rows per
  task) with all caps recorded in `data/processed/tasks_iot.json`.
  Full-scale GPU rerun is logged as follow-up.
- Task files: `tasks.npz` (legacy per-task scaler, random split), 
  `tasks_frozen.npz`, `tasks_chrono.npz`, `tasks_chrono_alt.npz`,
  `tasks_chrono_rev.npz`, `tasks_chrono_ci.npz`, `tasks_unsw.npz`,
  `tasks_iot.npz`. Archives: `data/processed_prefix0/`, `results_prefix0/`.

## 6. Immediate next steps (in order)

1. Check the four 2-thread workers (§0) and progress in
   `results/run_groups.log`. Verify newly written federated summaries have
   a `fed` field; the archived 165 invalid outputs must never re-enter results.
2. Investigate the c_f2 seed-11 low-accuracy anomaly (≈0.195 in both p0
   and p10); verify with a pinned 2-thread rerun before treating it as a
   finding. Audit earlier 8-thread vs new 2-thread result provenance before
   final cross-group comparisons.
3. `ar` (architecture sweep): complete. The Colab T4 run produced all 144
   expected GPU runs. The validated archive is stored at
   `artifacts/architecture_gpu_results.zip`; its per-seed outputs were imported
   into `results/`, and the one replaced CPU run is preserved under
   `results/_archive/architecture_cpu_pre_gpu/`. `baseline_table.csv`,
   `stats_summary.csv`, `wilcoxon.csv`, and `fig_architecture.png` were rebuilt.
4. When grids land: `python -m src.run_experiment --rebuild-table` →
   `python scripts/stats_summary.py` → `python scripts/make_figures.py`
   (new figures `fig_protocol_effects`, `fig_federated_corrected`,
   `fig_byzantine`, `fig_order_head`, `fig_cross_dataset`, `fig_architecture`
   auto-skip when their inputs are incomplete — that is by design).
5. Then rewrite `docs/results_overview.md` §PHASE-2 tables with final n=12
   numbers, and fill `docs/paper_draft.md` §6/§7 (abstract + intro framing
   must change to match the reversals).
6. Owner actions still outstanding: push to GitHub, Zenodo upload, Colab E8
   rerun, Scholar/Xplore/Scopus manual novelty counts, Su-2025 publisher-page
   confirmation, supervisor sign-off on the C&S target.

## 7. What NOT to do

- Do not delete or overwrite `results_prefix0/`, `results_prefix0/a2_bugfix/`,
  `results_prefix0/dispatch_bug_20260927/`, or `data/processed_prefix0/`
  (provenance policy).
- Do not cite any pre-2026-09-27 number in any document.
- Do not "restore" the AISec/ACM-sigconf framing; venue is Computers & Security.
- Do not add new methods/attacks/datasets that are not in
  `docs/proposal.md` §7/§8 or verified literature; if a claim is unverified,
  label it as such (see the Su-2025 handling, decision #34).
- Do not report average accuracy without the task-accuracy matrix, std, and a
  paired test that traces to `results/wilcoxon.csv`.
