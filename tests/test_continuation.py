"""Synthetic boundary tests: no training, data packages or final outcomes."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from kaggle_worker.selection import selected_settings
from kaggle_worker.worker import lock
from phase3_delivery.import_counts import import_counts
from src.phase3.common import ROOT, digest, read_json
from src.phase3_v2.evaluate import stage_counts


def synthetic_metric():
    classes = read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes']
    arrival = [next(c['arrival_stage'] for c in classes if c['source_code'] == i) for i in range(16)]
    eligible = [c['source_code'] for c in classes if c['scoring_eligible']]
    names = [str(i) for i in range(16)]
    stages, matrix = [], [[None]*4 for _ in range(4)]
    for t in range(1, 5):
        slots = [c['source_code'] for c in sorted(classes, key=lambda c: (c['arrival_stage'], c['source_code']))
                 if c['arrival_stage'] <= t]
        labels = [0]*4+[c for c in slots if c != 0]
        y = np.array(labels)
        cohorts = np.array([1, 2, 3, 4]+[arrival[c] for c in labels[4:]])
        counts = stage_counts(t, slots, y, y.copy(), eligible, names, arrival, cohorts,
                              np.zeros(len(y), dtype=bool))
        counts['bank_ids_sha256'] = str(t)*64
        stages.append(counts)
        for j in range(t):
            matrix[t-1][j] = 1.
    return {'schema': 'kaggle-qualification-development-metrics-v1', 'status': 'valid_development_only',
            'settings': {'seed': 1}, 'execution': {'settings_identity': 'a'*64, 'train_manifest_sha256': 'b'*64},
            'stages': stages, 'R_accuracy_by_stage_and_arrival_cohort': matrix,
            'A': 1., 'equal_stage_ACC4': 1., 'BWT4': 0., 'forgetting4': 0.,
            'final_test_accessed': False}, classes


class Continuation(unittest.TestCase):
    def test_seed_summary(self):
        from phase3_delivery.analysis import seed_summary
        seeds = list(range(1, 12))+[42]
        values = dict(zip(seeds, range(1, 13)))
        result = seed_summary(values)
        self.assertEqual(result['mean']['value'], 6.5)
        self.assertAlmostEqual(result['sample_standard_deviation'], 13**.5)
        values[42] = None
        self.assertIsNone(seed_summary(values)['mean'])
        values.pop(42)
        with self.assertRaises(ValueError):
            seed_summary(values)

    def test_selected_settings(self):
        for learner in ('FT', 'EI', 'DR'):
            settings = selected_settings(learner)
            self.assertEqual((settings.rounds, settings.epochs, settings.learning_rate), (12, 1, .001))
        self.assertEqual(selected_settings('EI').lambda_E, 100)
        self.assertEqual(selected_settings('DR').lambda_z, .1)
        with self.assertRaises(ValueError):
            selected_settings('DR', seed=42)

    def test_duplicate_writer_then_normal_release(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'worker.lock'
            program = 'from pathlib import Path; from kaggle_worker.worker import lock; import sys\nwith lock(Path(sys.argv[1])): print("acquired")'
            with lock(path):
                child = subprocess.run([sys.executable, '-c', program, str(path)], capture_output=True, text=True)
                self.assertNotEqual(child.returncode, 0)
            child = subprocess.run([sys.executable, '-c', program, str(path)], capture_output=True, text=True)
            self.assertEqual(child.returncode, 0, child.stderr)

    def test_cli_selection_and_override_guard(self):
        from kaggle_worker.worker import main
        base = ['worker', '--train-package', 'synthetic', '--train-manifest-sha256', 'a'*64,
                '--output', 'synthetic', '--learner', 'EI']
        with patch('sys.argv', base), patch('kaggle_worker.worker.run_job', return_value={}) as job:
            main()
            self.assertEqual(job.call_args.args[3].lambda_E, 100)
        with patch('sys.argv', base+['--lambda-E', '10']), patch('kaggle_worker.worker.run_job') as job:
            with self.assertRaises(SystemExit):
                main()
            job.assert_not_called()

    def test_preflight_storage_and_declared_limits(self):
        from kaggle_worker.preflight import inspect
        with tempfile.TemporaryDirectory() as directory:
            result = inspect('cpu', directory, 7200, 1)
            self.assertFalse(result['sklearn']['required'])
            self.assertFalse(result['durability_qualified'])
            self.assertFalse(result['session_limit_verified_by_provider'])
            with self.assertRaises(RuntimeError):
                inspect('cpu', directory, 7200, 10**30)
            with self.assertRaises(ValueError):
                inspect('cpu', directory, float('nan'), 1)

    def test_import_positive_and_duplicate_lineage(self):
        metric, classes = synthetic_metric()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'counts.json'
            path.write_text(json.dumps(metric))
            ids, conditions = set(), set()
            args = (path, digest(path), metric['settings'], metric['execution'], classes)
            result = import_counts(*args, kind='synthetic', run_id='first', seen_ids=ids, seen_conditions=conditions)
            self.assertEqual(result['endpoints']['acquisition_A'], 1)
            for run_id in ('first', 'alias'):
                with self.assertRaises(ValueError):
                    import_counts(*args, kind='synthetic', run_id=run_id, seen_ids=ids, seen_conditions=conditions)

    def test_cpu_metric_requires_bound_run(self):
        metric, classes = synthetic_metric()
        execution = metric.pop('execution')
        metric['schema'] = 'phase3-development-metrics-v3'
        with tempfile.TemporaryDirectory() as directory:
            path, run = Path(directory)/'counts.json', Path(directory)/'run.json'
            run.write_text(json.dumps({'status': 'complete', 'resumed_from': None,
                                      'settings': metric['settings'], 'execution': execution}))
            metric['run_manifest_sha256'] = digest(run)
            path.write_text(json.dumps(metric))
            args = (path, digest(path), metric['settings'], execution, classes)
            with self.assertRaises(ValueError):
                import_counts(*args, kind='synthetic', run_id='run', seen_ids=set(), seen_conditions=set())
            import_counts(*args, kind='synthetic', run_id='run', seen_ids=set(), seen_conditions=set(), run_manifest=run)
            run.write_text('{}')
            with self.assertRaises(ValueError):
                import_counts(*args, kind='synthetic', run_id='run', seen_ids=set(), seen_conditions=set(), run_manifest=run)

    def test_malformed_counts_and_bindings(self):
        metric, classes = synthetic_metric()
        mutations = {
            'missing_fields': lambda m: m.pop('stages'),
            'wrong_config': lambda m: m['settings'].update(seed=2),
            'wrong_runtime': lambda m: m['execution'].update(runtime='changed'),
            'incomplete_matrix': lambda m: m['R_accuracy_by_stage_and_arrival_cohort'].pop(),
            'false_matrix': lambda m: m['R_accuracy_by_stage_and_arrival_cohort'][3].__setitem__(0, .5),
            'future_cell': lambda m: m['R_accuracy_by_stage_and_arrival_cohort'][0].__setitem__(1, 0),
            'impossible_count': lambda m: m['stages'][3]['cohort_counts'][0].update(correct=999),
            'zero_denominator': lambda m: m['stages'][3]['cohort_counts'][0].update(total=0),
            'negative_confusion': lambda m: m['stages'][0]['full_seen_confusion_source_code_order'][0].__setitem__(0, -1),
            'incomplete_run': lambda m: m.update(status='partial'),
            'final_outcome': lambda m: m.update(final_test_accessed=True),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'counts.json'
            for name, mutate in mutations.items():
                with self.subTest(name=name):
                    changed = copy.deepcopy(metric)
                    mutate(changed)
                    path.write_text(json.dumps(changed))
                    ids, conditions = set(), set()
                    with self.assertRaises((ValueError, KeyError)):
                        import_counts(path, digest(path), metric['settings'], metric['execution'], classes,
                                      kind='synthetic', run_id='run', seen_ids=ids, seen_conditions=conditions)
                    self.assertFalse(ids or conditions)
            path.write_text(json.dumps(metric))
            for sha, kind in ((digest(path), 'final'), ('0'*64, 'synthetic'), (digest(path), 'development')):
                with self.assertRaises(ValueError):
                    import_counts(path, sha, metric['settings'], metric['execution'], classes,
                                  kind=kind, run_id='run', seen_ids=set(), seen_conditions=set())


if __name__ == '__main__':
    unittest.main()
