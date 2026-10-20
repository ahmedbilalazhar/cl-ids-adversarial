# Release bundle contents — git-ignored preservation artifacts

Generated 2026-09-29T02:18:56.329203+00:00 at commit `a4558b582a46352bc8f3708af3ce09aeadb8ef49` by
`python scripts/write_bundle_inventory.py`. Every path below is
git-ignored and MUST be copied explicitly into any release bundle;
a bundle without them is incomplete. Hashes are of the manifests
and snapshot zips as found on this host.

## Result/data archives

### `results/_archive/architecture_cpu_pre_gpu`

- files: 2
- manifest sha256: `3c6c4c59f51b26474ed2db00d6319237638bf88e060a1a090e3917af39810ff8`
- created: 
- reason: (legacy list manifest)

### `results/_archive/backdoor_protocol_20260928`

- files: 38
- manifest sha256: `c9351472dda929250d637be51afec8a3856f55f64ceec0ff228c364be3d148f7`
- created: 2026-09-28T07:12:18.385293+00:00
- reason: backdoor-20260928: legacy trigger training/evaluation mismatch, unscaled raw values, and invalid ASR fallback; rerun with v2 dedup task artifact

### `results/_archive/ci_filter_20260927`

- files: 14
- manifest sha256: `0fdd8778bce9e18512b5632a8048f7ce679036a30c44cf0f3508441c3b4c811b`
- created: 2026-09-27T17:19:09.128535+00:00
- reason: CI test-feature filtering bug fixed in src/tasks.py; rerun before citation

### `results/_archive/derived_pre_manifest_20260927`

- files: 3
- manifest sha256: `fa6e4bd639df125eb0316338d908acdf98944496cb1c74ef531cbcbf3123d88c`
- created: 2026-09-27T17:19:10.287216+00:00
- reason: Aggregates contained unmanifested and superseded UNSW/IoT/CI runs; rebuild from validated manifests

### `results/_archive/discovery_pre_asr_null_20260928`

- files: 4
- manifest sha256: `70006d9afbfc6c38de70c2fd745a8365c3dc7c4e8f28708943a410148ffa26a5`
- created: 2026-09-28T08:36:20.039449+00:00
- reason: eval-20260928: changed undefined ASR from numeric zero to null after E4 seed; manifest-v3 source hash no longer matches, so preserve and rerun

### `results/_archive/discovery_pre_code_hash_20260928`

- files: 4
- manifest sha256: `40d2d0a8bdfe76e871f87c33832f4eef8290a09cd422504093397b931a632ecd`
- created: 2026-09-28T08:26:06.262533+00:00
- reason: discovery-20260928: first no-poison diagnostic preceded attack-dose logging and source-tree fingerprint; keep measurement but rerun under manifest v3

### `results/_archive/discovery_pre_commit_asr_20260928`

- files: 37
- manifest sha256: `602350bf8e2c1ffd1057cf4f1156923da89e1f39a6aa28b065b1cb3f4b454bba`
- created: 2026-09-28T11:55:17.625814+00:00
- reason: Nine E4 diagnostics ran under source-tree hash b8081e8; subsequent ASR-null and buffer-poison fixes changed src/runner.py and src/federated/fedavg.py. Current source hash 94abb157 invalidates live v3 checks; preserve outputs and rerun.

### `results/_archive/discovery_prefedcontrols_20260928`

- files: 39
- manifest sha256: `bb486f416f775192771ba58c5d93ee56acff880f0f80b1140f7f6862bcee7ba0`
- created: 2026-09-28T13:24:56.199310+00:00
- reason: pre-Phase-D preservation copy; live against source_tree 94abb1576b44e9d5c52bc70a05b1b1688fd06f0d60458111fba9d83395668dfb at copy time; originals retained in results/diagnostics until a src change invalidates them

### `results/_archive/discovery_transductive_20260928`

