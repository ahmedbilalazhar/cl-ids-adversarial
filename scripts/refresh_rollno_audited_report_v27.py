"""Promote the current audited report refresh into the roll-number ZIP.
The previous report is already preserved in the v14 archive and pre-audit ZIP.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'submissions/23I-2568_23I-2581.zip'
BACKUP = ROOT / 'submissions/23I-2568_23I-2581-pre-audited.zip'
TEMP = ROOT / 'tmp/23I-2568_23I-2581-v27-building.zip'
REPORT = ROOT / 'submissions/phase3-audited-report'
INVENTORY_PATH = ROOT / 'results/phase3-rigorous-audit-v1/package-inventory.json'
VALIDATION_PATH = ROOT / 'results/phase3-rigorous-audit-v1/package-validation.json'
ORIGINAL_SHA256 = 'c219925799b2fe3b1d73e4203e25d1f94987b6c401f0288290f5f0bb67a2311f'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if not ARCHIVE.is_file() or TEMP.exists():
        raise FileExistsError('Missing current ZIP or prior v26 build artifact exists')

    additions: dict[str, bytes] = {}
    with zipfile.ZipFile(ARCHIVE, 'r') as old:
        if old.testzip() is not None:
            raise RuntimeError('Current roll-number ZIP has a CRC failure')
        prior = old.read('01_FINAL_REPORT/phase3-report.pdf')
        if '01_FINAL_REPORT/phase3-report-pre-audit.pdf' not in old.namelist():
            additions['01_FINAL_REPORT/phase3-report-pre-audit.pdf'] = prior

    additions['01_FINAL_REPORT/phase3-report.pdf'] = (REPORT / 'phase3-report.pdf').read_bytes()
    additions['01_FINAL_REPORT/phase3-report.tex'] = (REPORT / 'phase3-report.tex').read_bytes()
    additions['01_FINAL_REPORT/report-build.md'] = (REPORT / 'BUILD.md').read_bytes()
    additions['01_FINAL_REPORT/report-validation.json'] = (REPORT / 'pdf-validation.json').read_bytes()
    for path in sorted(REPORT.rglob('*')):
        if path.is_file():
            rel = path.relative_to(REPORT).as_posix()
            additions[f'03_REPRODUCIBLE_PROJECT/submissions/phase3-audited-report/{rel}'] = path.read_bytes()

    root_files = [
        'scripts/build_phase3_audited_report.py',
        'scripts/summarize_phase3_adopted_costs.py',
        'scripts/analyze_phase3_admission_mechanisms.py',
        'scripts/package_phase3_full_evidence_v26.py',
        'scripts/package_phase3_full_evidence_v27.py',
        'scripts/verify_phase3_report_clean_rebuild.py',
        'scripts/refresh_rollno_audited_report.py',
        'scripts/refresh_rollno_audited_report_v27.py',
        'src/phase3_v2/final_evaluate.py',
        'tests/test_phase3_final_evaluator.py',
        'docs/phase3-plan/final-test-readiness.md',
        'results/phase3-rigorous-audit-v1/final-evaluator-qualification-v1.json',
        'results/phase3-rigorous-audit-v1/admission-mechanism-v1/summary.json',
        'results/phase3-rigorous-audit-v1/admission-mechanism-v1/admission-class-counts.csv',
        'results/phase3-rigorous-audit-v1/admission-mechanism-v1/poison-memory-occupancy.csv',
        'results/phase3-rigorous-audit-v1/admission-mechanism-v1/family-f1-effects.csv',
        'results/phase3-rigorous-audit-v1/admission-mechanism-v1/admission-mechanism-diagnostic.pdf',
        'results/phase3-rigorous-audit-v1/primary-source-ledger.json',
        'scripts/run_phase3_overnight.py',
        'scripts/package_phase3_full_evidence_v26.py',
        'src/phase3_v2/global_filter.py',
        'src/phase3_v2/learning.py',
        'src/phase3_v2/protocol.py',
        'tests/test_phase3_overnight.py',
        'tests/test_phase3_eviction.py',
        'docs/phase3-rigorous-audit-v1/README.md',
        'docs/phase3-rigorous-audit-v1/reproduction.md',
        'docs/phase3-rigorous-audit-v1/phase3-completion-plan.md',
        'docs/phase3-rigorous-audit-v1/p0-scope-reconciliation.md',
        'docs/phase3-rigorous-audit-v1/gap-register.md',
        'docs/phase3-rigorous-audit-v1/gap-register.csv',
        'docs/phase3-rigorous-audit-v1/traceability-matrix.md',
        'docs/phase3-rigorous-audit-v1/dg-baseline-card.md',
        'docs/phase3-plan/README.md',
        'docs/phase3-plan/rubric-and-readiness.md',
        'docs/phase3-reference/research-comparability.md',
        'results/phase3-rigorous-audit-v1/followup-independent-audit.json',
        'results/phase3-rigorous-audit-v1/report-clean-rebuild-v21.json',
        'results/phase3-rigorous-audit-v1/report-clean-rebuild-v26.json',
        'submissions/phase3-completed/full-evidence-v26-validation.json',
        'docs/instructor_note.md',
        'docs/phase3-plan/amendment-register.md',
        'submissions/phase3-methodology-amendment.md',
        'results/phase3-rigorous-audit-v1/evidence-archive-verification-v21.json',
        'results/phase3-rigorous-audit-v1/ablation-cell-audit.json',
        'results/phase3-rigorous-audit-v1/checkpoint-semantics-focused-check.json',
        'results/phase3-rigorous-audit-v1/prospective-selector-check.json',
        'results/phase3-followup-ablation/completion-followup.json',
        'results/phase3-followup-ablation/identity.json',
    ]
    for rel in root_files:
        source = ROOT / rel
        if source.is_file():
            additions[f'03_REPRODUCIBLE_PROJECT/{rel}'] = source.read_bytes()

    start = '''PHASE 3 SUBMISSION\nRoll numbers: 23I-2568 and 23I-2581\n\nSTART HERE\nOpen 01_FINAL_REPORT/phase3-report.pdf for the audited nine-page report and its corrected journal DOI and resource disclosures. The pre-audit roll-number report is preserved as phase3-report-pre-audit.pdf. The original pre-deadline archive remains in 02_HISTORICAL/.\n\nThe complete raw follow-up evidence, including all 417 unique trajectories and checkpoint files, is in the separate versioned full-evidence archive referenced by the project audit documentation. The report rebuild verifier is scripts/verify_phase3_report_clean_rebuild.py; its v26 result confirms byte-matched sources and text/pixel-identical pages. No specific class feedback was given; no instructor approval is claimed. The adopted-profile DG selector is implemented, but its matched empirical outcomes and the FIFO/class-balanced block remain unrun.\n\nExternal held-out scoring and final-test evaluation remain gated. No final-test data are included in this archive.\n'''
    additions['00_START_HERE/README.txt'] = start.encode('utf-8')

    with zipfile.ZipFile(ARCHIVE, 'r') as old:
        names = old.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError('Current roll-number ZIP has duplicate member names')
        if 'PACKAGE_INVENTORY.json' not in names:
            raise RuntimeError('Current roll-number ZIP lacks package inventory')
        metadata = json.loads(old.read('PACKAGE_INVENTORY.json'))
        if metadata.get('original_submission_sha256') != ORIGINAL_SHA256:
            raise RuntimeError('Embedded original-submission hash differs from the preserved source')

    # Add the new report and audit sources, while retaining the prior ZIP report.
    temp_inventory: dict[str, dict] = {}
    with zipfile.ZipFile(ARCHIVE, 'r') as old, zipfile.ZipFile(TEMP, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as new:
        replaced = set(additions) | {'PACKAGE_INVENTORY.json'}
        for info in old.infolist():
            if info.filename in replaced:
                continue
            data = old.read(info.filename)
            new.writestr(info, data)
            temp_inventory[info.filename] = {'bytes': len(data), 'sha256': digest(data)}
        for name, data in sorted(additions.items()):
            new.writestr(name, data)
            temp_inventory[name] = {'bytes': len(data), 'sha256': digest(data)}
        metadata['files'] = dict(sorted(temp_inventory.items()))
        metadata['final_test_payload_included'] = False
        metadata['latest_report'] = '01_FINAL_REPORT/phase3-report.pdf'
        metadata['full_evidence_archive'] = 'submissions/phase3-completed/23I-2568_23I-2581-full-evidence-v27.zip'
        inventory_bytes = json.dumps(metadata, indent=2, sort_keys=True).encode('utf-8') + b'\n'
        new.writestr('PACKAGE_INVENTORY.json', inventory_bytes)

    with zipfile.ZipFile(TEMP, 'r') as check:
        if check.testzip() is not None:
            raise RuntimeError('Refreshed roll-number ZIP has a CRC failure')
        final_names = check.namelist()
        if len(final_names) != len(set(final_names)):
            raise RuntimeError('Refreshed ZIP has duplicate member names')
        final_meta = json.loads(check.read('PACKAGE_INVENTORY.json'))
        if set(final_meta['files']) != set(final_names) - {'PACKAGE_INVENTORY.json'}:
            raise RuntimeError('Refreshed ZIP inventory does not enumerate every payload')
        for name, record in final_meta['files'].items():
            data = check.read(name)
            if len(data) != record['bytes'] or digest(data) != record['sha256']:
                raise RuntimeError(f'Refreshed ZIP member failed hash validation: {name}')
        if digest(check.read('02_HISTORICAL/Phase3_Submission_23I-2568_23I-2581.zip')) != ORIGINAL_SHA256:
            raise RuntimeError('Original pre-deadline archive changed inside the refreshed ZIP')
        if check.read('01_FINAL_REPORT/phase3-report.pdf') != additions['01_FINAL_REPORT/phase3-report.pdf']:
            raise RuntimeError('Audited PDF was not promoted to the primary-report path')

    os.replace(TEMP, ARCHIVE)

    # The independent full-evidence packager consumes these exact current-base records.
    inventory_copy = metadata
    INVENTORY_PATH.write_text(json.dumps(inventory_copy, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    validation = {
        'archive': 'submissions/23I-2568_23I-2581.zip',
        'bytes': ARCHIVE.stat().st_size,
        'members': len(inventory_copy['files']),
        'sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        'all_payload_hashes_checked': True,
        'crc_checked': True,
        'original_preserved': True,
        'original_submission_sha256': ORIGINAL_SHA256,
        'pre_audit_roll_number_archive': BACKUP.relative_to(ROOT).as_posix(),
        'final_test_payload_included': False,
        'latest_report': '01_FINAL_REPORT/phase3-report.pdf',
    }
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    main()
