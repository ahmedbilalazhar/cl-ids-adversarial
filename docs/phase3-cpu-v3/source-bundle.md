# Source-only reproduction snapshot

`scripts/package_phase3_cpu.py` packages only whitelisted Phase3 Python source,
configuration/lock files, tests, contracts and small review documents from the
actual working tree. It does not substitute a Git commit for untracked source.
Every payload has a SHA256; verification reconstructs the exact frozen v3
numerical source identity from archived v1/v2/v3 files without importing them.

The archive uses fixed entry timestamps, order and permissions. Two archives of
the same snapshot must be byte-identical under the recorded Python/zlib runtime.
Python files are syntax-checked. Four intentionally invalid synthetic archives
exercise rejection of unsafe paths, a data/binary entry, changed source and
missing source. These fixtures contain no dataset feature payload.

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $py -m scripts.package_phase3_cpu --output results/phase3-source-bundle-v1/final-CPU-delivery
& $py -m scripts.package_phase3_cpu --verify results/phase3-source-bundle-v1/final-CPU-delivery/cpu-source.zip
```

Use a fresh output for a later snapshot. Earlier snapshots remain preserved and
may predate completion reports. This is a local source-only CPU snapshot, not a
qualified worker, complete installed environment, dataset bundle or GPU/final
release. It contains no prepared data, checkpoint or prediction arrays. A fresh
reproduction still needs the pinned CPU runtime and separately manifest-verified
training/development packages. No external upload or contributor message occurs.
