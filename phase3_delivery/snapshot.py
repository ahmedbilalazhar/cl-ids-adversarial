"""Portable logical catalog snapshots with verified reconstruction and history."""
import argparse
import hashlib
import os
import re
import tempfile
import zipfile
from pathlib import Path

from scripts.audit_phase3_endpoints import require
from src.phase3.common import canonical, digest, identity
from src.phase3_v2.checkpoint import strict_json

from .catalog import bound_manifest, connect, create_output, initialize, verify_catalog
from .io import MAX_JSON_BYTES, copy_verified_archive, read_verified_bytes

MAX_ARCHIVE_BYTES = 4*1024**3
MAX_MEMBERS = 10000


def object_name(name):
    return type(name) is str and re.fullmatch(r'(?:[0-9a-f]{64}|uncommitted-[A-Za-z0-9_-]{1,100})', name) is not None


def object_inventory(folder):
    require(not folder.is_symlink(), 'Object store cannot be a symbolic directory')
    if not folder.exists():
        return {}
    files = {}
    for path in sorted(folder.iterdir()):
        require(object_name(path.name) and not path.is_symlink() and path.is_file(), 'Unexpected object-store entry')
        require(path.stat().st_size <= MAX_JSON_BYTES, 'Object exceeds snapshot byte reservation')
        files[path.name] = path
    require(len(files) < MAX_MEMBERS, 'Too many snapshot objects')
    return files


def logical_state(connection, pin):
    bound_manifest(connection, pin)
    layout = set(connection.execute("SELECT type,name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"))
    require(layout == {('table', name) for name in ('metadata', 'observations', 'aliases', 'attempts')},
            'Snapshot supports only the declared catalog schema; extra objects would be lost')
    sequence = connection.execute("SELECT seq FROM sqlite_sequence WHERE name='attempts'").fetchone()
    maximum = connection.execute('SELECT COALESCE(MAX(id),0) FROM attempts').fetchone()[0]
    require((0 if sequence is None else sequence[0]) == maximum,
            'Nonstandard attempt counter cannot be reconstructed without changing next-ID semantics')
    metadata = dict(connection.execute('SELECT key,value FROM metadata'))
    require(set(metadata) == {'schema', 'manifest_sha256', 'manifest_bytes'}, 'Unsupported catalog metadata fields')
    return {'schema': 'phase3-catalog-snapshot-v1', 'manifest_sha256': pin,
            'manifest_bytes': metadata['manifest_bytes'],
            'observations': [list(row) for row in connection.execute('SELECT * FROM observations ORDER BY run_id')],
            'aliases': dict(connection.execute('SELECT alias_id,parent_id FROM aliases ORDER BY alias_id')),
            'attempts': [list(row) for row in connection.execute('SELECT * FROM attempts ORDER BY id')],
            'final_test_accessed': False, 'final_dispatchable': False}


def member(name):
    info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
    info.compress_type, info.create_system = zipfile.ZIP_DEFLATED, 3
    info.external_attr = 0o100600 << 16
    return info


