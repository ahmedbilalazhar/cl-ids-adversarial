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
  final seed count is zero. The new E4 chronology configs use the
  duplicate-disjoint task artifact; nine manifest-v3 exploratory diagnostics
  were current under `results/diagnostics/` until the Phase-D source change
  (preserved in `discovery_prefedcontrols_20260928/`).
- `results/_archive/discovery_pre_code_hash_20260928/` and
  `results/_archive/discovery_pre_asr_null_20260928/`: exploratory E4
  no-poison seed-1 R/summary/manifest/resource sets before runtime-source
  fingerprinting and undefined-ASR repair, respectively. Neither is a
  current completion manifest or a paired effect.
- `results/_archive/discovery_pre_commit_asr_20260928/`: 37 files from an
  earlier nine-seed E4 diagnostic whose source hash was superseded by
  undefined-ASR and buffer-poison fixes. All nine arms/seeds were rerun under
  source hash `94abb157…` and passed live manifest checks. They remain
  exploratory, with no final paired effect.
- `results/_archive/discovery_prefedcontrols_20260928/`: copy-preservation
  (39 files + SHA-256 manifest) of the nine live E4 diagnostics above, taken
  before the Phase-D federated-controls source change. The Phase-D change
  alters the manifest-v3 source fingerprint, so those nine no longer pass
  live checks; this archive is their record. The plain-FedAvg aggregation
  path itself is byte-unchanged (bit-identical), but no F2/F4 result may be
  cited under the new fingerprint without rerun.
- `results/_archive/order_rev_benign_dup_20260928/`: 24 `a3_order_rev_c`
  R/summary files. The task builder sampled the shared Monday-benign pool
  with one seed, duplicating identical benign rows across tasks whenever
  Monday was not first (reverse order). The builder now tracks consumed ids;
  the alt-order arm verified clean. Order-invariance claims await a rebuilt
  rev artifact and rerun.

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
