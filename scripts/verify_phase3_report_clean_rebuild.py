"""Rebuild and compare the audited Phase 3 report from the v26 evidence ZIP.

This verifies report reproducibility only. It does not train models, rerun the
full data audit, or certify held-out effectiveness.

Run from the project root:
    python scripts/verify_phase3_report_clean_rebuild.py

The process needs the Python report dependencies and ``tectonic`` on PATH.
It uses a temporary extraction and writes a small JSON verification record.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import pymupdf


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "submissions/phase3-completed/23I-2568_23I-2581-full-evidence-v26.zip"
REFERENCE_PREFIX = "submissions/phase3-audited-report/"
REPORT_FILES = (
    "phase3-report.pdf",
    "phase3-report.tex",
    "source-ledger.json",
    "revision-provenance.json",
    "observed-run-costs.csv",
    "observed-run-costs-summary.json",
)
STATIC_INPUTS = (
    "scripts/build_phase3_audited_report.py",
    "scripts/summarize_phase3_adopted_costs.py",
    "scripts/analyze_phase3_admission_mechanisms.py",
    "scripts/audit_phase3_reliability.py",
    "results/phase3-followup-ablation/completion-followup.json",
    "results/phase3-rigorous-audit-v1/followup-independent-audit.json",
    "results/phase3-rigorous-audit-v1/validation.json",
    "results/phase3-rigorous-audit-v1/data-audit.json",
    "results/phase3-rigorous-audit-v1/trajectory-metrics.json",
    "results/phase3-rigorous-audit-v1/core-summary.json",
    "results/phase3-rigorous-audit-v1/comparisons-29.json",
    "results/phase3-rigorous-audit-v1/oracle-repair.json",
    "results/phase3-rigorous-audit-v1/cohort-metrics.json",
    "results/phase3-rigorous-audit-v1/primary-source-ledger.json",
    "results/phase3-rigorous-audit-v1/admission-mechanism-v1/summary.json",
    "results/phase3-rigorous-audit-v1/admission-mechanism-v1/admission-mechanism-diagnostic.pdf",
    "results/phase3-rigorous-audit-v1/submitted-foundation/phase3-report.tex",
    "data/processed/phase3-reference74-v1/development/manifest.json",
)
RESULT_PREFIX = "results/phase3-followup-ablation/"
RECORD = ROOT / "results/phase3-rigorous-audit-v1/report-clean-rebuild-v26.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safely_write(base: Path, name: str, data: bytes) -> Path:
    target = (base / PurePosixPath(name)).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"Unsafe archive member path: {name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def render_page(page: pymupdf.Page) -> tuple[str, bytes]:
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False)
    return page.get_text(), pixmap.samples


def main() -> int:
    if not ARCHIVE.is_file():
        raise FileNotFoundError(ARCHIVE)
    records: dict[str, object]
    with tempfile.TemporaryDirectory(prefix="phase3-v26-report-") as temporary:
        stage = Path(temporary).resolve()
        with zipfile.ZipFile(ARCHIVE) as package:
            names = set(package.namelist())
            missing_static = set(STATIC_INPUTS) - names
            missing_report = {REFERENCE_PREFIX + name for name in REPORT_FILES} - names
            if missing_static or missing_report:
                raise RuntimeError(
                    f"v26 archive lacks required members: "
                    f"{sorted(missing_static | missing_report)[:12]}"
                )

            manifest = json.loads(
                package.read("results/phase3-followup-ablation/completion-followup.json")
            )
            result_hashes = {
                f"{RESULT_PREFIX}{relative}": expected
                for relative, expected in manifest["files"].items()
                if relative.replace("\\", "/").endswith("/result.json")
            }
            if len(result_hashes) != 690:
                raise RuntimeError(f"Expected 690 result records, found {len(result_hashes)}")

            original_candidates = [
                name for name in names
                if name.endswith("/Phase3_Submission_23I-2568_23I-2581.zip")
            ]
            if not original_candidates:
                raise RuntimeError("Preserved original submission ZIP is missing")
            original = sorted(original_candidates, key=len)[0]

            input_names = set(STATIC_INPUTS) | set(result_hashes) | {original}
            for name in sorted(input_names):
                data = package.read(name)
                expected = result_hashes.get(name)
                if expected is not None and sha256_bytes(data) != expected:
                    raise RuntimeError(f"Completion-manifest hash mismatch: {name}")
                safely_write(stage, name, data)

            baseline = stage / "baseline-report"
            for name in REPORT_FILES:
                data = package.read(REFERENCE_PREFIX + name)
                safely_write(baseline, name, data)

        (stage / "submissions").mkdir(exist_ok=True)
        build = subprocess.run(
            [sys.executable, "scripts/build_phase3_audited_report.py"],
            cwd=stage,
            text=True,
            capture_output=True,
            check=False,
        )
        if build.returncode:
            raise RuntimeError(
                "Clean report build failed.\n"
                f"stdout:\n{build.stdout[-4000:]}\n"
                f"stderr:\n{build.stderr[-4000:]}"
            )

        rebuilt = stage / "submissions/phase3-audited-report"
        source_checks = {
            name: (baseline / name).read_bytes() == (rebuilt / name).read_bytes()
            for name in REPORT_FILES
            if name != "phase3-report.pdf"
        }
        baseline_pdf = pymupdf.open(baseline / "phase3-report.pdf")
        rebuilt_pdf = pymupdf.open(rebuilt / "phase3-report.pdf")
        page_checks = []
        for index in range(min(len(baseline_pdf), len(rebuilt_pdf))):
            old_text, old_pixels = render_page(baseline_pdf[index])
            new_text, new_pixels = render_page(rebuilt_pdf[index])
            page_checks.append(
                {
                    "page": index + 1,
                    "text_equal": old_text == new_text,
                    "rendered_pixels_equal": old_pixels == new_pixels,
                }
            )
        baseline_pdf.close()
        rebuilt_pdf.close()

        baseline_pdf_bytes = (baseline / "phase3-report.pdf").read_bytes()
        rebuilt_pdf_bytes = (rebuilt / "phase3-report.pdf").read_bytes()
        checks_pass = (
            len(page_checks) == 9
            and all(source_checks.values())
            and all(row["text_equal"] and row["rendered_pixels_equal"] for row in page_checks)
        )
        records = {
            "status": "passed" if checks_pass else "failed",
            "source_archive": str(ARCHIVE.relative_to(ROOT)).replace("\\", "/"),
            "source_archive_sha256": sha256_file(ARCHIVE),
            "verification_command": "python scripts/verify_phase3_report_clean_rebuild.py",
            "verifier_sha256": sha256_file(Path(__file__).resolve()),
            "command": "python scripts/build_phase3_audited_report.py",
            "extraction": "fresh selective extraction from the v26 ZIP; result hashes checked against the completion manifest",
            "source_files_exact_match": source_checks,
            "page_count_current": 9,
            "page_count_rebuilt": len(page_checks),
            "page_checks": page_checks,
            "pdf_sha256_equal": sha256_bytes(baseline_pdf_bytes) == sha256_bytes(rebuilt_pdf_bytes),
            "note": "PDF container hashes may differ because generated metadata can vary; page text and rendered pixels are compared independently.",
        }

    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))
    return 0 if records["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
