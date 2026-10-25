"""Private notebook qualification bundle: explicit source/train/dev allowlists."""
from __future__ import annotations

import argparse
import ast
import hashlib
import shutil
import zipfile
from pathlib import Path

from src.phase3.common import ROOT, canonical, digest, identity, read_json, write_json
from src.phase3_v2.data import BASE_DEV, TRAIN_FILES, verify_files, verify_train
from src.phase3_v2.checkpoint import strict_json
from src.phase3_v3.protocol import Settings, code_files, code_identity

from .runtime import FROZEN, source_files
from .artifacts import valid_name
from .selection import SELECTION

SOURCE_EXTRA = ['configs/phase3/cpu-v2.json', 'configs/phase3/cpu-v3.json',
                'configs/phase3/reference74-v1.json', 'configs/phase3/taxonomy-v1.json',
                'docs/phase3-cpu-v2/decisions-2026-10-24.md', 'docs/phase3-cpu-v3/decisions-2026-10-24.md',
                'docs/phase3-reference/evidence/preparation-rebuild.json',
                'docs/phase3-plan/experiment-manifest.json', 'docs/phase3-plan/analysis-contrasts.json', SELECTION]


def verify(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or any(not valid_name(n) for n in names):
            raise ValueError('Unsafe/duplicate archive paths')
        if sum(info.file_size for info in infos) > 2*1024**3:
            raise ValueError('Unexpected expanded qualification bundle size')
        manifest = strict_json(archive.read('SNAPSHOT.json').decode('utf-8'))
        files = manifest['files']
        if set(names) != set(files) | {'SNAPSHOT.json'}:
            raise ValueError('Archive inventory differs')
        allowed_source = set(manifest['frozen_sources']) | set(manifest['worker_sources']) | set(SOURCE_EXTRA)
        allowed = {'project/'+name for name in allowed_source}
        allowed |= {'project/inputs/train/'+name for name in TRAIN_FILES | {'manifest.json'}}
        if manifest['includes_development']:
            allowed |= {'project/inputs/development/'+name for name in ('manifest.json', 'x.npy', 'y.npy', 'ids.npy', 'cohort.npy', 'attempted.npy')}
        if set(files) != allowed:
            raise ValueError('Unexpected source/data entry')
        if (set(manifest['frozen_sources']) != set(code_files()) or
                manifest['worker_sources'] != source_files() or
                identity(manifest['frozen_sources']) != FROZEN or
                manifest['final_dispatchable'] is not False or manifest['final_test_accessed'] is not False or
                manifest['seed'] != 101 or manifest['dose'] != [0, 1]):
            raise ValueError('Invalid qualification boundary or frozen source identity')
        for name, expected in files.items():
            hasher = hashlib.sha256()
            with archive.open(name) as handle:
                for chunk in iter(lambda: handle.read(8*1024**2), b''):
                    hasher.update(chunk)
            if hasher.hexdigest() != expected:
                raise ValueError('Archive payload hash differs: '+name)
            if name.endswith('.py'):
                ast.parse(archive.read(name).decode('utf-8-sig'), filename=name)
        for collection in ('frozen_sources', 'worker_sources'):
            if any(files['project/'+name] != expected for name, expected in manifest[collection].items()):
                raise ValueError('Source submanifest differs')
    return manifest


def create(output, include_development=True):
    if output.exists():
        raise FileExistsError(output)
    if code_identity() != FROZEN:
        raise ValueError('Frozen source changed')
    train = ROOT/'data/processed/phase3-cpu-v2/s101-p000/train'
    train_hash = digest(train/'manifest.json')
    verify_train(train, Settings(seed=101, dose=(0, 1)), train_hash)
    paths = {'project/'+name: ROOT/name for name in set(code_files()) | set(source_files()) | set(SOURCE_EXTRA)}
    paths.update({'project/inputs/train/'+name: train/name for name in TRAIN_FILES | {'manifest.json'}})
    if include_development:
        development = ROOT/'data/processed/phase3-reference74-v1/development'
        if digest(development/'manifest.json') != BASE_DEV:
            raise ValueError('Development identity differs')
        manifest = read_json(development/'manifest.json')
        verify_files(development, manifest['files'], {f'{k}.npy' for k in ('x', 'y', 'ids', 'cohort', 'attempted')})
        paths.update({'project/inputs/development/'+name: development/name for name in set(manifest['files']) | {'manifest.json'}})
    files = {name: digest(path) for name, path in sorted(paths.items())}
    manifest = {'schema': 'kaggle-qualification-snapshot-v1', 'seed': 101, 'dose': [0, 1],
                'files': files, 'frozen_sources': code_files(), 'worker_sources': source_files(),
                'train_manifest_sha256': train_hash, 'includes_development': include_development,
                'development_manifest_sha256': BASE_DEV if include_development else None,
                'private_upload_only': True, 'final_test_accessed': False, 'final_dispatchable': False}
    output.mkdir(parents=True)
    archive_path = output/'qualification.zip'
    with zipfile.ZipFile(archive_path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, path in sorted(paths.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type, info.create_system = zipfile.ZIP_DEFLATED, 3
            info.external_attr = 0o100644 << 16
            with path.open('rb') as source, archive.open(info, 'w') as target:
                shutil.copyfileobj(source, target, 8*1024**2)
        archive.writestr('SNAPSHOT.json', canonical(manifest)+'\n')
    verified = verify(archive_path)
    receipt = {'status': 'passed', 'files_verified': len(verified['files']), 'archive_sha256': digest(archive_path),
               'archive_bytes': archive_path.stat().st_size, 'frozen_code_identity': code_identity(),
               'worker_source_identity': identity(source_files()), 'train_manifest_sha256': train_hash,
               'final_test_accessed': False, 'final_dispatchable': False, 'uploaded': False}
    write_json(output/'acceptance.json', receipt)
    write_json(output/'snapshot.json', manifest)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--without-development', action='store_true')
    args = parser.parse_args()
    if args.verify:
        manifest = verify(args.verify)
        print({'status': 'passed', 'files_verified': len(manifest['files'])})
    elif args.output:
        print(create(args.output, not args.without_development))
    else:
        parser.error('--output or --verify required')


if __name__ == '__main__':
    main()
