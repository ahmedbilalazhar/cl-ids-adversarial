"""Persistent import and analysis integration using fabricated integer counts."""
import copy
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from phase3_delivery.assemble import assemble
from phase3_delivery.catalog import initialize, ingest, validate_manifest, verify_catalog
from src.phase3.common import ROOT, digest, identity
from src.phase3_v3.protocol import DECISIONS, PROTOCOL, Settings
from kaggle_worker.runtime import FROZEN
from tests.test_continuation import synthetic_metric


def fixture_row(folder, run_id, arm='DR', seed=1, dose=(0, 1)):
    learner, admission = (arm, 'NONE') if arm in ('FT', 'EI', 'DR') else ('DR', arm)
    settings = Settings(learner=learner, admission=admission, seed=seed, rounds=12, epochs=1,
                        lambda_E=100 if learner == 'EI' else 10, lambda_z=.1 if learner == 'DR' else .5,
                        dose=dose)
    values = {**settings.__dict__, 'dose': list(dose)}
    execution = {'study_revision': 'synthetic-count-fixture-v1', 'frozen_code_identity': FROZEN,
                 'worker_source_identity': 'a'*64, 'runtime_identity': 'b'*64,
                 'settings_identity': identity(settings.scientific()),
                 'train_manifest_sha256': identity({'seed': seed, 'dose': dose}),
                 'taxonomy_sha256': digest(ROOT/'configs/phase3/taxonomy-v1.json'),
                 'protocol_sha256': digest(PROTOCOL), 'decisions_sha256': digest(DECISIONS),
                 'final_dispatchable': False}
    metric, _ = synthetic_metric()
    metric.update(settings=values, execution=execution)
    path = folder/(run_id+'.json')
    path.write_text(json.dumps(metric), encoding='utf-8')
    row = {'run_id': run_id, 'arm': arm, 'settings': values, 'execution': execution,
           'metric_sha256': digest(path), 'run_manifest_sha256': None}
    return row, path


def manifest(folder, rows, aliases=None):
    value = {'schema': 'phase3-count-registry-v1', 'kind': 'synthetic',
             'taxonomy_sha256': digest(ROOT/'configs/phase3/taxonomy-v1.json'),
             'final_dispatchable': False, 'rows': rows, 'aliases': aliases or {}}
    path = folder/'manifest.json'
    path.write_text(json.dumps(value), encoding='utf-8')
    return value, path, digest(path)


