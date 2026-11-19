"""Independently reconstruct corrected-release rows and compare the audit cache.

Uses only Python's csv/zipfile modules for parsing (the cache builder used pandas).
This is a source-to-cache identity audit, not an adoption decision or model run.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import struct
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data/raw/phase3-feasibility-corrected"
WORK = BASE / "no-headers-74"
DOCS = ROOT / "docs/phase3-plan"
OUT = DOCS / "corrected-no-headers-74-independent-source-row-audit.json"
META_FIELDS = ("row_id", "file_index", "archive_row", "src_ip", "src_port", "dst_ip",
               "dst_port", "protocol", "timestamp_raw", "duration_us_raw",
               "reference_label_raw", "source_label_before_attempted_policy",
               "attempted_category", "valid_numeric")


def number(text: str) -> float:
    try:
        return float(text.strip())
    except (ValueError, AttributeError):
        return math.nan


def source_string(text: str) -> str:
    """Match pandas' CSV serialization for a scalar source metadata value."""
    value = number(text)
    if math.isfinite(value) and value.is_integer():
        return str(int(value))
    return text


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def main() -> int:
    started = time.monotonic()
    manifest = json.loads((DOCS / "corrected-no-headers-74-input-manifest.json").read_text(encoding="utf-8"))
    acquisition = json.loads((DOCS / "corrected-acquisition-full.json").read_text(encoding="utf-8"))
    archive_path = BASE / "CICIDS2017_improved.zip"
    archive_digest = hashlib.sha256()
    with archive_path.open("rb") as archive_file:
        for block in iter(lambda: archive_file.read(1024 * 1024), b""):
            archive_digest.update(block)
    archive_sha256 = archive_digest.hexdigest()
    if archive_sha256 != acquisition["archive_sha256"]:
        raise RuntimeError("Corrected archive hash differs from the recorded acquisition")
    source_columns = manifest["source_feature_order"]
    expected_rows = int(manifest["total_rows"])
    width = len(source_columns)
    if width != 74:
        raise RuntimeError(f"Expected the prospective 74-column projection, found {width}")
    features_path = WORK / "candidate-features-fp64.raw"
    transformed_path = WORK / "candidate-transformed-fp32.raw"
    if features_path.stat().st_size != expected_rows * width * 8:
        raise RuntimeError("Feature cache has an unexpected byte length")
    if transformed_path.stat().st_size != expected_rows * width * 4:
        raise RuntimeError("Transformed feature cache has an unexpected byte length")
    component_report = json.loads((DOCS / "corrected-no-headers-74-component-feasibility.json").read_text(encoding="utf-8"))
    scaler = component_report["scaler_features"]
    minima = [float(item["minimum_T0"]) for item in scaler]
    denominators = [float(item["denominator"]) for item in scaler]
    metadata_path = BASE / "component-metadata.csv"
    total = feature_mismatches = feature_cell_mismatches = fp32_row_mismatches = fp32_cell_mismatches = metadata_mismatches = 0
    first_feature = first_fp32 = first_metadata = None
    file_counts = []
    sha_features = hashlib.sha256()
    sha_metadata = hashlib.sha256()
    feature_source = features_path.open("rb")
    transformed_source = transformed_path.open("rb")
    metadata_file = metadata_path.open("r", encoding="utf-8", newline="")
    with feature_source, transformed_source, metadata_file, zipfile.ZipFile(archive_path) as archive:
        cached_meta = csv.DictReader(metadata_file)
        if tuple(cached_meta.fieldnames or ()) != META_FIELDS:
            raise RuntimeError("Metadata cache schema changed")
        names = sorted(name for name in archive.namelist() if name.endswith(".csv"))
        for file_index, name in enumerate(names):
            local_count = 0
            with archive.open(name) as raw, __import__("io").TextIOWrapper(raw, encoding="utf-8-sig", newline="") as stream:
                source_rows = csv.DictReader(stream)
                if not source_rows.fieldnames or any(c not in source_rows.fieldnames for c in source_columns):
                    raise RuntimeError(f"Feature columns missing from {name}")
                for archive_row, row in enumerate(source_rows):
                    values = []
                    for column in source_columns:
                        value = number(row[column])
                        if value == 0:
                            value = 0.0
                        values.append(value)
                    source_bytes = struct.pack("<" + "d" * width, *values)
                    cached_bytes = feature_source.read(width * 8)
                    if len(cached_bytes) != width * 8:
                        raise RuntimeError("Feature cache ended before source rows")
                    sha_features.update(source_bytes)
                    cached_values = struct.unpack("<" + "d" * width, cached_bytes)
                    differing_columns = [i for i, (source_value, cached_value) in enumerate(zip(values, cached_values))
                                         if not (source_value == cached_value or (math.isnan(source_value) and math.isnan(cached_value)))]
                    if differing_columns:
                        feature_mismatches += 1
                        feature_cell_mismatches += len(differing_columns)
                        if first_feature is None:
                            first_feature = {"row_id": total, "file": name, "archive_row": archive_row,
                                             "columns": [{"index": i, "name": source_columns[i],
                                                          "source": values[i], "cache": cached_values[i]}
                                                         for i in differing_columns[:5]]}

                    cached_fp32 = struct.unpack("<" + "f" * width, transformed_source.read(width * 4))
                    projected_fp32 = []
                    for i, value in enumerate(values):
                        scaled = (value - minima[i]) / denominators[i] if not math.isnan(value) else math.nan
                        projected_fp32.append(struct.unpack("<f", struct.pack("<f", scaled))[0])
                    differing_fp32 = [i for i, (source_value, cached_value) in enumerate(zip(projected_fp32, cached_fp32))
                                      if not (source_value == cached_value or (math.isnan(source_value) and math.isnan(cached_value)))]
                    if differing_fp32:
                        fp32_row_mismatches += 1
                        fp32_cell_mismatches += len(differing_fp32)
                        if first_fp32 is None:
                            first_fp32 = {"row_id": total, "file": name, "archive_row": archive_row,
                                           "columns": [{"index": i, "name": source_columns[i],
                                                        "independent": projected_fp32[i], "cache": cached_fp32[i]}
                                                       for i in differing_fp32[:5]]}

                    attempted = number(row["Attempted Category"])
                    annotation_valid = math.isfinite(attempted) and attempted.is_integer()
                    label = (row["Label"].strip() if attempted == -1 else "BENIGN") if annotation_valid else ""
                    expected_meta = {
                        "row_id": str((file_index << 32) | archive_row),
                        "file_index": str(file_index),
                        "archive_row": str(archive_row),
                        "src_ip": row["Src IP"],
                        "src_port": source_string(row["Src Port"]),
                        "dst_ip": row["Dst IP"],
                        "dst_port": source_string(row["Dst Port"]),
                        "protocol": source_string(row["Protocol"]),
                        "timestamp_raw": row["Timestamp"],
                        "duration_us_raw": source_string(row["Flow Duration"]),
                        "reference_label_raw": label,
                        "source_label_before_attempted_policy": row["Label"],
                        "attempted_category": source_string(row["Attempted Category"]),
                        "valid_numeric": str(all(math.isfinite(value) for value in values)),
                    }
                    actual_meta = next(cached_meta, None)
                    if actual_meta is None:
                        raise RuntimeError("Metadata cache ended before source rows")
                    sha_metadata.update((json.dumps(expected_meta, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
                    if any(actual_meta.get(key) != value for key, value in expected_meta.items()):
                        metadata_mismatches += 1
                        if first_metadata is None:
                            first_metadata = {"row_id": total, "file": name, "archive_row": archive_row,
                                              "expected": expected_meta, "actual": actual_meta}
                    total += 1
                    local_count += 1
            file_counts.append({"member": name, "rows": local_count})
            print(json.dumps({"member": name, "rows": local_count, "total_rows": total,
                              "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
        if feature_source.tell() != features_path.stat().st_size:
            raise RuntimeError("Feature cache contains extra or unread projected rows")
        if transformed_source.tell() != transformed_path.stat().st_size:
            raise RuntimeError("Transformed cache contains extra or unread rows")
        if next(cached_meta, None) is not None:
            raise RuntimeError("Metadata cache contains extra rows")
    result = {
        "schema": "phase3-independent-corrected-source-row-audit-v1",
        "status": "exact_metadata_and_fp32_model_input_parity" if total == expected_rows and not fp32_cell_mismatches and not metadata_mismatches else "mismatch",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "parser": "Python csv.DictReader; independent of pandas-based cache builder",
        "archive": "data/raw/phase3-feasibility-corrected/CICIDS2017_improved.zip",
        "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": archive_sha256,
        "matches_recorded_archive_sha256": True,
        "projection": "user-adopted corrected_no_headers_74 profile; this source-parity audit contributes no additional model results",
        "rows_expected": expected_rows,
        "rows_reconstructed": total,
        "features_per_row": width,
        "fp64_parser_rounding_row_mismatches": feature_mismatches,
        "fp64_parser_rounding_cell_mismatches": feature_cell_mismatches,
        "transformed_fp32_model_input_row_mismatches": fp32_row_mismatches,
        "transformed_fp32_model_input_cell_mismatches": fp32_cell_mismatches,
        "metadata_row_mismatches": metadata_mismatches,
        "first_feature_mismatch": first_feature,
        "first_fp32_model_input_mismatch": first_fp32,
        "first_metadata_mismatch": first_metadata,
        "files": file_counts,
        "reconstructed_feature_stream_sha256": sha_features.hexdigest(),
        "reconstructed_metadata_canonical_sha256": sha_metadata.hexdigest(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    result = json_safe(result)
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["status"] == "exact_metadata_and_fp32_model_input_parity" else 2


if __name__ == "__main__":
    sys.exit(main())
