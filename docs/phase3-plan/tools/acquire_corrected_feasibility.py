"""Acquire the authors' public corrected capture for a feasibility audit only.

This does not select the primary release, build experiment splits or train a model.
Raw data stays in the ignored data/raw directory. No credentials are used.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
URL = "https://intrusion-detection.distrinet-research.be/CNS2022/Datasets/CICIDS2017_improved.zip"
EXPECTED_BYTES = 343549013  # Previously observed provider size; fail on a changed object.
DEST = ROOT / "data/raw/phase3-feasibility-corrected/CICIDS2017_improved.zip"
EVIDENCE = ROOT / "docs/phase3-plan/corrected-acquisition-full.json"


def acquire(*, url=URL, expected_bytes=EXPECTED_BYTES, destination=DEST, evidence=EVIDENCE, expected_sha256=None, release_note="Corrected capture is not an independent external dataset") -> None:
    started = time.monotonic()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(destination.parent).free < 3 * 1024**3:
        raise RuntimeError("Need at least 3 GiB free for this bounded audit.")
    if not destination.exists():
        partial = destination.with_suffix(".zip.partial")
        request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
        total = 0
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 200:
                raise RuntimeError(f"Expected complete HTTP 200, received {response.status}")
            advertised = int(response.headers.get("Content-Length", "0"))
            if advertised != expected_bytes:
                raise RuntimeError(f"Provider object changed size: {advertised}")
            with partial.open("wb") as output:
                while block := response.read(1024 * 1024):
                    total += len(block)
                    if total > expected_bytes:
                        raise RuntimeError("Transfer exceeded the recorded object size")
                    output.write(block)
                output.flush()
                os.fsync(output.fileno())
        if total != expected_bytes:
            raise RuntimeError(f"Incomplete transfer: {total}")
        partial.replace(destination)
    if destination.stat().st_size != expected_bytes:
        raise RuntimeError("Local archive size mismatch")
    with destination.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise RuntimeError("Pinned archive SHA-256 mismatch; do not promote this object")
    entries = []
    with zipfile.ZipFile(destination) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            file_digest = hashlib.sha256()
            size = 0
            with archive.open(info) as source:
                while block := source.read(1024 * 1024):
                    file_digest.update(block)
                    size += len(block)
            # ZipExtFile checks CRC when the complete member is consumed.
            entries.append({"name": info.filename, "bytes": size,
                            "sha256": file_digest.hexdigest(), "zip_crc32": f"{info.CRC:08x}",
                            "complete_read_crc_verified": True})
    result = {
        "status": "download_and_member_integrity_verified_not_experiment_ready",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "url": url, "local_archive": destination.relative_to(ROOT).as_posix(),
        "archive_bytes": destination.stat().st_size, "archive_sha256": digest,
        "matches_expected_sha256": digest == expected_sha256 if expected_sha256 else None,
        "members": entries, "elapsed_seconds": round(time.monotonic() - started, 3),
        "primary_release_selected": False, "trained_models": False,
        "limits": ["No feature-semantic equivalence established", "No final data split or support approval", release_note]
    }
    evidence.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "archive_bytes": result["archive_bytes"],
                      "members": len(entries), "sha256": digest, "elapsed_seconds": result["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    acquire()
