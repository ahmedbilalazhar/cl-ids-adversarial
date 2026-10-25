"""Bounded transparent fixtures; writes evidence without reading research features."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from unittest.mock import patch

from .runtime import FROZEN, configure

import numpy as np
import torch

from src.phase3.common import ROOT, digest, identity, read_json, write_json
from src.phase3.model import ReferenceMLP
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.data import StageInput
from src.phase3_v2.learning import importance_reference
from src.phase3_v2.prepare import corrupt
from src.phase3_v2.train import Simulator
from src.phase3_v3.protocol import Settings, code_identity

from .accelerator import dark_loss
from .checkpoint import restore
from .data import StageCache
from .handoff import inspect
from .planner import plan
from .simulator import execute
from .worker import inventory, run_job


def fixtures():
    stages = {}
    for stage, codes in enumerate(((0, 7, 12), (0, 3, 4), (0, 10, 13), (0, 1, 2)), 1):
        generator = np.random.default_rng(124+stage)
        owners = np.repeat(np.arange(5, dtype='i1'), (131, 27, 0, 11, 0))
        n = len(owners)
        x = generator.uniform(-.2, .2, (n, 74)).astype('<f4')
        labels = np.asarray([0 if i < 90 else codes[1+i % 2] for i in range(n)], dtype='<i8')
        stages[stage] = StageInput(stage, x, labels, np.arange(stage*10000, stage*10000+n, dtype='<u8'), owners)
    return stages


def equal_checkpoint(left, right, execution):
    lm, la, lc = read_transaction(left, execution)
    rm, ra, rc = read_transaction(right, execution)
    if lm != rm or la.keys() != ra.keys() or lc['state_identity'] != rc['state_identity']:
        raise AssertionError('Checkpoint metadata/inventory/logical identity mismatch')
    for key in la:
        if la[key].dtype != ra[key].dtype or not np.array_equal(la[key], ra[key]):
            raise AssertionError('Typed array mismatch: '+key)
    # Raw NPZ bytes may carry different timestamps; logical equality is required.
    return len(la)


def run(device='cpu'):
    runtime = configure(device)
    started = time.perf_counter()
    reports = []
    stages = fixtures()
    methods = [('FT', 'NONE'), ('EI', 'NONE'), ('DR', 'NONE'), ('DR', 'DM'), ('DR', 'DC'), ('DR', 'DQ')]
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        for budget in ((3, 1), (3, 4), (12, 1)):
            for learner, admission in methods:
                # 12-round backend check for all arms, both v3 budgets exercised.
                settings = Settings(learner, admission, rounds=budget[0], epochs=budget[1])
                execution = {'fixture': 'no_dataset_rows', 'settings': identity(settings.scientific())}
                key = f'{learner}-{admission}-{budget[0]}r{budget[1]}'
                reference, cached, emulated = [base/(key+suffix) for suffix in ('-reference', '-cache', '-device')]
                cache = StageCache(stages.__getitem__)
                with contextlib.redirect_stdout(io.StringIO()):
                    expected = Simulator(settings, stages.__getitem__, execution).execute(reference)
                    actual = execute(settings, cache, execution, cached)
                    execute(settings, StageCache(stages.__getitem__), execution, emulated, emulate_accelerator=True)
                if expected['ledger'] != actual['ledger'] or cache.loads != 4:
                    raise AssertionError('Caching changed ledger or repeated stage loads')
                array_checks = 0
                for row in expected['checkpoints']:
                    array_checks += equal_checkpoint(reference/row['file'], cached/row['file'], execution)
                    array_checks += equal_checkpoint(reference/row['file'], emulated/row['file'], execution)
                # Independent target construction and current-pool protection.
                value = cache(1)
                targets = value.targets([0, 7, 12])
                expected_targets = np.searchsorted([0, 7, 12], value.y)
                if not np.array_equal(targets, expected_targets):
                    raise AssertionError('Cached target mapping wrong')
                targets[0] = 99
                if not np.array_equal(value.targets([0, 7, 12]), expected_targets):
                    raise AssertionError('Caller mutated cached targets')
                reports.append({'check': key, 'status': 'passed', 'checkpoint_pairs': 2*len(expected['checkpoints']),
                                'typed_arrays_exact': array_checks, 'stage_loads': cache.loads,
                                'reference_fixture_seconds': expected['elapsed_seconds'],
                                'cached_fixture_seconds': actual['elapsed_seconds'],
                                'timing_scope': 'Synthetic correctness fixture, not a research workload benchmark'})
        # Recovery covers every retained-state category, all four stage transitions,
        # and a committed boundary before any stage-end importance update.
        for learner in ('FT', 'EI', 'DR'):
            settings = Settings(learner, rounds=3, epochs=4)
            execution = {'fixture': 'recovery', 'learner': learner, 'device': device}
            whole, prefix, suffix = [base/f'recovery-{learner}-{s}' for s in ('whole', 'prefix', 'suffix')]
            with contextlib.redirect_stdout(io.StringIO()):
                expected = execute(settings, StageCache(stages.__getitem__), execution, whole, device)
                execute(settings, StageCache(stages.__getitem__), execution, prefix, device, stop_after_commits=2)
                result = execute(settings, StageCache(stages.__getitem__), execution, suffix, device,
                                 resume=prefix/'E1-R2.npz')
            if result['ledger'] != expected['ledger']:
                raise AssertionError('Recovered ledger differs')
            for row in result['checkpoints']:
                equal_checkpoint(whole/row['file'], suffix/row['file'], execution)
            wrong_execution = {**execution, 'device': 'wrong-runtime'}
            try:
                restore(prefix/'E1-R2.npz', wrong_execution, settings, stages.__getitem__, device)
            except ValueError:
                pass
            else:
                raise AssertionError('Incompatible resume accepted')
            reports.append({'check': f'{device}-{learner}-exact-recovery', 'status': 'passed',
                            'suffix_checkpoints_exact': len(result['checkpoints'])})
            # The suffix starts in a new interpreter, not a live Python process.
            fresh = base/f'fresh-{learner}'
            command = [sys.executable, '-m', 'kaggle_worker.fixture', '--learner', learner,
                       '--device', device, '--output', str(fresh), '--resume', str(prefix/'E1-R2.npz'),
                       '--execution-json', json.dumps(execution, sort_keys=True, separators=(',', ':'))]
            subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT)}, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            fresh_result = read_json(fresh/'run.json')
            if fresh_result['ledger'] != expected['ledger']:
                raise AssertionError('Fresh-process recovered ledger differs')
            for row in fresh_result['checkpoints']:
                equal_checkpoint(whole/row['file'], fresh/row['file'], execution)
            reports.append({'check': f'{device}-{learner}-fresh-process-recovery', 'status': 'passed',
                            'suffix_checkpoints_exact': len(fresh_result['checkpoints'])})
        # Exercise the actual job wrapper against injected synthetic stage inputs;
        # package authentication remains a separate full-data bundle verification.
        settings = Settings('DR', rounds=3, epochs=4)
        job = base/'wrapper-job'
        def package_fixture(*args):
            return StageCache(stages.__getitem__)
        with patch('kaggle_worker.worker.StageCache.package', side_effect=package_fixture), contextlib.redirect_stdout(io.StringIO()):
            first = run_job(base, '0'*64, job, settings, 'cpu', max_commits=2)
            second = run_job(base, '0'*64, job, settings, 'cpu')
            third = run_job(base, '0'*64, job, settings, 'cpu')
        if (first['commits_verified'], second['commits_verified'], third['status']) != (2, 12, 'already_complete_verified'):
            raise AssertionError('Wrapper resumed or deduplicated work incorrectly')
        procedure = read_json(job/'job.json')
        rows = inventory(job, procedure['execution'], settings, stages.__getitem__, 'cpu')
        if sorted(rows) != list(range(1, 13)):
            raise AssertionError('Job collection has missing/duplicate boundaries')
        handoff = base/'handoff.zip'
        synthetic_evidence = {'status': 'passed', 'runtime': configure('cpu'), 'final_dispatchable': False,
                              'actual_CUDA_fixtures_passed': False,
                              'checks': [{'status': 'passed', 'check': 'synthetic-handoff-fixture'}]}
        with zipfile.ZipFile(handoff, 'x') as archive:
            archive.writestr('synthetic-acceptance.json', json.dumps(synthetic_evidence))
            for path in sorted(job.rglob('*')):
                if path.is_file():
                    archive.write(path, 'DR/'+path.relative_to(job).as_posix())
        inspected = inspect(handoff, digest(handoff))
        if inspected['jobs'][0]['commits_verified'] != 12:
            raise AssertionError('Handoff failed to verify synthetic committed job')
        for kind in ('unsafe-path', 'changed-checkpoint'):
            invalid = base/(kind+'.zip')
            with zipfile.ZipFile(handoff) as source, zipfile.ZipFile(invalid, 'x') as target:
                for name in source.namelist():
                    payload = source.read(name)
                    if kind == 'changed-checkpoint' and name == 'DR/segment-0001/E1-R1.npz':
                        payload += b'corrupt'
                    target.writestr(name, payload)
                if kind == 'unsafe-path':
                    target.writestr('../unsafe.txt', 'synthetic')
            try:
                inspect(invalid, digest(invalid))
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid handoff accepted: '+kind)
        reports.append({'check': 'handoff-full-collection-and-invalid-archives', 'status': 'passed',
                        'rejected_corruptions': 2})
        # Wrong execution and payload corruption must stop; no silent restart.
        corrupt_path = rows[1][0]
        original_bytes = corrupt_path.read_bytes()
        corrupt_path.write_bytes(original_bytes+b'corrupt')
        try:
            inventory(job, procedure['execution'], settings, stages.__getitem__, 'cpu')
        except ValueError:
            pass
        else:
            raise AssertionError('Corrupt job payload accepted')
        reports.append({'check': 'wrapper-resume-deduplication-and-corruption-rejection', 'status': 'passed'})
        for settings in (Settings(seed=1), Settings(seed=42), Settings(rounds=24)):
            try:
                execute(settings, stages.__getitem__, {}, base/'forbidden')
            except ValueError:
                pass
            else:
                raise AssertionError('Final seed or undeclared budget accepted')
        reports.append({'check': 'final-seal-and-settings-rejection', 'status': 'passed', 'rejected': 3})
        original = stages[2]
        last = set()
        for dose in ((0, 1), (1, 10), (3, 10), (1, 2)):
            labels, info = corrupt(original.y, original.ids, original.owner, 101, 2, dose)
            chosen = set(info['poison_ids'])
            if not last <= chosen or len(chosen) != dose[0]*info['eligible_hulk']//dose[1]:
                raise AssertionError('Non-nested or incorrect integer poison count')
            last = chosen
        poisoned = {**stages, 2: StageInput(2, original.x, labels, original.ids, original.owner)}
        for learner, admission in methods:
            settings = Settings(learner, admission, rounds=3, epochs=4, dose=(1, 2))
            execution = {'fixture': 'synthetic-half-dose', 'settings': identity(settings.scientific())}
            reference = base/f'poison-{learner}-{admission}-reference'
            candidate = base/f'poison-{learner}-{admission}-candidate'
            with contextlib.redirect_stdout(io.StringIO()):
                expected = Simulator(settings, poisoned.__getitem__, execution).execute(reference)
                execute(settings, StageCache(poisoned.__getitem__), execution, candidate, emulate_accelerator=True)
            for row in expected['checkpoints']:
                equal_checkpoint(reference/row['file'], candidate/row['file'], execution)
        reports.append({'check': 'nested-corruption-and-device-emulation-parity-all-arms', 'status': 'passed',
                        'dose_prefixes': 4, 'method_trajectories': 6})
        # Exact arithmetic example: per-record normalization, mask before square.
        predicted = torch.tensor([[2., 4., 999.], [1., 5., 7.]], device=device, requires_grad=True)
        teachers = torch.tensor([[1., 2., float('nan')], [0., 3., 4.]], device=device)
        widths = torch.tensor([2, 3], device=device)
        value = dark_loss(predicted, teachers, widths)
        torch.testing.assert_close(value, torch.tensor((5/2+14/3)/2, device=device), rtol=2e-7, atol=2e-7)
        value.backward()
        torch.testing.assert_close(predicted.grad, torch.tensor([[.5, 1., 0.], [1/3, 2/3, 1.]], device=device),
                                   rtol=2e-7, atol=2e-7)
        reports.append({'check': 'independent-masked-dark-loss-and-gradient', 'status': 'passed'})
        if device.startswith('cuda'):
            from src.phase3_v2.learning import empirical_importance
            model = ReferenceMLP(3, 101).to(device).eval()
            x = torch.from_numpy(stages[1].x[:7].copy()).to(device)
            targets = torch.tensor([0, 1, 2, 0, 1, 2, 0], device=device)
            actual = empirical_importance(model, x, targets)
            expected = importance_reference(model, x, targets)
            for key in actual:
                torch.testing.assert_close(actual[key], expected[key], rtol=2e-5, atol=2e-7)
            cpu = ReferenceMLP(3, 101).eval()
            cpu.load_state_dict({k: v.cpu() for k, v in model.state_dict().items()})
            torch.testing.assert_close(model(x).cpu(), cpu(x.cpu()), rtol=2e-5, atol=2e-7)
            reports.append({'check': 'actual-CUDA-independent-importance-and-forward', 'status': 'passed',
                            'rtol': 2e-5, 'atol': 2e-7})
        for package in ('core', 'course', 'complete', 'focused'):
            for contributors in (1, 8):
                schedule = plan(package, contributors)
                seeds = [s for v in schedule['assignments'].values() for s in v['seeds']]
                if len(seeds) != len(set(seeds)) or sorted(seeds) != [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 42]:
                    raise AssertionError('Schedule duplicates/drops seeds')
                if schedule['final_dispatchable'] or any(len(b['conditions']) != len(set(b['conditions'])) for b in schedule['blocks']):
                    raise AssertionError('Schedule became dispatchable or duplicated conditions')
        reports.append({'check': 'planning-counts-and-paired-seed-allocation', 'status': 'passed', 'plans': 8})
    if code_identity() != FROZEN:
        raise AssertionError('Frozen source changed')
    return {'schema': 'kaggle-worker-acceptance-v1', 'status': 'passed', 'runtime': runtime,
            'checks': reports, 'elapsed_seconds': time.perf_counter()-started,
            'GPU_qualified': False, 'actual_CUDA_fixtures_passed': device.startswith('cuda'),
            'scope': 'Synthetic fixtures only. CPU cache/device-emulation exactness; same-runtime recovery. Full-data target-runtime confirmations, costs and release remain pending.',
            'final_test_accessed': False, 'final_dispatchable': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=['cpu', 'cuda:0', 'cuda:1'], default='cpu')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verify-existing', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        if not args.verify_existing:
            raise FileExistsError(args.output)
        previous = read_json(args.output)
        if (previous.get('status') != 'passed' or previous.get('runtime') != configure(args.device) or
                not previous.get('checks') or any(r['status'] != 'passed' for r in previous['checks'])):
            raise ValueError('Existing fixture evidence is failed or incompatible')
        print({'status': 'existing_fixture_evidence_verified', 'no_new_execution': True})
        return
    try:
        result = run(args.device)
    except Exception as exc:
        write_json(args.output, {'status': 'failed_attempt_retained', 'exception': type(exc).__name__, 'message': str(exc)})
        raise
    write_json(args.output, result)
    print({'status': result['status'], 'groups': len(result['checks']), 'elapsed_seconds': result['elapsed_seconds']})


if __name__ == '__main__':
    main()
