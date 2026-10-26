"""Transactional, manifest-bound development/synthetic result registry.

SQLite serializes writers; content-addressed files retain the exact imported
bytes. No final-data mode, training entry point or mutable manifest is provided.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from kaggle_worker.contracts import parse_settings, sha256_value
from kaggle_worker.runtime import FROZEN
from scripts.audit_phase3_endpoints import require
from src.phase3.common import ROOT, canonical, digest, identity, read_json
from src.phase3_v2.checkpoint import strict_json
from src.phase3_v3.protocol import DECISIONS, PROTOCOL

from .import_counts import FINAL_SEEDS, import_counts
from .io import publish_new_bytes, read_verified_bytes


def encoded(value):
    """Keep exact endpoints serializable; never turn Fraction into inference floats."""
    from fractions import Fraction
    if isinstance(value, Fraction):
        return {'exact': [str(value.numerator), str(value.denominator)]}
    if isinstance(value, dict):
        return {key: encoded(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(item) for item in value]
    return value


def validate_manifest(value):
    require(set(value) == {'schema', 'kind', 'taxonomy_sha256', 'final_dispatchable', 'rows', 'aliases'},
            'Unexpected registry manifest fields')
    require(value['schema'] == 'phase3-count-registry-v1' and value['final_dispatchable'] is False,
            'Registry is not development-only')
    require(value['kind'] in ('development', 'synthetic'), 'Final registry creation is sealed')
    require(value['taxonomy_sha256'] == digest(ROOT/'configs/phase3/taxonomy-v1.json'), 'Taxonomy differs')
    require(type(value['rows']) is list and bool(value['rows']) and type(value['aliases']) is dict,
            'Registry requires physical rows and explicit aliases')
    protocol_sha, decisions_sha = digest(PROTOCOL), digest(DECISIONS)
    parent_sha = read_json(PROTOCOL)['parent_code_identity']
    rows, conditions = {}, set()
    for row in value['rows']:
        require(type(row) is dict and set(row) == {'run_id', 'arm', 'settings', 'execution',
                                                 'metric_sha256', 'run_manifest_sha256'}, 'Invalid registry row')
        run_id = row['run_id']
        require(type(run_id) is str and 0 < len(run_id) <= 200 and run_id not in rows, 'Duplicate/invalid run ID')
        settings = row['settings']
        seed = settings['seed']
        require(type(seed) is int and seed in (FINAL_SEEDS if value['kind'] == 'synthetic' else (101, 102, 103)),
                'Wrong registry seed set')
        # Synthetic fixtures may use final-seed labels; no final data are read.
        parsed = parse_settings({**settings, 'seed': 101})
        scientific = {**parsed.scientific(), 'seed': seed}
        arm = parsed.learner if parsed.admission == 'NONE' else parsed.admission
        require(row['arm'] == arm, 'Arm differs from learner/admission settings')
        execution = row['execution']
        require(type(execution) is dict, 'Invalid execution binding')
        common = {'study_revision', 'decisions_sha256', 'protocol_sha256', 'runtime_identity',
                  'settings_identity', 'taxonomy_sha256', 'train_manifest_sha256'}
        if execution.get('study_revision') == 'cpu-v3':
            expected = common | {'code_identity', 'parent_code_identity'}
            code = execution.get('code_identity')
            require(execution.get('parent_code_identity') == parent_sha, 'CPU parent source identity differs')
        else:
            expected = common | {'frozen_code_identity', 'worker_source_identity', 'final_dispatchable'}
            code = execution.get('frozen_code_identity')
            allowed = ('synthetic-count-fixture-v1',) if value['kind'] == 'synthetic' else (
                'kaggle-qualification-v4', 'kaggle-qualification-v5')
            require(execution.get('study_revision') in allowed and execution.get('final_dispatchable') is False,
                    'Unsupported registry execution revision')
        require(set(execution) == expected and code == FROZEN, 'Invalid source binding fields')
        for name, item in execution.items():
            if name not in ('study_revision', 'final_dispatchable'):
                sha256_value(item, name)
        require(execution['settings_identity'] == identity(scientific), 'Consumed settings identity differs')
        require(execution['protocol_sha256'] == protocol_sha and
                execution['decisions_sha256'] == decisions_sha and
                execution['taxonomy_sha256'] == value['taxonomy_sha256'], 'Protocol/decision/taxonomy binding differs')
        sha256_value(row['metric_sha256'], 'metric')
        if execution['study_revision'] == 'cpu-v3':
            sha256_value(row['run_manifest_sha256'], 'CPU run manifest')
        else:
            require(row['run_manifest_sha256'] is None, 'Embedded-execution metrics need no CPU sidecar')
        condition = condition_identity(row)
        require(condition not in conditions, 'Duplicate physical condition; declare an alias instead')
        conditions.add(condition)
        rows[run_id] = row
    for alias, parent in value['aliases'].items():
        require(type(alias) is str and 0 < len(alias) <= 200 and alias not in rows and
                type(parent) is str and parent in rows, 'Alias must reference one physical parent without cycles')
    return rows


def condition_identity(row):
    return identity([row['settings']['seed'], row['execution']['settings_identity'],
                     row['execution']['train_manifest_sha256']])


@contextmanager
def connect(database):
    connection = sqlite3.connect(Path(database).resolve().as_uri()+'?mode=rw', uri=True,
                                 timeout=30, isolation_level=None)
    try:
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('PRAGMA synchronous=FULL')
        yield connection
    finally:
        connection.close()


def initialize(database, manifest, expected_sha256):
    database = Path(database)
    payload = read_verified_bytes(manifest, expected_sha256)
    value = strict_json(payload.decode('utf-8'))
    validate_manifest(value)
    database.parent.mkdir(parents=True, exist_ok=True)
    # Atomic creation must not attach to or replace an existing registry.
    with database.open('xb'):
        pass
    with connect(database) as connection:
        connection.executescript('''
            BEGIN IMMEDIATE;
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE observations (
                run_id TEXT PRIMARY KEY, condition_id TEXT NOT NULL UNIQUE,
                metric_sha TEXT NOT NULL, run_sha TEXT, result_json TEXT NOT NULL);
            CREATE TABLE aliases (alias_id TEXT PRIMARY KEY,
                parent_id TEXT NOT NULL REFERENCES observations(run_id));
            CREATE TABLE attempts (id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL, outcome TEXT NOT NULL, detail TEXT NOT NULL);
        ''')
        connection.executemany('INSERT INTO metadata VALUES (?, ?)',
                               [('schema', 'phase3-count-catalog-v1'), ('manifest_sha256', expected_sha256),
                                ('manifest_bytes', payload.decode('utf-8'))])
        connection.commit()
    return {'status': 'initialized', 'manifest_sha256': expected_sha256, 'final_dispatchable': False}


def bound_manifest(connection, expected_sha256):
    metadata = dict(connection.execute('SELECT key,value FROM metadata'))
    require(metadata['schema'] == 'phase3-count-catalog-v1' and
            metadata['manifest_sha256'] == expected_sha256 and
            hashlib.sha256(metadata['manifest_bytes'].encode()).hexdigest() == expected_sha256,
            'Catalog manifest binding differs')
    # Cache only approval of immutable bytes, never mutable row dictionaries.
    # Config identities in the key invalidate approval if a bound file changes.
    approve_manifest(metadata['manifest_bytes'], digest(PROTOCOL), digest(DECISIONS),
                     digest(ROOT/'configs/phase3/taxonomy-v1.json'))
    value = strict_json(metadata['manifest_bytes'])
    return value, {row['run_id']: row for row in value['rows']}


@lru_cache(maxsize=4)
def approve_manifest(payload, protocol_sha, decisions_sha, taxonomy_sha):
    value = strict_json(payload)
    validate_manifest(value)


def store_object(database, path, expected_sha256):
    """Publish verified bytes with an atomic hard link; crashes leave only orphans."""
    objects = Path(str(database)+'.objects')
    objects.mkdir(parents=True, exist_ok=True)
    target = objects/expected_sha256
    payload = read_verified_bytes(path, expected_sha256)
    descriptor, temporary = tempfile.mkstemp(prefix='uncommitted-', dir=objects)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            pass
        require(digest(target) == expected_sha256, 'Stored object is corrupt')
    finally:
        Path(temporary).unlink(missing_ok=True)
    return target


def ingest(database, expected_sha256, run_id, metric, run_manifest=None):
    with connect(database) as connection:
        connection.execute('BEGIN IMMEDIATE')
        value, rows = bound_manifest(connection, expected_sha256)
        try:
            parent = value['aliases'].get(run_id, run_id)
            require(parent in rows, 'Run ID is outside the frozen import manifest')
            row = rows[parent]
            payload = store_object(database, metric, row['metric_sha256'])
            sidecar = None
            if row['run_manifest_sha256'] is not None:
                require(run_manifest is not None, 'Missing CPU run manifest')
                sidecar = store_object(database, run_manifest, row['run_manifest_sha256'])
            result = import_counts(payload, row['metric_sha256'], row['settings'], row['execution'],
                                   read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes'],
                                   kind=value['kind'], run_id=parent, seen_ids=set(), seen_conditions=set(),
                                   run_manifest=sidecar)
            packed = canonical(encoded(result))
            expected_row = (condition_identity(row), row['metric_sha256'], row['run_manifest_sha256'], packed)
            existing = connection.execute('SELECT condition_id,metric_sha,run_sha,result_json FROM observations WHERE run_id=?',
                                          (parent,)).fetchone()
            if run_id != parent:
                require(existing == expected_row,
                        'Alias parent must be imported and verified first')
                previous_alias = connection.execute('SELECT parent_id FROM aliases WHERE alias_id=?', (run_id,)).fetchone()
                require(previous_alias is None or previous_alias == (parent,), 'Existing alias lineage differs')
                if previous_alias is None:
                    connection.execute('INSERT INTO aliases VALUES (?, ?)', (run_id, parent))
                status, added = 'alias_verified', 0
            elif existing is not None:
                require(existing == expected_row,
                        'Existing observation differs')
                status, added = 'already_imported_verified', 0
            else:
                connection.execute('INSERT INTO observations VALUES (?, ?, ?, ?, ?)',
                                   (parent, condition_identity(row), row['metric_sha256'],
                                    row['run_manifest_sha256'], packed))
                status, added = 'imported', 1
            connection.execute('INSERT INTO attempts(run_id,outcome,detail) VALUES (?, ?, ?)',
                               (run_id, status, 'independent_trajectories_added='+str(added)))
            connection.commit()
            return {'status': status, 'independent_trajectories_added': added, 'final_dispatchable': False}
        except Exception as exc:
            connection.rollback()
            connection.execute('INSERT INTO attempts(run_id,outcome,detail) VALUES (?, ?, ?)',
                               (run_id, 'rejected', type(exc).__name__+': '+str(exc)))
            raise


def verify_catalog(database, expected_sha256):
    with connect(database) as connection:
        connection.execute('BEGIN')
        require(connection.execute('PRAGMA integrity_check').fetchone() == ('ok',), 'SQLite integrity failed')
        require(not connection.execute('PRAGMA foreign_key_check').fetchall(), 'Catalog foreign key failure')
        value, rows = bound_manifest(connection, expected_sha256)
        objects = Path(str(database)+'.objects')
        ids, conditions, records, referenced = set(), set(), [], set()
        for run_id, condition, metric_sha, run_sha, packed in connection.execute('SELECT * FROM observations ORDER BY run_id'):
            require(run_id in rows, 'Unexpected persisted run')
            row = rows[run_id]
            require((condition, metric_sha, run_sha) ==
                    (condition_identity(row), row['metric_sha256'], row['run_manifest_sha256']), 'Stored identity differs')
            result = import_counts(objects/metric_sha, metric_sha, row['settings'], row['execution'],
                                   read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes'],
                                   kind=value['kind'], run_id=run_id, seen_ids=ids, seen_conditions=conditions,
                                   run_manifest=None if run_sha is None else objects/run_sha)
            require(packed == canonical(encoded(result)), 'Stored endpoints differ from source counts')
            referenced.add(metric_sha)
            if run_sha is not None:
                referenced.add(run_sha)
            records.append({'row': row, 'counts': result})
        aliases = dict(connection.execute('SELECT alias_id,parent_id FROM aliases ORDER BY alias_id'))
        require(all(value['aliases'].get(alias) == parent and parent in ids for alias, parent in aliases.items()),
                'Stored alias lineage differs')
        attempts = [dict(zip(('id', 'run_id', 'outcome', 'detail'), record))
                    for record in connection.execute('SELECT * FROM attempts ORDER BY id')]
        orphaned = sorted(p.name for p in objects.iterdir() if p.name not in referenced) if objects.exists() else []
        return {'schema': 'phase3-count-catalog-verification-v1', 'status': 'passed',
                'manifest_sha256': expected_sha256, 'kind': value['kind'], 'records': records,
                'aliases': aliases, 'attempts': attempts, 'unreferenced_objects': orphaned,
                'missing_run_ids': sorted(set(rows)-ids), 'final_dispatchable': False, 'final_test_accessed': False}


def create_output(path, value):
    """Publish only complete, flushed receipts without replacing prior evidence."""
    payload = (json.dumps(encoded(value), indent=2, sort_keys=True, allow_nan=False)+'\n').encode('utf-8')
    publish_new_bytes(path, payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('init', 'ingest', 'verify'):
        sub = commands.add_parser(command)
        sub.add_argument('--database', type=Path, required=True)
        sub.add_argument('--manifest-sha256', required=True)
        sub.add_argument('--output', type=Path, required=True)
        if command == 'init':
            sub.add_argument('--manifest', type=Path, required=True)
        if command == 'ingest':
            sub.add_argument('--run-id', required=True)
            sub.add_argument('--metrics', type=Path, required=True)
            sub.add_argument('--run-manifest', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    try:
        if args.command == 'init':
            result = initialize(args.database, args.manifest, args.manifest_sha256)
        elif args.command == 'ingest':
            result = ingest(args.database, args.manifest_sha256, args.run_id, args.metrics, args.run_manifest)
        else:
            result = verify_catalog(args.database, args.manifest_sha256)
    except Exception as exc:
        create_output(args.output, {'status': 'failed_attempt_retained', 'exception': type(exc).__name__,
                                   'message': str(exc), 'final_dispatchable': False})
        raise
    create_output(args.output, result)
    print({'status': result['status'], 'final_dispatchable': False})


if __name__ == '__main__':
    main()
