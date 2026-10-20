# Improvement roadmap (2026-09-28)

Source of requirements: `docs/plan.md`. Current `main` is
`a4558b582a46352bc8f3708af3ce09aeadb8ef49`; the plan's reference commit
was `9e635aef56c2a48d0c2937d172069a621eb753df`. The 211-config baseline inventory is in `docs/inventory.md`; 214
YAML configs currently pass the preflight validator. `docs/invalidation_table.md`
records artifact impact. Do not launch the full grid from this roadmap.

| Phase | Current state | Evidence and next gate |
|---|---|---|
| A: execution/results | Implemented; synthetic exit gate tested | Transactional manifests and all-config preflight are present. New v3 manifests include a hash of all runtime `src/*.py`, including uncommitted files; a seed fails if code changes during execution. Earlier v2 diagnostics remain exploratory with `pre-code-hash` provenance. Main results contain zero validated seeds. Clean reproduction remains a Phase H gate. |
| B: data semantics | Implemented, audited, and reproduction-proven | Duplicate-disjoint CICIDS audits at zero exact train/test content matches. Both v2 artifacts rebuild bit-identically under the fixed builder (temp rebuild, all arrays incl. ids). UNSW has 3,723 and IoT 604 cross-pool matches; exclude both from final claims until deduped. Both IoT parquets are present locally; the capped build was measured at 107 s wall / 3.2 GB sampled peak RSS (fixed chunk-consolidating builder) on the 31.8 GB host — inside the ~15 GB Colab budget with headroom, unlike the 11.3 GB pre-fix peak. |
| C: attacks and endpoints | E3 corrected; E4 causal implementation and nine code-hashed exploratory seeds | E4 fits AE on benign training flows, calibrates separately, clusters a seeded cap of training candidates, maps provisional IDs into classifier training, and assigns held-out flows against frozen cluster geometry. A direct-label-poison control exists. Historical E4/E5 outputs are archived. FWT is null until measured. Three-seed score audits show inverted T1 discrimination (AUC 0.120–0.128); three 5,000-versus-4,000 cap checks show ARI 0.628–0.728. See `docs/e4_detector_cap_audit.md`. Detector redesign, larger cap/downstream sensitivity, packet-to-flow E3 validation, and broad dose review remain. No final paired effect is established. |
| D: controls | Per-client logging implemented + synthetic-tested; matched controls pending | `run_federated` records pre/post-defense counts, class mix, participation, optimizer steps, buffer occupancy/bytes, and comm bytes per client-task; inactive submissions are excluded from unweighted rules with exclusions recorded (`tests/test_fedcontrols.py`, 16 passed). Stable-partition variant (`fed.partition: stable`, id-hash site proxy) and multi-round mechanism (`fed.rounds`, poison-once + per-round work rows, legacy path untouched for rounds=1) implemented and tested. Synthetic round probe: steps scale exactly 3x, comm stable, buffer capped (diagnostic only). Plain-FedAvg path is byte-unchanged. Work-matched multi-round study and same-aggregator clean controls remain, and stay gated in `docs/analysis_spec.json`. |
| E: prespecified inference | Spec written (`docs/analysis_spec.json`: 27 families, 200 pairs); runs pending | Generated from `WILCOXON_FAMILIES` + group seed protocol without reading results: two-sided Wilcoxon, Holm-within-family, MIDs 0.02/0.01, gates 105 ready / 42 controls / 46 dedup / 6 detector / 1 extractor. Six CICIDS finetune seeds are manifest-v2 checked diagnostics only. |
| F: performance | IoT ingestion profiled, fixed, measured; replay/kNN/HDBSCAN profiling pending | Per-batch RSS bisect found ~10k few-row DataFrame chunks accumulating to 11.3 GB peak; periodic per-group consolidation (`CONSOLIDATE_EVERY=20`) cut the capped build to 3.2 GB / 107 s with bit-identical output (`tests/test_data_tasks.py`). Replay-list, kNN/HDBSCAN, and inference-batching profiling remain. |
| G: production path | Inference contract implemented + tested; benchmark pending | `src/inference.py` exports/loads versioned trained bundles with weight hashes, strict schema validation, counted imputation, batch bounds, explicit abstention, and latency metrics (`tests/test_inference.py`, 5 passed) plus hash-chained versioning with fail-closed rollback. E8 random-model numbers stay a software proxy. A trained T0 bundle was benchmarked on this host (19,087 params, p50 0.39ms, 31k sps; exploratory, in `results/diagnostics/`). Monitoring design and real-federation spec remain. |
| H: paper/release | Pending | Strict lint still has broader debt. Build a claim ledger, reconcile stale prose, pin dependencies/container, and reproduce a table and figure in a clean environment. |

## Current evidence boundary

- Main `results/runs/`: zero completion manifests; no current final paper
  comparisons or completed Holm families.
