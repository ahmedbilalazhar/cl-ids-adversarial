"""Rebuild source-row validity, domain, metadata, label and T0 masks independently.

The reference cache was produced with pandas; this audit streams the source ZIP
with Python's csv module and compares every reconstructed row flag to the frozen
74-feature graph arrays. It does not rebuild content-conflict quarantine or the
split allocator and never exports/opens a model test package.
"""
from __future__ import annotations

import csv
import hashlib
import ipaddress
import json
import math
import re
import struct
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data/raw/phase3-feasibility-corrected"
WORK = BASE / "no-headers-74"
DOCS = ROOT / "docs/phase3-plan"
OUT = DOCS / "corrected-no-headers-74-independent-mask-audit.json"
INT64_MAX = (1 << 63) - 1
ALIASES = {
    "BENIGN": "Benign", "DoS slowloris": "DoS Slowloris", "DoS slowhttptest": "DoS Slowhttptest",
    "Web Attack - Brute Force": "Web Attack Brute Force", "Web Attack - XSS": "Web Attack XSS",
    "Web Attack - Sql Injection": "Web Attack Sql Injection", "Web Attack - SQL Injection": "Web Attack Sql Injection",
    "Botnet": "Bot", "Portscan": "PortScan",
}


def numeric(text):
    try:
        return float(text.strip())
    except (ValueError, AttributeError):
        return math.nan


def integer(text):
    value = numeric(text)
    return int(value) if math.isfinite(value) and value.is_integer() else None


def timestamp_us(text):
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            value = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            delta = value - datetime(1970, 1, 1, tzinfo=timezone.utc)
            return delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds
        except ValueError:
            pass
    return None


def as_f32(value):
    if math.isnan(value):
        return math.nan
    if value > 3.4028234663852886e38:
        return math.inf
    if value < -3.4028234663852886e38:
        return -math.inf
    return struct.unpack("<f", struct.pack("<f", value))[0]


def conflicting_content_rows(hashes, valid, labels):
    positions = np.flatnonzero(valid)
    _, inverse, counts = np.unique(hashes[positions], return_inverse=True, return_counts=True)
    low = np.full(len(counts), np.iinfo(np.int16).max, dtype=np.int16)
    high = np.full(len(counts), -1, dtype=np.int16)
    np.minimum.at(low, inverse, labels[positions])
    np.maximum.at(high, inverse, labels[positions])
    bad = (counts > 1) & (low != high)
    result = np.zeros(len(labels), dtype=bool)
    result[positions] = bad[inverse]
    return result, int(bad.sum())


