"""Regressions for reproduced metadata and persisted-lineage weaknesses."""
import copy
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from phase3_delivery.catalog import ingest, initialize, validate_manifest, verify_catalog
from phase3_delivery.import_counts import import_counts
from src.phase3.common import ROOT, digest, read_json
from tests.test_delivery_catalog import fixture_row, manifest
from src.phase3_v3.protocol import PROTOCOL
from kaggle_worker.runtime import FROZEN


class AuditIntegrity(unittest.TestCase):
    def test_cpu_declared_parent_is_bound_to_protocol(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, _ = fixture_row(folder, 'parent')
            value, _, _ = manifest(folder, [row])
            execution = row['execution']
            for field in ('worker_source_identity', 'frozen_code_identity', 'final_dispatchable'):
                execution.pop(field)
            execution.update(study_revision='cpu-v3', code_identity=FROZEN,
                             parent_code_identity=read_json(PROTOCOL)['parent_code_identity'])
            row['run_manifest_sha256'] = 'c'*64
            validate_manifest(value)
            execution['parent_code_identity'] = '0'*64
            with self.assertRaises(ValueError):
                validate_manifest(value)

    def test_boolean_and_numeric_type_coercion_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, path = fixture_row(folder, 'typed')
            original = read_json(path)
            for section, key, value in [('settings', 'epochs', True), ('settings', 'rounds', 12.0),
                                        ('settings', 'lambda_y', True), ('settings', 'seed', True),
                                        ('execution', 'final_dispatchable', 0),
                                        (None, 'final_dispatchable', True), (None, 'final_dispatchable', 0)]:
                with self.subTest(section=section, field=key):
                    metric = copy.deepcopy(original)
                    if section is None:
                        metric[key] = value
                    else:
                        metric[section][key] = value
                    path.write_text(json.dumps(metric))
                    ids, conditions = set(), set()
                    with self.assertRaises(ValueError):
                        import_counts(path, digest(path), row['settings'], row['execution'],
                                      read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes'],
                                      kind='synthetic', run_id='typed', seen_ids=ids, seen_conditions=conditions)
                    self.assertFalse(ids or conditions)

    def test_cpu_sidecar_requires_schema_and_exact_setting_types(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, path = fixture_row(folder, 'typed')
            original = read_json(path)
            original['schema'] = 'phase3-development-metrics-v3'
            original.pop('execution')
            run = {'schema': 'phase3-run-v2', 'status': 'complete', 'resumed_from': None,
                   'settings': row['settings'], 'execution': row['execution']}
            sidecar = folder/'run.json'
            for mutate in (lambda r: r.pop('schema'), lambda r: r.update(schema='old-run'),
                           lambda r: r['settings'].update(epochs=True)):
                modified = copy.deepcopy(run)
                mutate(modified)
                sidecar.write_text(json.dumps(modified))
                metric = {**original, 'run_manifest_sha256': digest(sidecar)}
                path.write_text(json.dumps(metric))
                with self.assertRaises(ValueError):
                    import_counts(path, digest(path), row['settings'], row['execution'],
                                  read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes'],
                                  kind='synthetic', run_id='typed', seen_ids=set(), seen_conditions=set(),
                                  run_manifest=sidecar)

    def test_retry_rejects_persisted_condition_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, path = fixture_row(folder, 'physical')
            _, spec, sha = manifest(folder, [row])
            db = folder/'catalog.sqlite'
            initialize(db, spec, sha)
            ingest(db, sha, 'physical', path)
            with closing(sqlite3.connect(db)) as connection:
                connection.execute('UPDATE observations SET condition_id=?', ('0'*64,))
                connection.commit()
            with self.assertRaises(ValueError):
                ingest(db, sha, 'physical', path)
            with closing(sqlite3.connect(db)) as connection:
                self.assertEqual(connection.execute('SELECT outcome FROM attempts ORDER BY id DESC').fetchone(), ('rejected',))

    def test_alias_reimport_rejects_changed_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            first, a = fixture_row(folder, 'first')
            second, b = fixture_row(folder, 'second', dose=(1, 2))
            _, spec, sha = manifest(folder, [first, second], {'alias': 'first'})
            db = folder/'catalog.sqlite'
            initialize(db, spec, sha)
            ingest(db, sha, 'first', a)
            ingest(db, sha, 'second', b)
            ingest(db, sha, 'alias', a)
            with closing(sqlite3.connect(db)) as connection:
                connection.execute('UPDATE aliases SET parent_id=? WHERE alias_id=?', ('second', 'alias'))
                connection.commit()
            with self.assertRaises(ValueError):
                ingest(db, sha, 'alias', a)
            with self.assertRaises(ValueError):
                verify_catalog(db, sha)


if __name__ == '__main__':
    unittest.main()