- `results/diagnostics/runs/`: six manifest-v2 checked finetune seeds, three each for
  T0-only and duplicate-disjoint CICIDS. They use different populations and
  leakage controls and are not a causal head-to-head result.
- `results/_archive/backdoor_protocol_20260928/`: 38 historical E3 seed files
  and a SHA-256 manifest. The prior ASR 1.0 statement is invalid.
- `results/_archive/discovery_transductive_20260928/`: 157 historical E4/E5
  files and checksum manifest. Their reported absorption and classifier effects
  are invalid. `results/_archive/discovery_pre_code_hash_20260928/` retains
  the first no-poison E4 diagnostic. `discovery_pre_asr_null_20260928/` and
  `discovery_pre_commit_asr_20260928/` retain subsequent diagnostics whose
  source hashes no longer match the current tree.
- `results/diagnostics/runs/`: nine E4 seeds (three each for no
  poison, anchor poison, and direct-label poison) passed live checks against
  source hash `94abb157…` and remain exploratory. Their ACC
  means are 0.521883, 0.530564, and 0.554113 respectively. The mean pooled
  attack absorption is 0 for no poison and 0.000935 for both poison arms;
  these are descriptive values, not a final paired effect. NOTE 2026-09-28:
  the Phase-D source change altered the manifest-v3 fingerprint, so these
  nine no longer pass live checks (0/9); their copy-preserved record with
  SHA-256 manifest is
  `results/_archive/discovery_prefedcontrols_20260928/`. Seed-1 no-poison
  discovery miss is 0.755 across attack-containing tasks, including 0.998
  at T1.
- `results/diagnostics/e4_cluster_cap_4000_of_5000.json`: on a 5,000-row
  seeded training-candidate subset of task 2, fitting 4,000 versus all 5,000
  yielded 103 versus 126 clusters and adjusted Rand index 0.628. Peak
  process-tree RSS for this probe was 539 MB. This demonstrates material
  decision changes; E4 must be described as a capped discovery protocol,
  not equivalent to uncapped HDBSCAN on 125,570 novel task-2 candidates.
- A corrected E3 dataset run, full 12-paired-seed comparison, capped IoT
  build resource measurement, and Colab measurement have not been executed.
- Order invariance: the reverse-order arm is invalid (builder duplicated
  Monday-benign rows across tasks; 24 files archived, builder fixed, pair
  gated `gated-rev-rebuild` in the spec). The alt-order arm verified clean.

## Next implementation order

1. Preserve the Phase A synthetic exit gate; finish Phase B IoT memory
   measurement when raw parquets are available, and keep UNSW/IoT out of final
   claims meanwhile.
2. Use `docs/e4_detector_cap_audit.md` to decide whether the current E4
   discovery endpoint is viable. Its T1 score ranking is inverted and the
   4,000-candidate cap changes clusters on all three sampled references.
   Family-level score analysis, a separately specified detector protocol,
   larger cap/downstream sensitivity, and E3 packet-to-flow validation remain.
   FWT remains N/A.
3. `docs/analysis_spec.json` now holds the prespecified families/endpoints
   (write Phase E spec: done). New group `c_f2x` (dedup-baseline, stable,
   2-round finetune arms) is validated at 0/36 TODO for the matched
   sensitivity comparison; spec family and runs pending. Run small probes,
   inspect resource use, then launch selected 12-seed experiments with
   `CL_THREADS=2` and `--resume`, only for gate-cleared families.
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

For E4, the bounded three-arm, three-seed diagnostic below has completed on
the duplicate-disjoint task artifact. It can be resumed to verify its
manifest-backed outputs; a 12-seed comparison awaits the detector and cap
gates:

```powershell
$env:CL_THREADS = "2"
foreach ($seed in @(1,2,3)) {
    python -m src.run_experiment --config configs/novelty/e4_novelty_nopois_c.yaml --seed $seed --results-dir results/diagnostics --resume
    python -m src.run_experiment --config configs/novelty/e4_novelty_anchor_c.yaml --seed $seed --results-dir results/diagnostics --resume
    python -m src.run_experiment --config configs/novelty/e4_novelty_label_control_c.yaml --seed $seed --results-dir results/diagnostics --resume
}
```

The current-source seed-1 resource probes took 144.2 s / 862.3 MB (no poison),
145.6 s / 863.9 MB (anchor), and 124.7 s / 895.0 MB (direct-label control)
sampled process-tree peak RSS on an 8-logical-CPU, 31.8 GB RAM Windows host
(`CL_THREADS=2`). These do not establish Colab performance. The capped IoT
build (both parquets present locally) was measured at 107 s wall / 3.2 GB
sampled peak RSS with the fixed builder (was 11.3 GB before chunk
consolidation); the artifact rebuilds bit-identically.
