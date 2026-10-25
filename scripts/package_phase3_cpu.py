"""Deterministic, hash-verified source-only CPU implementation snapshot."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
import zipfile
import zlib
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FROZEN_V3 = '38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def allowed(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '\\' in name or ':' in name or '..' in p.parts or str(p) != name:
        return False
    return ((name.startswith(('src/phase3/', 'src/phase3_v2/', 'src/phase3_v3/', 'src/phase3_analysis/')) and p.suffix == '.py')
            or (name.startswith('scripts/') and len(p.parts) == 2 and 'phase3' in p.name and p.suffix == '.py')
            or (name.startswith('tests/test_phase3') and len(p.parts) == 2 and p.suffix == '.py')
            or (name.startswith('configs/phase3/') and p.suffix in ('.json', '.lock'))
            or (name.startswith('docs/phase3-') and p.suffix in ('.md', '.json'))
            or name == 'submissions/phase3-methodology-amendment.md')


def collect():
    paths = []
    for folder in ('src/phase3', 'src/phase3_v2', 'src/phase3_v3', 'src/phase3_analysis', 'configs/phase3', 'docs'):
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and allowed(p.relative_to(ROOT).as_posix()))
    paths.extend(p for p in (ROOT/'scripts').glob('*phase3*.py') if allowed(p.relative_to(ROOT).as_posix()))
    paths.extend((ROOT/'tests').glob('test_phase3*.py'))
    paths.append(ROOT/'submissions/phase3-methodology-amendment.md')
    payloads = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in sorted(set(paths))}
    if any(len(v) > 8*1024**2 for v in payloads.values()):
        raise ValueError('Source snapshot unexpectedly contains a large artifact')
    for name, payload in payloads.items():
        if name.endswith('.py'):
            ast.parse(payload.decode('utf-8-sig'), filename=name)
    files = {name: sha(value) for name, value in payloads.items()}
    source = {k: v for k, v in files.items() if k.startswith(('src/phase3/', 'src/phase3_v2/', 'src/phase3_v3/'))}
    if sha(canonical(source)) != FROZEN_V3:
        raise ValueError('Frozen v3 numerical source identity differs')
    return payloads, files


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(set(names)) != len(names) or 'SOURCE-MANIFEST.json' not in names or any(not allowed(n) and n != 'SOURCE-MANIFEST.json' for n in names):
            raise ValueError('Archive has duplicate/unexpected/unsafe paths')
        manifest = json.loads(archive.read('SOURCE-MANIFEST.json'))
        files = manifest['files']
        if set(names) != set(files) | {'SOURCE-MANIFEST.json'}:
            raise ValueError('Archive inventory differs from manifest')
        actual = {name: sha(archive.read(name)) for name in files}
        if actual != files:
            raise ValueError('Archive payload hash mismatch')
        source = {k: v for k, v in actual.items() if k.startswith(('src/phase3/', 'src/phase3_v2/', 'src/phase3_v3/'))}
        if sha(canonical(source)) != FROZEN_V3 or manifest['code_identity'] != FROZEN_V3:
            raise ValueError('Archived scientific source identity differs')
        for name in files:
            if name.endswith('.py'):
                ast.parse(archive.read(name).decode('utf-8-sig'), filename=name)
        if manifest['artifact_kind'] != 'source_only_CPU_snapshot' or manifest['gpu_dispatchable'] is not False or manifest['final_test_accessed'] is not False:
            raise ValueError('Unexpected qualification or release claim')
    return {'status': 'passed', 'files_verified': len(files), 'code_identity': FROZEN_V3,
            'archive_sha256': sha(path.read_bytes()), 'archive_bytes': path.stat().st_size,
            'scope': 'Every archived payload hash, exact frozen numerical source identity, Python syntax and source-only path allowlist; no environment/model execution'}


def create(path, payloads, manifest):
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        entries = {**payloads, 'SOURCE-MANIFEST.json': canonical(manifest)+b'\n'}
        for name, payload in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 24, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)


def rejection_checks(output, payloads, manifest):
    folder = output/'intentionally-invalid-fixtures'
    folder.mkdir()
    cases = {
        'unsafe-path': {**payloads, '../unexpected.py': b'# invalid path\n'},
        'binary-data-entry': {**payloads, 'data/processed/forbidden.npy': b'intentionally empty synthetic fixture'},
        'changed-source': {**payloads, 'src/phase3/common.py': payloads['src/phase3/common.py']+b'\n'},
        'missing-source': {k: v for k, v in payloads.items() if k != 'src/phase3/common.py'},
    }
    checks = []
    for name, values in cases.items():
        path = folder/(name+'.zip')
        create(path, values, manifest)
        try:
            verify(path)
        except ValueError:
            checks.append({'fixture': name, 'rejected': True})
        else:
            raise AssertionError('Invalid source archive accepted: '+name)
    return checks


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'results/phase3-source-bundle-v1')
    p.add_argument('--verify', type=Path)
    args = p.parse_args()
    if args.verify is not None:
        print(json.dumps(verify(args.verify), sort_keys=True))
        return
    if args.output.exists():
        raise FileExistsError(args.output)
    payloads, files = collect()
    manifest = {'schema': 'phase3-source-only-bundle-v1', 'artifact_kind': 'source_only_CPU_snapshot', 'code_identity': FROZEN_V3,
                'files': files, 'source_tree_manifest_sha256': sha(canonical(files)),
                'archive_runtime': {'python': platform.python_version(), 'zlib': zlib.ZLIB_RUNTIME_VERSION},
                'scope': 'Working-tree source, pinned configuration/contracts/tests and small document review artifacts available at snapshot time. Not a complete worker/data/environment bundle or evidence that untracked files exist in Git HEAD.',
                'excluded': ['Dataset/features/labels/IDs and prepared packages', 'Checkpoints/prediction arrays', 'Credentials/account state', 'Installed environment/cache'],
                'reconstruction': 'Extract into a fresh directory, verify SOURCE-MANIFEST.json, install the pinned CPU environment and separately supply exact manifest-verified train/development packages. Final inference remains sealed.',
                'final_test_accessed': False, 'gpu_dispatchable': False}
    args.output.mkdir(parents=True)
    first, second = args.output/'cpu-source.zip', args.output/'cpu-source-repeat.zip'
    create(first, payloads, manifest)
    create(second, payloads, manifest)
    result = verify(first)
    result['same_snapshot_repeat_archive_exact'] = sha(first.read_bytes()) == sha(second.read_bytes())
    if not result['same_snapshot_repeat_archive_exact']:
        raise AssertionError('Deterministic same-snapshot packaging failed')
    result['rejection_checks'] = rejection_checks(args.output, payloads, manifest)
    (args.output/'acceptance.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    (args.output/'source-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
