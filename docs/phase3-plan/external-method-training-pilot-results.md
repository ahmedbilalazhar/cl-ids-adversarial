# External method adapter pilot

**Status:** completed train-only execution; no held-out test metrics. The external test scoring gate remains closed.

## What ran

The isolated variable-input adapter reused the project's existing FT, EI, replay, admission, and importance routines. It trained a 128/64 MLP on each dataset's native schema and the existing four-task schedule. Each dataset used five persistent synthetic clients. The task-1 intervention relabeled half of one eligible synthetic client's selected source-class rows to benign; the client was withdrawn before task 2.

| Dataset | Input width | Paired arms | Train rows per four-task run | Task-1 source rows on attacker | Relabeled rows |
|---|---:|---:|---:|---:|---:|
| UNSW-NB15 | 194 | FT, EI, DR, DR+DC; clean and attacked | 175,341 | 11,480 | 5,740 |
| CICIoT2023 | 39 | FT, EI, DR, DR+DC; clean and attacked | 121,378 | 2,240 | 1,120 |

All arms used seed 101, three synchronization rounds per task, one epoch per round, batch size 128, CPU FP32, deterministic algorithms, and the versioned coefficients. This is a single-seed execution pilot, not a complete three-seed experiment. There are 16 arms and 64 task-stage checkpoints; recorded successful arm runtime totals 589.9 CPU seconds.

## What the result establishes

Every configured arm produced four task checkpoints and finite-value checks passed through the shared training routines. The per-arm JSON records training traces, learner settings, model hashes, dataset and input hashes, and checkpoint hashes. The summary inventory rechecks all expected arms, protocol/dataset/input hashes, checkpoint files, and the no-test boundary.

This establishes that the adapter can execute the training path on these input widths under the pilot configuration. It does **not** establish poisoning persistence, attack success, learning acquisition, defense efficacy, or generalization: no external test arrays were loaded and no held-out metric was computed. The client ownership is synthetic and does not represent physical owners or independent sessions. Results must not be described as a faithful replication of the primary CICIDS experiment.

## Reproduction and next gates

- Protocol: `configs/phase3/external-method-extension-v1.json`
- Runner: `scripts/run_phase3_external_method_trainpilot.py`
- Inventory builder: `scripts/summarize_phase3_external_method_pilot.py`
- Summary and source hashes: `results/phase3-followup/external-method-training-pilot-summary-v1.json`
- Per-arm traces and task checkpoints: `results/phase3-followup/external-method-training-pilot-v1/`
- Synthetic train-only client/poison masks: `results/phase3-followup/external-method-inputs-v2/`

Before extending the training seed set, document the single-seed limitations and freeze all implementation hashes. Before any external test scoring, implement and qualify a separate evaluator, resolve the limits of provider-pool IDs, freeze the analysis and failure policy, then record the protocol amendment. This pilot did not access the CICIDS2017 final-test package.
