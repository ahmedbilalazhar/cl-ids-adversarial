# Data

Datasets are **not** committed (CIC-IDS-2017 ≈ 8.8 GB unzipped, derived artifacts ≈ 1.7 GB).

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
python -m src.data.sequence --processed data/processed --out data/processed/tasks.npz --scenario cii
```

Source: <https://www.unb.ca/cic/datasets/ids-2017.html>
