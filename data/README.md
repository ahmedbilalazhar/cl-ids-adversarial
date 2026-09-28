# Data

Datasets are **not** committed (CIC-IDS-2017 ≈ 8.8 GB unzipped, derived artifacts ≈ 1.7 GB).

New task artifacts use pickle-free `taskset-v2` NPZ plus a JSON sidecar with
source checksums, row IDs, ordered features/units, split/scaler parameters,
and protocol ID. The eight audited legacy CICIDS task files load only by
checked-in SHA-256 allowlist. Existing artifacts are never overwritten;
archive them with `scripts/archive_artifacts.py` first.

`tasks_chrono_t0.npz` is a T0-only frozen-scaler sensitivity arm.
`tasks_chrono_dedup.npz` is an offline-init duplicate-disjoint CICIDS
sensitivity arm. The historical `tasks_chrono.npz` is not future-blind at T0
and has substantial duplicate-content test exposure; see `docs/task_audit.md`.
Cross-file model-input fingerprints from the eight CICIDS CSVs are counted in
`docs/cicids_cross_file_audit.md`.
UNSW/IoT train and test are separate source pools but still have some
identical feature records across pools. The IoT builder streams batches and
caps per-label samples; it does not load both full pools into pandas.

## Layout

```
data/
  raw/            CIC-IDS-2017 CSVs (8 files) — from download script or UNB site
  processed/      clean parquet + tasks_chrono*.npz, tasks_frozen.npz
  processed_v1/   legacy processed snapshot (kept for reproducibility)
  _archive/processed_prefix0/  pre-fix snapshot (archived, invalid — do not use)
  raw_unsw/       UNSW-NB15 mirror (see docs/proposal.md)
  raw_iot/        IoT mirror (see docs/proposal.md)
  external/       third-party mirrors + row-count fingerprints
```

## Regenerate

```bash
python scripts/download_cicids.py          # writes into data/raw/
python -m src.data.clean --raw data/raw --out data/processed
python -m src.data.sequence --processed data/processed/cicids2017_clean.parquet --out data/processed/tasks_chrono.npz --scenario cii --split chrono --scaler frozen
```

Source: <https://www.unb.ca/cic/datasets/ids-2017.html>
