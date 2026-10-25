"""Committed-evaluation reuse checks without model construction or inference."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from kaggle_worker.contracts import make_procedure
from kaggle_worker.evaluate import evaluate
from kaggle_worker.runtime import configure
from src.phase3.common import array_identity, digest, identity, read_json, write_json
from src.phase3_v2.data import BASE_DEV
from src.phase3_v3.protocol import Settings
from tests.test_continuation import synthetic_metric


class EvaluationReuse(unittest.TestCase):
    def fixture(self, root):
        runtime = configure('cpu')
        job, output, development = root/'job', root/'evaluation', root/'development'
        job.mkdir()
        output.mkdir()
        development.mkdir()
        # The published bank hash is mocked; no research bank is opened.
        (development/'manifest.json').write_text('fabricated bank manifest')
        procedure = make_procedure(Settings('FT', rounds=3, epochs=1), runtime, 'a'*64)
        write_json(job/'job.json', procedure)
        metrics, _ = synthetic_metric()
        metrics.update(settings=procedure['settings'], execution=procedure['execution'], evaluation_runtime=runtime,
                       final_dispatchable=False, development_manifest_sha256=BASE_DEV)
        snapshots = {}
        for stage in metrics['stages']:
            slots = stage['source_codes_in_slot_order']
            state = {'classifier.bias': np.zeros(len(slots), dtype=np.float32)}
            snapshots[stage['stage']] = {'slots': slots, 'model': state}
            stage['model_sha256'] = identity({'slots': slots, 'weights': {k: array_identity(v) for k, v in state.items()}})
            np.savez(output/f"E{stage['stage']}-predictions.npz", fabricated=np.array([1]))
        write_json(output/'metrics.json', metrics)
        self.commit(job, output, runtime)
        return job, output, development, snapshots, runtime

    def commit(self, job, output, runtime):
        files = {'metrics.json'} | {f'E{stage}-predictions.npz' for stage in range(1, 5)}
        write_json(output/'evaluation.commit.json', {'schema': 'kaggle-evaluation-commit-v1',
                   'job_manifest_sha256': digest(job/'job.json'), 'development_manifest_sha256': BASE_DEV,
                   'evaluation_runtime_identity': identity(runtime),
                   'files': {name: digest(output/name) for name in files}})

    def bank_digest(self, path):
        return BASE_DEV if path.parent.name == 'development' else digest(path)

    def test_valid_committed_output_is_reused_without_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            job, output, development, snapshots, _ = self.fixture(Path(directory))
            with patch('kaggle_worker.evaluate.digest', side_effect=self.bank_digest), \
                 patch('kaggle_worker.evaluate.stage_snapshots', return_value=snapshots), \
                 patch('kaggle_worker.evaluate.ReferenceMLP', side_effect=AssertionError('inference must not repeat')):
                result = evaluate(job, development, output, verify_existing=True)
            self.assertFalse(result['new_inference'])
            self.assertEqual(result['status'], 'existing_evaluation_verified')
            with self.assertRaises(FileExistsError):
                evaluate(job, development, output)

    def test_corrupt_prediction_and_incomplete_evaluation_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            job, output, development, snapshots, _ = self.fixture(Path(directory))
            with patch('kaggle_worker.evaluate.digest', side_effect=self.bank_digest), \
                 patch('kaggle_worker.evaluate.stage_snapshots', return_value=snapshots):
                (output/'E1-predictions.npz').write_bytes(b'corrupt')
                with self.assertRaises(ValueError):
                    evaluate(job, development, output, verify_existing=True)
                (output/'evaluation.commit.json').unlink()
                with self.assertRaises(FileNotFoundError):
                    evaluate(job, development, output, verify_existing=True)

    def test_changed_model_or_settings_rejected_even_if_commit_hashes_updated(self):
        for change in ('model', 'settings', 'uncommitted_file'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                job, output, development, snapshots, runtime = self.fixture(Path(directory))
                metrics = read_json(output/'metrics.json')
                if change == 'model':
                    metrics['stages'][0]['model_sha256'] = '0'*64
                elif change == 'settings':
                    metrics['settings']['epochs'] = True
                else:
                    (output/'leftover.tmp').write_text('interrupted publish')
                write_json(output/'metrics.json', metrics)
                self.commit(job, output, runtime)
                with patch('kaggle_worker.evaluate.digest', side_effect=self.bank_digest), \
                     patch('kaggle_worker.evaluate.stage_snapshots', return_value=snapshots):
                    with self.assertRaises(ValueError):
                        evaluate(job, development, output, verify_existing=True)


if __name__ == '__main__':
    unittest.main()
