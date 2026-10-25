"""Fault injection and measured synthetic performance checks for candidate v2."""
from __future__ import annotations

import argparse
import contextlib
import gc
import io
import json
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path
from unittest.mock import patch

from .runtime import configure

import numpy as np

from src.phase3.common import digest, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v3.protocol import Settings

from . import bootstrap as setup
from .checks import fixtures
from .data import StageCache, map_targets
from .evaluate import stage_snapshots
from .worker import run_job


def peak(function):
    gc.collect()
    tracemalloc.start()
    try:
        value = function()
        _, maximum = tracemalloc.get_traced_memory()
        return value, maximum
    finally:
        tracemalloc.stop()


def run():
    runtime = configure('cpu')
    reports = []
    stages = fixtures()
    with tempfile.TemporaryDirectory(prefix='phase3-review-v2-') as temporary:
        base = Path(temporary)
        settings = Settings('DR', rounds=3, epochs=4)
        job = base/'crash-job'
        def supplied_package(*args):
            return StageCache(stages.__getitem__)
        with patch('kaggle_worker.worker.StageCache.package', side_effect=supplied_package):
            with contextlib.redirect_stdout(io.StringIO()), patch('kaggle_worker.worker.publish_receipt', side_effect=RuntimeError('injected crash before final receipt')):
                try:
                    run_job(base, '0'*64, job, settings, 'cpu')
                except RuntimeError as exc:
                    assert 'injected crash' in str(exc)
                else:
                    raise AssertionError('Fault injection did not run')
            before = {path.relative_to(job).as_posix(): digest(path) for path in job.glob('segment-*/*') if path.is_file()}
            assert not list(job.glob('invocation-*.json'))
            recovered = run_job(base, '0'*64, job, settings, 'cpu')
            assert recovered['status'] == 'complete' and recovered['recovered_completion_receipt'] is True
            assert recovered['commits_verified'] == 12
            after = {path.relative_to(job).as_posix(): digest(path) for path in job.glob('segment-*/*') if path.is_file()}
            assert before == after, 'Recovery re-executed or changed committed artifacts'
            assert len(list(job.glob('segment-*'))) == 1
            third = run_job(base, '0'*64, job, settings, 'cpu')
            assert third['status'] == 'already_complete_verified'
        reports.append({'check': 'crash-after-final-commit-before-receipt', 'status': 'passed',
                        'committed_files_unchanged': len(before), 'new_model_executions_on_recovery': 0})
        procedure = read_json(job/'job.json')
        execution = procedure['execution']
        paths = sorted(job.glob('segment-*/E*-R*.npz'))
        def old_retention():
            return [read_transaction(path, execution) for path in paths]
        old, old_peak = peak(old_retention)
        original_arrays = sum(value.nbytes for _, arrays, _ in old for value in arrays.values())
        expected = {meta['commits']//3: {'slots': meta['slots'],
                    'model': {key[6:]: value.copy() for key, value in arrays.items() if key.startswith('model.')}}
                    for meta, arrays, marker in old if marker['stage_end']}
        del old
        snapshots, new_peak = peak(lambda: stage_snapshots(job, execution, settings.rounds))
        new_arrays = sum(value.nbytes for snapshot in snapshots.values() for value in snapshot['model'].values())
        assert snapshots.keys() == expected.keys()
        for stage in snapshots:
            assert snapshots[stage]['slots'] == expected[stage]['slots']
            assert snapshots[stage]['model'].keys() == expected[stage]['model'].keys()
            for key in snapshots[stage]['model']:
                np.testing.assert_array_equal(snapshots[stage]['model'][key], expected[stage]['model'][key])
        assert new_arrays < original_arrays and new_peak < old_peak
        reports.append({'check': 'streaming-stage-snapshots-exact-and-memory', 'status': 'passed',
                        'retained_numpy_bytes_before': original_arrays, 'retained_numpy_bytes_after': new_arrays,
                        'tracemalloc_peak_before_bytes': old_peak, 'tracemalloc_peak_after_bytes': new_peak,
                        'scope': 'Synthetic 12-checkpoint DR collection; traced Python/NumPy allocations, not process RSS or GPU memory'})
        # Completed receipt contents are immutable even when checkpoint state passes.
        settings_file = next(job.glob('segment-*/settings.json'))
        settings_file.write_text(settings_file.read_text()+'\n', encoding='utf-8')
        with patch('kaggle_worker.worker.StageCache.package', side_effect=supplied_package):
            try:
                run_job(base, '0'*64, job, settings, 'cpu')
            except ValueError as exc:
                assert 'receipt payload changed' in str(exc)
            else:
                raise AssertionError('Completed receipt ignored changed artifact')
        reports.append({'check': 'completed-job-artifact-drift-rejected', 'status': 'passed'})
        root = base/'working'
        root.mkdir()
        environment = root/'environment'
        commands = []
        installed = {'python': setup.PYTHON_VERSION, 'packages': {'numpy': '2.3.5', 'torch': '2.7.0+cpu'}}
        def fake_command(command, **kwargs):
            commands.append(command)
            if 'venv' in command:
                python = environment/'bin/python'
                python.parent.mkdir(parents=True)
                python.write_text('synthetic interpreter placeholder', encoding='utf-8')
        with patch.object(setup.sys, 'platform', 'linux'), patch.object(setup.platform, 'machine', return_value='x86_64'), patch.object(setup, 'version', return_value=setup.UV_VERSION), patch.object(setup.subprocess, 'run', side_effect=fake_command), patch.object(setup, 'fingerprint', return_value=installed):
            setup.bootstrap('cpu', environment, root)
            assert len(commands) == 3 and 'sync' in commands[-1] and '--require-hashes' in commands[-1]
            first_count = len(commands)
            setup.bootstrap('cpu', environment, root)
            assert len(commands) == first_count, 'Reuse unexpectedly performed an install/network operation'
            with patch.object(setup, 'fingerprint', return_value={**installed, 'python': '3.11.0'}):
                try:
                    setup.bootstrap('cpu', environment, root)
                except ValueError:
                    pass
                else:
                    raise AssertionError('Environment drift accepted')
            try:
                setup.bootstrap('cuda', environment, root)
            except ValueError:
                pass
            else:
                raise AssertionError('Another lock profile reused the environment')
        reports.append({'check': 'locked-bootstrap-install-reuse-and-drift', 'status': 'passed',
                        'subprocesses_mocked': True, 'reuse_install_commands': 0})
    # Match the representative training row count with synthetic labels only.
    generator = np.random.default_rng(20261025)
    slots = [0, 3, 7, 12, 15]
    labels = generator.choice(np.asarray(slots, dtype=np.int64), size=183045)
    mapping = {code: index for index, code in enumerate(slots)}
    baseline = lambda: np.array([mapping[int(label)] for label in labels], dtype=np.int64)
    np.testing.assert_array_equal(baseline(), map_targets(labels, slots))
    old_times, new_times = [], []
    for _ in range(9):
        began = time.perf_counter()
        baseline()
        old_times.append(time.perf_counter()-began)
        began = time.perf_counter()
        map_targets(labels, slots)
        new_times.append(time.perf_counter()-began)
    try:
        map_targets(np.asarray([4], dtype=np.int64), slots)
    except KeyError:
        pass
    else:
        raise AssertionError('Unregistered supplied label mapped silently')
    reports.append({'check': 'vectorized-target-map-exact-benchmark', 'status': 'passed', 'rows': len(labels),
                    'baseline_seconds': old_times, 'vectorized_seconds': new_times,
                    'baseline_median_seconds': statistics.median(old_times),
                    'vectorized_median_seconds': statistics.median(new_times),
                    'median_kernel_speedup': statistics.median(old_times)/statistics.median(new_times),
                    'scope': 'Synthetic label mapping only, concurrent background CPU study; no full-training speedup claim'})
    return {'status': 'passed', 'schema': 'kaggle-review-v2', 'runtime': runtime, 'checks': reports,
            'final_test_accessed': False, 'actual_GPU_qualified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    try:
        result = run()
    except Exception as exc:
        write_json(args.output, {'status': 'failed_attempt_retained', 'exception': type(exc).__name__, 'message': str(exc)})
        raise
    write_json(args.output, result)
    print(json.dumps({'status': result['status'], 'checks': len(result['checks'])}))


if __name__ == '__main__':
    main()
