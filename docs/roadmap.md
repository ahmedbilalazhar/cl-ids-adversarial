# Improvement roadmap (2026-09-28)

Source of requirements: `docs/plan.md`. Source commit is still
`9e635aef56c2a48d0c2937d172069a621eb753df` on `main`; the worktree has
uncommitted changes. The 211-config baseline inventory is in `docs/inventory.md`; 214
YAML configs currently pass the preflight validator. `docs/invalidation_table.md`
records artifact impact. Do not launch the full grid from this roadmap.

| Phase | Current state | Evidence and next gate |
|---|---|---|
| A: execution/results | Implemented; synthetic exit gate tested | Transactional manifests and all-config preflight are present. New v3 manifests include a hash of all runtime `src/*.py`, including uncommitted files; a seed fails if code changes during execution. Earlier v2 diagnostics remain exploratory with `pre-code-hash` provenance. Main results contain zero validated seeds. Clean reproduction remains a Phase H gate. |
| B: data semantics | Implemented and audited in part | Duplicate-disjoint CICIDS audits at zero exact train/test content matches. UNSW has 3,723 and IoT 604 cross-pool matches; exclude both from final claims until deduped. Raw IoT parquets are unavailable locally, so capped-build peak RSS is pending. |
| C: attacks and endpoints | E3 corrected; E4 causal implementation and synthetic checks; one v3 no-poison diagnostic | E4 fits AE on benign training flows, calibrates separately, clusters a seeded cap of training candidates, maps provisional IDs into classifier training, and assigns held-out flows against frozen cluster geometry. A direct-label-poison control exists. Historical E4/E5 outputs are archived. FWT is null until measured. E4 no-poison seed 1 is code-hashed exploratory evidence (116 s, 895 MB sampled peak RSS); no paired effect. Packet-to-flow E3 validation, attack-family probes, capped-cluster sensitivity, and broad dose review remain. |
| D: controls | Pending | Stable-client and multi-round sensitivity, per-client accounting, same-aggregator clean controls, optimizer/replay audit, and honest description of the single-token transformer. |
| E: prespecified inference | Pending | Write machine-readable comparison families and endpoints before selected 12-paired-seed runs. Investigate anomalous federated seed, record resource use, run selected arms, then rebuild statistics and claims. Current six validated CICIDS seeds are diagnostics only. |
| F: performance | Pending | Profile replay, kNN/HDBSCAN, inference batching, and IoT ingestion; quantify any numerical changes. |
| G: production path | Pending | Current deployment numbers are a random-model software proxy. Export and benchmark a trained, versioned preprocessing/model bundle before any inference claim. |
| H: paper/release | Pending | Strict lint still has broader debt. Build a claim ledger, reconcile stale prose, pin dependencies/container, and reproduce a table and figure in a clean environment. |

## Current evidence boundary

- Main `results/runs/`: zero completion manifests; no current final paper
  comparisons or completed Holm families.
- `results/diagnostics/runs/`: six validated finetune seeds, three each for
  T0-only and duplicate-disjoint CICIDS. They use different populations and
  leakage controls and are not a causal head-to-head result.
- `results/_archive/backdoor_protocol_20260928/`: 38 historical E3 seed files
  and a SHA-256 manifest. The prior ASR 1.0 statement is invalid.
- `results/_archive/discovery_transductive_20260928/`: 157 historical E4/E5
  files and checksum manifest. Their reported absorption and classifier effects
  are invalid. `results/_archive/discovery_pre_code_hash_20260928/` retains
  the first no-poison E4 diagnostic and its measured resource record.
- `results/diagnostics/runs/`: one manifest-v3 E4 no-poison seed (seed 1)
  is exploratory. Its per-task metrics record a high unweighted discovery miss
  mean of 0.755 across tasks with attacks. This is a baseline warning, not a
  poisoning effect estimate.
- `results/diagnostics/e4_cluster_cap_4000_of_5000.json`: on a 5,000-row
  seeded training-candidate subset of task 2, fitting 4,000 versus all 5,000
  yielded 103 versus 126 clusters and adjusted Rand index 0.628. Peak
  process-tree RSS for this probe was 539 MB. This demonstrates material
  decision changes; E4 must be described as a capped discovery protocol,
  not equivalent to uncapped HDBSCAN on 125,570 novel task-2 candidates.
- A corrected E3 dataset run, full 12-paired-seed comparison, capped IoT
  build resource measurement, and Colab measurement have not been executed.

## Next implementation order

1. Preserve the Phase A synthetic exit gate; finish Phase B IoT memory
   measurement when raw parquets are available, and keep UNSW/IoT out of final
   claims meanwhile.
2. Inspect the v3 E4 no-poison diagnostic. Run small anchor/no-poison/direct
   label-control probes, then check capped-cluster sensitivity and high
   baseline miss rate. Verify E3 packet-to-flow values. FWT remains N/A.
3. Write Phase E analysis specification and selected comparison list, after
   Phase D controls are explicit. Run small probes, inspect resource use, then
   launch selected 12-seed experiments with `CL_THREADS=2` and `--resume`.
4. Rebuild validated tables, statistics, and figures; populate a claim ledger
   and update the manuscript only from those artifacts.

## Resumable commands after the stated gates

These are prepared commands, not completed runs. On the CPU laptop, run one
seed at a time and measure memory before adding workers. The first selected
comparison is the two existing CICIDS sensitivity arms; do not interpret it
as a controlled scaler-only comparison because the populations differ.

```powershell
$env:CL_THREADS = "2"
foreach ($seed in @(1,2,3,4,5,6,7,8,9,10,11,42)) {
    python -m src.run_experiment --config configs/baselines/e1_finetune_dedup.yaml --seed $seed --results-dir results --resume
    python -m src.run_experiment --config configs/baselines/e1_finetune_t0.yaml --seed $seed --results-dir results --resume
}
python -m src.run_experiment --rebuild-table --results-dir results
python scripts/stats_summary.py --results-dir results
```

For corrected E3, first complete packet-to-flow validation and a three-seed
diagnostic in `results/diagnostics/`, then use the same seed loop with
`configs/backdoor/e3_backdoor_c.yaml` and the prespecified clean comparator.
The old E3 files cannot be resumed as valid results.

For E4, after inspecting the baseline miss rate and candidate-cap sensitivity,
the next bounded comparison is no poison, anchor poison, and direct-label
poison control on the same duplicate-disjoint task artifact. These commands
are pending, not completed:

```powershell
$env:CL_THREADS = "2"
foreach ($seed in @(1,2,3)) {
    python -m src.run_experiment --config configs/novelty/e4_novelty_nopois_c.yaml --seed $seed --results-dir results/diagnostics --resume
    python -m src.run_experiment --config configs/novelty/e4_novelty_anchor_c.yaml --seed $seed --results-dir results/diagnostics --resume
    python -m src.run_experiment --config configs/novelty/e4_novelty_label_control_c.yaml --seed $seed --results-dir results/diagnostics --resume
}
```

The version-3 no-poison seed took 116.0 s and 895.3 MB sampled process-tree
peak RSS on an 8-logical-CPU, 31.8 GB RAM Windows host (`CL_THREADS=2`).
The nearly identical pre-v3 run was archived (121.7 s, 864.4 MB). Neither
establishes Colab performance or a paired effect. The capped IoT raw parquets
are absent locally, so its builder's peak RSS remains unmeasured.
