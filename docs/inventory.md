# Phase-0 inventory — 211 configs (audited commit 9e635ae, 2026-09-27)

> **Current repair state, 2026-09-28:** The table below is the immutable
> 211-config baseline inventory at `9e635ae`, not the current completion
> count. Two sensitivity configs and an E4 direct-label-poison control were
> added, giving 214 parseable YAMLs.
> The active `results/runs/` tree now has 1,122 historical summary files
> across 114 config prefixes and **zero validated manifests**. The main
> aggregate CSVs have zero result rows. Six validated seeds across
> `e1_finetune_dedup` and `e1_finetune_t0` are isolated in
> `results/diagnostics/` and are not paper evidence. UNSW/IoT label-affected
> runs, class-IL filter runs, and
> former derived tables were moved to hashed, reasoned archives.
> The pre-repair `artifacts/architecture_gpu_results.zip` and old upload
> bundle remain intact but lack v2 per-seed completion manifests; their GPU
> numbers are historical and require a new Colab export before validation.

> **2026-09-28 E3 amendment:** The three backdoor configs now reference
> `tasks_chrono_dedup.npz` and the corrected model-space trigger/ASR path.
> The 38 old E3 R/summary files in the rows below were archived under
> `results/_archive/backdoor_protocol_20260928/`. Current validated E3 seed
> count is zero; the per-config table remains the audited-commit snapshot.

> **2026-09-28 E4 amendment:** Historical E4/E5 outputs (157 files including
> figures) are in `results/_archive/discovery_transductive_20260928/`.
> Chronological E4 configs now use `tasks_chrono_dedup.npz`, and
> `e4_novelty_label_control_c` is the 214th config. No historical E4 row
> below counts toward the current protocol. The initial no-poison diagnostic
> was archived separately before source-tree fingerprinting; one v3 no-poison
> seed is isolated in `results/diagnostics/`, not final evidence.

Audited-commit source: `configs/**/*.yaml` x 211; seed artifacts:
`results/runs/*_summary_seed*.json` (1340 files, 135 distinct prefixes before
the repair archives). Baseline verification: **84 configs x 12 seeds, 45 x 7
seeds, 6 x 1-5 seeds, 76 x 0 seeds**. These are historical execution counts,
not present-day validated completion counts.

Partial (1-5 seeds): `bz_ft_lie_trust_c` (3: 1,2,3), `e6_knnadapt_knn_c` (3: 1,2,3), `f2_fed_ewc_p40_c` (4: 1,2,3,4), `i_e1_clean` (1: 1), `i_f2_fed_ewc_p0` (1: 1), `u_f2_fed_derpp_p10` (5: 1,2,3,4,5).

## States (different things)

- **implemented**: 211 audited configs parse and have owning code paths (single-node, federated, Byzantine, defenses, discovery, and architecture). Three configs were added later; all 214 parse.
- **executed**: at the audited commit, 135 config prefixes had at least one summary (129 at their then-target seed count plus six partial). After the repair archives, 114 historical prefixes remain active; they are still only execution evidence.
- **validated**: a seed needs a matching completion manifest, summary, R matrix, and config/task provenance. The main result tree currently has zero such seeds. Six diagnostic seeds (three per sensitivity arm) are validated in a separate directory and do not meet the 12-paired-seed final standard.
- **documented**: prior numeric claims in `docs/results_overview.md` and the paper draft are marked historical. They must not be cited as validated findings until selected comparisons are rerun and the tables rebuilt.

## Breakdown

- protocol (tasks file): chrono/frozen 113, random/per-task 38, iot/capped 24, unsw/standard 24, random/frozen 7, chrono-alt/frozen 1, chrono-rev/frozen 1, chrono-ci/frozen 1, random-ci/per-task 1, order-alt/per-task 1.
- dataset: cicids2017 163, unsw-nb15 24, ciciot2023 24.
- runner: federated 131 (all carry `fed:`), single-node 80.
- cl_method: finetune 62, ewc 61, er 43, derpp 35, joint 5, lwf 5.
- attack.type: label_flip 118, None(clean) 82, novelty 8, backdoor 3; plus update_attack sign_flip/lie/model_replacement inside byzantine configs (34).
- defense: none 181, small_loss 27, knn_consistency 3.
- arch: mlp-default 199 (incl. wide-[128,64] er baselines), wide 6, transformer 6.

## Findings (fix in Phase-1, no grid started)

