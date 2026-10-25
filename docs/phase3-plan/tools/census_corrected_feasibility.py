"""Read-only corrected-release census; not the canonical experiment builder.

The candidate 76-column aliases support a feasibility audit only. Equal names
do not prove feature-semantic equivalence with the original extractor.
"""
from __future__ import annotations

import csv
import io
import json
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "data/raw/phase3-feasibility-corrected"
ARCHIVE = WORK / "CICIDS2017_improved.zip"
OUT = ROOT / "docs/phase3-plan/corrected-full-census.json"
ALIASES = {
    "Total Fwd Packets": "Total Fwd Packet", "Total Backward Packets": "Total Bwd packets",
    "Total Length of Fwd Packets": "Total Length of Fwd Packet",
    "Total Length of Bwd Packets": "Total Length of Bwd Packet",
    "Min Packet Length": "Packet Length Min", "Max Packet Length": "Packet Length Max",
    "CWE Flag Count": "CWR Flag Count", "Avg Fwd Segment Size": "Fwd Segment Size Avg",
    "Avg Bwd Segment Size": "Bwd Segment Size Avg", "Fwd Avg Bytes/Bulk": "Fwd Bytes/Bulk Avg",
    "Fwd Avg Packets/Bulk": "Fwd Packet/Bulk Avg", "Fwd Avg Bulk Rate": "Fwd Bulk Rate Avg",
    "Bwd Avg Bytes/Bulk": "Bwd Bytes/Bulk Avg", "Bwd Avg Packets/Bulk": "Bwd Packet/Bulk Avg",
    "Bwd Avg Bulk Rate": "Bwd Bulk Rate Avg", "Init_Win_bytes_forward": "FWD Init Win Bytes",
    "Init_Win_bytes_backward": "Bwd Init Win Bytes", "act_data_pkt_fwd": "Fwd Act Data Pkts",
    "min_seg_size_forward": "Fwd Seg Size Min",
}


def add_counts(target: Counter, series: pd.Series) -> None:
    target.update({str(k): int(v) for k, v in series.value_counts(dropna=False).items()})


def safe_integer(series: pd.Series, dtype: str, missing: int = -1) -> pd.Series:
    bounds = np.iinfo(np.dtype(dtype))
    usable = np.isfinite(series) & series.between(bounds.min + 1, bounds.max) & series.mod(1).eq(0)
    return series.where(usable, missing).astype(dtype)


