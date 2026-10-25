"""Bounded input and exact-byte parsing tests, including a deterministic race."""
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phase3_delivery.import_counts import import_counts
from phase3_delivery.io import MAX_JSON_BYTES, read_verified_bytes
from src.phase3.common import ROOT, digest, read_json
from tests.test_delivery_catalog import fixture_row


class TransportIntegrity(unittest.TestCase):
    def test_exact_bytes_hash_and_size_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'fixture.json'
            path.write_bytes(b'{"count":1}')
            expected = digest(path)
            self.assertEqual(read_verified_bytes(path, expected), b'{"count":1}')
            with self.assertRaises(ValueError):
                read_verified_bytes(path, expected, max_bytes=4)
            with self.assertRaises(ValueError):
                read_verified_bytes(path, '0'*64)
            with self.assertRaises(ValueError):
                read_verified_bytes(path, expected, max_bytes=True)
            with path.open('wb') as stream:
                stream.truncate(MAX_JSON_BYTES+1)
            with self.assertRaises(ValueError):
                read_verified_bytes(path, expected)

    @unittest.skipIf(os.name == 'nt', 'POSIX FIFO has no equivalent local Windows fixture')
    def test_fifo_is_rejected_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'pipe'
            os.mkfifo(path)
            with self.assertRaises(ValueError):
                read_verified_bytes(path, '0'*64)

    def test_parse_uses_verified_snapshot_after_source_file_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, path = fixture_row(folder, 'snapshot')
            expected = row['metric_sha256']
            original = read_json(path)
            def snapshot_then_change(source, pin):
                payload = read_verified_bytes(source, pin)
                changed = {**original, 'A': 0}
                path.write_text(json.dumps(changed))
                return payload
            from src.phase3_v2.checkpoint import strict_json
            def parse_exact(payload):
                self.assertEqual(hashlib.sha256(payload.encode('utf-8')).hexdigest(), expected)
                return strict_json(payload)
            with patch('phase3_delivery.import_counts.read_verified_bytes', side_effect=snapshot_then_change), \
                 patch('phase3_delivery.import_counts.strict_json', side_effect=parse_exact):
                result = import_counts(path, expected, row['settings'], row['execution'],
                                       read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes'],
                                       kind='synthetic', run_id='snapshot', seen_ids=set(), seen_conditions=set())
            self.assertEqual(result['endpoints']['acquisition_A'], 1)
            self.assertNotEqual(digest(path), expected)
            with self.assertRaises(ValueError):
                import_counts(path, expected, row['settings'], row['execution'],
                              read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes'],
                              kind='synthetic', run_id='snapshot', seen_ids=set(), seen_conditions=set())


if __name__ == '__main__':
    unittest.main()
