"""Build a separate full-evidence archive without modifying the submitted baseline."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ROLL = '23I-2568_23I-2581'
BASE = ROOT / 'submissions/phase3-final/23I-2568_23I-2581.zip'
BASE_VALIDATION = ROOT / 'submissions/phase3-overnight/upload-validation.json'
OUT_DIR = ROOT / 'submissions/phase3-completed'
TARGET = OUT_DIR / f'{ROLL}-full-evidence-v4.zip'


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    if TARGET.exists():
        raise FileExistsError(f'Refusing to overwrite {TARGET}; choose a new versioned filename.')
    base_validation = json.loads(BASE_VALIDATION.read_text(encoding='utf-8'))
    if digest_path(BASE) != base_validation['sha256']:
        raise RuntimeError('Base submission archive differs from its recorded SHA-256')
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    temp = TARGET.with_suffix('.building.zip')
    if temp.exists():
        raise FileExistsError(f'Refusing to overwrite interrupted build {temp}')

    additions = []
    additions.extend(sorted((ROOT / 'results/phase3-overnight/runs').glob('*/E*-weights.npz')))
    for rel in ('docs/phase3-plan', 'docs/phase3-reference',
                'docs/phase3-rigorous-audit-v1', 'submissions/phase3-audited-report'):
        additions.extend(sorted((ROOT / rel).rglob('*')))
    additions.extend([
        ROOT / 'src/phase3_v2/final_evaluate.py',
        ROOT / 'tests/test_phase3_final_evaluator.py',
        ROOT / 'scripts/package_phase3_full_evidence.py',
    ])
    additions = sorted({p.resolve() for p in additions if p.is_file()})
    addition_by_rel = {path.relative_to(ROOT).as_posix(): path for path in additions}
    replacement_names = {f'{ROLL}/{rel}' for rel in addition_by_rel}

    inventory = {}
    seen = set()
    old_inventory = None
    with zipfile.ZipFile(BASE, 'r') as source:
        if source.testzip() is not None:
            raise RuntimeError('Base submission archive has a CRC failure')
        inventory_entry = next((n for n in source.namelist() if n.endswith('/UPLOAD_INVENTORY.json')), None)
        if inventory_entry is None:
            raise RuntimeError('Base archive has no upload inventory')
        old_inventory = json.loads(source.read(inventory_entry))
        expected_old = old_inventory['files']
        with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as target:
            for info in source.infolist():
                name = info.filename
                if name.endswith('/UPLOAD_INVENTORY.json'):
                    continue
                if name in replacement_names:
                    continue
                data = source.read(name)
                rel = name.split('/', 1)[1] if name.startswith(ROLL + '/') else name
                expected = expected_old.get(rel)
                if expected is not None and digest_bytes(data) != expected:
                    raise RuntimeError(f'Base inventory hash mismatch: {rel}')
                target.writestr(info, data)
                if rel in expected_old:
                    inventory[rel] = expected
                seen.add(name)

            for rel, path in addition_by_rel.items():
                name = f'{ROLL}/{rel}'
                data_hash = digest_path(path)
                with path.open('rb') as stream, target.open(name, 'w', force_zip64=True) as member:
                    while True:
                        block = stream.read(8 * 1024 * 1024)
                        if not block:
                            break
                        member.write(block)
                inventory[rel] = data_hash
                seen.add(name)

            weight_count = sum('/E' in f and f.endswith('-weights.npz') for f in inventory)
            full_inventory = {
                'files': inventory,
                'final_test_features_included': False,
                'full_evidence': {
                    'schema': 'phase3-full-evidence-archive-v1',
                    'base_archive_sha256': base_validation['sha256'],
                    'overnight_study_identity_sha256': json.loads(
                        (ROOT / 'results/phase3-overnight/identity.json').read_text(encoding='utf-8')
                    )['sha256'],
                    'completed_stage_weight_files': weight_count,
                    'overnight_independent_audit':
                        'docs/phase3-plan/phase3-overnight-independent-audit.json',
                    'contains_final_test_payload': False,
                },
            }
            target.writestr(f'{ROLL}/UPLOAD_INVENTORY.json',
                            json.dumps(full_inventory, indent=2, sort_keys=True).encode('utf-8'))

    with zipfile.ZipFile(temp, 'r') as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Built evidence archive has a CRC failure')
        names = set(archive.namelist())
        inventory_name = f'{ROLL}/UPLOAD_INVENTORY.json'
        parsed = json.loads(archive.read(inventory_name))
        for rel, expected in parsed['files'].items():
            name = f'{ROLL}/{rel}'
            if name not in names or digest_bytes(archive.read(name)) != expected:
                raise RuntimeError(f'Built archive file failed inventory verification: {rel}')
        if parsed['final_test_features_included'] is not False:
            raise RuntimeError('Final-test data must remain excluded')

    os.replace(temp, TARGET)
    validation = {
        'path': str(TARGET), 'sha256': digest_path(TARGET),
        'bytes': TARGET.stat().st_size, 'files': len(inventory),
        'all_hashes_valid': True, 'final_test_features_included': False,
    }
    (OUT_DIR / 'full-evidence-v4-validation.json').write_text(
        json.dumps(validation, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT_DIR / 'STATUS-v4.md').write_text(
        '# Phase 3 full evidence archive\n\n'
        f'Archive: `{TARGET.name}`\n\nSHA-256: `{validation["sha256"]}`\n\n'
        'The archive contains the frozen overnight development results, all stage '
        'weights, independent cell and metric audit, current final-evaluator source '
        'and synthetic qualification, and the audit/report documents. It contains '
        'no final-test payload or scores. The earlier course submission ZIP remains '
        'unchanged.\n', encoding='utf-8')
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    main()
