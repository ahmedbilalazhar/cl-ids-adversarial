"""Logical catalog recovery, corruption, writer isolation and partial publication."""
import copy
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from phase3_delivery.catalog import initialize, ingest, verify_catalog
from phase3_delivery.snapshot import export_snapshot, logical_state, restore_snapshot
from src.phase3.common import digest
from tests.test_delivery_catalog import fixture_row, manifest


class CatalogSnapshot(unittest.TestCase):
    def test_unknown_schema_extensions_are_rejected_instead_of_silently_dropped(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            db, pin, _, _, _ = self.fixture(folder)
            with closing(sqlite3.connect(db)) as connection:
                connection.execute('CREATE TABLE extra_history(note TEXT)')
                connection.execute('INSERT INTO extra_history VALUES (?)', ('preserve this too',))
                connection.commit()
            with self.assertRaises(ValueError):
                export_snapshot(db, pin, folder/'unsupported.zip')
            self.assertFalse((folder/'unsupported.zip').exists())
            with closing(sqlite3.connect(db)) as connection:
                self.assertEqual(connection.execute('SELECT note FROM extra_history').fetchall(), [('preserve this too',)])
                connection.execute('DROP TABLE extra_history')
                connection.execute("UPDATE sqlite_sequence SET seq=1000 WHERE name='attempts'")
                connection.commit()
            with self.assertRaises(ValueError):
                export_snapshot(db, pin, folder/'unsupported-counter.zip')
            self.assertFalse((folder/'unsupported-counter.zip').exists())

    def test_empty_catalog_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            row, _ = fixture_row(folder, 'not-yet-imported')
            _, spec, pin = manifest(folder, [row])
            database = folder/'empty.sqlite'
            initialize(database, spec, pin)
            before = verify_catalog(database, pin)
            archive = folder/'empty.zip'
            receipt = export_snapshot(database, pin, archive)
            self.assertEqual(receipt['objects'], 0)
            restored = folder/'restored'
            restore_snapshot(archive, digest(archive), pin, restored)
            self.assertEqual(verify_catalog(restored/'catalog.sqlite', pin), before)

    def fixture(self, folder):
        first, metric = fixture_row(folder, 'first')
        second, other = fixture_row(folder, 'second', 'EI', 2)
        _, spec, pin = manifest(folder, [first, second], {'alias': 'first'})
        db = folder/'catalog.sqlite'
        initialize(db, spec, pin)
        ingest(db, pin, 'first', metric)
        ingest(db, pin, 'first', metric)
        ingest(db, pin, 'alias', metric)
        with self.assertRaises(ValueError):
            ingest(db, pin, 'unknown', metric)
        # Retain an unreferenced interrupted object without treating it as data.
        (Path(str(db)+'.objects')/('0'*64)).write_bytes(b'failed fixture artifact')
        archive = folder/'snapshot.zip'
        receipt = export_snapshot(db, pin, archive)
        return db, pin, archive, receipt, other

    def alter(self, source, destination, change):
        with zipfile.ZipFile(source) as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        change(entries)
        with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED) as archive:
            for name, payload in entries.items():
                archive.writestr(name, payload)

    def test_round_trip_retains_history_aliases_orphans_missingness_and_next_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            db, pin, archive, receipt, other = self.fixture(folder)
            original = verify_catalog(db, pin)
            again = export_snapshot(db, pin, folder/'snapshot-again.zip')
            self.assertEqual(receipt['archive_sha256'], again['archive_sha256'])
            restored = folder/'restored'
            result = restore_snapshot(archive, digest(archive), pin, restored)
            self.assertEqual(result['new_research_trajectories'], 0)
            self.assertEqual(verify_catalog(restored/'catalog.sqlite', pin), original)
            self.assertEqual((restored/'catalog.sqlite.objects'/('0'*64)).read_bytes(), b'failed fixture artifact')
            self.assertTrue((restored/'restore.commit.json').is_file())
            self.assertEqual(ingest(restored/'catalog.sqlite', pin, 'second', other)['independent_trajectories_added'], 1)
            after = verify_catalog(restored/'catalog.sqlite', pin)
            self.assertEqual(after['attempts'][-1]['id'], original['attempts'][-1]['id']+1)
            self.assertEqual(verify_catalog(db, pin), original)

    def test_wrong_pins_and_existing_destinations_never_replace_data(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            _, pin, archive, _, _ = self.fixture(folder)
            for archive_pin, manifest_pin in (('0'*64, pin), (digest(archive), '0'*64)):
                with self.assertRaises(ValueError):
                    restore_snapshot(archive, archive_pin, manifest_pin, folder/'not-created')
                self.assertFalse((folder/'not-created').exists())
            destination = folder/'existing'
            destination.mkdir()
            sentinel = destination/'sentinel'
            sentinel.write_text('preserve this')
            with self.assertRaises(FileExistsError):
                restore_snapshot(archive, digest(archive), pin, destination)
            self.assertEqual(sentinel.read_text(), 'preserve this')

    def test_archive_paths_payloads_and_history_tampering_rejected_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            _, pin, archive, _, _ = self.fixture(folder)
            def state_change(entries, mutate):
                state = json.loads(entries['catalog.json'])
                mutate(state)
                entries['catalog.json'] = json.dumps(state).encode()
            changes = [
                lambda e: e.update({'../escape': b'never extract this'}),
                lambda e: state_change(e, lambda s: s['observations'][0].__setitem__(4, '{}')),
                lambda e: state_change(e, lambda s: s['attempts'][0].__setitem__(0, True)),
                lambda e: state_change(e, lambda s: s['attempts'].append(copy.deepcopy(s['attempts'][0]))),
                lambda e: state_change(e, lambda s: s.update(final_dispatchable=0)),
                lambda e: e.__setitem__(next(n for n in e if n.startswith('objects/') and not n.endswith('0'*64)), b'changed'),
            ]
            for index, mutate in enumerate(changes):
                changed, destination = folder/f'changed-{index}.zip', folder/f'rejected-{index}'
                self.alter(archive, changed, mutate)
                with self.subTest(case=index), self.assertRaises((ValueError, sqlite3.DatabaseError)):
                    restore_snapshot(changed, digest(changed), pin, destination)
                self.assertFalse(destination.exists())
            self.assertFalse((folder/'escape').exists())

    def test_export_owns_writer_slot_and_does_not_overwrite_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            db, pin, archive, _, _ = self.fixture(folder)
            def inspect_lock(connection, expected):
                with closing(sqlite3.connect(db, timeout=0)) as other:
                    with self.assertRaises(sqlite3.OperationalError):
                        other.execute('BEGIN IMMEDIATE')
                return logical_state(connection, expected)
            with patch('phase3_delivery.snapshot.logical_state', side_effect=inspect_lock):
                export_snapshot(db, pin, folder/'locked.zip')
            before = digest(archive)
            with self.assertRaises(FileExistsError):
                export_snapshot(db, pin, archive)
            self.assertEqual(digest(archive), before)

    def test_partial_publication_retains_failure_marker_and_never_claims_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            _, pin, archive, _, _ = self.fixture(folder)
            rename = Path.rename
            def fail_objects(path, target):
                if path.name.endswith('.objects'):
                    raise OSError('injected publication failure')
                return rename(path, target)
            destination = folder/'partial'
            with patch.object(Path, 'rename', fail_objects), self.assertRaises(OSError):
                restore_snapshot(archive, digest(archive), pin, destination)
            self.assertTrue((destination/'catalog.sqlite').exists())
            self.assertTrue((destination/'restore.failed.json').exists())
            self.assertFalse((destination/'restore.commit.json').exists())
            with self.assertRaises(FileExistsError):
                restore_snapshot(archive, digest(archive), pin, destination)

    def test_cli_preserves_failed_attempt_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            _, pin, archive, _, _ = self.fixture(folder)
            receipt = folder/'failure.json'
            command = [sys.executable, '-m', 'phase3_delivery.snapshot', 'restore', '--archive', str(archive),
                       '--archive-sha256', '0'*64, '--manifest-sha256', pin,
                       '--destination', str(folder/'never-created'), '--output', str(receipt)]
            result = subprocess.run(command, capture_output=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(receipt.read_text())['status'], 'failed_attempt_retained')
            before = digest(receipt)
            subprocess.run(command, capture_output=True, timeout=60)
            self.assertEqual(digest(receipt), before)
            self.assertFalse((folder/'never-created').exists())


if __name__ == '__main__':
    unittest.main()
