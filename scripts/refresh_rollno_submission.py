"""Refresh the existing roll-number ZIP with the follow-up addendum and sources."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "submissions/23I-2568_23I-2581.zip"
WORK = ROOT / "tmp/phase3-submission-update"
TEMP_ARCHIVE = WORK / "23I-2568_23I-2581.zip"
BACKUP = WORK / "23I-2568_23I-2581-before-preflight-sync.zip"
PREFIX = "03_REPRODUCIBLE_PROJECT/"

FILES = [
    "configs/phase3/discovery-development-v1.json",
    "configs/phase3/discovery-development-sensitivity-v1.json",
    "configs/phase3/discovery-development-replicates-v1.json",
    "configs/phase3/external-discovery-replication-v1.json",
    "configs/phase3/external-method-extension-v1.json",
    "docs/phase3-plan/follow-up-execution-plan.md",
    "docs/phase3-plan/discovery-development-results.md",
    "docs/phase3-plan/external-dataset-readiness.md",
    "docs/phase3-plan/submission-evidence-map.md",
    "docs/phase3-plan/final-test-readiness.md",
    "docs/phase3-plan/external-method-extension-v1.md",
    "docs/phase3-plan/external-method-training-pilot-results.md",
    "docs/phase3-plan/figures/discovery-development-sensitivity.svg",
    "docs/phase3-plan/figures/external-discovery-by-task.svg",
    "scripts/phase3_followup_preflight.py",
    "scripts/audit_phase3_external_compatibility.py",
    "scripts/audit_phase3_external_id_isolation.py",
    "scripts/audit_phase3_external_training_support.py",
    "scripts/prepare_phase3_external_method_inputs.py",
    "scripts/run_phase3_external_method_trainpilot.py",
    "scripts/summarize_phase3_external_method_pilot.py",
    "scripts/run_phase3_discovery_development.py",
    "scripts/summarize_phase3_discovery_replicates.py",
    "scripts/summarize_phase3_discovery_assignment.py",
    "scripts/plot_phase3_discovery_sensitivity.py",
    "scripts/run_phase3_external_discovery.py",
    "scripts/summarize_phase3_external_discovery.py",
    "scripts/plot_phase3_external_discovery.py",
    "scripts/build_phase3_followup_addendum.py",
    "scripts/refresh_rollno_submission.py",
    "src/discovery/pipeline.py",
    "src/phase3_external/__init__.py",
    "src/phase3_external/model.py",
    "results/phase3-followup/discovery-development-sensitivity-v2.json",
    "results/phase3-followup/discovery-development-assignment-v1.json",
    "results/phase3-followup/discovery-development-assignment-seed-2027.json",
    "results/phase3-followup/discovery-development-assignment-seed-2028.json",
    "results/phase3-followup/discovery-development-assignment-summary-v1.json",
    "results/phase3-followup/discovery-development-seed-2027.json",
    "results/phase3-followup/discovery-development-seed-2028.json",
    "results/phase3-followup/discovery-development-replicates-summary-v1.json",
    "results/phase3-followup/external-discovery-v2.json",
    "results/phase3-followup/external-discovery-summary-v2.json",
    "results/phase3-followup/external-full-method-compatibility-v1.json",
    "results/phase3-followup/external-training-support-audit-v1.json",
    "results/phase3-followup/external-id-isolation-audit-v1.json",
    "results/phase3-followup/external-method-inputs-summary-v2.json",
    "results/phase3-followup/external-method-training-pilot-summary-v1.json",
    "results/phase3-followup/followup-preflight-v2.json",
    "results/phase3-followup/followup-preflight-v1.json",
    "submissions/phase3-report/phase3-followup-addendum.pdf",
    "submissions/phase3-report/phase3-report.tex",
    "submissions/phase3-report/phase3-report-updated.pdf",
    "submissions/phase3-report/report.md",
    "submissions/phase3-report/README.md",
    "submissions/phase3-report/primary-source-ledger.json",
    "scripts/phase3_references.py",
    "scripts/write_phase3_report.py",
    "scripts/build_phase3_reference_correction_manifest.py",
    "submissions/phase3-report/report-correction-manifest.json",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if not ARCHIVE.is_file():
        raise FileNotFoundError(ARCHIVE)
    WORK.mkdir(parents=True, exist_ok=True)
    if BACKUP.exists() or TEMP_ARCHIVE.exists():
        raise FileExistsError("Submission update workspace already contains an archive")
    additions = {}
    dynamic_files = list(FILES)
    for base in ("results/phase3-followup/external-method-inputs-v2",
                 "results/phase3-followup/external-method-training-pilot-v1"):
        folder = ROOT / base
        for path in sorted(folder.rglob("*")):
            if path.is_file() and path.name != "resume.log":
                dynamic_files.append(path.relative_to(ROOT).as_posix())
    if "results/phase3-followup/external-method-training-pilot-v1/summary.json" not in dynamic_files:
        dynamic_files.append("results/phase3-followup/external-method-training-pilot-v1/summary.json")
    dynamic_files = list(dict.fromkeys(dynamic_files))
    for rel in dynamic_files:
        source = ROOT / rel
        if not source.is_file():
            raise FileNotFoundError(source)
        rel_in_zip = PREFIX + rel.replace("\\", "/")
        additions[rel_in_zip] = source.read_bytes()
    additions["01_FINAL_REPORT/phase3-followup-addendum.pdf"] = (ROOT / "submissions/phase3-report/phase3-followup-addendum.pdf").read_bytes()
    additions["01_FINAL_REPORT/phase3-report.pdf"] = (ROOT / "submissions/phase3-report/phase3-report-updated.pdf").read_bytes()
    additions["01_FINAL_REPORT/report-correction-manifest.json"] = (ROOT / "submissions/phase3-report/report-correction-manifest.json").read_bytes()
    additions["00_START_HERE/README.txt"] = ("""PHASE 3 SUBMISSION