def main() -> None:
    started = time.monotonic()
    original = json.loads((ROOT / "docs/phase3-plan/candidate-feature-schema.json").read_text(encoding="utf-8"))["features"]
    mapped = [ALIASES.get(c, c) for c in original]
    if len(mapped) != 76 or len(set(mapped)) != 76:
        raise ValueError("Candidate projection is not 76 unique columns")
    summaries, total = [], 0
    metadata_path = WORK / "feasibility-metadata.csv"
    features_path = WORK / "candidate-features-fp32.raw"
    first_metadata_chunk = True
    with zipfile.ZipFile(ARCHIVE) as archive, features_path.open("wb") as feature_output, metadata_path.open("w", encoding="utf-8", newline="") as metadata_output:
        for file_index, name in enumerate(sorted(archive.namelist())):
            if not name.endswith(".csv"):
                continue
            with archive.open(name) as source:
                header = next(csv.reader(io.TextIOWrapper(source, encoding="utf-8-sig")))
            missing = sorted(set(mapped) - set(header))
            if missing or len(header) != len(set(header)):
                raise ValueError(f"Invalid candidate header {name}: {missing}")
            summary = {"name": name, "column_count": len(header), "rows": 0,
                       "raw_labels": Counter(), "policy_labels": Counter(),
                       "attempted_categories": Counter(), "invalid_metadata": 0,
                       "nonfinite_candidate_inputs": 0, "rows_valid_both": 0,
                       "valid_policy_labels": Counter(), "bad_numeric_columns": Counter(),
                       "timestamp_min": None, "timestamp_max": None,
                       "duration_min_us": None, "duration_max_us": None,
                       "nonmonotonic_adjacent_starts": 0}
            previous_start = None
            with archive.open(name) as source:
                for frame in pd.read_csv(source, chunksize=50000, low_memory=False):
                    count = len(frame)
                    raw_labels = frame["Label"].astype(str).str.strip()
                    attempted = pd.to_numeric(frame["Attempted Category"], errors="coerce")
                    labels = raw_labels.where(attempted.eq(-1), "BENIGN")
                    add_counts(summary["raw_labels"], raw_labels)
                    add_counts(summary["policy_labels"], labels)
                    add_counts(summary["attempted_categories"], attempted)
                    numeric = frame[mapped].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=np.float64)
                    with np.errstate(over="ignore", invalid="ignore"):
                        inputs = numeric.astype("<f4")
                    inputs[inputs == 0] = 0  # Canonical positive zero.
                    finite = np.isfinite(inputs).all(axis=1)
                    bad_cols = (~np.isfinite(inputs)).sum(axis=0)
                    summary["bad_numeric_columns"].update({c: int(n) for c, n in zip(mapped, bad_cols) if n})
                    duration = pd.to_numeric(frame["Flow Duration"], errors="coerce")
                    starts = pd.to_datetime(frame["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f", errors="coerce")
                    missing_starts = starts.isna()
                    if missing_starts.any():
                        starts.loc[missing_starts] = pd.to_datetime(frame.loc[missing_starts, "Timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
                    source_ports = pd.to_numeric(frame["Src Port"], errors="coerce")
                    destination_ports = pd.to_numeric(frame["Dst Port"], errors="coerce")
                    protocols = pd.to_numeric(frame["Protocol"], errors="coerce")
                    meta_valid = (starts.notna() & duration.notna() & np.isfinite(duration)
                                  & duration.ge(0) & duration.mod(1).eq(0)
                                  & source_ports.between(0, 65535) & source_ports.mod(1).eq(0)
                                  & destination_ports.between(0, 65535) & destination_ports.mod(1).eq(0)
                                  & protocols.between(0, 255) & protocols.mod(1).eq(0)
                                  & frame["Src IP"].notna() & frame["Dst IP"].notna()
                                  & np.isfinite(attempted) & attempted.mod(1).eq(0))
                    valid = finite & meta_valid.to_numpy()
                    summary["invalid_metadata"] += int((~meta_valid).sum())
                    summary["nonfinite_candidate_inputs"] += int((~finite).sum())
                    summary["rows_valid_both"] += int(valid.sum())
                    add_counts(summary["valid_policy_labels"], labels[valid])
                    valid_starts = starts.dropna()
                    if len(valid_starts):
                        lo, hi = valid_starts.min().isoformat(), valid_starts.max().isoformat()
                        summary["timestamp_min"] = min(summary["timestamp_min"] or lo, lo)
                        summary["timestamp_max"] = max(summary["timestamp_max"] or hi, hi)
                        start_ints = valid_starts.to_numpy(dtype="datetime64[us]").astype(np.int64)
                        summary["nonmonotonic_adjacent_starts"] += int((np.diff(start_ints) < 0).sum())
                        if previous_start is not None and start_ints[0] < previous_start:
                            summary["nonmonotonic_adjacent_starts"] += 1
                        previous_start = int(start_ints[-1])
                    finite_duration = duration[np.isfinite(duration)]
                    if len(finite_duration):
                        lo, hi = float(finite_duration.min()), float(finite_duration.max())
                        summary["duration_min_us"] = min(summary["duration_min_us"] if summary["duration_min_us"] is not None else lo, lo)
                        summary["duration_max_us"] = max(summary["duration_max_us"] if summary["duration_max_us"] is not None else hi, hi)
                    local_start = summary["rows"]
                    ids = (np.uint64(file_index) << np.uint64(32)) | np.arange(local_start, local_start + count, dtype=np.uint64)
                    meta = pd.DataFrame({
                        "row_id": ids, "file_index": np.full(count, file_index, dtype=np.uint8),
                        "archive_row": np.arange(local_start, local_start + count, dtype=np.uint32),
                        "src_ip": frame["Src IP"].astype(str), "src_port": safe_integer(source_ports, "int32"),
                        "dst_ip": frame["Dst IP"].astype(str), "dst_port": safe_integer(destination_ports, "int32"),
                        "protocol": safe_integer(protocols, "int16"),
                        "start_us": starts.to_numpy(dtype="datetime64[us]").astype(np.int64),
                        "duration_us": safe_integer(duration, "int64"),
                        "reference_label": labels.astype(str), "raw_label": raw_labels,
                        "attempted_category": safe_integer(attempted, "int16", -999),
                        "valid_metadata": meta_valid.to_numpy(), "valid_candidate_input": finite,
                    })
                    meta.to_csv(metadata_output, index=False, header=first_metadata_chunk)
                    first_metadata_chunk = False
                    feature_output.write(inputs.tobytes(order="C"))
                    summary["rows"] += count
                    total += count
            summaries.append(summary)
            print(json.dumps({"file": name, "rows": summary["rows"], "valid_both": summary["rows_valid_both"],
                              "elapsed_seconds": round(time.monotonic()-started, 2)}), flush=True)
    result = {"status": "candidate_release_census_not_final_experiment_builder", "completed_utc": datetime.now(timezone.utc).isoformat(),
              "source": "corrected-acquisition-full.json", "total_rows": total, "files": summaries,
              "candidate_feature_projection": [{"original": a, "corrected": b, "semantic_equivalence_verified": False} for a,b in zip(original,mapped)],
              "attempted_policy_for_this_audit": "Non--1 attempted category maps to BENIGN; unknown annotations invalidate metadata.",
              "metadata_file": metadata_path.relative_to(ROOT).as_posix(),
              "candidate_feature_file": features_path.relative_to(ROOT).as_posix(),
              "candidate_dtype": "little-endian float32, C order, 76 columns", "elapsed_seconds": round(time.monotonic()-started,3),
              "limits": ["Candidate name aliases are not a feature-semantic audit", "No final T0/split/ownership adopted", "No model training or performance evaluation", "IP string syntax not yet validated in this census", "No session/content support approval yet"]}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "rows": total, "elapsed_seconds": result["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