def main():
    started = time.monotonic()
    manifest = json.loads((DOCS / "corrected-no-headers-74-input-manifest.json").read_text(encoding="utf-8"))
    acquisition = json.loads((DOCS / "corrected-acquisition-full.json").read_text(encoding="utf-8"))
    component_report = json.loads((DOCS / "corrected-no-headers-74-component-feasibility.json").read_text(encoding="utf-8"))
    archive_path = BASE / "CICIDS2017_improved.zip"
    archive_hash = hashlib.file_digest(archive_path.open("rb"), "sha256").hexdigest()
    if archive_hash != acquisition["archive_sha256"]:
        raise RuntimeError("Archive differs from the recorded acquisition identity")

    with np.load(WORK / "conditional-components-120.npz", allow_pickle=False) as npz_context:
        states = {key: npz_context[key] for key in npz_context.files}
    n = int(manifest["total_rows"])
    if len(states["row_ids"]) != n:
        raise RuntimeError("Frozen state row count changed")
    feature_names = manifest["source_feature_order"]
    names = component_report["label_code_order"]
    label_map = {name: i for i, name in enumerate(names)}
    window_cols = {i for i, name in enumerate(feature_names) if name in {"FWD Init Win Bytes", "Bwd Init Win Bytes"}}
    if len(feature_names) != 74 or len(window_cols) != 2:
        raise RuntimeError("Adopted feature schema changed")
    scaler = component_report["scaler_features"]
    minima = np.asarray([float(row["minimum_T0"]) for row in scaler], dtype=np.float64)
    denom = np.asarray([float(row["denominator"]) for row in scaler], dtype=np.float64)
    check_names = ("row_ids", "file_index", "labels", "valid_domain", "valid_metadata", "final_finite", "start_us", "t0_fit", "raw_conflict", "final_conflict", "survivor", "kept")
    mismatches = {key: 0 for key in check_names}
    first = {key: None for key in check_names}
    counts = {key: 0 for key in ("finite_numeric", "valid_domain", "valid_metadata", "final_finite", "t0_fit")}
    raw_hashes = np.zeros(n, dtype="V32")
    final_hashes = np.zeros(n, dtype="V32")
    reconstructed_labels = np.full(n, -1, dtype=np.int16)
    reconstructed_finite = np.zeros(n, dtype=bool)
    reconstructed_domain = np.zeros(n, dtype=bool)
    reconstructed_metadata = np.zeros(n, dtype=bool)
    reconstructed_final_finite = np.zeros(n, dtype=bool)
    reconstructed_start = np.full(n, -(1 << 63), dtype=np.int64)
    reconstructed_t0 = np.zeros(n, dtype=bool)
    total = 0
    files = []
    finite_cache = np.fromfile(WORK / "candidate-finite.raw", dtype=np.uint8)
    if finite_cache.shape != (n,):
        raise RuntimeError("Finite-feature cache row count changed")
    mismatches["finite_numeric"] = 0
    first["finite_numeric"] = None
    with zipfile.ZipFile(archive_path) as archive:
        names_in_zip = sorted(name for name in archive.namelist() if name.endswith(".csv"))
        monday_index = names_in_zip.index("monday.csv")
        for file_index, member in enumerate(names_in_zip):
            rows_here = 0
            with archive.open(member) as raw, __import__("io").TextIOWrapper(raw, encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                for archive_row, row in enumerate(reader):
                    row_id = (file_index << 32) | archive_row
                    values = [numeric(row[key]) for key in feature_names]
                    finite = all(math.isfinite(value) for value in values)
                    valid_domain = all(value >= 0 for i, value in enumerate(values) if i not in window_cols)
                    valid_domain = valid_domain and all(
                        values[i] == -1 or (values[i] >= 0 and values[i] <= 65535 and values[i].is_integer())
                        for i in window_cols
                    )

                    attempted = numeric(row["Attempted Category"])
                    annotation_valid = math.isfinite(attempted) and attempted.is_integer()
                    raw_label = row["Label"].strip() if attempted == -1 else "BENIGN"
                    raw_label = re.sub(r"\s+", " ", raw_label.replace("–", "-").replace("—", "-"))
                    label_name = ALIASES.get(raw_label, raw_label) if annotation_valid else None
                    label = label_map.get(label_name, -1)
                    start = timestamp_us(row["Timestamp"])
                    src_ip = dst_ip = None
                    try:
                        src_ip = int(ipaddress.IPv4Address(row["Src IP"]))
                    except ipaddress.AddressValueError:
                        pass
                    try:
                        dst_ip = int(ipaddress.IPv4Address(row["Dst IP"]))
                    except ipaddress.AddressValueError:
                        pass
                    src_port, dst_port, protocol = (integer(row[key]) for key in ("Src Port", "Dst Port", "Protocol"))
                    duration = numeric(row["Flow Duration"])
                    valid_metadata = (
                        start is not None and src_ip is not None and dst_ip is not None and label >= 0
                        and src_port is not None and 0 <= src_port <= 65535
                        and dst_port is not None and 0 <= dst_port <= 65535
                        and protocol is not None and 0 <= protocol <= 255
                        and math.isfinite(duration) and duration >= 0 and duration.is_integer()
                        and duration <= INT64_MAX - max(start or 0, 0)
                    )
                    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                        projected = np.asarray(values, dtype=np.float64)
                        transformed = (projected - minima) / denom
                        transformed = transformed.astype(np.float32)
                    final_finite = bool(np.isfinite(transformed).all()) and finite
                    t0_fit = file_index == monday_index and label == 0 and finite and valid_metadata and valid_domain
                    reconstructed_labels[total] = label
                    reconstructed_finite[total] = finite
                    reconstructed_domain[total] = valid_domain
                    reconstructed_metadata[total] = valid_metadata
                    reconstructed_final_finite[total] = final_finite
                    reconstructed_start[total] = start if start is not None else -(1 << 63)
                    reconstructed_t0[total] = t0_fit
                    if finite:
                        raw_bytes = struct.pack("<" + "d" * len(values), *(0.0 if value == 0 else value for value in values))
                        raw_hashes[total] = np.frombuffer(hashlib.sha256(raw_bytes).digest(), dtype="V32")[0]
                    if final_finite:
                        transformed[transformed == 0] = 0
                        final_bytes = np.ascontiguousarray(transformed, dtype="<f4").tobytes()
                        final_hashes[total] = np.frombuffer(hashlib.sha256(final_bytes).digest(), dtype="V32")[0]
                    expected = {
                        "row_ids": row_id,
                        "file_index": file_index,
                        "labels": label,
                        "valid_domain": valid_domain,
                        "valid_metadata": valid_metadata,
                        "final_finite": final_finite,
                        "start_us": start if start is not None else -(1 << 63),
                        "t0_fit": t0_fit,
                    }
                    if int(finite_cache[total]) != int(finite):
                        mismatches["finite_numeric"] += 1
                        if first["finite_numeric"] is None:
                            first["finite_numeric"] = {"row_id": row_id, "archive": member, "archive_row": archive_row,
                                                       "expected": finite, "cached": int(finite_cache[total])}
                    for key, value in expected.items():
                        if value != states[key][total]:
                            mismatches[key] += 1
                            if first[key] is None:
                                first[key] = {"row_id": row_id, "archive": member, "archive_row": archive_row,
                                              "expected": value, "cached": states[key][total].item()}
                    counts["finite_numeric"] += int(finite)
                    counts["valid_domain"] += int(valid_domain)
                    counts["valid_metadata"] += int(valid_metadata)
                    counts["final_finite"] += int(final_finite)
                    counts["t0_fit"] += int(t0_fit)
                    total += 1
                    rows_here += 1
            files.append({"member": member, "rows": rows_here})
            print(json.dumps({"member": member, "rows": rows_here, "total_rows": total,
                              "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)

    raw_conflict, raw_conflict_groups = conflicting_content_rows(raw_hashes, reconstructed_finite & (reconstructed_labels >= 0), reconstructed_labels)
    final_conflict, final_conflict_groups = conflicting_content_rows(final_hashes, reconstructed_final_finite & (reconstructed_labels >= 0), reconstructed_labels)
    for key, reconstructed in (("raw_conflict", raw_conflict), ("final_conflict", final_conflict)):
        differences = np.flatnonzero(reconstructed != states[key])
        mismatches[key] = len(differences)
        if len(differences):
            i = int(differences[0])
            first[key] = {"row_id": int(states["row_ids"][i]), "expected": bool(reconstructed[i]), "cached": bool(states[key][i])}
    quarantine = raw_conflict | final_conflict
    eligible = reconstructed_finite & reconstructed_final_finite & reconstructed_metadata & reconstructed_domain & ~quarantine
    eligible_ids = np.flatnonzero(eligible)
    _, content_group = np.unique(final_hashes[eligible_ids], return_inverse=True)
    order = np.lexsort((states["row_ids"][eligible_ids], reconstructed_start[eligible_ids], content_group))
    ordered = eligible_ids[order]
    ordered_content_group = content_group[order]
    first_in_content_group = np.r_[True, ordered_content_group[1:] != ordered_content_group[:-1]]
    survivor = np.zeros(n, dtype=bool)
    survivor[ordered[first_in_content_group]] = True
    kept = survivor & ~states["t0_closure"]
    for key, reconstructed in (("survivor", survivor), ("kept", kept)):
        differences = np.flatnonzero(reconstructed != states[key])
        mismatches[key] = len(differences)
        if len(differences):
            i = int(differences[0])
            first[key] = {"row_id": int(states["row_ids"][i]), "expected": bool(reconstructed[i]), "cached": bool(states[key][i])}

    split = np.load(WORK / "conditional-candidate-split.npz", allow_pickle=False)
    split_positions = split["source_positions"]
    expected_positions = np.flatnonzero(kept)
    split_membership_mismatches = int(np.count_nonzero(split_positions != expected_positions)) if len(split_positions) == len(expected_positions) else abs(len(split_positions) - len(expected_positions)) + 1
    role_components = []
    canonical = np.full(n, np.iinfo(np.uint64).max, dtype=np.uint64)
    np.minimum.at(canonical, states["roots"], states["row_ids"])
    canonical = canonical[states["roots"]]
    role_names = ("train", "development", "test")
    for role in range(3):
        role_components.append(np.unique(canonical[split_positions[split["roles"] == role]]))
    overlap = {f"{role_names[a]}_{role_names[b]}": int(np.intersect1d(role_components[a], role_components[b]).size)
               for a, b in ((0, 1), (0, 2), (1, 2))}

    result = {
        "schema": "phase3-independent-source-mask-audit-v1",
        "status": "exact_independent_row_exclusion_and_survivor_parity" if total == n and not any(mismatches.values()) and split_membership_mismatches == 0 and not any(overlap.values()) else "mismatch",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "archive_sha256": archive_hash,
        "matches_recorded_archive_sha256": True,
        "rows_expected": n,
        "rows_reconstructed": total,
        "independent_row_counts": counts,
        "row_mismatches_by_field": mismatches,
        "first_mismatch_by_field": first,
        "raw_conflict_groups": raw_conflict_groups,
        "final_conflict_groups": final_conflict_groups,
        "split_membership_mismatches": split_membership_mismatches,
        "cross_role_component_intersections": overlap,
        "files": files,
        "not_reconstructed": ["StratifiedGroupKFold fold assignment (role membership only checked against the frozen split)"],
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["status"] == "exact_independent_row_exclusion_and_survivor_parity" else 2


if __name__ == "__main__":
    import sys
    sys.exit(main())
