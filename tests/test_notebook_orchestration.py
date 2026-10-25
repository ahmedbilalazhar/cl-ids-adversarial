"""Execute generated orchestration cells with mocked subprocesses and budgets."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from kaggle_worker.notebook import generate
from kaggle_worker.session import CommandFailed, SessionBudget


class Clock:
    now = 100.
    def monotonic(self):
        return self.now
    def perf_counter(self):
        return self.now
    def time_ns(self):
        return int(self.now*10**9)


class NotebookOrchestration(unittest.TestCase):
    def run_cells(self, root, full_data, worker_seconds=1, fail_bootstrap=False, partial_evaluation=False):
        notebook = json.loads(generate({'archive_sha256': 'a'*64}, root/'notebook').read_text())
        clock, commands, exports = Clock(), [], []
        working = root/'working'
        project = root/'project'
        project.mkdir()
        def logged(command, module, output, cwd, env, timeout):
            commands.append((module, command, timeout))
            if module.endswith('bootstrap'):
                if fail_bootstrap:
                    raise CommandFailed({'module': module, 'outcome': 'injected_failure'})
                environment = Path(command[command.index('--output')+1])
                environment.mkdir(parents=True)
                (environment/'.phase3-environment.json').write_text('{}')
            elif module.endswith('worker'):
                clock.now += worker_seconds
                job = Path(command[command.index('--output')+1])
                job.mkdir(parents=True, exist_ok=True)
                (job/'invocation-0001.json').write_text('{"status":"complete"}')
            elif module.endswith('evaluate'):
                destination = Path(command[command.index('--output')+1])
                destination.mkdir(parents=True, exist_ok=True)
                (destination/'evaluation.commit.json').write_text('{}')
            return {'outcome': 'succeeded'}
        def export(output, destination):
            exports.append((output, destination))
            return {'archive': 'fixture.zip', 'archive_sha256': 'b'*64}
        def sha(path):
            return hashlib.sha256(path.read_bytes()).hexdigest()
        scope = {'Path': Path, 'json': json, 'time': clock, 'os': os, 'sys': sys,
                 'SESSION_REMAINING_SECONDS': 7200, 'SESSION_STARTED': 100,
                 'EXPORT_RESERVE_SECONDS': 240, 'MINIMUM_FREE_BYTES': 1,
                 'DEVICE': 'cpu', 'RUN_FULL_DATA': full_data, 'PROJECT': project,
                 'manifest': {'train_manifest_sha256': 'a'*64}, 'sha': sha}
        environment = ''.join(notebook['cells'][3]['source']).replace('/kaggle/working', working.as_posix())
        def factory(seconds, reserve, started):
            return SessionBudget(seconds, reserve, started, clock.monotonic)
        with patch('kaggle_worker.session.SessionBudget', side_effect=factory), \
             patch('kaggle_worker.session.run_logged', side_effect=logged), \
             patch('kaggle_worker.session.export_outputs', side_effect=export):
            if fail_bootstrap:
                with self.assertRaises(CommandFailed):
                    exec(compile(environment, 'generated-environment', 'exec'), scope)
            else:
                exec(compile(environment, 'generated-environment', 'exec'), scope)
                if partial_evaluation:
                    (scope['OUTPUT']/'FT-development').mkdir()
                    (scope['OUTPUT']/'FT-development-attempt-0001').mkdir()
                exec(compile(''.join(notebook['cells'][5]['source']), 'generated-jobs', 'exec'), scope)
        return notebook, commands, exports

    def test_default_runs_no_full_data_jobs(self):
        with tempfile.TemporaryDirectory() as directory:
            notebook, commands, _ = self.run_cells(Path(directory), False)
            self.assertTrue(any('RUN_FULL_DATA = False' in ''.join(c['source']) for c in notebook['cells']))
            self.assertFalse(any(module.endswith('worker') for module, _, _ in commands))

    def test_remaining_session_budget_prevents_second_long_job(self):
        with tempfile.TemporaryDirectory() as directory:
            _, commands, _ = self.run_cells(Path(directory), True, worker_seconds=6900)
            workers = [command for module, command, _ in commands if module.endswith('worker')]
            self.assertEqual(len(workers), 1)
            self.assertEqual(float(workers[0][workers[0].index('--budget-seconds')+1]), 6960)

    def test_setup_failure_exports_once_and_retains_original_error(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, exports = self.run_cells(Path(directory), False, fail_bootstrap=True)
            self.assertEqual(len(exports), 1)

    def test_partial_evaluation_uses_fresh_path_and_completed_output_verifier(self):
        with tempfile.TemporaryDirectory() as directory:
            _, commands, _ = self.run_cells(Path(directory), True, partial_evaluation=True)
            evaluations = [command for module, command, _ in commands if module.endswith('evaluate')]
            self.assertTrue(str(evaluations[0][evaluations[0].index('--output')+1]).endswith('FT-development-attempt-0002'))
            self.assertTrue(all('--verify-existing' in command for command in evaluations))


if __name__ == '__main__':
    unittest.main()
