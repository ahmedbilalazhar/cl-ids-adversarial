"""Record the corrected Phase 3 report PDF and its authoritative sources."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submissions/phase3-report/report-correction-manifest.json"
FILES = [
    "submissions/phase3-report/phase3-report-updated.pdf",
    "submissions/phase3-report/phase3-report.tex",
    "submissions/phase3-report/report.md",
    "submissions/phase3-report/primary-source-ledger.json",
    "scripts/phase3_references.py",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    hashes = {name: sha256(ROOT / name) for name in FILES}
    result = {
        "schema": "phase3-report-correction-manifest-v1",
        "report_pdf": "submissions/phase3-report/phase3-report-updated.pdf",
        "pages": 14,
        "correction": {
            "reference_number": 1,
            "change": "Corrected author list to L. Lavaur, Y. Busnel, and F. Autrel; removed an incorrectly listed M.-O. Pahl.",
            "primary_record": "https://doi.org/10.1016/j.cose.2025.104462",
        },
        "files_sha256": hashes,
        "final_test_accessed": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "schema": result["schema"], "files": len(hashes)}, indent=2))


if __name__ == "__main__":
    main()
