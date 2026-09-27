"""Grid driver: run one group at its configured 7- or 12-seed protocol.
Skips (config,seed) pairs whose summary file already exists in results/runs/,
so interrupted runs resume cleanly without repeating work.
Usage: python scripts/run_grid.py <group>  (groups: e1, e2e3, e4, e6a2,
  f2_ft, f2_ewc, f2_derpp). f2_* groups run the federated wrapper
  (src/federated/fedavg.py); all others run single-node src/runner.py.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml, time
from src.paths import RESULTS_DIR, RUNS_DIR, find_config
from src.run_experiment import run, save_results, append_table

GROUPS = {
    "e1": ["e1_clean","e1_derpp","e1_ewc","e1_finetune","e1_joint","e1_lwf"],
    "e2e3": ["e2_labelflip","e2_labelflip_5pct","e2_labelflip_random_05pct","e2_bufferflip","e3_backdoor"],
    "e4": ["e4_novelty","e4_novelty_anchor","e4_novelty_nopois","e4_novelty_suppress"],
    "e6a2": ["e6_defense_knnconsist","e6_defense_smallloss","a2_classil"],
    "f2_ft": ["f2_fed_finetune_p0","f2_fed_finetune_p1","f2_fed_finetune_p5","f2_fed_finetune_p10"],
    "f2_ewc": ["f2_fed_ewc_p0","f2_fed_ewc_p1","f2_fed_ewc_p5","f2_fed_ewc_p10"],
    "f2_derpp": ["f2_fed_derpp_p0","f2_fed_derpp_p1","f2_fed_derpp_p5","f2_fed_derpp_p10"],
    "f4_ft": ["f4_fed_finetune_p5_sl","f4_fed_finetune_p10_sl"],
    "f4_ewc": ["f4_fed_ewc_p5_sl","f4_fed_ewc_p10_sl"],
    "f4_derpp": ["f4_fed_derpp_p5_sl","f4_fed_derpp_p10_sl"],
    "f2_b100": ["f2_fed_derpp_p0_b100","f2_fed_derpp_p10_b100"],
    "scaler_abl": ["e1_finetune_frozen"],
    # Phase-2 chrono+frozen primary suite (_c), random+frozen (_rf),
    # growing-head (_gh). _c/_gh run at SEEDS12 (power+Holm, step 9);
    # _rf runs at SEEDS7 (paired against locked 7-seed secondaries only).
    "c_e1": ["e1_clean_c","e1_derpp_c","e1_ewc_c","e1_finetune_c","e1_joint_c","e1_lwf_c"],
    "c_e2e3": ["e2_labelflip_c","e2_labelflip_5pct_c","e2_labelflip_random_05pct_c","e2_bufferflip_c","e3_backdoor_c"],
    "c_e4": ["e4_novelty_c","e4_novelty_anchor_c","e4_novelty_nopois_c","e4_novelty_suppress_c"],
    "c_e6a2": ["e6_defense_knnconsist_c","e6_defense_smallloss_c","a2_classil_c"],
    "c_a1": ["a1_buffer_1000_c"],
    "c_a3": ["a3_order_alt_c","a3_order_rev_c"],
    "c_f2": ["f2_fed_finetune_p0_c","f2_fed_finetune_p1_c","f2_fed_finetune_p5_c","f2_fed_finetune_p10_c","f2_fed_ewc_p0_c","f2_fed_ewc_p1_c","f2_fed_ewc_p5_c","f2_fed_ewc_p10_c","f2_fed_derpp_p0_c","f2_fed_derpp_p1_c","f2_fed_derpp_p5_c","f2_fed_derpp_p10_c","f2_fed_er_p0_c","f2_fed_er_p1_c","f2_fed_er_p5_c","f2_fed_er_p10_c"],
    "c_f4": ["f4_fed_finetune_p5_sl_c","f4_fed_finetune_p10_sl_c","f4_fed_ewc_p5_sl_c","f4_fed_ewc_p10_sl_c","f4_fed_derpp_p5_sl_c","f4_fed_derpp_p10_sl_c"],
    "rf_e1": ["e1_clean_rf","e1_derpp_rf","e1_ewc_rf","e1_finetune_rf","e1_joint_rf","e1_lwf_rf"],
    "gh": ["e1_finetune_gh"],
    # Phase-3 grids (all chrono+frozen, SEEDS12); skip-if-exists resumes.
    "bz": ["bz_ft_sf_fedavg_c","bz_ft_sf_trim_c","bz_ft_sf_med_c","bz_ft_sf_krum_c","bz_ft_sf_trust_c","bz_ft_lie_fedavg_c","bz_ft_lie_trim_c","bz_ft_lie_med_c","bz_ft_lie_krum_c","bz_ft_lie_trust_c","bz_ft_mr_fedavg_c","bz_ft_mr_trim_c","bz_ft_mr_med_c","bz_ft_mr_krum_c","bz_ft_mr_trust_c","bz_ewc_sf_fedavg_c","bz_ewc_sf_trim_c","bz_ewc_sf_med_c","bz_ewc_sf_krum_c","bz_ewc_sf_trust_c","bz_ewc_lie_fedavg_c","bz_ewc_lie_trim_c","bz_ewc_lie_med_c","bz_ewc_lie_krum_c","bz_ewc_lie_trust_c","bz_ewc_mr_fedavg_c","bz_ewc_mr_trim_c","bz_ewc_mr_med_c","bz_ewc_mr_krum_c","bz_ewc_mr_trust_c","bz_ft_lie05_fedavg_c","bz_ft_lie05_trust_c","bz_ewc_lie05_fedavg_c","bz_ewc_lie05_trust_c"],
    "f2r": ["f2r_ft_p5_trim_c","f2r_ft_p5_med_c","f2r_ft_p5_krum_c","f2r_ft_p5_trust_c","f2r_ewc_p5_trim_c","f2r_ewc_p5_med_c","f2r_ewc_p5_krum_c","f2r_ewc_p5_trust_c"],
    "mech": ["f2_fed_ewc_p0_l0_c","f2_fed_ewc_p0_l1000_c"],
    "brk": ["f2_fed_ft_p5_m2_c","f2_fed_ft_p5_m3_c","f2_fed_ewc_p5_m2_c","f2_fed_ewc_p5_m3_c","f2_fed_ft_p20_c","f2_fed_ft_p40_c","f2_fed_ewc_p40_c"],
    "perst_sn": ["e2_persist_er_c","e2_persist_ft_c","e2_persist_ewc_c"],
    "perst_fed": ["f2_fed_ft_persist_p5_c","f2_fed_ewc_persist_p5_c"],
    "adapt": ["e2_adaptive_c","e6_adaptive_sl_c","e6_knnadapt_knn_c"],
    "trig": ["e3_grounded_c"],
    "ar": ["ar_ft_wide_clean_c","ar_ft_wide_p5_c","ar_ft_tr_clean_c","ar_ft_tr_p5_c","ar_ewc_wide_clean_c","ar_ewc_wide_p5_c","ar_ewc_tr_clean_c","ar_ewc_tr_p5_c","ar_derpp_wide_clean_c","ar_derpp_wide_p5_c","ar_derpp_tr_clean_c","ar_derpp_tr_p5_c"],
    # Phase-4 replication (UNSW u_, IoT i_; SEEDS12; fed groups dispatch wrapper).
    "u_e1": ["u_e1_clean","u_e1_derpp","u_e1_ewc","u_e1_finetune","u_e1_joint","u_e1_lwf"],
    "u_f2": ["u_f2_fed_finetune_p0","u_f2_fed_finetune_p1","u_f2_fed_finetune_p5","u_f2_fed_finetune_p10","u_f2_fed_ewc_p0","u_f2_fed_ewc_p1","u_f2_fed_ewc_p5","u_f2_fed_ewc_p10","u_f2_fed_derpp_p0","u_f2_fed_derpp_p1","u_f2_fed_derpp_p5","u_f2_fed_derpp_p10"],
    "u_f4": ["u_f4_fed_finetune_p5_sl","u_f4_fed_finetune_p10_sl","u_f4_fed_ewc_p5_sl","u_f4_fed_ewc_p10_sl","u_f4_fed_derpp_p5_sl","u_f4_fed_derpp_p10_sl"],
    "i_e1": ["i_e1_clean","i_e1_derpp","i_e1_ewc","i_e1_finetune","i_e1_joint","i_e1_lwf"],
    "i_f2": ["i_f2_fed_finetune_p0","i_f2_fed_finetune_p1","i_f2_fed_finetune_p5","i_f2_fed_finetune_p10","i_f2_fed_ewc_p0","i_f2_fed_ewc_p1","i_f2_fed_ewc_p5","i_f2_fed_ewc_p10","i_f2_fed_derpp_p0","i_f2_fed_derpp_p1","i_f2_fed_derpp_p5","i_f2_fed_derpp_p10"],
    "i_f4": ["i_f4_fed_finetune_p5_sl","i_f4_fed_finetune_p10_sl","i_f4_fed_ewc_p5_sl","i_f4_fed_ewc_p10_sl","i_f4_fed_derpp_p5_sl","i_f4_fed_derpp_p10_sl"],
}
FED_GROUPS = {"f2_ft", "f2_ewc", "f2_derpp", "f4_ft", "f4_ewc", "f4_derpp", "f2_b100", "c_f2", "c_f4", "bz", "f2r", "mech", "brk", "perst_fed", "u_f2", "u_f4", "i_f2", "i_f4"}
SEEDS7 = [1,2,3,4,5,6,42]
# Phase-2 step 9: n=12 — exact Wilcoxon min-p 0.00049 survives Holm in the
# largest family (chrono_single m=13 -> threshold 0.0038); locked 7 seeds
# contained, so locked-seed pairings stay valid subsets.
SEEDS12 = [1,2,3,4,5,6,7,8,9,10,11,42]
SEEDS12_GROUPS = {"c_e1","c_e2e3","c_e4","c_e6a2","c_a1","c_a3","c_f2","c_f4","gh","bz","f2r","mech","brk","perst_sn","perst_fed","adapt","trig","ar","u_e1","u_f2","u_f4","i_e1","i_f2","i_f4"}
group = sys.argv[1]
SEEDS = SEEDS12 if group in SEEDS12_GROUPS else SEEDS7
if group in FED_GROUPS:
    from src.federated.fedavg import run_federated as run
done, skipped = 0, 0
t0=time.time()
for name in GROUPS[group]:
    cfg = yaml.safe_load(find_config(name).read_text())
    if bool(cfg.get("fed")) != (group in FED_GROUPS):
        raise ValueError(f"Federated runner mismatch for group={group}, config={name}")
    for sd in SEEDS:
        out = RUNS_DIR/f"{name}_summary_seed{sd}.json"
        legacy = RESULTS_DIR/f"{name}_summary_seed{sd}.json"
        if out.exists() or legacy.exists():
            skipped += 1
            continue
        cfg["seed"]=sd
        r = run(cfg)
        save_results(r, cfg, RUNS_DIR)
        append_table(r, cfg, RESULTS_DIR)
        done += 1
        print(f"DONE {name} seed {sd} acc={r['summary']['acc']:.4f} wall={r['summary']['wall_sec']:.0f}s", flush=True)
print(f"group {group}: ran {done}, skipped {skipped}, elapsed {(time.time()-t0)/60:.1f} min")
