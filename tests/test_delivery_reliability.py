"""Receipt failure injection and label-free saved-prediction consistency."""
import copy
import io
import json
import os
import random
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import numpy as np

from phase3_delivery.catalog import create_output, initialize, verify_catalog
from phase3_delivery.io import publish_new_bytes
from phase3_delivery.prediction_integrity import validate_predictions
from phase3_delivery.snapshot import export_snapshot, restore_snapshot
from src.phase3.common import array_identity, digest
from tests.test_delivery_catalog import fixture_row, manifest


def prediction_fixture():
    values = {'ids': np.array([1, 3, 6, 9, 10], dtype='<u8'),
              'predicted_slots': np.array([1, 0, 2, 1, 0], dtype='u1'),
              'source_codes_in_slot_order': np.array([0, 5, 2], dtype='<i2')}
    matrix = [[0]*16 for _ in range(16)]
    matrix[0][0], matrix[5][5], matrix[2][5], matrix[5][2] = 2, 1, 1, 1
    stage = {'full_seen_bank_rows': 5, 'bank_ids_sha256': array_identity(values['ids']),
             'source_codes_in_slot_order': [0, 5, 2], 'full_seen_confusion_source_code_order': matrix}
    return values, stage


def npz_bytes(values):
    stream = io.BytesIO()
    np.savez(stream, **values)
    return stream.getvalue()


class PredictionIntegrity(unittest.TestCase):
    def test_seeded_marginal_oracle_and_guaranteed_single_prediction_mutations(self):
        # This seed belongs to an artifact-validator fixture, not training.
        generator = random.Random(701106)
        for case in range(80):
            width = generator.randrange(2, 17)
            codes = [0]+generator.sample(list(range(1, 16)), width-1)
            size = generator.randrange(1, 1200)
            ids = np.asarray(sorted(generator.sample(range(100000), size)), dtype='<u8')
            choices = [generator.randrange(width) for _ in range(size)]
            truths = [generator.choice(codes) for _ in range(size)]
            matrix = [[0]*16 for _ in range(16)]
            # Scalar-loop oracle is independent of the validator's bincount.
            for truth, choice in zip(truths, choices):
                matrix[truth][codes[choice]] += 1
            values = {'ids': ids, 'predicted_slots': np.asarray(choices, dtype='u1'),
                      'source_codes_in_slot_order': np.asarray(codes, dtype='<i2')}
            stage = {'full_seen_bank_rows': size, 'bank_ids_sha256': array_identity(ids),
                     'source_codes_in_slot_order': codes, 'full_seen_confusion_source_code_order': matrix}
            with self.subTest(case=case, width=width, size=size):
                self.assertEqual(validate_predictions(npz_bytes(values), stage)['prediction_rows'], size)
                index = generator.randrange(size)
                values['predicted_slots'][index] = (choices[index]+1) % width
                with self.assertRaisesRegex(ValueError, 'confusion-column'):
                    validate_predictions(npz_bytes(values), stage)

    def test_source_code_marginals_use_registered_slots_and_no_reference_labels(self):
        values, stage = prediction_fixture()
        result = validate_predictions(npz_bytes(values), stage)
        self.assertEqual(result['prediction_rows'], 5)
        self.assertTrue(result['class_marginals_verified'])
        self.assertFalse(result['reference_labels_accessed'])
        self.assertFalse(result['new_inference'])

    def test_wrong_id_shape_dtype_order_identity_and_duplicates_rejected(self):
        original, stage = prediction_fixture()
        for ids in (original['ids'][:-1], original['ids'].reshape(1, -1), original['ids'].astype('<i8'),
                    original['ids'][::-1], np.array([1, 1, 6, 9, 10], dtype='<u8'),
                    original['ids']+np.uint64(1)):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                validate_predictions(npz_bytes({**original, 'ids': ids}), stage)

    def test_prediction_slots_schema_dtype_range_and_source_order_rejected(self):
        original, stage = prediction_fixture()
        for values in ({**original, 'extra': np.array([1])},
                       {key: value for key, value in original.items() if key != 'predicted_slots'},
                       {**original, 'predicted_slots': original['predicted_slots'].astype('f4')},
                       {**original, 'predicted_slots': original['predicted_slots'].reshape(1, -1)},
                       {**original, 'predicted_slots': np.array([255]*5, dtype='u1')},
                       {**original, 'source_codes_in_slot_order': np.array([0, 2, 5], dtype='<i2')},
                       {**original, 'source_codes_in_slot_order': np.array([0, 5, 2], dtype='<i8')}):
            with self.subTest(keys=list(values)), self.assertRaises(ValueError):
                validate_predictions(npz_bytes(values), stage)

    def test_rehashed_bytes_with_inconsistent_prediction_counts_rejected(self):
        values, stage = prediction_fixture()
        values['predicted_slots'][:] = 0
        with self.assertRaisesRegex(ValueError, 'confusion-column'):
            validate_predictions(npz_bytes(values), stage)

    def test_invalid_count_metadata_rejected_before_binning(self):
        values, stage = prediction_fixture()
        mutations = [lambda s: s.update(full_seen_bank_rows=True), lambda s: s.update(full_seen_bank_rows=0),
                     lambda s: s.update(source_codes_in_slot_order=[0, 0, 2]),
                     lambda s: s.update(source_codes_in_slot_order=[False, 5, 2]),
                     lambda s: s['full_seen_confusion_source_code_order'][0].__setitem__(0, True),
                     lambda s: s['full_seen_confusion_source_code_order'][0].__setitem__(0, -1),
                     lambda s: s['full_seen_confusion_source_code_order'].pop()]
        for mutate in mutations:
            changed = copy.deepcopy(stage)
            mutate(changed)
            with self.subTest(stage=changed), self.assertRaises(ValueError):
                validate_predictions(npz_bytes(values), changed)

    def test_marginal_validation_does_not_claim_per_example_label_correctness(self):
        values, stage = prediction_fixture()
        values['predicted_slots'] = values['predicted_slots'][::-1].copy()
        # A different assignment with identical totals remains indistinguishable
        # without reference labels. Keep this limitation executable and explicit.
        self.assertTrue(validate_predictions(npz_bytes(values), stage)['class_marginals_verified'])


