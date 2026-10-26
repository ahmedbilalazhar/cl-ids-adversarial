"""Toy worker archive integration; no research packages or final bank are used."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import numpy as np

from kaggle_worker.data import StageCache
from kaggle_worker.evaluate import evaluate
from kaggle_worker.runtime import configure
from kaggle_worker.session import export_outputs
from kaggle_worker.worker import run_job
from phase3_delivery.catalog import initialize, verify_catalog
from phase3_delivery.worker_import import ingest_export
from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v2.data import BASE_DEV, StageInput
from src.phase3_v3.protocol import Settings


class VerifiedWorkerImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='toy-worker-export-')
        root = cls.root = Path(cls.temporary.name)
        output = root/'worker-output'
        output.mkdir()
        classes = read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes']
        stages = {}
        for stage in range(1, 5):
            codes = [0]+[c['source_code'] for c in classes if c['source_code'] != 0 and c['arrival_stage'] == stage]
            y = np.array([code for code in codes for _ in range(8)], dtype='<i8')
            x = np.random.default_rng(8100+stage).uniform(-.1, .1, (len(y), 74)).astype('<f4')
            stages[stage] = StageInput(stage, x, y, np.arange(stage*1000, stage*1000+len(y), dtype='<u8'),
                                       (np.arange(len(y)) % 5).astype('i1'))
        with patch('kaggle_worker.worker.StageCache.package', side_effect=lambda *a: StageCache(stages.__getitem__)), \
             contextlib.redirect_stdout(io.StringIO()):
            for learner in ('FT', 'EI', 'DR'):
                run_job(root, 'a'*64, output/learner, Settings(learner, rounds=3, epochs=1), 'cpu')
        bank = root/'toy-development-bank'
        bank.mkdir()
        labels = np.array([0]*20+[code for code in range(1, 16) for _ in range(4)], dtype='<i8')
        arrival = [next(c['arrival_stage'] for c in classes if c['source_code'] == i) for i in range(16)]
        cohorts = np.array([j for j in range(1, 5) for _ in range(5)]+
                           [arrival[code] for code in range(1, 16) for _ in range(4)], dtype='i1')
        values = {'x': np.random.default_rng(9909).uniform(-.1, .1, (len(labels), 74)).astype('<f4'),
                  'y': labels, 'ids': np.arange(100000, 100000+len(labels), dtype='<u8'),
                  'cohort': cohorts, 'attempted': np.zeros(len(labels), dtype=bool)}
        for name, value in values.items():
            np.save(bank/(name+'.npy'), value)
        write_json(bank/'manifest.json', {'role': 'development_only', 'arrival': arrival,
                   'eligible_codes': [c['source_code'] for c in classes if c['scoring_eligible']],
                   'families': [next(c['label'] for c in classes if c['source_code'] == i) for i in range(16)],
                   'files': {name+'.npy': digest(bank/(name+'.npy')) for name in values}})
        def toy_bank_digest(path):
            return BASE_DEV if Path(path) == bank/'manifest.json' else digest(path)
        with patch('kaggle_worker.evaluate.digest', side_effect=toy_bank_digest):
            for learner in ('FT', 'EI', 'DR'):
                evaluate(output/learner, bank, output/(learner+'-development'))
        runtime = configure('cpu')
        write_json(output/'synthetic-acceptance.json', {'schema': 'kaggle-worker-acceptance-v1', 'status': 'passed',
                   'runtime': runtime, 'checks': [{'check': 'toy archive wire fixture, not qualification evidence', 'status': 'passed'}],
                   'actual_CUDA_fixtures_passed': False, 'final_dispatchable': False, 'final_test_accessed': False})
        exported = export_outputs(output, root/'exports')
        cls.archive = root/'exports'/exported['archive']
        cls.archive_sha = exported['archive_sha256']
        cls.procedures = {learner: read_json(output/learner/'job.json') for learner in ('FT', 'EI', 'DR')}
        cls.metric_hashes = {learner: digest(output/(learner+'-development')/'metrics.json')
                             for learner in ('FT', 'EI', 'DR')}
        cls.procedure, cls.metric_sha = cls.procedures['FT'], cls.metric_hashes['FT']

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def registry(self, folder, metric_sha=None, learner='FT', aliases=None):
        procedure = self.procedures[learner]
        row = {'run_id': 'toy-'+learner+'-101', 'arm': learner, 'settings': procedure['settings'],
               'execution': procedure['execution'], 'metric_sha256': metric_sha or self.metric_hashes[learner],
               'run_manifest_sha256': None}
        spec = folder/'manifest.json'
        write_json(spec, {'schema': 'phase3-count-registry-v1', 'kind': 'development',
                         'taxonomy_sha256': digest(ROOT/'configs/phase3/taxonomy-v1.json'),
                         'final_dispatchable': False, 'rows': [row], 'aliases': aliases or {}})
        db = folder/'catalog.sqlite'
        initialize(db, spec, digest(spec))
        return db, digest(spec)

    @property
    def mapping(self):
        return [{'run_id': 'toy-FT-101', 'job_prefix': 'FT', 'metrics_path': 'FT-development/metrics.json'}]

    def test_complete_bound_export_import_and_retry(self):
        for learner in ('FT', 'EI', 'DR'):
            with self.subTest(learner=learner), tempfile.TemporaryDirectory() as directory:
                db, pin = self.registry(Path(directory), learner=learner)
                mapping = [{'run_id': 'toy-'+learner+'-101', 'job_prefix': learner,
                            'metrics_path': learner+'-development/metrics.json'}]
                result = ingest_export(db, pin, self.archive, self.archive_sha, mapping)
                self.assertEqual(result['independent_trajectories_added'], 1)
                self.assertEqual(result['envelope']['npz_files_checked'], 60)  # 20 per toy learner.
                self.assertEqual(ingest_export(db, pin, self.archive, self.archive_sha, mapping)
                                 ['independent_trajectories_added'], 0)
                self.assertEqual(len(verify_catalog(db, pin)['records']), 1)

    def test_alias_first_mapping_imports_one_physical_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            db, pin = self.registry(Path(directory), aliases={'toy-FT-alias': 'toy-FT-101'})
            mapping = [{**self.mapping[0], 'run_id': 'toy-FT-alias'}, self.mapping[0]]
            result = ingest_export(db, pin, self.archive, self.archive_sha, mapping)
            self.assertEqual(result['independent_trajectories_added'], 1)
            self.assertEqual(result['unique_evaluations_verified'], 1)
            self.assertTrue(result['prediction_structure_and_marginals_verified'])
            self.assertFalse(result['prediction_reference_labels_accessed'])
            self.assertEqual([row['run_id'] for row in result['rows']], ['toy-FT-101', 'toy-FT-alias'])
            self.assertEqual(mapping[0]['run_id'], 'toy-FT-alias')  # Do not mutate caller input.
            self.assertEqual(ingest_export(db, pin, self.archive, self.archive_sha, mapping)
                             ['independent_trajectories_added'], 0)
            verified = verify_catalog(db, pin)
            self.assertEqual(len(verified['records']), 1)
            self.assertEqual(verified['aliases'], {'toy-FT-alias': 'toy-FT-101'})

    def test_changed_model_binding_rejected_before_catalog_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with zipfile.ZipFile(self.archive) as source:
                payloads = {name: source.read(name) for name in source.namelist()}
            metrics = json.loads(payloads['FT-development/metrics.json'])
            metrics['stages'][0]['model_sha256'] = '0'*64
            payloads['FT-development/metrics.json'] = json.dumps(metrics).encode()
            import hashlib
            metric_sha = hashlib.sha256(payloads['FT-development/metrics.json']).hexdigest()
            commit = json.loads(payloads['FT-development/evaluation.commit.json'])
            commit['files']['metrics.json'] = metric_sha
            payloads['FT-development/evaluation.commit.json'] = json.dumps(commit).encode()
            altered = root/'altered.zip'
            with zipfile.ZipFile(altered, 'w') as target:
                for name, payload in payloads.items():
                    target.writestr(name, payload)
            db, pin = self.registry(root, metric_sha)
            with self.assertRaises(ValueError):
                ingest_export(db, pin, altered, digest(altered), self.mapping)
            self.assertEqual(verify_catalog(db, pin)['records'], [])

    def test_source_mutation_after_copy_uses_only_verified_snapshot(self):
        from phase3_delivery.io import copy_verified_archive
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            incoming = root/'incoming.zip'
            shutil.copyfile(self.archive, incoming)
            db, pin = self.registry(root)
            def snapshot_then_change(source, destination, expected):
                count = copy_verified_archive(source, destination, expected)
                incoming.write_bytes(b'changed external archive after verified copy')
                return count
            with patch('phase3_delivery.worker_import.copy_verified_archive', side_effect=snapshot_then_change):
                result = ingest_export(db, pin, incoming, self.archive_sha, self.mapping)
            self.assertEqual(result['independent_trajectories_added'], 1)
            self.assertNotEqual(digest(incoming), self.archive_sha)
            self.assertEqual(len(verify_catalog(db, pin)['records']), 1)

    def test_rehashed_prediction_inconsistency_rejected_before_catalog_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with zipfile.ZipFile(self.archive) as source:
                payloads = {name: source.read(name) for name in source.namelist()}
            prediction_name = 'FT-development/E1-predictions.npz'
            with np.load(io.BytesIO(payloads[prediction_name]), allow_pickle=False) as arrays:
                values = {name: arrays[name] for name in arrays.files}
            # Keep the file well-formed and update its hash. The inconsistency
            # must be found by semantics, rather than a stale transport hash.
            values['predicted_slots'][0] = (int(values['predicted_slots'][0])+1) % len(values['source_codes_in_slot_order'])
            fixture = io.BytesIO()
            np.savez(fixture, **values)
            payloads[prediction_name] = fixture.getvalue()
            import hashlib
            commit_name = 'FT-development/evaluation.commit.json'
            commit = json.loads(payloads[commit_name])
            commit['files']['E1-predictions.npz'] = hashlib.sha256(fixture.getvalue()).hexdigest()
            payloads[commit_name] = json.dumps(commit).encode()
            altered = root/'rehashed-predictions.zip'
            with zipfile.ZipFile(altered, 'x') as target:
                for name, payload in payloads.items():
                    target.writestr(name, payload)
            db, pin = self.registry(root)
            with self.assertRaises(ValueError):
                ingest_export(db, pin, altered, digest(altered), self.mapping)
            self.assertEqual(verify_catalog(db, pin)['records'], [])

    def test_wrong_archive_hash_and_unsafe_mapping_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            db, pin = self.registry(Path(directory))
            with self.assertRaises(ValueError):
                ingest_export(db, pin, self.archive, '0'*64, self.mapping)
            mapping = [{**self.mapping[0], 'job_prefix': '../FT'}]
            with self.assertRaises(ValueError):
                ingest_export(db, pin, self.archive, self.archive_sha, mapping)
            for malformed in ([None], [{}], [{**self.mapping[0], 'run_id': True}], self.mapping*2):
                with self.subTest(mapping=malformed), self.assertRaises(ValueError):
                    ingest_export(db, pin, self.archive, self.archive_sha, malformed)
            self.assertEqual(verify_catalog(db, pin)['records'], [])


if __name__ == '__main__':
    unittest.main()
