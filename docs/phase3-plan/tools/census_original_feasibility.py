"""Full source census of a pinned metadata-bearing original-release mirror.

No split, calibration, model training or session-clock correction is adopted.
Numeric inputs and metadata are read from the same archive row. The original
timestamp strings are retained because their precision/12-hour ambiguity matters.
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
WORK = ROOT / "data/raw/phase3-feasibility-original"
ARCHIVE = WORK / "GeneratedLabelledFlows.zip"
DOCS = ROOT / "docs/phase3-plan"


def add_counts(target, series):
    target.update({str(k): int(v) for k,v in series.value_counts(dropna=False).items()})


def main():
    started = time.monotonic()
    features = json.loads((ROOT / "docs/phase3-plan/candidate-feature-schema.json").read_text(encoding="utf-8"))["features"]
    records, total = [], 0
    metadata_path = WORK / "feasibility-metadata.csv"
    feature_path = WORK / "candidate-features-fp64.raw"
    valid_path = WORK / "candidate-finite.raw"
    first_chunk = True
    with zipfile.ZipFile(ARCHIVE) as archive, metadata_path.open("w", encoding="utf-8", newline="") as metadata_output, feature_path.open("wb") as feature_output, valid_path.open("wb") as valid_output:
        names = sorted(name for name in archive.namelist() if name.endswith(".csv"))
        for file_index, name in enumerate(names):
            with archive.open(name) as source:
                raw_header = next(csv.reader(io.TextIOWrapper(source, encoding="cp1252")))
            stripped = [c.strip() for c in raw_header]
            duplicate_names = sorted(k for k,v in Counter(stripped).items() if v>1)
            summary = {"name": name, "file_index": file_index, "column_count": len(raw_header),
                       "duplicate_header_names": duplicate_names, "duplicate_header_values_differ": 0,
                       "rows": 0, "raw_labels": Counter(), "valid_numeric_labels": Counter(),
                       "nonfinite_numeric_rows": 0, "nonfinite_numeric_columns": Counter(),
                       "timestamp_formats": Counter(), "timestamp_hours": Counter(), "date_strings": Counter()}
            with archive.open(name) as source:
                for frame in pd.read_csv(source, encoding="cp1252", chunksize=50000, low_memory=False):
                    frame.columns = [c.strip() for c in frame.columns]
                    missing = set(features) - set(frame.columns)
                    if missing:
                        raise ValueError(f"Missing declared columns in {name}: {sorted(missing)}")
                    numeric = frame[features].apply(pd.to_numeric, errors="coerce").to_numpy(dtype="<f8", copy=True)
                    numeric[numeric == 0] = 0
                    finite = np.isfinite(numeric).all(axis=1)
                    labels = frame["Label"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
                    add_counts(summary["raw_labels"], labels)
                    add_counts(summary["valid_numeric_labels"], labels[finite])
                    summary["nonfinite_numeric_rows"] += int((~finite).sum())
                    bad_columns = (~np.isfinite(numeric)).sum(axis=0)
                    summary["nonfinite_numeric_columns"].update({k: int(v) for k,v in zip(features,bad_columns) if v})
                    if "Fwd Header Length.1" in frame:
                        left = pd.to_numeric(frame["Fwd Header Length"], errors="coerce")
                        right = pd.to_numeric(frame["Fwd Header Length.1"], errors="coerce")
                        summary["duplicate_header_values_differ"] += int((~(left.eq(right) | (left.isna() & right.isna()))).sum())
                    timestamps = frame["Timestamp"].astype(str).str.strip()
                    date_strings = timestamps.str.extract(r"^(\S+)", expand=False)
                    hours = timestamps.str.extract(r"\s(\d{1,2}):", expand=False)
                    has_seconds = timestamps.str.match(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2}(?:\.\d+)?$")
                    minute_only = timestamps.str.match(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}$")
                    styles = pd.Series(np.where(has_seconds,"seconds",np.where(minute_only,"minute_only","other")), index=frame.index)
                    add_counts(summary["timestamp_formats"], styles)
                    add_counts(summary["timestamp_hours"], hours)
                    add_counts(summary["date_strings"], date_strings)
                    local_start, count = summary["rows"], len(frame)
                    ids = (np.uint64(file_index)<<np.uint64(32)) | np.arange(local_start,local_start+count,dtype=np.uint64)
                    meta = pd.DataFrame({"row_id": ids, "file_index": np.full(count,file_index,dtype=np.uint8),
                        "archive_row": np.arange(local_start,local_start+count,dtype=np.uint32),
                        "src_ip": frame["Source IP"].astype(str), "src_port": frame["Source Port"],
                        "dst_ip": frame["Destination IP"].astype(str), "dst_port": frame["Destination Port"],
                        "protocol": frame["Protocol"], "timestamp_raw": timestamps,
                        "duration_us_raw": frame["Flow Duration"], "reference_label_raw": labels,
                        "valid_numeric": finite})
                    meta.to_csv(metadata_output,index=False,header=first_chunk)
                    first_chunk = False
                    feature_output.write(numeric.tobytes(order="C"))
                    valid_output.write(finite.astype(np.uint8).tobytes())
                    summary["rows"] += count
                    total += count
            records.append(summary)
            print(json.dumps({"file": Path(name).name, "rows": summary["rows"],
                "nonfinite_numeric": summary["nonfinite_numeric_rows"], "timestamp_formats": summary["timestamp_formats"],
                "elapsed_seconds": round(time.monotonic()-started,2)}),flush=True)
    result = {"status": "original_mirror_full_source_census_not_final_builder", "completed_utc": datetime.now(timezone.utc).isoformat(),
              "acquisition_evidence": "original-acquisition-full.json", "total_rows": total, "files": records,
              "numeric_feature_order": features, "numeric_dtype": "little-endian float64 before frozen transform", "metadata_file": metadata_path.relative_to(ROOT).as_posix(),
              "feature_file": feature_path.relative_to(ROOT).as_posix(), "finite_mask_file": valid_path.relative_to(ROOT).as_posix(),
              "elapsed_seconds": round(time.monotonic()-started,3),
              "limits": ["Third-party mirror provenance is not provider authentication", "No final feature/unit/label contract adopted", "Timestamp clock/precision ambiguity remains explicit", "No session/content split or model experiment executed"]}
    (DOCS/"original-full-census.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"rows":total,"elapsed_seconds":result["elapsed_seconds"]}),flush=True)


if __name__ == "__main__":
    main()