class ReceiptPublication(unittest.TestCase):
    def test_publication_failure_retains_complete_staging_and_prior_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prior = root/'prior.json'
            prior.write_bytes(b'previous evidence\n')
            with patch('phase3_delivery.io.os.link', side_effect=OSError('injected publication failure')), \
                    self.assertRaises(OSError):
                publish_new_bytes(root/'not-published.json', b'complete staged payload\n')
            self.assertFalse((root/'not-published.json').exists())
            self.assertEqual(prior.read_bytes(), b'previous evidence\n')
            self.assertEqual([p.read_bytes() for p in root.glob('uncommitted-receipt-*')],
                             [b'complete staged payload\n'])

    def test_flush_failure_leaves_staging_evidence_without_success_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root/'acceptance.json'
            with patch('phase3_delivery.io.os.fsync', side_effect=OSError('injected flush failure')), \
                    self.assertRaises(OSError):
                create_output(target, {'status': 'passed'})
            self.assertFalse(target.exists())
            staged = list(root.glob('uncommitted-receipt-*'))
            self.assertEqual(len(staged), 1)
            self.assertEqual(json.loads(staged[0].read_text(encoding='utf-8')), {'status': 'passed'})

    def test_serialization_failure_and_existing_path_never_publish_or_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root/'receipt.json'
            with self.assertRaises(ValueError):
                create_output(target, {'invalid': float('nan')})
            self.assertEqual(list(root.iterdir()), [])
            create_output(target, {'status': 'original', 'unicode': '\u03b1'})
            before = target.read_bytes()
            with self.assertRaises(FileExistsError):
                create_output(target, {'status': 'replacement'})
            self.assertEqual(target.read_bytes(), before)

    def test_two_publishers_racing_commit_one_complete_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root/'race.json'
            barrier, real_link = threading.Barrier(2), os.link
            def racing_link(source, destination):
                barrier.wait(timeout=10)
                return real_link(source, destination)
            def publish(index):
                try:
                    create_output(target, {'writer': index, 'payload': str(index)*10000})
                    return 'committed'
                except FileExistsError:
                    return 'retained_previous'
            with patch('phase3_delivery.io.os.link', side_effect=racing_link), ThreadPoolExecutor(2) as pool:
                results = list(pool.map(publish, range(2)))
            self.assertEqual(sorted(results), ['committed', 'retained_previous'])
            value = json.loads(target.read_text(encoding='utf-8'))
            self.assertEqual(value['payload'], str(value['writer'])*10000)

    def test_cleanup_failure_cannot_reclassify_an_already_committed_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(Path, 'unlink', side_effect=OSError('injected cleanup failure')):
                publish_new_bytes(root/'committed.json', b'{"status":"passed"}\n')
            self.assertEqual(json.loads((root/'committed.json').read_text(encoding='utf-8'))['status'], 'passed')
            self.assertEqual(len(list(root.glob('uncommitted-receipt-*'))), 1)

    def test_restore_marker_flush_failure_never_leaves_a_commit_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row, _ = fixture_row(root, 'not-imported')
            _, spec, pin = manifest(root, [row])
            db, archive, destination = root/'catalog.sqlite', root/'snapshot.zip', root/'restored'
            initialize(db, spec, pin)
            before = verify_catalog(db, pin)
            export_snapshot(db, pin, archive)
            real_fsync, failed = os.fsync, []
            def fail_marker_flush(descriptor):
                if destination.exists() and not failed:
                    failed.append(True)
                    raise OSError('injected restore marker flush failure')
                return real_fsync(descriptor)
            with patch('phase3_delivery.io.os.fsync', side_effect=fail_marker_flush), self.assertRaises(OSError):
                restore_snapshot(archive, digest(archive), pin, destination)
            self.assertFalse((destination/'restore.commit.json').exists())
            self.assertTrue((destination/'restore.failed.json').exists())
            self.assertEqual(len(list(destination.glob('uncommitted-receipt-*'))), 1)
            self.assertEqual(verify_catalog(db, pin), before)


