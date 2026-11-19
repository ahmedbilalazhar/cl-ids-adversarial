"""Build a versioned full-evidence archive from the audited roll-number ZIP.

The original submission and the current roll-number ZIP are read-only inputs.
The output adds raw follow-up results/checkpoints and an independently rerunnable
audit; it never includes final-test payloads.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'submissions/23I-2568_23I-2581.zip'
BASE_INVENTORY = ROOT / 'results/phase3-rigorous-audit-v1/package-inventory.json'
BASE_VALIDATION = ROOT / 'results/phase3-rigorous-audit-v1/package-validation.json'
RUN_ROOT = ROOT / 'results/phase3-followup-ablation'
OUT_DIR = ROOT / 'submissions/phase3-completed'
TARGET = OUT_DIR / '23I-2568_23I-2581-full-evidence-v10.zip'
OUT_VALIDATION = OUT_DIR / 'full-evidence-v10-validation.json'
OUT_STATUS = OUT_DIR / 'STATUS-v10.md'


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    if TARGET.exists() or TARGET.with_suffix('.building.zip').exists():
        raise FileExistsError('Refusing to overwrite existing or interrupted v7 archive')
    validation = json.loads(BASE_VALIDATION.read_text(encoding='utf-8'))
    inventory = json.loads(BASE_INVENTORY.read_text(encoding='utf-8'))
    if digest_file(BASE) != validation['sha256']:
        raise RuntimeError('Current roll-number ZIP differs from its validated digest')
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    additions: dict[str, Path] = {}
    # Include both the canonical result directory and recorded duplicate copies;
    # the audit verifies their byte identity instead of counting them as trials.
    for path in (RUN_ROOT / 'runs').rglob('*'):
        if path.is_file():
            additions[path.relative_to(ROOT).as_posix()] = path
    explicit = [
        RUN_ROOT / 'completion-followup.json', RUN_ROOT / 'identity.json',
        ROOT / 'results/phase3-rigorous-audit-v1/followup-independent-audit.json',
        ROOT / 'results/phase3-rigorous-audit-v1/ablation-cell-audit.json',
        ROOT / 'results/phase3-rigorous-audit-v1/trajectory-metrics.csv',
        ROOT / 'results/phase3-rigorous-audit-v1/comparisons-29.csv',
        ROOT / 'results/phase3-rigorous-audit-v1/family-metrics.csv',
        ROOT / 'docs/phase3-rigorous-audit-v1/tools/audit_phase3_followup_matrix.py',
        ROOT / 'docs/phase3-rigorous-audit-v1/README.md',
        ROOT / 'docs/phase3-rigorous-audit-v1/phase3-completion-plan.md',
        ROOT / 'docs/phase3-plan/rubric-and-readiness.md',
        ROOT / 'docs/phase3-plan/README.md',
        ROOT / 'docs/phase3-reference/research-comparability.md',
        ROOT / 'docs/phase3-plan/phase3-overnight-independent-audit.json',
        ROOT / 'scripts/run_phase3_followup_ablations.py',
        ROOT / 'scripts/package_phase3_full_evidence_v10.py',
        ROOT / 'scripts/build_phase3_audited_report.py',
        ROOT / 'scripts/audit_phase3_reliability.py',
        ROOT / 'docs/phase3-rigorous-audit-v1/p0-scope-reconciliation.md',
        ROOT / 'results/phase3-rigorous-audit-v1/reproduction-attempt2/verification.json',
        ROOT / 'docs/phase3-plan/final-test-readiness.md',
        ROOT / 'submissions/phase3-final/23I-2568_23I-2581.zip',
    ]
    for path in explicit:
        if path.is_file():
            additions[path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT / 'submissions/phase3-audited-report').rglob('*'):
        if path.is_file():
            additions[path.relative_to(ROOT).as_posix()] = path
    # A last check excludes a mistaken final-role payload from this package.
    if any('final_test' in rel.lower() and ('features' in rel.lower() or 'payload' in rel.lower())
           for rel in additions):
        raise RuntimeError('A final-test payload path was selected for packaging')

    expected_base = dict(inventory['files'])
    archive_names = set()
    payload_inventory: dict[str, str] = {}
    temp = TARGET.with_suffix('.building.zip')
    with zipfile.ZipFile(BASE, 'r') as source:
        if source.testzip() is not None:
            raise RuntimeError('Base roll-number ZIP has a CRC failure')
        inventory_member = 'PACKAGE_INVENTORY.json'
        actual_files = {i.filename for i in source.infolist() if not i.is_dir()}
        if actual_files != set(expected_base) | {inventory_member}:
            raise RuntimeError('Base archive file set differs from its independent package inventory')
        base_inventory_hash = digest_bytes(source.read(inventory_member))
        if base_inventory_hash != digest_file(BASE_INVENTORY):
            raise RuntimeError('Embedded base package inventory differs from the validated external copy')
        expected_base[inventory_member] = {'sha256': base_inventory_hash}
        for name, record in expected_base.items():
            data = source.read(name)
            expected_hash = record['sha256'] if isinstance(record, dict) else record
            if digest_bytes(data) != expected_hash:
                raise RuntimeError(f'Base payload hash mismatch: {name}')

        replacement_names = set(additions)
        with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as target:
            for info in source.infolist():
                if info.is_dir() or info.filename in replacement_names:
                    continue
                data = source.read(info.filename)
                target.writestr(info, data)
                payload_inventory[info.filename] = digest_bytes(data)
                archive_names.add(info.filename)
            for rel, path in sorted(additions.items()):
                if rel in archive_names:
                    raise RuntimeError(f'Unexpected archive-name collision: {rel}')
                data_hash = digest_file(path)
                with path.open('rb') as stream, target.open(rel, 'w', force_zip64=True) as member:
                    while True:
                        block = stream.read(8 * 1024 * 1024)
                        if not block:
                            break
                        member.write(block)
                payload_inventory[rel] = data_hash
                archive_names.add(rel)

            metadata = {
        'schema': 'phase3-full-evidence-v2',
                'supersedes_archive': 'submissions/phase3-completed/23I-2568_23I-2581-full-evidence-v9.zip',
                'report_pdf_sha256': digest_file(ROOT / 'submissions/phase3-audited-report/phase3-report.pdf'),
                'report_pdf_validation_sha256': digest_file(ROOT / 'submissions/phase3-audited-report/pdf-validation.json'),
                'files': dict(sorted(payload_inventory.items())),
                'final_test_payload_included': False,
                'base_roll_number_archive_sha256': validation['sha256'],
                'frozen_source_archive': 'submissions/phase3-final/23I-2568_23I-2581.zip',
                'followup_study_identity_sha256': json.loads(
                    (RUN_ROOT / 'identity.json').read_text(encoding='utf-8'))['sha256'],
                'followup_unique_trajectories': 417,
                'followup_result_files_including_exact_copies': 690,
                'followup_stage_and_oracle_weight_files_including_exact_copies': 2856,
                'independent_followup_audit':
                    'results/phase3-rigorous-audit-v1/followup-independent-audit.json',
            }
            meta_bytes = json.dumps(metadata, indent=2, sort_keys=True).encode('utf-8') + b'\n'
            target.writestr('UPLOAD_INVENTORY.json', meta_bytes)

    with zipfile.ZipFile(temp, 'r') as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Built evidence ZIP has a CRC failure')
        parsed = json.loads(archive.read('UPLOAD_INVENTORY.json'))
        actual = {i.filename for i in archive.infolist() if not i.is_dir()} - {'UPLOAD_INVENTORY.json'}
        if actual != set(parsed['files']):
            raise RuntimeError('Built evidence ZIP file set differs from its inventory')
        for name, expected in parsed['files'].items():
            if digest_bytes(archive.read(name)) != expected:
                raise RuntimeError(f'Built payload failed hash validation: {name}')
        if parsed['final_test_payload_included'] is not False:
            raise RuntimeError('Final-test payload inclusion flag is not false')

    os.replace(temp, TARGET)
    final = {
        'path': str(TARGET), 'sha256': digest_file(TARGET),
        'bytes': TARGET.stat().st_size, 'files': len(payload_inventory),
        'all_hashes_valid': True, 'final_test_payload_included': False,
        'base_roll_number_archive_sha256': validation['sha256'],
        'unique_followup_trajectories': 417,
        'copied_duplicate_result_records': 273,
    }
    OUT_VALIDATION.write_text(json.dumps(final, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_STATUS.write_text(
        '# Phase 3 full-evidence archive v10\n\n'
        f'Archive: `{TARGET.name}`\n\nSHA-256: `{final["sha256"]}`\n\n'
        'Based on the hash-validated current roll-number ZIP. Adds all follow-up '
        'result files and stage/oracle checkpoints, the independent follow-up '
        'verifier and audit output, the current report, and the frozen source archive. '
        'It preserves duplicate result copies only as integrity evidence; the audit '
        'counts unique trajectories separately. It contains no final-test payload.\n',
        encoding='utf-8')
    print(json.dumps(final, indent=2))


if __name__ == '__main__':
    main()


