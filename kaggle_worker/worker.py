"""Notebook CLI: development qualification only, no final seed dispatch option."""
from __future__ import annotations

import argparse
import contextlib
import os
import time
from dataclasses import asdict
from pathlib import Path

from .runtime import configure, resources, safe_output

from src.phase3.common import digest, identity, read_json, write_json

from .checkpoint import restore
from .artifacts import HistoryValidator, discover, validate_receipt, verify_local_files
from .contracts import make_procedure, parse_settings, validate_procedure
from .data import StageCache
from .simulator import execute
from .selection import selected_settings


@contextlib.contextmanager
def lock(path):
    # Kernel releases this OS lock after a crash; the small lock file is retained.
    with path.open('a+b') as handle:
        if os.name == 'nt':
            import msvcrt
            handle.seek(0)
            if not handle.read(1):
                handle.write(b'0')
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            if os.name == 'nt':
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def inventory(job, execution, settings, loader, device):
    rows = {}
    # Only durable commit markers are candidates. Uncommitted payloads/logs remain.
    history = HistoryValidator(settings.rounds, settings.learner)
    for ref in discover(job, settings.rounds):
        path = job/ref.payload
        _, _, meta, commit = restore(path, execution, settings, loader, device)
        history.accept(meta, commit, ref)
        rows[ref.ordinal] = (path, commit, meta)
    return rows


def publish_receipt(output, index, rows, execution, runtime, loader, device, started, status, rounds,
                    recovered_completion=False):
    # Validate again at the publication boundary. A changed source/config/input
    # leaves committed evidence intact and cannot acquire a success receipt.
    validate_procedure(read_json(output/'job.json'))
    loader.verify_integrity()
    receipt = {'schema': 'kaggle-worker-receipt-v1', 'status': status,
               'execution': execution, 'commits_verified': len(rows), 'trajectory_count': 1,
               'segment_count_is_not_replicate_count': True, 'runtime_identity': identity(runtime),
               'whole_invocation_seconds': time.perf_counter()-started, 'stage_cache_loads': loader.loads,
               'whole_invocation_excludes_imports': True, 'resources': resources(device),
               'recovered_completion_receipt': recovered_completion,
               'checkpoints': [{'path': path.relative_to(output).as_posix(), **marker}
                               for path, marker, _ in rows.values()],
               'files': {path.relative_to(output).as_posix(): digest(path)
                         for path in sorted(output.glob('segment-*/*')) if path.is_file()},
               'final_test_accessed': False, 'final_dispatchable': False}
    destination = output/f'invocation-{index:04d}.json'
    if destination.exists():
        raise FileExistsError('Receipt history is immutable')
    validate_receipt(receipt, execution, rounds)
    write_json(destination, receipt)
    return receipt


def run_job(train, expected_manifest, output, settings, device, budget=3600, reserve=120,
            transition_bound=600, max_commits=None):
    started = time.perf_counter()
    settings = parse_settings(asdict(settings))
    runtime = configure(device)
    procedure = make_procedure(settings, runtime, expected_manifest)
    execution = procedure['execution']
    loader = StageCache.package(train, settings, expected_manifest)
    output = safe_output(output)
    output.mkdir(parents=True, exist_ok=True)
    with lock(output/'worker.lock'):
        procedure_path = output/'job.json'
        if procedure_path.exists():
            validate_procedure(read_json(procedure_path))
            # JSON turns dose tuples into lists; compare canonical serialized data.
            if identity(read_json(procedure_path)) != identity(procedure):
                raise ValueError('Job identity changed; preserve this job and use a new output')
        else:
            if any(p.name != 'worker.lock' for p in output.iterdir()):
                raise ValueError('Output contains unbound artifacts')
            write_json(procedure_path, procedure)
        rows = inventory(output, execution, settings, loader, device)
        receipts = sorted(output.glob('invocation-*.json'))
        latest = read_json(receipts[-1]) if receipts else None
        if latest is not None:
            recorded = validate_receipt(latest, execution, settings.rounds)
            actual = discover(output, settings.rounds)
            if tuple(ref.payload for ref in recorded) != tuple(ref.payload for ref in actual[:len(recorded)]):
                raise ValueError('Receipt prefix differs from actual committed lineage')
            verify_local_files(output, latest['files'])
        index = 1
        while (output/f'segment-{index:04d}').exists() or (output/f'invocation-{index:04d}.json').exists():
            index += 1
        if len(rows) == settings.rounds*4:
            if (latest is None or latest.get('status') != 'complete' or
                    latest.get('commits_verified') != len(rows) or latest.get('execution') != execution):
                return publish_receipt(output, index, rows, execution, runtime, loader, device, started,
                                       'complete', settings.rounds, recovered_completion=True)
            verify_local_files(output, latest['files'], exact=True)
            return {'status': 'already_complete_verified', 'commits': len(rows), 'no_new_execution': True}
        resume = rows[max(rows)][0] if rows else None
        remaining = budget-(time.perf_counter()-started)
        result = execute(settings, loader, execution, output/f'segment-{index:04d}', device, resume,
                         budget_seconds=remaining, reserve_seconds=reserve, transition_bound_seconds=transition_bound,
                         stop_after_commits=max_commits)
        rows = inventory(output, execution, settings, loader, device)
        # This receipt covers all checkpoint bytes, including states from a crash
        # recovered at the last valid committed boundary; retries add no seed.
        return publish_receipt(output, index, rows, execution, runtime, loader, device, started,
                               result['status'], settings.rounds)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=['cpu', 'cuda:0', 'cuda:1'], default='cpu')
    parser.add_argument('--train-package', type=Path, required=True)
    parser.add_argument('--train-manifest-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--learner', choices=['FT', 'EI', 'DR'], default='DR')
    parser.add_argument('--admission', choices=['NONE', 'DM', 'DC', 'DQ'], default='NONE')
    parser.add_argument('--seed', type=int, choices=[101, 102, 103], default=101)
    parser.add_argument('--dose', nargs=2, type=int, default=[0, 1])
    parser.add_argument('--qualification-overrides', action='store_true',
                        help='Explicitly permit non-selected development fixture settings')
    parser.add_argument('--rounds', type=int, choices=[3, 12])
    parser.add_argument('--epochs', type=int, choices=[1, 4])
    parser.add_argument('--learning-rate', type=float)
    parser.add_argument('--lambda-E', type=float)
    parser.add_argument('--lambda-y', type=float)
    parser.add_argument('--lambda-z', type=float)
    parser.add_argument('--budget-seconds', type=float, default=3600)
    parser.add_argument('--reserve-seconds', type=float, default=120)
    parser.add_argument('--transition-bound-seconds', type=float, default=600)
    parser.add_argument('--max-commits', type=int, help='Optional early stop at a durable round boundary')
    args = parser.parse_args()
    settings = selected_settings(args.learner, args.seed, args.admission, tuple(args.dose))
    overrides = {key: getattr(args, key) for key in
                 ('rounds', 'epochs', 'learning_rate', 'lambda_E', 'lambda_y', 'lambda_z')
                 if getattr(args, key) is not None}
    if overrides and not args.qualification_overrides:
        parser.error('Non-selected settings require --qualification-overrides')
    settings = parse_settings({**asdict(settings), **overrides})
    result = run_job(args.train_package, args.train_manifest_sha256, args.output, settings, args.device,
                     args.budget_seconds, args.reserve_seconds, args.transition_bound_seconds, args.max_commits)
    print({k: v for k, v in result.items() if k in ('status', 'commits_verified', 'whole_invocation_seconds', 'commits')})


if __name__ == '__main__':
    main()
