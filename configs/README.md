# Configs

211 experiment configs in family subdirs. Every reported number must be
regenerable from one file here. Refer to configs by **bare name**
(`e1_clean`); `src/paths.py::find_config()` resolves the subdir, so grid
groups and the CLI keep working unchanged.

```
configs/
  baselines/    e1_* clean baselines (finetune, ewc, lwf, er, derpp, joint)
  label_flip/   e2_* stream, buffer, random 0.5%, 5%, adaptive, persist
  backdoor/     e3_* (+ grounded trigger)
  novelty/      e4_* vanilla, nopois, suppress, anchor
  defenses/     e6_* small-loss, kNN-consistency, kNN-adapt
  ablations/    a1/a2/a3_* buffer size, class-IL, task order
  federated/    f2_*, f2r_*, f4_* across methods × poison levels
  byzantine/    bz_* attacks (sf/lie/mr) × robust aggregators
  arch/         ar_* architecture sweep (thin/wide × clean/poisoned)
  mirrors/      u_* (UNSW-NB15) / i_* (IoT) dataset mirrors
```

## Naming convention

```
[<dataset>_]<exp>[_<method>][_p<poison_pct>][_sl][_b<buffer>][_m<arch>][_l<ewc_lambda>][_c|_rf|_gh]
```

| Token | Meaning |
|-------|---------|
| `e1…e6`, `a1…a3` | experiment / ablation family (see table) |
| `f2`, `f4` | federated variants (F2 cross-silo, F4 single-loss) |
| `f2r`, `bz`, `ar` | robust-federated, Byzantine, architecture sweeps |
| `ft`, `ewc`, `derpp`, `er` | CL method override |
| `_p0/_p1/_p5/_p10…` | poison percentage |
| `_sl` | single-loss (F4) |
| `_c` / `_rf` / `_gh` | chrono+frozen (primary) / random+frozen / growing-head |
| `u_` / `i_` prefix | UNSW-NB15 / IoT dataset mirror (same grid, different `data.tasks`) |

## Families

| Prefix | Experiment |
|--------|-----------|
| `e1_*` | clean baselines (finetune, ewc, lwf, er, derpp, joint oracle) |
| `e2_*` | label-flip: stream, buffer, random 0.5%, 5%, adaptive, persist |
| `e3_*` | backdoor (+ grounded trigger) |
| `e4_*` | novelty poisoning: vanilla, nopois, suppress, anchor |
| `e6_*` | defences: small-loss, kNN-consistency, kNN-adapt |
| `a1/a2/a3_*` | ablations: buffer size, class-IL, task order |
| `f2_*` | federated F2 across methods × poison levels |
| `f4_*` | federated F4 single-loss |
| `bz_*` | Byzantine attacks (sf/lie/mr) × robust aggregators |
| `ar_*` | architecture sweep (thin/wide × clean/poisoned) |

## Grid groups (`scripts/run_grid.py` GROUPS)

Run a whole group with skip-if-exists resume:

```bash
CL_THREADS=2 python scripts/run_groups.py c_e1 c_e2e3
# or: bash scripts/reproduce.sh c_e1
```

| Group | Contents |
|-------|----------|
| `e1`, `e2e3`, `e4`, `e6a2` | phase-1 sweeps (original seeds) |
| `c_e1`, `c_e2e3`, `c_e4`, `c_e6a2`, `c_a1`, `c_a3` | chrono+frozen primary suite (12 seeds) |
| `c_f2`, `c_f4` | federated chrono+frozen (dominates wall time — run last) |
| `rf_e1`, `gh`, `scaler_abl`, `f2_b100` | random+frozen, growing-head, scaler ablations |
| `bz`, `f2r`, `mech`, `brk` | Byzantine + robust + mechanism ablations |
| `perst_sn`, `perst_fed`, `adapt`, `trig`, `ar` | persistence, adaptive attacks, triggers, architecture |
| `u_e1`, `u_f2`, `u_f4` / `i_e1`, `i_f2`, `i_f4` | UNSW-NB15 / IoT mirrors |

Full paper order: `c_e1 rf_e1 gh c_e2e3 c_e4 c_e6a2 c_a1 c_a3 c_f2 c_f4 bz f2r mech brk perst_sn perst_fed adapt trig ar`
(see `scripts/reproduce.sh` header).