- files: 157
- manifest sha256: `50ae5b5ee274367bfbb7a972893ed68660a5e31c18fa8f9e3d3a00f3dbb37771`
- created: 2026-09-28T08:04:53.549589+00:00
- reason: discovery-20260928: E4 joint train/test clustering was transductive and post-training; E5 discovery endpoints inherited the legacy interpretation; rerun causal train-only protocol

### `results/_archive/label_fix_20260928`

- files: 422
- manifest sha256: `8167725a892cfe36dc7399634f6f6ea4e4d93a7d05285f3796b17dcf393aee40`
- created: 
- reason: label-fix v2 regen; pre-fix UNSW (benign id 7) and IoT (benign id 1, target id 0 unmapped) results must not be cited

### `results/_archive/order_rev_benign_dup_20260928`

- files: 24
- manifest sha256: `34c255dafbd118a4edb2cdb6d2532238de072274a6eac00d778cf60ac3b6f806`
- created: 2026-09-28T14:20:36.380743+00:00
- reason: order-rev Monday-benign duplication: same-seed sampling handed identical benign rows to every task when Monday was not first; cross-task train/test contamination in a3_order_rev_c (12 seeds)

### `data/_archive/dedup_pre_postscale_20260928`

- files: 2
- manifest sha256: `f52016ac886389d9172160111fe88872ac2791ad05297d34d6a90b475382c6bb`
- created: 2026-09-28T01:47:39.067836+00:00
- reason: cicids-chrono-dedup-v2: post-scaling exact test matches remained; superseded by test exclusion against all train tasks

### `data/_archive/label_fix_20260927`

- files: 2
- manifest sha256: `fbcf87ab1a9b44307d7b06e489973f250a9903c6e70574db928511e9cdd8c391`
- created: 2026-09-27T17:19:07.995732+00:00
- reason: UNSW benign label ID corrected from 7 to 0; regenerate taskset-v2

### `data/_archive/label_fix_20260928`

- files: None
- manifest sha256: `f5e09a7b46d4f37b376c13785d74380b7b480e9fbeb1dc62ad82290b63f8e367`
- created: 
- reason: v2 task rebuild with corrected benign label maps (parenthesized union-minus; benign_id==0) + name-resolved poisoning targets + taskset-v2 schema

## Runtime source snapshots

### `artifacts/source_snapshots/runtime_94abb1576b44e9d5c52bc70a05b1b1688fd06f0d60458111fba9d83395668dfb.json`

- source_tree_hash: `94abb1576b44e9d5c52bc70a05b1b1688fd06f0d60458111fba9d83395668dfb`
- source_commit: `a4558b582a46352bc8f3708af3ce09aeadb8ef49`
- zip: `artifacts/source_snapshots/runtime_94abb1576b44e9d5c52bc70a05b1b1688fd06f0d60458111fba9d83395668dfb.zip` (present: True)
- zip sha256: `dc8219b949706964bd69836a9220751e1959765318579e3542f78d8e070c347d`
- note: Preserves dirty runtime source for exploratory E4 manifest-v3 seeds; config/task hashes remain in each seed manifest.

### `artifacts/source_snapshots/runtime_b8081e8badc537d49178ee82dd15bdf081cd8a13e02671520cff6b14532a3c66.json`

- source_tree_hash: `b8081e8badc537d49178ee82dd15bdf081cd8a13e02671520cff6b14532a3c66`
- source_commit: `9e635aef56c2a48d0c2937d172069a621eb753df`
- zip: `artifacts/source_snapshots/runtime_b8081e8badc537d49178ee82dd15bdf081cd8a13e02671520cff6b14532a3c66.zip` (present: True)
- zip sha256: `b858e05e529e017432c44b99c73e360fd92fe05b2f7eb8fc69e5484f297bc258`
- note: Preserves dirty runtime source for exploratory E4 manifest-v3 seeds; config/task hashes remain in each seed manifest.

## Verify on the bundling host

```powershell
python scripts/write_bundle_inventory.py
git status --short  # confirm no archive or snapshot path is missing
```
