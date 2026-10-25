"""Notebook scheduling/export regressions; synthetic commands and files only."""
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

from kaggle_worker.session import CommandFailed, SessionBudget, export_outputs, file_lock, run_logged, sha256


class NotebookSession(unittest.TestCase):
    def test_session_budget_decreases_and_keeps_export_reservation(self):
        clock = Mock(side_effect=[100., 600., 7000.])
        budget = SessionBudget(7200, 240, 100, clock)
        self.assertEqual(budget.job_seconds(1080), 6960)
        self.assertEqual(budget.job_seconds(1080), 6460)
        self.assertEqual(budget.job_seconds(1080), 0)
        for seconds, reserve, started in ((True, 240, 0), (7200, 7200, 0), (7200, 240, float('nan'))):
            with self.assertRaises(ValueError):
                SessionBudget(seconds, reserve, started)
        with self.assertRaises(ValueError):
            SessionBudget(7200, 240, 100, lambda: 99).available()

    def test_commands_record_success_failure_timeout_and_launch_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run_logged([sys.executable, '-c', 'print("fixture")'], 'fixture.success', root, root, os.environ.copy(), 30)
            self.assertEqual(result['outcome'], 'succeeded')
            for command, timeout, outcome in [
                    ([sys.executable, '-c', 'raise RuntimeError("fixture failure")'], 30, 'failed'),
                    ([sys.executable, '-c', 'import time;time.sleep(10)'], .2, 'timed_out'),
                    ([str(root/'missing-interpreter')], 30, 'launch_failed')]:
                with self.subTest(outcome=outcome), self.assertRaises(CommandFailed) as failure:
                    run_logged(command, 'fixture.failure', root, root, os.environ.copy(), timeout)
                self.assertEqual(failure.exception.receipt['outcome'], outcome)
            receipts = sorted(root.glob('command-*.json'))
            self.assertEqual(len(receipts), 4)
            for path in receipts:
                value = json.loads(path.read_text())
                self.assertEqual(value['log_sha256'], sha256(path.with_suffix('.log')))

    def test_export_is_repeatable_and_preserves_orphaned_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, exports = root/'output', root/'exports'
            (output/'FT').mkdir(parents=True)
            (output/'FT/job.json').write_text('{}')
            (output/'failed-attempt.log').write_text('retained failure')
            first = export_outputs(output, exports)
            second = export_outputs(output, exports)
            self.assertEqual(first['archive_sha256'], second['archive_sha256'])
            self.assertNotEqual(first['archive'], second['archive'])
            self.assertFalse(first['provider_durability_qualified'])
            self.assertEqual(first['excluded_runtime_files'], ['FT/worker.lock'])
            self.assertNotIn('FT/worker.lock', first['files'])
            (exports/'phase3-qualification-output-0003.json').write_text('retain this receipt')
            third = export_outputs(output, exports)
            self.assertEqual(third['archive'], 'phase3-qualification-output-0004.zip')
            with zipfile.ZipFile(exports/third['archive']) as archive:
                self.assertEqual(archive.read('failed-attempt.log'), b'retained failure')
            with self.assertRaises(ValueError):
                export_outputs(output, output/'nested')

    def test_export_refuses_an_active_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root/'output'
            (output/'FT').mkdir(parents=True)
            (output/'FT/job.json').write_text('{}')
            with file_lock(output/'FT/worker.lock'):
                with self.assertRaises(OSError):
                    export_outputs(output, root/'exports')
            self.assertFalse(list((root/'exports').glob('*.zip')))
            self.assertEqual(export_outputs(output, root/'exports')['status'], 'complete_export')

    def test_export_detects_mutation_and_retains_failed_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root/'output'
            output.mkdir()
            source = output/'fixture.log'
            source.write_text('before export')
            close = zipfile.ZipFile.close
            mutated = False
            def change_after_close(container):
                nonlocal mutated
                close(container)
                if not mutated:
                    source.write_text('changed while exporting')
                    mutated = True
            with patch('kaggle_worker.session.zipfile.ZipFile.close', change_after_close):
                with self.assertRaises(ValueError):
                    export_outputs(output, root/'exports')
            receipt = json.loads((root/'exports/phase3-qualification-output-0001.json').read_text())
            self.assertEqual(receipt['status'], 'failed_export_retained')
            self.assertTrue((root/'exports/phase3-qualification-output-0001.zip').exists())
            self.assertEqual(export_outputs(output, root/'exports')['status'], 'complete_export')


if __name__ == '__main__':
    unittest.main()