def export_snapshot(database, manifest_sha256, archive_path):
    database, archive_path = Path(database), Path(archive_path)
    objects = Path(str(database)+'.objects')
    require(archive_path.resolve() != database.resolve() and not archive_path.resolve().is_relative_to(objects.resolve()),
            'Snapshot destination conflicts with the catalog or its objects')
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the SQLite writer slot before capturing tables and object files.
    # Readers remain possible; normal catalog writers wait until export ends.
    with connect(database) as connection:
        connection.execute('BEGIN IMMEDIATE')
        verified = verify_catalog(database, manifest_sha256)
        state = logical_state(connection, manifest_sha256)
        files = object_inventory(objects)
        state['objects'] = {name: digest(path) for name, path in files.items()}
        payload = (canonical(state)+'\n').encode('utf-8')
        total_bytes = len(payload)+sum(p.stat().st_size for p in files.values())
        require(len(payload) <= MAX_JSON_BYTES and total_bytes <= MAX_ARCHIVE_BYTES,
                'Snapshot exceeds its byte reservation')
        with zipfile.ZipFile(archive_path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            archive.writestr(member('catalog.json'), payload)
            for name, path in files.items():
                archive.writestr(member('objects/'+name), read_verified_bytes(path, state['objects'][name]))
        with zipfile.ZipFile(archive_path) as archive:
            require(canonical(load_snapshot(archive, manifest_sha256)) == canonical(state),
                    'Written snapshot metadata differs')
            for name, sha in state['objects'].items():
                require(hashlib.sha256(archive.read('objects/'+name)).hexdigest() == sha,
                        'Written snapshot object differs')
        require(set(object_inventory(objects)) == set(files) and
                all(digest(path) == state['objects'][name] for name, path in files.items()),
                'Object inventory changed during export; retain this failed archive')
    with archive_path.open('r+b') as stream:
        os.fsync(stream.fileno())
    return {'schema': 'phase3-catalog-snapshot-receipt-v1', 'status': 'complete_snapshot',
            'archive_sha256': digest(archive_path), 'manifest_sha256': manifest_sha256,
            'archive_bytes': archive_path.stat().st_size, 'uncompressed_bytes': total_bytes,
            'archive_payloads_verified': True,
            'logical_identity': identity(state), 'physical_observations': len(verified['records']),
            'aliases': len(verified['aliases']), 'attempts': len(verified['attempts']),
            'objects': len(files), 'unreferenced_objects': verified['unreferenced_objects'],
            'new_research_trajectories': 0, 'provider_durability_qualified': False,
            'final_test_accessed': False, 'final_dispatchable': False}


def load_snapshot(archive, pin):
    infos = archive.infolist()
    names = [item.filename for item in infos]
    require(len(names) == len(set(names)) and len(names) <= MAX_MEMBERS and
            all(item.file_size <= MAX_JSON_BYTES and not item.is_dir() and
                item.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) for item in infos) and
            sum(item.file_size for item in infos) <= MAX_ARCHIVE_BYTES, 'Invalid snapshot resource envelope')
    state = strict_json(archive.read('catalog.json').decode('utf-8'))
    canonical(state)
    require(set(state) == {'schema', 'manifest_sha256', 'manifest_bytes', 'observations', 'aliases',
                           'attempts', 'objects', 'final_test_accessed', 'final_dispatchable'} and
            state['schema'] == 'phase3-catalog-snapshot-v1' and state['manifest_sha256'] == pin and
            state['final_test_accessed'] is False and state['final_dispatchable'] is False,
            'Snapshot identity or release boundary differs')
    require(type(state['manifest_bytes']) is str and
            hashlib.sha256(state['manifest_bytes'].encode('utf-8')).hexdigest() == pin,
            'Snapshot does not contain the independently pinned manifest bytes')
    require(type(state['objects']) is dict and all(object_name(name) for name in state['objects']) and
            set(names) == {'catalog.json'} | {'objects/'+name for name in state['objects']},
            'Unexpected snapshot object inventory')
    require(type(state['observations']) is list and
            all(type(row) is list and len(row) == 5 and all(type(v) is str for v in (row[0], row[1], row[2], row[4])) and
                (row[3] is None or type(row[3]) is str) for row in state['observations']), 'Invalid observation rows')
    require(type(state['aliases']) is dict and all(type(k) is str and type(v) is str for k, v in state['aliases'].items()),
            'Invalid alias rows')
    require(type(state['attempts']) is list and all(type(row) is list and len(row) == 4 and
            type(row[0]) is int and row[0] > 0 and all(type(v) is str for v in row[1:]) and
            row[2] in ('imported', 'already_imported_verified', 'alias_verified', 'rejected')
            for row in state['attempts']), 'Invalid attempt history')
    ids = [row[0] for row in state['attempts']]
    require(ids == sorted(set(ids)), 'Attempt IDs must be unique and ordered')
    return state