Roll numbers: 23I-2568 and 23I-2581

START HERE
Open 01_FINAL_REPORT/phase3-report.pdf for the corrected primary report.
Read 01_FINAL_REPORT/phase3-followup-addendum.pdf for the additional
development discovery, external discovery and train-only method pilot, and
readiness results. The pilot reports training execution only, with no test metrics.
The evidence map is at 03_REPRODUCIBLE_PROJECT/docs/phase3-plan/submission-evidence-map.md.

FOLDER GUIDE
01_FINAL_REPORT/                 Primary report, follow-up addendum, figures, and evidence inventory.
02_METHODOLOGY_AMENDMENT/        Phase 2 feedback changes and adopted methodology amendments.
03_REPRODUCIBLE_PROJECT/         Project sources, configs, protocols, scripts, and result artifacts.

External held-out scoring and final-test evaluation remain gated as documented.
Final-test data are not included in this archive.
""").encode("utf-8")
    manifest = {name: digest(payload) for name, payload in sorted(additions.items())}
    inventory_bytes = (json.dumps({"schema": "phase3-followup-submission-inventory-v1",
                                   "roll_numbers": ["23I-2568", "23I-2581"],
                                   "final_test_included": False, "added_files": manifest},
                                  indent=2) + "\n").encode("utf-8")
    additions["01_FINAL_REPORT/follow-up-inventory.json"] = inventory_bytes

    with zipfile.ZipFile(ARCHIVE, "r") as old:
        original_names = old.namelist()
        if len(original_names) != len(set(original_names)):
            raise ValueError("Original submission ZIP contains duplicate member names")
        old_data = {name: old.read(name) for name in original_names}
    replaced = set(additions)
    with zipfile.ZipFile(TEMP_ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as new:
        for name, payload in old_data.items():
            if name not in replaced:
                new.writestr(name, payload)
        for name, payload in additions.items():
            new.writestr(name, payload)

    with zipfile.ZipFile(TEMP_ARCHIVE, "r") as check:
        names = check.namelist()
        if len(names) != len(set(names)) or not set(old_data).issubset(names) or not set(additions).issubset(names):
            raise ValueError("Updated archive failed member inventory checks")
        for name, payload in additions.items():
            if digest(check.read(name)) != digest(payload):
                raise ValueError(f"Updated member hash mismatch: {name}")
        for name, payload in old_data.items():
            if name not in replaced and digest(check.read(name)) != digest(payload):
                raise ValueError(f"Original member changed unexpectedly: {name}")
    # Move the validated source archive to a reversible backup, then atomically install the replacement.
    shutil.copy2(ARCHIVE, BACKUP)
    os.replace(TEMP_ARCHIVE, ARCHIVE)
    with zipfile.ZipFile(ARCHIVE, "r") as final:
        if not {"01_FINAL_REPORT/phase3-report.pdf", "01_FINAL_REPORT/phase3-followup-addendum.pdf"}.issubset(final.namelist()):
            raise ValueError("Final report files missing after install")
    print(json.dumps({"archive": str(ARCHIVE), "backup": str(BACKUP),
                      "members": len(names), "added_or_replaced": len(additions),
                      "final_report": "01_FINAL_REPORT/phase3-report.pdf",
                      "followup_addendum": "01_FINAL_REPORT/phase3-followup-addendum.pdf",
                      "final_test_included": False}, indent=2))


if __name__ == "__main__":
    main()