class Catalog(unittest.TestCase):
    def test_historical_windows_path_relocation_and_escape_rejection(self):
        from phase3_delivery.development import receipt_path
        expected = ROOT/'results/phase3-cpu-v3/development/executions/row/metrics.json'
        self.assertEqual(receipt_path(r'C:\old\checkout\results\phase3-cpu-v3\development\executions\row\metrics.json'), expected)
        with self.assertRaises(ValueError):
            receipt_path('results/phase3-cpu-v3/development/../../../outside.json')
        with self.assertRaises(ValueError):
            receipt_path('results/final/metrics.json')

    def test_persistence_idempotency_alias_and_rejections(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, metric = fixture_row(folder, 'physical')
            value, spec, sha = manifest(folder, [row], {'alias': 'physical'})
            db = folder/'catalog.sqlite'
            initialize(db, spec, sha)
            with self.assertRaises(ValueError):
                ingest(db, sha, 'alias', metric)
            self.assertEqual(ingest(db, sha, 'physical', metric)['independent_trajectories_added'], 1)
            self.assertEqual(ingest(db, sha, 'physical', metric)['independent_trajectories_added'], 0)
            self.assertEqual(ingest(db, sha, 'alias', metric)['independent_trajectories_added'], 0)
            with self.assertRaises(ValueError):
                ingest(db, sha, 'unregistered', metric)
            verified = verify_catalog(db, sha)
            self.assertEqual(len(verified['records']), 1)
            self.assertEqual(verified['aliases'], value['aliases'])
            self.assertEqual([r['outcome'] for r in verified['attempts']],
                             ['rejected', 'imported', 'already_imported_verified', 'alias_verified', 'rejected'])
            metric.write_text('{}')
            with self.assertRaises(ValueError):
                ingest(db, sha, 'physical', metric)
            self.assertEqual(len(verify_catalog(db, sha)['records']), 1)
            with self.assertRaises(FileExistsError):
                initialize(db, spec, sha)
            with self.assertRaises(ValueError):
                verify_catalog(db, '0'*64)

    def test_manifest_rejects_final_seeds_bindings_and_duplicate_conditions(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, _ = fixture_row(folder, 'physical')
            value, _, _ = manifest(folder, [row])
            changes = [lambda m: m.update(kind='final'),
                       lambda m: m.update(kind='development'),
                       lambda m: m['rows'].append({**copy.deepcopy(row), 'run_id': 'duplicate'}),
                       lambda m: m['aliases'].update(cycle='cycle'),
                       lambda m: m['rows'][0]['execution'].update(settings_identity='0'*64),
                       lambda m: m['rows'][0].update(arm='FT'),
                       lambda m: m.update(final_dispatchable=True)]
            for mutate in changes:
                modified = copy.deepcopy(value)
                mutate(modified)
                with self.assertRaises(ValueError):
                    validate_manifest(modified)

    def test_persisted_counts_and_endpoint_tampering_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, metric = fixture_row(folder, 'physical')
            _, spec, sha = manifest(folder, [row])
            db = folder/'catalog.sqlite'
            initialize(db, spec, sha)
            ingest(db, sha, 'physical', metric)
            objects = Path(str(db)+'.objects')
            orphan = objects/('0'*64)
            orphan.write_text('interrupted before database commit')
            self.assertEqual(verify_catalog(db, sha)['unreferenced_objects'], ['0'*64])
            with closing(sqlite3.connect(db)) as connection:
                connection.execute("UPDATE observations SET result_json='{}'")
                connection.commit()
            with self.assertRaises(ValueError):
                verify_catalog(db, sha)

    def test_abrupt_writer_exit_rolls_back_uncommitted_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, metric = fixture_row(folder, 'physical')
            _, spec, sha = manifest(folder, [row])
            db = folder/'catalog.sqlite'
            initialize(db, spec, sha)
            program = ('import os,sqlite3,sys; c=sqlite3.connect(sys.argv[1]); '
                       'c.execute("BEGIN IMMEDIATE"); '
                       'c.execute("INSERT INTO attempts(run_id,outcome,detail) VALUES (?,?,?)",'
                       '("uncommitted","partial","crash fixture")); os._exit(37)')
            result = subprocess.run([sys.executable, '-c', program, str(db)], capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 37)
            self.assertEqual(verify_catalog(db, sha)['attempts'], [])
            self.assertEqual(ingest(db, sha, 'physical', metric)['independent_trajectories_added'], 1)

    def test_cli_preserves_failed_receipt_and_does_not_replace_output(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, _ = fixture_row(folder, 'physical')
            _, spec, _ = manifest(folder, [row])
            db, output = folder/'catalog.sqlite', folder/'failed.json'
            command = [sys.executable, '-m', 'phase3_delivery.catalog', 'init', '--database', str(db),
                       '--manifest', str(spec), '--manifest-sha256', '0'*64, '--output', str(output)]
            result = subprocess.run(command, capture_output=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(output.read_text())['status'], 'failed_attempt_retained')
            sha = digest(output)
            subprocess.run(command, capture_output=True, timeout=60)
            self.assertEqual(digest(output), sha)
            self.assertFalse(db.exists())

    def test_concurrent_duplicate_import_adds_one_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, metric = fixture_row(folder, 'physical')
            _, spec, sha = manifest(folder, [row])
            db = folder/'catalog.sqlite'
            initialize(db, spec, sha)
            program = ('from pathlib import Path; import sys; from phase3_delivery.catalog import ingest; '
                       'print(ingest(Path(sys.argv[1]),sys.argv[2],"physical",Path(sys.argv[3])))')
            processes = [subprocess.Popen([sys.executable, '-c', program, str(db), sha, str(metric)],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
            outputs = [p.communicate(timeout=60) for p in processes]
            self.assertEqual([p.returncode for p in processes], [0, 0], outputs)
            verified = verify_catalog(db, sha)
            self.assertEqual(len(verified['records']), 1)
            self.assertEqual(sorted(r['outcome'] for r in verified['attempts']),
                             ['already_imported_verified', 'imported'])

    def test_full_synthetic_matrix_and_missing_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            rows, paths = [], {}
            for arm in ('FT', 'EI', 'DR', 'DM', 'DC'):
                for dose in ((0, 1), (1, 10), (3, 10), (1, 2)):
                    for seed in list(range(1, 12))+[42]:
                        run_id = f'{arm}-{dose[0]}-{dose[1]}-{seed}'
                        row, metric = fixture_row(folder, run_id, arm, seed, dose)
                        rows.append(row)
                        paths[run_id] = metric
            _, spec, sha = manifest(folder, rows, {'alias': rows[0]['run_id']})
            db = folder/'catalog.sqlite'
            initialize(db, spec, sha)
            for row in rows:
                ingest(db, sha, row['run_id'], paths[row['run_id']])
            ingest(db, sha, 'alias', paths[rows[0]['run_id']])
            verified = verify_catalog(db, sha)
            result = assemble(verified)
            self.assertEqual(result['physical_trajectories'], 240)
            self.assertEqual(result['aliases_counted_as_replicates'], 0)
            self.assertEqual(len(result['analysis']['rows']), 29)
            self.assertTrue(all(r['available_pairs'] == 12 and r['raw_p']['value'] == 1
                                for r in result['analysis']['rows']))
            # Remove one clean arm/seed from the assembled view to exercise fixed
            # family missingness; no fabricated endpoint is filled in.
            partial = copy.deepcopy(verified)
            partial['records'] = [r for r in partial['records'] if r['row']['run_id'] != 'FT-0-1-42']
            partial['missing_run_ids'] = ['FT-0-1-42']
            missing = assemble(partial)
            unavailable = [r for r in missing['analysis']['rows'] if r['status'] == 'unavailable_with_protocol_deviation']
            self.assertEqual(len(unavailable), 12)
            self.assertTrue(all(r['missing_seeds'] == [42] and r['raw_p'] is None for r in unavailable))
            self.assertEqual(len(missing['analysis']['rows']), 29)
            bad = copy.deepcopy(verified)
            bad['records'][0]['counts']['banks'][0]['bank_ids_sha256'] = '0'*64
            with self.assertRaises(ValueError):
                assemble(bad)
            bad = copy.deepcopy(verified)
            bad['records'][0]['row']['execution']['worker_source_identity'] = '0'*64
            with self.assertRaises(ValueError):
                assemble(bad)


if __name__ == '__main__':
    unittest.main()