def restore_snapshot(archive_path, archive_sha256, manifest_sha256, destination):
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='catalog-restore-', dir=destination.parent) as directory:
        temporary = Path(directory)
        source = temporary/'snapshot.zip'
        copy_verified_archive(archive_path, source, archive_sha256)
        with zipfile.ZipFile(source) as archive:
            state = load_snapshot(archive, manifest_sha256)
            manifest = temporary/'manifest.json'
            manifest.write_bytes(state['manifest_bytes'].encode('utf-8'))
            database = temporary/'catalog.sqlite'
            initialize(database, manifest, manifest_sha256)
            objects = Path(str(database)+'.objects')
            objects.mkdir()
            for name, expected in state['objects'].items():
                payload = archive.read('objects/'+name)
                require(hashlib.sha256(payload).hexdigest() == expected, 'Snapshot object payload changed')
                with (objects/name).open('xb') as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
            with connect(database) as connection:
                connection.execute('BEGIN IMMEDIATE')
                connection.executemany('INSERT INTO observations VALUES (?,?,?,?,?)', state['observations'])
                connection.executemany('INSERT INTO aliases VALUES (?,?)', sorted(state['aliases'].items()))
                connection.executemany('INSERT INTO attempts VALUES (?,?,?,?)', state['attempts'])
                connection.commit()
            verified = verify_catalog(database, manifest_sha256)
            with connect(database) as connection:
                rebuilt = logical_state(connection, manifest_sha256)
            rebuilt['objects'] = {name: digest(path) for name, path in object_inventory(objects).items()}
            require(canonical(rebuilt) == canonical(state), 'Restored logical contents differ')
        # Exclusively reserve a new directory. A commit receipt is the publication
        # boundary; any crash/failure before it leaves an explicit partial attempt.
        destination.mkdir()
        try:
            database.rename(destination/'catalog.sqlite')
            objects.rename(destination/'catalog.sqlite.objects')
            result = {'schema': 'phase3-catalog-restore-v1', 'status': 'complete_catalog_restore',
                      'archive_sha256': archive_sha256, 'manifest_sha256': manifest_sha256,
                      'logical_identity': identity(state), 'physical_observations': len(verified['records']),
                      'aliases': len(verified['aliases']), 'attempts': len(verified['attempts']),
                      'unreferenced_objects': verified['unreferenced_objects'], 'new_research_trajectories': 0,
                      'provider_durability_qualified': False, 'final_test_accessed': False, 'final_dispatchable': False}
            create_output(destination/'restore.commit.json', result)
        except BaseException as exc:
            create_output(destination/'restore.failed.json', {'status': 'partial_restore_retained',
                          'exception': type(exc).__name__, 'message': str(exc), 'final_dispatchable': False})
            raise
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('export', 'restore'):
        sub = commands.add_parser(name)
        sub.add_argument('--manifest-sha256', required=True)
        sub.add_argument('--archive', type=Path, required=True)
        sub.add_argument('--output', type=Path, required=True)
        if name == 'export':
            sub.add_argument('--database', type=Path, required=True)
        else:
            sub.add_argument('--archive-sha256', required=True)
            sub.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    try:
        if args.command == 'export':
            result = export_snapshot(args.database, args.manifest_sha256, args.archive)
        else:
            result = restore_snapshot(args.archive, args.archive_sha256, args.manifest_sha256, args.destination)
    except Exception as exc:
        create_output(args.output, {'status': 'failed_attempt_retained', 'exception': type(exc).__name__,
                                   'message': str(exc), 'final_dispatchable': False})
        raise
    create_output(args.output, result)
    print({'status': result['status'], 'physical_observations': result['physical_observations']})


if __name__ == '__main__':
    main()