- `scripts/e5_evasion.py` imports `load_tasks,train_autoencoder` from `src.run_experiment` (not exposed; owners are `src/data/sequence.py` and `src/runner.py`).
- `notebooks/architecture_colab.ipynb` globs `configs/ar_*.yaml`; files live at `configs/arch/ar_*.yaml`.
- `scripts/import_architecture_gpu.py` targets `results/` flat; live layout is `results/runs/`; must preserve GPU manifest and keep CPU/GPU distinct.
- `scripts/grid_status.py` exec-slices `run_grid.py`; replace with import-safe shared group registry.
- `src/reporting.py::save_results` calls `np.array2string` without importing numpy (writes R+summary then crashes); `run_grid.py` skip-on-summary-exists then skips the seed on retry. Needs transactional persistence + manifest.
- `Makefile lint` swallows failures with `|| true`.
- Display/file-stem mismatch: `configs/label_flip/e2_labelflip_random_05pct.yaml` carries `name: e2_labelflip_random_0.5pct`; `run_grid` skip-check uses the group key (stem) while `save_results` prefixes the display name — skip never hits. Canonicalize on display `name`.
- `tests/test_project.py::test_configs_parse` samples only first 20 YAMLs; must validate all 211.

## Per-config table

| file | name | protocol | dataset | runner | method | attack | mode/upd | defense | arch | n | seeds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ablations/a1_buffer_1000.yaml | a1_buffer_1000 | random/per-task | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 0 |  |
| ablations/a1_buffer_1000_c.yaml | a1_buffer_1000_c | chrono/frozen | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| ablations/a2_classil.yaml | a2_classil | random-ci/per-task | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| ablations/a2_classil_c.yaml | a2_classil_c | chrono-ci/frozen | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 0 |  |
| ablations/a3_order_alt.yaml | a3_order_alt | order-alt/per-task | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 0 |  |
| ablations/a3_order_alt_c.yaml | a3_order_alt_c | chrono-alt/frozen | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| ablations/a3_order_rev_c.yaml | a3_order_rev_c | chrono-rev/frozen | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_derpp_tr_clean_c.yaml | ar_derpp_tr_clean_c | chrono/frozen | cicids2017 | single-node | derpp | - | None/None | None | transformer | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_derpp_tr_p5_c.yaml | ar_derpp_tr_p5_c | chrono/frozen | cicids2017 | single-node | derpp | label_flip | targeted/None | None | transformer | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_derpp_wide_clean_c.yaml | ar_derpp_wide_clean_c | chrono/frozen | cicids2017 | single-node | derpp | - | None/None | None | wide | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_derpp_wide_p5_c.yaml | ar_derpp_wide_p5_c | chrono/frozen | cicids2017 | single-node | derpp | label_flip | targeted/None | None | wide | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_ewc_tr_clean_c.yaml | ar_ewc_tr_clean_c | chrono/frozen | cicids2017 | single-node | ewc | - | None/None | None | transformer | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_ewc_tr_p5_c.yaml | ar_ewc_tr_p5_c | chrono/frozen | cicids2017 | single-node | ewc | label_flip | targeted/None | None | transformer | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_ewc_wide_clean_c.yaml | ar_ewc_wide_clean_c | chrono/frozen | cicids2017 | single-node | ewc | - | None/None | None | wide | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_ewc_wide_p5_c.yaml | ar_ewc_wide_p5_c | chrono/frozen | cicids2017 | single-node | ewc | label_flip | targeted/None | None | wide | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_ft_tr_clean_c.yaml | ar_ft_tr_clean_c | chrono/frozen | cicids2017 | single-node | finetune | - | None/None | None | transformer | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_ft_tr_p5_c.yaml | ar_ft_tr_p5_c | chrono/frozen | cicids2017 | single-node | finetune | label_flip | targeted/None | None | transformer | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_ft_wide_clean_c.yaml | ar_ft_wide_clean_c | chrono/frozen | cicids2017 | single-node | finetune | - | None/None | None | wide | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| arch/ar_ft_wide_p5_c.yaml | ar_ft_wide_p5_c | chrono/frozen | cicids2017 | single-node | finetune | label_flip | targeted/None | None | wide | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| backdoor/e3_backdoor.yaml | e3_backdoor | random/per-task | cicids2017 | single-node | er | backdoor | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| backdoor/e3_backdoor_c.yaml | e3_backdoor_c | chrono/frozen | cicids2017 | single-node | er | backdoor | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| backdoor/e3_grounded_c.yaml | e3_grounded_c | chrono/frozen | cicids2017 | single-node | er | backdoor | None/None | None | mlp-default | 0 |  |
| baselines/e1_clean.yaml | e1_clean | random/per-task | cicids2017 | single-node | er | - | None/None | None | wide-[128, 64] | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_clean_c.yaml | e1_clean_c | chrono/frozen | cicids2017 | single-node | er | - | None/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| baselines/e1_clean_rf.yaml | e1_clean_rf | random/frozen | cicids2017 | single-node | er | - | None/None | None | wide-[128, 64] | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_derpp.yaml | e1_derpp | random/per-task | cicids2017 | single-node | derpp | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_derpp_c.yaml | e1_derpp_c | chrono/frozen | cicids2017 | single-node | derpp | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| baselines/e1_derpp_rf.yaml | e1_derpp_rf | random/frozen | cicids2017 | single-node | derpp | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_ewc.yaml | e1_ewc | random/per-task | cicids2017 | single-node | ewc | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_ewc_c.yaml | e1_ewc_c | chrono/frozen | cicids2017 | single-node | ewc | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| baselines/e1_ewc_rf.yaml | e1_ewc_rf | random/frozen | cicids2017 | single-node | ewc | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_finetune.yaml | e1_finetune | random/per-task | cicids2017 | single-node | finetune | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_finetune_c.yaml | e1_finetune_c | chrono/frozen | cicids2017 | single-node | finetune | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| baselines/e1_finetune_frozen.yaml | e1_finetune_frozen | random/frozen | cicids2017 | single-node | finetune | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_finetune_gh.yaml | e1_finetune_gh | chrono/frozen | cicids2017 | single-node | finetune | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| baselines/e1_finetune_rf.yaml | e1_finetune_rf | random/frozen | cicids2017 | single-node | finetune | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_joint.yaml | e1_joint | random/per-task | cicids2017 | single-node | joint | - | None/None | None | wide-[128, 64] | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_joint_c.yaml | e1_joint_c | chrono/frozen | cicids2017 | single-node | joint | - | None/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| baselines/e1_joint_rf.yaml | e1_joint_rf | random/frozen | cicids2017 | single-node | joint | - | None/None | None | wide-[128, 64] | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_lwf.yaml | e1_lwf | random/per-task | cicids2017 | single-node | lwf | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| baselines/e1_lwf_c.yaml | e1_lwf_c | chrono/frozen | cicids2017 | single-node | lwf | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| baselines/e1_lwf_rf.yaml | e1_lwf_rf | random/frozen | cicids2017 | single-node | lwf | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| byzantine/bz_ewc_lie05_fedavg_c.yaml | bz_ewc_lie05_fedavg_c | chrono/frozen | cicids2017 | federated | ewc | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ewc_lie05_trust_c.yaml | bz_ewc_lie05_trust_c | chrono/frozen | cicids2017 | federated | ewc | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ewc_lie_fedavg_c.yaml | bz_ewc_lie_fedavg_c | chrono/frozen | cicids2017 | federated | ewc | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ewc_lie_krum_c.yaml | bz_ewc_lie_krum_c | chrono/frozen | cicids2017 | federated | ewc | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ewc_lie_med_c.yaml | bz_ewc_lie_med_c | chrono/frozen | cicids2017 | federated | ewc | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ewc_lie_trim_c.yaml | bz_ewc_lie_trim_c | chrono/frozen | cicids2017 | federated | ewc | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ewc_lie_trust_c.yaml | bz_ewc_lie_trust_c | chrono/frozen | cicids2017 | federated | ewc | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ewc_mr_fedavg_c.yaml | bz_ewc_mr_fedavg_c | chrono/frozen | cicids2017 | federated | ewc | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ewc_mr_krum_c.yaml | bz_ewc_mr_krum_c | chrono/frozen | cicids2017 | federated | ewc | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ewc_mr_med_c.yaml | bz_ewc_mr_med_c | chrono/frozen | cicids2017 | federated | ewc | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ewc_mr_trim_c.yaml | bz_ewc_mr_trim_c | chrono/frozen | cicids2017 | federated | ewc | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ewc_mr_trust_c.yaml | bz_ewc_mr_trust_c | chrono/frozen | cicids2017 | federated | ewc | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ewc_sf_fedavg_c.yaml | bz_ewc_sf_fedavg_c | chrono/frozen | cicids2017 | federated | ewc | byz-sign_flip | None/sign_flip | None | mlp-default | 0 |  |
| byzantine/bz_ewc_sf_krum_c.yaml | bz_ewc_sf_krum_c | chrono/frozen | cicids2017 | federated | ewc | byz-sign_flip | None/sign_flip | None | mlp-default | 0 |  |
| byzantine/bz_ewc_sf_med_c.yaml | bz_ewc_sf_med_c | chrono/frozen | cicids2017 | federated | ewc | byz-sign_flip | None/sign_flip | None | mlp-default | 0 |  |
| byzantine/bz_ewc_sf_trim_c.yaml | bz_ewc_sf_trim_c | chrono/frozen | cicids2017 | federated | ewc | byz-sign_flip | None/sign_flip | None | mlp-default | 0 |  |
| byzantine/bz_ewc_sf_trust_c.yaml | bz_ewc_sf_trust_c | chrono/frozen | cicids2017 | federated | ewc | byz-sign_flip | None/sign_flip | None | mlp-default | 0 |  |
| byzantine/bz_ft_lie05_fedavg_c.yaml | bz_ft_lie05_fedavg_c | chrono/frozen | cicids2017 | federated | finetune | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ft_lie05_trust_c.yaml | bz_ft_lie05_trust_c | chrono/frozen | cicids2017 | federated | finetune | byz-lie | None/lie | None | mlp-default | 0 |  |
| byzantine/bz_ft_lie_fedavg_c.yaml | bz_ft_lie_fedavg_c | chrono/frozen | cicids2017 | federated | finetune | byz-lie | None/lie | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| byzantine/bz_ft_lie_krum_c.yaml | bz_ft_lie_krum_c | chrono/frozen | cicids2017 | federated | finetune | byz-lie | None/lie | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| byzantine/bz_ft_lie_med_c.yaml | bz_ft_lie_med_c | chrono/frozen | cicids2017 | federated | finetune | byz-lie | None/lie | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| byzantine/bz_ft_lie_trim_c.yaml | bz_ft_lie_trim_c | chrono/frozen | cicids2017 | federated | finetune | byz-lie | None/lie | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| byzantine/bz_ft_lie_trust_c.yaml | bz_ft_lie_trust_c | chrono/frozen | cicids2017 | federated | finetune | byz-lie | None/lie | None | mlp-default | 3 | 1,2,3 |
| byzantine/bz_ft_mr_fedavg_c.yaml | bz_ft_mr_fedavg_c | chrono/frozen | cicids2017 | federated | finetune | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ft_mr_krum_c.yaml | bz_ft_mr_krum_c | chrono/frozen | cicids2017 | federated | finetune | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ft_mr_med_c.yaml | bz_ft_mr_med_c | chrono/frozen | cicids2017 | federated | finetune | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ft_mr_trim_c.yaml | bz_ft_mr_trim_c | chrono/frozen | cicids2017 | federated | finetune | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ft_mr_trust_c.yaml | bz_ft_mr_trust_c | chrono/frozen | cicids2017 | federated | finetune | byz-model_replacement | None/model_replacement | None | mlp-default | 0 |  |
| byzantine/bz_ft_sf_fedavg_c.yaml | bz_ft_sf_fedavg_c | chrono/frozen | cicids2017 | federated | finetune | byz-sign_flip | None/sign_flip | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| byzantine/bz_ft_sf_krum_c.yaml | bz_ft_sf_krum_c | chrono/frozen | cicids2017 | federated | finetune | byz-sign_flip | None/sign_flip | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| byzantine/bz_ft_sf_med_c.yaml | bz_ft_sf_med_c | chrono/frozen | cicids2017 | federated | finetune | byz-sign_flip | None/sign_flip | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| byzantine/bz_ft_sf_trim_c.yaml | bz_ft_sf_trim_c | chrono/frozen | cicids2017 | federated | finetune | byz-sign_flip | None/sign_flip | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| byzantine/bz_ft_sf_trust_c.yaml | bz_ft_sf_trust_c | chrono/frozen | cicids2017 | federated | finetune | byz-sign_flip | None/sign_flip | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| defenses/e6_adaptive_sl_c.yaml | e6_adaptive_sl_c | chrono/frozen | cicids2017 | single-node | er | label_flip | adaptive/None | small_loss | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| defenses/e6_defense_knnconsist.yaml | e6_defense_knnconsist | random/per-task | cicids2017 | single-node | er | label_flip | targeted/None | knn_consistency | mlp-default | 7 | 1,2,3,4,5,6,42 |
| defenses/e6_defense_knnconsist_c.yaml | e6_defense_knnconsist_c | chrono/frozen | cicids2017 | single-node | er | label_flip | targeted/None | knn_consistency | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| defenses/e6_defense_smallloss.yaml | e6_defense_smallloss | random/per-task | cicids2017 | single-node | er | label_flip | targeted/None | small_loss | mlp-default | 7 | 1,2,3,4,5,6,42 |
| defenses/e6_defense_smallloss_c.yaml | e6_defense_smallloss_c | chrono/frozen | cicids2017 | single-node | er | label_flip | targeted/None | small_loss | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| defenses/e6_knnadapt_knn_c.yaml | e6_knnadapt_knn_c | chrono/frozen | cicids2017 | single-node | er | label_flip | knn_adaptive/None | knn_consistency | mlp-default | 3 | 1,2,3 |
| federated/f2_fed_derpp_p0.yaml | f2_fed_derpp_p0 | random/per-task | cicids2017 | federated | derpp | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_derpp_p0_b100.yaml | f2_fed_derpp_p0_b100 | random/per-task | cicids2017 | federated | derpp | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_derpp_p0_c.yaml | f2_fed_derpp_p0_c | chrono/frozen | cicids2017 | federated | derpp | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_derpp_p1.yaml | f2_fed_derpp_p1 | random/per-task | cicids2017 | federated | derpp | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_derpp_p10.yaml | f2_fed_derpp_p10 | random/per-task | cicids2017 | federated | derpp | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_derpp_p10_b100.yaml | f2_fed_derpp_p10_b100 | random/per-task | cicids2017 | federated | derpp | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_derpp_p10_c.yaml | f2_fed_derpp_p10_c | chrono/frozen | cicids2017 | federated | derpp | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_derpp_p1_c.yaml | f2_fed_derpp_p1_c | chrono/frozen | cicids2017 | federated | derpp | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_derpp_p5.yaml | f2_fed_derpp_p5 | random/per-task | cicids2017 | federated | derpp | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_derpp_p5_c.yaml | f2_fed_derpp_p5_c | chrono/frozen | cicids2017 | federated | derpp | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_er_p0_c.yaml | f2_fed_er_p0_c | chrono/frozen | cicids2017 | federated | er | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,7 |
| federated/f2_fed_er_p10_c.yaml | f2_fed_er_p10_c | chrono/frozen | cicids2017 | federated | er | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2_fed_er_p1_c.yaml | f2_fed_er_p1_c | chrono/frozen | cicids2017 | federated | er | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2_fed_er_p5_c.yaml | f2_fed_er_p5_c | chrono/frozen | cicids2017 | federated | er | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2_fed_ewc_p0.yaml | f2_fed_ewc_p0 | random/per-task | cicids2017 | federated | ewc | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_ewc_p0_c.yaml | f2_fed_ewc_p0_c | chrono/frozen | cicids2017 | federated | ewc | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ewc_p0_l0_c.yaml | f2_fed_ewc_p0_l0_c | chrono/frozen | cicids2017 | federated | ewc | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ewc_p0_l1000_c.yaml | f2_fed_ewc_p0_l1000_c | chrono/frozen | cicids2017 | federated | ewc | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ewc_p1.yaml | f2_fed_ewc_p1 | random/per-task | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_ewc_p10.yaml | f2_fed_ewc_p10 | random/per-task | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_ewc_p10_c.yaml | f2_fed_ewc_p10_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ewc_p1_c.yaml | f2_fed_ewc_p1_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ewc_p40_c.yaml | f2_fed_ewc_p40_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 4 | 1,2,3,4 |
| federated/f2_fed_ewc_p5.yaml | f2_fed_ewc_p5 | random/per-task | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_ewc_p5_c.yaml | f2_fed_ewc_p5_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ewc_p5_m2_c.yaml | f2_fed_ewc_p5_m2_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ewc_p5_m3_c.yaml | f2_fed_ewc_p5_m3_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ewc_persist_p5_c.yaml | f2_fed_ewc_persist_p5_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | persistent/None | None | mlp-default | 0 |  |
| federated/f2_fed_finetune_p0.yaml | f2_fed_finetune_p0 | random/per-task | cicids2017 | federated | finetune | - | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_finetune_p0_c.yaml | f2_fed_finetune_p0_c | chrono/frozen | cicids2017 | federated | finetune | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_finetune_p1.yaml | f2_fed_finetune_p1 | random/per-task | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_finetune_p10.yaml | f2_fed_finetune_p10 | random/per-task | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_finetune_p10_c.yaml | f2_fed_finetune_p10_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_finetune_p1_c.yaml | f2_fed_finetune_p1_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_finetune_p5.yaml | f2_fed_finetune_p5 | random/per-task | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f2_fed_finetune_p5_c.yaml | f2_fed_finetune_p5_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ft_p20_c.yaml | f2_fed_ft_p20_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ft_p40_c.yaml | f2_fed_ft_p40_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ft_p5_m2_c.yaml | f2_fed_ft_p5_m2_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ft_p5_m3_c.yaml | f2_fed_ft_p5_m3_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| federated/f2_fed_ft_persist_p5_c.yaml | f2_fed_ft_persist_p5_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | persistent/None | None | mlp-default | 0 |  |
| federated/f2r_ewc_p5_krum_c.yaml | f2r_ewc_p5_krum_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2r_ewc_p5_med_c.yaml | f2r_ewc_p5_med_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2r_ewc_p5_trim_c.yaml | f2r_ewc_p5_trim_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2r_ewc_p5_trust_c.yaml | f2r_ewc_p5_trust_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2r_ft_p5_krum_c.yaml | f2r_ft_p5_krum_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2r_ft_p5_med_c.yaml | f2r_ft_p5_med_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2r_ft_p5_trim_c.yaml | f2r_ft_p5_trim_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f2r_ft_p5_trust_c.yaml | f2r_ft_p5_trust_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | None | mlp-default | 0 |  |
| federated/f4_fed_derpp_p10_sl.yaml | f4_fed_derpp_p10_sl | random/per-task | cicids2017 | federated | derpp | label_flip | targeted/None | small_loss | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f4_fed_derpp_p10_sl_c.yaml | f4_fed_derpp_p10_sl_c | chrono/frozen | cicids2017 | federated | derpp | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| federated/f4_fed_derpp_p5_sl.yaml | f4_fed_derpp_p5_sl | random/per-task | cicids2017 | federated | derpp | label_flip | targeted/None | small_loss | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f4_fed_derpp_p5_sl_c.yaml | f4_fed_derpp_p5_sl_c | chrono/frozen | cicids2017 | federated | derpp | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| federated/f4_fed_ewc_p10_sl.yaml | f4_fed_ewc_p10_sl | random/per-task | cicids2017 | federated | ewc | label_flip | targeted/None | small_loss | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f4_fed_ewc_p10_sl_c.yaml | f4_fed_ewc_p10_sl_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| federated/f4_fed_ewc_p5_sl.yaml | f4_fed_ewc_p5_sl | random/per-task | cicids2017 | federated | ewc | label_flip | targeted/None | small_loss | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f4_fed_ewc_p5_sl_c.yaml | f4_fed_ewc_p5_sl_c | chrono/frozen | cicids2017 | federated | ewc | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| federated/f4_fed_finetune_p10_sl.yaml | f4_fed_finetune_p10_sl | random/per-task | cicids2017 | federated | finetune | label_flip | targeted/None | small_loss | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f4_fed_finetune_p10_sl_c.yaml | f4_fed_finetune_p10_sl_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| federated/f4_fed_finetune_p5_sl.yaml | f4_fed_finetune_p5_sl | random/per-task | cicids2017 | federated | finetune | label_flip | targeted/None | small_loss | mlp-default | 7 | 1,2,3,4,5,6,42 |
| federated/f4_fed_finetune_p5_sl_c.yaml | f4_fed_finetune_p5_sl_c | chrono/frozen | cicids2017 | federated | finetune | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| label_flip/e2_adaptive_c.yaml | e2_adaptive_c | chrono/frozen | cicids2017 | single-node | er | label_flip | adaptive/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| label_flip/e2_bufferflip.yaml | e2_bufferflip | random/per-task | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| label_flip/e2_bufferflip_c.yaml | e2_bufferflip_c | chrono/frozen | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| label_flip/e2_labelflip.yaml | e2_labelflip | random/per-task | cicids2017 | single-node | er | label_flip | targeted/None | None | wide-[128, 64] | 7 | 1,2,3,4,5,6,42 |
| label_flip/e2_labelflip_5pct.yaml | e2_labelflip_5pct | random/per-task | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| label_flip/e2_labelflip_5pct_c.yaml | e2_labelflip_5pct_c | chrono/frozen | cicids2017 | single-node | er | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| label_flip/e2_labelflip_c.yaml | e2_labelflip_c | chrono/frozen | cicids2017 | single-node | er | label_flip | targeted/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| label_flip/e2_labelflip_random_05pct.yaml | e2_labelflip_random_0.5pct | random/per-task | cicids2017 | single-node | er | label_flip | random/None | None | mlp-default | 0 |  |
| label_flip/e2_labelflip_random_05pct_c.yaml | e2_labelflip_random_05pct_c | chrono/frozen | cicids2017 | single-node | er | label_flip | random/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| label_flip/e2_persist_er_c.yaml | e2_persist_er_c | chrono/frozen | cicids2017 | single-node | er | label_flip | persistent/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| label_flip/e2_persist_ewc_c.yaml | e2_persist_ewc_c | chrono/frozen | cicids2017 | single-node | ewc | label_flip | persistent/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| label_flip/e2_persist_ft_c.yaml | e2_persist_ft_c | chrono/frozen | cicids2017 | single-node | finetune | label_flip | persistent/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/i_e1_clean.yaml | i_e1_clean | iot/capped | ciciot2023 | single-node | er | - | None/None | None | wide-[128, 64] | 1 | 1 |
| mirrors/i_e1_derpp.yaml | i_e1_derpp | iot/capped | ciciot2023 | single-node | derpp | - | None/None | None | mlp-default | 0 |  |
| mirrors/i_e1_ewc.yaml | i_e1_ewc | iot/capped | ciciot2023 | single-node | ewc | - | None/None | None | mlp-default | 0 |  |
| mirrors/i_e1_finetune.yaml | i_e1_finetune | iot/capped | ciciot2023 | single-node | finetune | - | None/None | None | mlp-default | 0 |  |
| mirrors/i_e1_joint.yaml | i_e1_joint | iot/capped | ciciot2023 | single-node | joint | - | None/None | None | wide-[128, 64] | 0 |  |
| mirrors/i_e1_lwf.yaml | i_e1_lwf | iot/capped | ciciot2023 | single-node | lwf | - | None/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_derpp_p0.yaml | i_f2_fed_derpp_p0 | iot/capped | ciciot2023 | federated | derpp | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_derpp_p1.yaml | i_f2_fed_derpp_p1 | iot/capped | ciciot2023 | federated | derpp | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_derpp_p10.yaml | i_f2_fed_derpp_p10 | iot/capped | ciciot2023 | federated | derpp | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_derpp_p5.yaml | i_f2_fed_derpp_p5 | iot/capped | ciciot2023 | federated | derpp | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_ewc_p0.yaml | i_f2_fed_ewc_p0 | iot/capped | ciciot2023 | federated | ewc | label_flip | targeted/None | None | mlp-default | 1 | 1 |
| mirrors/i_f2_fed_ewc_p1.yaml | i_f2_fed_ewc_p1 | iot/capped | ciciot2023 | federated | ewc | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_ewc_p10.yaml | i_f2_fed_ewc_p10 | iot/capped | ciciot2023 | federated | ewc | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_ewc_p5.yaml | i_f2_fed_ewc_p5 | iot/capped | ciciot2023 | federated | ewc | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_finetune_p0.yaml | i_f2_fed_finetune_p0 | iot/capped | ciciot2023 | federated | finetune | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_finetune_p1.yaml | i_f2_fed_finetune_p1 | iot/capped | ciciot2023 | federated | finetune | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_finetune_p10.yaml | i_f2_fed_finetune_p10 | iot/capped | ciciot2023 | federated | finetune | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f2_fed_finetune_p5.yaml | i_f2_fed_finetune_p5 | iot/capped | ciciot2023 | federated | finetune | label_flip | targeted/None | None | mlp-default | 0 |  |
| mirrors/i_f4_fed_derpp_p10_sl.yaml | i_f4_fed_derpp_p10_sl | iot/capped | ciciot2023 | federated | derpp | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/i_f4_fed_derpp_p5_sl.yaml | i_f4_fed_derpp_p5_sl | iot/capped | ciciot2023 | federated | derpp | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/i_f4_fed_ewc_p10_sl.yaml | i_f4_fed_ewc_p10_sl | iot/capped | ciciot2023 | federated | ewc | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/i_f4_fed_ewc_p5_sl.yaml | i_f4_fed_ewc_p5_sl | iot/capped | ciciot2023 | federated | ewc | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/i_f4_fed_finetune_p10_sl.yaml | i_f4_fed_finetune_p10_sl | iot/capped | ciciot2023 | federated | finetune | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/i_f4_fed_finetune_p5_sl.yaml | i_f4_fed_finetune_p5_sl | iot/capped | ciciot2023 | federated | finetune | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/u_e1_clean.yaml | u_e1_clean | unsw/standard | unsw-nb15 | single-node | er | - | None/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_e1_derpp.yaml | u_e1_derpp | unsw/standard | unsw-nb15 | single-node | derpp | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_e1_ewc.yaml | u_e1_ewc | unsw/standard | unsw-nb15 | single-node | ewc | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_e1_finetune.yaml | u_e1_finetune | unsw/standard | unsw-nb15 | single-node | finetune | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_e1_joint.yaml | u_e1_joint | unsw/standard | unsw-nb15 | single-node | joint | - | None/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_e1_lwf.yaml | u_e1_lwf | unsw/standard | unsw-nb15 | single-node | lwf | - | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_derpp_p0.yaml | u_f2_fed_derpp_p0 | unsw/standard | unsw-nb15 | federated | derpp | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_derpp_p1.yaml | u_f2_fed_derpp_p1 | unsw/standard | unsw-nb15 | federated | derpp | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_derpp_p10.yaml | u_f2_fed_derpp_p10 | unsw/standard | unsw-nb15 | federated | derpp | label_flip | targeted/None | None | mlp-default | 5 | 1,2,3,4,5 |
| mirrors/u_f2_fed_derpp_p5.yaml | u_f2_fed_derpp_p5 | unsw/standard | unsw-nb15 | federated | derpp | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_ewc_p0.yaml | u_f2_fed_ewc_p0 | unsw/standard | unsw-nb15 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_ewc_p1.yaml | u_f2_fed_ewc_p1 | unsw/standard | unsw-nb15 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_ewc_p10.yaml | u_f2_fed_ewc_p10 | unsw/standard | unsw-nb15 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_ewc_p5.yaml | u_f2_fed_ewc_p5 | unsw/standard | unsw-nb15 | federated | ewc | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_finetune_p0.yaml | u_f2_fed_finetune_p0 | unsw/standard | unsw-nb15 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_finetune_p1.yaml | u_f2_fed_finetune_p1 | unsw/standard | unsw-nb15 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_finetune_p10.yaml | u_f2_fed_finetune_p10 | unsw/standard | unsw-nb15 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f2_fed_finetune_p5.yaml | u_f2_fed_finetune_p5 | unsw/standard | unsw-nb15 | federated | finetune | label_flip | targeted/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| mirrors/u_f4_fed_derpp_p10_sl.yaml | u_f4_fed_derpp_p10_sl | unsw/standard | unsw-nb15 | federated | derpp | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/u_f4_fed_derpp_p5_sl.yaml | u_f4_fed_derpp_p5_sl | unsw/standard | unsw-nb15 | federated | derpp | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/u_f4_fed_ewc_p10_sl.yaml | u_f4_fed_ewc_p10_sl | unsw/standard | unsw-nb15 | federated | ewc | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/u_f4_fed_ewc_p5_sl.yaml | u_f4_fed_ewc_p5_sl | unsw/standard | unsw-nb15 | federated | ewc | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/u_f4_fed_finetune_p10_sl.yaml | u_f4_fed_finetune_p10_sl | unsw/standard | unsw-nb15 | federated | finetune | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| mirrors/u_f4_fed_finetune_p5_sl.yaml | u_f4_fed_finetune_p5_sl | unsw/standard | unsw-nb15 | federated | finetune | label_flip | targeted/None | small_loss | mlp-default | 0 |  |
| novelty/e4_novelty.yaml | e4_novelty | random/per-task | cicids2017 | single-node | er | novelty | None/None | None | wide-[128, 64] | 7 | 1,2,3,4,5,6,42 |
| novelty/e4_novelty_anchor.yaml | e4_novelty_anchor | random/per-task | cicids2017 | single-node | er | novelty | anchor/None | None | wide-[128, 64] | 7 | 1,2,3,4,5,6,42 |
| novelty/e4_novelty_anchor_c.yaml | e4_novelty_anchor_c | chrono/frozen | cicids2017 | single-node | er | novelty | anchor/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| novelty/e4_novelty_c.yaml | e4_novelty_c | chrono/frozen | cicids2017 | single-node | er | novelty | None/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| novelty/e4_novelty_nopois.yaml | e4_novelty_nopois | random/per-task | cicids2017 | single-node | er | novelty | None/None | None | wide-[128, 64] | 7 | 1,2,3,4,5,6,42 |
| novelty/e4_novelty_nopois_c.yaml | e4_novelty_nopois_c | chrono/frozen | cicids2017 | single-node | er | novelty | None/None | None | wide-[128, 64] | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |
| novelty/e4_novelty_suppress.yaml | e4_novelty_suppress | random/per-task | cicids2017 | single-node | er | novelty | None/None | None | mlp-default | 7 | 1,2,3,4,5,6,42 |
| novelty/e4_novelty_suppress_c.yaml | e4_novelty_suppress_c | chrono/frozen | cicids2017 | single-node | er | novelty | None/None | None | mlp-default | 12 | 1,2,3,4,5,6,7,8,9,10,11,42 |

76 with zero seeds: a1_buffer_1000, a2_classil_c, a3_order_alt, e3_grounded_c, 20x bz_ewc_* (lie/lie05/mr/sf x fedavg/krum/med/trim/trust), bz_ft_lie05_fedavg_c, bz_ft_lie05_trust_c, 5x bz_ft_mr_*, f2_fed_er_p{1,5,10}_c, f2_fed_{ewc,ft}_persist_p5_c, 8x f2r_*, 6x f4_*_c, e2_labelflip_random_0.5pct (stem e2_labelflip_random_05pct), 5x i_e1 (derpp/ewc/finetune/joint/lwf), 12x i_f2 (derpp/ewc/finetune x p), 6x i_f4, 6x u_f4.
