"""Grid driver: run one group of configs at n=7 seeds (1,2,3,4,5,6,42).
Skips (config,seed) pairs whose summary file already exists in results/, so
interrupted runs resume cleanly without repeating work.
Usage: python scripts/run_grid.py <group>  (groups: e1, e2e3, e4, e6a2,
  f2_ft, f2_ewc, f2_derpp). f2_* groups run the federated wrapper
  (src/federated/fedavg.py); all others run single-node src/run_experiment.py.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml, time
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
}
FED_GROUPS = {"f2_ft", "f2_ewc", "f2_derpp", "f4_ft", "f4_ewc", "f4_derpp", "f2_b100", "c_f2", "c_f4"}
SEEDS7 = [1,2,3,4,5,6,42]
# Phase-2 step 9: n=12 — exact Wilcoxon min-p 0.00049 survives Holm in the
# largest family (chrono_single m=13 -> threshold 0.0038); locked 7 seeds
# contained, so locked-seed pairings stay valid subsets.
SEEDS12 = [1,2,3,4,5,6,7,8,9,10,11,42]
SEEDS12_GROUPS = {"c_e1","c_e2e3","c_e4","c_e6a2","c_a1","c_a3","c_f2","c_f4","gh"}
group = sys.argv[1]
SEEDS = SEEDS12 if group in SEEDS12_GROUPS else SEEDS7
if group in FED_GROUPS:
    from src.federated.fedavg import run_federated as run
done, skipped = 0, 0
t0=time.time()
for name in GROUPS[group]:
    cfg = yaml.safe_load((ROOT/f"configs/{name}.yaml").read_text())
    for sd in SEEDS:
        out = ROOT/f"results/{name}_summary_seed{sd}.json"
        if out.exists():
            skipped += 1
            continue
        cfg["seed"]=sd
        r = run(cfg)
        save_results(r, cfg, ROOT/"results")
        append_table(r, cfg, ROOT/"results")
        done += 1
        print(f"DONE {name} seed {sd} acc={r['summary']['acc']:.4f} wall={r['summary']['wall_sec']:.0f}s", flush=True)
print(f"group {group}: ran {done}, skipped {skipped}, elapsed {(time.time()-t0)/60:.1f} min")
