"""Verify a Phase 3 full-evidence ZIP using only its embedded inventory.

This check needs only the Python standard library. It verifies exact member
coverage, every member SHA-256 and ZIP CRC, the frozen original submission,
the report digest, and the declared absence of final-test payloads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ORIGINAL_SHA256 = "c219925799b2fe3b1d73e4203e25d1f94987b6c401f0288290f5f0bb67a2311f"
ORIGINAL_MEMBER = "02_HISTORICAL/Phase3_Submission_23I-2568_23I-2581.zip"
INVENTORY_MEMBER = "UPLOAD_INVENTORY.json"
REPORT_MEMBER = "01_FINAL_REPORT/phase3-report.pdf"


def hash_member(archive: zipfile.ZipFile, name: str) -> str:
    digest = hashlib.sha256()
    with archive.open(name, "r") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(path: Path) -> dict:
    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        files = [info.filename for info in infos if not info.is_dir()]
        if len(files) != len(set(files)):
            raise ValueError("ZIP contains duplicate member names")
        if INVENTORY_MEMBER not in files:
            raise ValueError("ZIP has no embedded UPLOAD_INVENTORY.json")
        inventory = json.loads(archive.read(INVENTORY_MEMBER))
        expected = inventory.get("files")
        if not isinstance(expected, dict):
            raise ValueError("Inventory has no files mapping")
        if set(files) != set(expected) | {INVENTORY_MEMBER}:
            raise ValueError("ZIP member set differs from embedded inventory")
        if inventory.get("final_test_payload_included") is not False:
            raise ValueError("Inventory does not declare final-test payload exclusion")
        forbidden = [name for name in files if "final_test" in name.lower()
                     and ("features" in name.lower() or "payload" in name.lower())]
        if forbidden:
            raise ValueError(f"Final-test payload-like members found: {forbidden[:5]}")

        for name, expected_hash in expected.items():
            if not isinstance(expected_hash, str) or len(expected_hash) != 64:
                raise ValueError(f"Invalid SHA-256 record for {name}")
            actual_hash = hash_member(archive, name)
            if actual_hash != expected_hash:
                raise ValueError(f"SHA-256 mismatch for {name}: {actual_hash}")

        if ORIGINAL_MEMBER not in expected or expected[ORIGINAL_MEMBER] != ORIGINAL_SHA256:
            raise ValueError("Frozen original submission identity is missing or changed")
        report_hash = expected.get(REPORT_MEMBER)
        if report_hash is None or inventory.get("report_pdf_sha256") != report_hash:
            raise ValueError("Report PDF digest does not agree with the upload inventory")

    return {
        "archive": str(path.resolve()),
        "sha256": hash_file(path),
        "files": len(expected),
        "all_member_hashes_and_crcs_valid": True,
        "frozen_original_preserved": True,
        "report_digest_matches": True,
        "final_test_payload_included": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="full-evidence ZIP to verify")
    args = parser.parse_args()
    print(json.dumps(verify(args.archive), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
