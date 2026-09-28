# Phase-0 invalidation table — what must be archived + rerun on scientific change

Rule: **never overwrite an invalidated result or silently combine it with a new protocol.**
Archive with SHA-256 hashes + `superseded_by` reason (as done for
`results/_archive/prefix0/`, `a2_bugfix/`, `dispatch_bug_20260927/`,
`architecture_cpu_pre_gpu/`); rerun before citing. Keep the FedAvg path
bit-identical unless a parity test + versioned replacement justifies change
(decisions #38, #52).

| Change surface | Invalidates (archive + rerun) | Unaffected (kept) | superseded_by reason template |
|---|---|---|---|
| labels / cleaning (`src/data/clean.py`, label map, Thursday repair) | ALL configs (every task file changes row identity) | nothing | `labels-clean-<date>: <what changed>` |
| preprocessing / splits / scaler (`src/data/sequence.py`, `tasks*.npz`, frozen vs per-task, chrono vs random, flow_order) | all configs on the rebuilt task file; scaler change = all CICIDS configs (cf. decisions #49: ranking inverted) | other datasets' task files | `preproc-<taskfile>-<date>: <split/scaler change>` |
| attack application (`src/attacks/*`, budgets, modes, trigger values, persistent/adaptive) | configs carrying that attack type/mode (incl. federated shards via `_poison_shard`) | clean baselines, other attack families | `attack-<type/mode>-<date>: <change>` |
| discovery (`src/discovery/*`, AE threshold, HDBSCAN, novelty poison) | E4/E5 + any config with `attack.type=novelty`; E5 JSONs | classifier-only E1/E2/E3/F2 | `discovery-<date>: <change>` |
| evaluation (`src/metrics.py`, `summarize`, ASR definitions, R layout) | derived tables only (`baseline_table`, `stats_summary`, `wilcoxon`, figures) — rebuild from intact per-seed files; per-seed files get `eval-` suffix note but are NOT deleted | per-seed R/summary payloads (re-derive) | `eval-<date>: <metric change>; per-seed retained, tables rebuilt` |
| federation (`src/federated/*`, partition, broadcast, FedAvg vs delta path, robust rules, EWC anchor sync) | all `fed:` configs for that code path; robust-rule change = only that aggregator; FedAvg locked path = NO change without parity test | single-node configs | `fed-<path>-<date>: <change>` |
| defenses (`src/defenses/*`, keep_ratio, kNN) | configs carrying that defense (+ adaptive attackers targeting it) | undefended baselines | `defense-<type>-<date>: <change>` |
| model/arch (`src/models/*`, `src/cl/*`, hyperparams in config) | configs with that `cl_method`/`arch`/hyperparam | other methods/archs | `model-<method/arch>-<date>: <change>` |
| infra only (reporting/manifest, grid drivers, status/stats/table code, notebook paths, lint) | NOTHING scientific — but all *future* runs gain manifests; old unmanifested files stay `executed, not validated` until rerun | all existing numbers stand as executed artifacts | `infra-<date>: no numeric change; manifests from here on` |

2026-09-28 execution of this table:

- `results/_archive/label_fix_20260928/`: 422 UNSW/IoT R/summary files;
  labels and poisoning targets were corrected. Their comparisons are pending.
- `data/_archive/label_fix_20260927/`: old UNSW task NPZ/sidecar.
- `results/_archive/ci_filter_20260927/`: 14 class-IL R/summary files;
  `filter_ci` had substituted labels for test features.
- `results/_archive/derived_pre_manifest_20260927/`: three aggregate CSVs
  built from unmanifested results.
- `data/_archive/dedup_pre_postscale_20260928/`: first v2 duplicate arm;
  five post-scaling content matches remained. Its successor excludes six
  test matches against all training tasks and audits at zero.
- `results/_archive/backdoor_protocol_20260928/`: 38 historical E3 backdoor
  R/summary files. Training ignored the configured trigger, raw values were
  placed in scaled feature space, and absent PortScan tasks were incorrectly
  scored against all test rows. All three E3 configs now point to the separate
  v2 duplicate-disjoint task artifact; their old numerical claims are invalid.
- `results/_archive/discovery_transductive_20260928/`: 157 E4 R/summary
  files, E5 JSONs, and related figures. E4 fitted clusters on training plus
  held-out test flows after classifier training, so neither its cluster
  endpoint nor an attributed classifier effect is valid. Corrected E4/E5
  seed count is zero. The new E4 chronology configs use the duplicate-disjoint
  task artifact and require new manifests.
- `results/_archive/discovery_pre_code_hash_20260928/` and
  `results/_archive/discovery_pre_asr_null_20260928/`: exploratory E4
  no-poison seed-1 R/summary/manifest/resource sets before runtime-source
  fingerprinting and undefined-ASR repair, respectively. Neither is a
  current completion manifest or a paired effect. A repeated seed-1
  diagnostic uses manifest v3 and the final endpoint definition.

These archives contain SHA-256 manifests with `superseded_by` reasons.
The duplicate-disjoint arm has a distinct protocol and config; it does not
retroactively validate legacy CICIDS results. A change to evaluation logic
invalidates any derived summary fields and completion manifests affected by
those fields, not just aggregate CSVs; rederive or rerun before citing.
The cleaned CICIDS parquet retains many duplicate model-input rows within
and across original CSV files because the legacy cleaner deduplicated before
dropping identifiers; see `docs/cicids_cross_file_audit.md`.

FedAvg lock: `src/federated/fedavg.py` keeps weighted model-averaging for plain
FedAvg; robust rules + update-attacks use the delta path. Any unification
requires (a) seed-matched parity test bit-identical on F2/F4, (b) versioned
replacement + archive of prior outputs with `superseded_by: fedavg-unify-<date>`.
Threading (`CL_THREADS`, `limit_threads`, `n_jobs=1`) is part of the repro
contract: never compare across thread settings (decision #52).