class RecoverySoak(unittest.TestCase):
    def test_one_cycle_counts_only_qualification_and_ledger_chain(self):
        from scripts.qualify_delivery_recovery import qualify
        from src.phase3.common import identity
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = qualify(root/'evidence', root/'private', 1, 812321)
            self.assertEqual(result['status'], 'passed')
            self.assertEqual(result['research_model_executions'], 0)
            self.assertEqual(result['forced_uncommitted_exits'], result['cycles'])
            self.assertEqual(result['attempts'], 5+3*result['cycles'])
            self.assertFalse(result['final_test_accessed'])
            previous = '0'*64
            lines = (root/'evidence/cycles.jsonl').read_text(encoding='utf-8').splitlines()
            for line in lines:
                row = json.loads(line)
                sha = row.pop('ledger_sha256')
                self.assertEqual(row['previous_ledger_sha256'], previous)
                self.assertEqual(sha, identity(row))
                previous = sha
            self.assertEqual(len(lines), result['cycles'])
            self.assertEqual(previous, result['last_ledger_sha256'])
            self.assertEqual(digest(root/'evidence/cycles.jsonl'), result['ledger_sha256'])

    def test_invalid_duration_or_overlapping_paths_rejected_before_workspace_creation(self):
        from scripts.qualify_delivery_recovery import qualify
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for seconds in (0, -1, True, 7201):
                with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                    qualify(root/'evidence', root/'private', seconds, 1)
            with self.assertRaises(ValueError):
                qualify(root/'evidence', root/'evidence/private', 1, 1)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
