# Project cleanup log — 2026-11-18

Cleanup was limited to generated archives that had been superseded by the validated v28 evidence package, plus one byte-identical temporary qualification bundle. Validation records and historical result files were retained.

## Removed superseded evidence archives

| Removed archive | Bytes | SHA-256 |
|---|---:|---|
| `23I-2568_23I-2581-full-evidence-v16.zip` | 561,086,604 | `caf51cf16afc52ca5054cb5666e90640b81288710e417080f72c96a86cf33e09` |
| `23I-2568_23I-2581-full-evidence-v26.zip` | 561,677,623 | `7dd234a9473111b88d047d42dd01cae4917f144cc9e9a3fb10644e5eb03e8bce` |
| `23I-2568_23I-2581-full-evidence-v27.zip` | 561,711,752 | `d21ed0ec5a1e19f2caaebb3edea3770cdbacfd72fd319456d7b3f0302fea8510` |
| `23I-2568_23I-2581-full-evidence.zip` | 148,324,469 | `7a745cdd449724a7ef926b8165ff7868fbe2ef97b6fa7ea7a03fc3e473f6ee38` |

The retained [v28 archive](23I-2568_23I-2581-full-evidence-v28.zip) is 561,728,412 bytes, SHA-256 `e427c77383923201441f897ef7609986ddeb824cdaf8b018cf15f30d022d126a`; its validation record reports all 6,629 member hashes valid. The per-version validation JSON files for the removed archives remain. The archive manifest was updated to record removals.

## Removed exact temporary duplicate

Removed `tmp/phase3-reliability-audit-v2/upload-emulation/qualification.zip` (51,767,791 bytes). Its SHA-256 matched the retained canonical `results/phase3-two-hour-audit-v1/candidate-v5/bundle-final/qualification.zip`: `51fa652d5b47de0d2e7935b861988ac7ed7d1abd8526fb2d82196ff23527fa7b`.

Removed the byte-identical temporary copy of `phase3-implementation/results/final-run/part-b-experiment-runs.zip` (1,855,388 bytes); the canonical copy and the rest of the portability evidence remain.

Also removed the empty `results/phase3-dg-baseline-v1/` directory. It contained no files and had no project references; the failed-run record, if any, remains in the audit notes.

Removed stale `execution.lock` files from the incomplete DG v2 and v3 attempts after confirming their recorded PIDs (25356 and 25260) were not running. The incomplete result records, hashes, and partial checkpoints remain preserved and explicitly excluded from analysis.

Pruned **493 files (328,568,521 bytes)** from `tmp/phase3-portable-check/23I-2568_23I-2581/` only where each file’s size and SHA-256 exactly matched a same-relative-path project file. Unique or changed files and all archives were retained. The removed-path/hash map is in `results/phase3-rigorous-audit-v1/portable-check-pruning-v1.json`; the extraction folder is now a partial evidence snapshot rather than a runnable package. The source archives remain available, and the reliability auditor now prefers its retained executed-source snapshot before consulting the temporary extraction.

Removed **21 uploaded-emulation NumPy copies (142,862,657 bytes)** from `tmp/phase3-reliability-audit-v2/upload-emulation/phase3-v5/project/inputs/` after verifying each against the canonical `data/processed/phase3-reference74-v1/` array by size and SHA-256. Their complete copy-to-source hash map is in `results/phase3-rigorous-audit-v1/temp-data-pruning-v1.json`.

Removed **14 older generated before-update ZIP snapshots (151,377,958 bytes)** from `tmp/phase3-submission-update/`. The latest recovery ZIP, historical report PDF, and all canonical submission archives remain. The removed archive paths, byte sizes, and hashes are recorded in `results/phase3-rigorous-audit-v1/submission-update-pruning-v1.json`.

Removed the superseded `tmp/phase3-upload-preflight/phase3-before-overnight.zip` (59,952,799 bytes; SHA-256 `65a89e5fbab16d062b9810b0d96c4ae0872d19c9f3d0c6a0a1bdc73a3e5efda7`). The canonical overnight baseline, current source files, and later preflight candidate remain; its archive digest record is in `results/phase3-rigorous-audit-v1/preflight-backup-prune-v1.json`.

Removed the obsolete `tmp/phase3-upload-preflight/23I-2568_23I-2581.zip` candidate (61,178,370 bytes; SHA-256 `75b0ecd323601207407437b10a0d87fcf5c4f36364ec1785183a7b12f73663ef`). Original, current phase3-final, and validated v28 submission archives remain. Its digest record is in `results/phase3-rigorous-audit-v1/preflight-candidate-prune-v1.json`.

## Preserved

Raw datasets, transformed feature files, current submission archives, historical experiment outputs and validation evidence, the pinned Python environment, the incomplete DG attempt records, and the active adaptation-capacity experiment were not removed. Several similarly named qualification bundles have different hashes and were retained. The original and domain-checked feature arrays also have different hashes, so neither was treated as a duplicate.

Total space reclaimed by this cleanup: **2,630,363,942 bytes** (about 2.45 GiB).
