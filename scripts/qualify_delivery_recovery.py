"""Bounded, repeatable catalog concurrency/recovery soak using fabricated counts.

No model, feature bank or research condition is executed. Every cycle races an
export against independent valid/rejected writers and an abruptly exiting SQL
writer, then verifies the restored snapshot against the live catalog's history.
"""
import argparse
import ctypes
import json
import os
import random
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from phase3_delivery.catalog import create_output, initialize, ingest, verify_catalog
from phase3_delivery.snapshot import export_snapshot, restore_snapshot
from src.phase3.common import ROOT, canonical, digest, identity
from tests.test_delivery_catalog import fixture_row, manifest


def resources():
    """Observational process handle/working-set measurements, never GPU capacity."""
    if os.name != 'nt':
        folder = Path('/proc/self/fd')
        return {'open_handles': len(list(folder.iterdir())) if folder.is_dir() else None,
                'working_set_bytes': None}
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('faults', wintypes.DWORD)]+[
            (name, ctypes.c_size_t) for name in ('peak', 'working', 'paged_peak', 'paged',
                                               'nonpaged_peak', 'nonpaged', 'pagefile', 'pagefile_peak')]
    kernel = ctypes.windll.kernel32
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    process = kernel.GetCurrentProcess()
    handles, counters = wintypes.DWORD(), Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel.GetProcessHandleCount.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    got_handles = kernel.GetProcessHandleCount(process, ctypes.byref(handles))
    got_memory = ctypes.windll.psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb)
    return {'open_handles': handles.value if got_handles else None,
            'working_set_bytes': counters.working if got_memory else None}


def abrupt_writer(database, cycle):
    program = '''import os,sqlite3,sys
from pathlib import Path
c=sqlite3.connect(sys.argv[1],timeout=30)
c.execute("BEGIN IMMEDIATE")
c.execute("INSERT INTO attempts(run_id,outcome,detail) VALUES (?,?,?)",
          ("crash-"+sys.argv[2],"uncommitted","forced process exit fixture"))
if int(sys.argv[2])%16==0:
    path=Path(sys.argv[1]+".objects")/("uncommitted-crash-"+sys.argv[2])
    with path.open("xb") as stream:
        stream.write(sys.argv[2].encode()); stream.flush(); os.fsync(stream.fileno())
os._exit(37)
'''
    result = subprocess.run([sys.executable, '-c', program, str(database), str(cycle)],
                            capture_output=True, text=True, timeout=60)
    if result.returncode != 37:
        raise ValueError('Crash fixture did not reach its uncommitted write: '+result.stderr)
    return {'status': 'uncommitted_process_exited', 'exit_code': result.returncode}


def retire_successful_fixture(folder, cycle):
    """Bound synthetic disk usage; retain the first, latest and any failed cycle.

    Only generated successful-cycle fixtures in the new private workspace may
    be removed. The original catalog, raw objects and durable ledger survive.
    """
    archive = folder/f'cycle-{cycle:05d}.zip'
    restored = folder/f'restored-{cycle:05d}'
    if (archive.is_symlink() or restored.is_symlink() or
            archive.resolve().parent != folder.resolve() or restored.resolve().parent != folder.resolve() or
            any(path.is_symlink() for path in restored.rglob('*'))):
        raise ValueError('Synthetic fixture cleanup escaped its reserved workspace')
    archive.unlink()
    shutil.rmtree(restored.resolve())


def qualify(output, workspace, seconds, fixture_seed):
    if type(seconds) is not int or not 1 <= seconds <= 7200:
        raise ValueError('Choose a bounded duration from 1 to 7200 seconds')
    if output.resolve().is_relative_to(workspace.resolve()) or workspace.resolve().is_relative_to(output.resolve()):
        raise ValueError('Durable evidence and private workspace must be separate directories')
    output.mkdir(parents=True, exist_ok=False)
    workspace.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc)
    began = time.perf_counter()
    source_files = {str(path.relative_to(ROOT)): digest(path)
                    for path in sorted((ROOT/'phase3_delivery').glob('*.py'))}
    source_files.update({name: digest(ROOT/name) for name in
                         ('scripts/qualify_delivery_recovery.py', 'tests/test_delivery_catalog.py',
                          'tests/test_continuation.py')})
    randomizer = random.Random(fixture_seed)
    cycles, previous, added = 0, '0'*64, 0
    create_output(output/'started.json', {'schema': 'phase3-catalog-soak-start-v1', 'started_utc': started.isoformat(),
                  'duration_seconds': seconds, 'fixture_seed': fixture_seed, 'source_files': source_files,
                  'scope': 'Fabricated counts and forced SQL-process exits; no training or inference',
                  'final_test_accessed': False, 'final_dispatchable': False})
    ledger = output/'cycles.jsonl'
    try:
        rows, paths = [], {}
        for seed in range(1, 7):
            for arm in ('FT', 'EI', 'DR', 'DM', 'DC'):
                run_id = f'fixture-{arm}-{seed}'
                row, path = fixture_row(workspace, run_id, arm, seed,
                                        randomizer.choice(((0, 1), (1, 10), (3, 10), (1, 2))))
                rows.append(row)
                paths[run_id] = path
        aliases = {'alias-'+str(index): rows[index]['run_id'] for index in range(5)}
        _, spec, pin = manifest(workspace, rows, aliases)
        database = workspace/'catalog.sqlite'
        initialize(database, spec, pin)
        for parent in aliases.values():
            added += ingest(database, pin, parent, paths[parent])['independent_trajectories_added']
        bad = workspace/'deliberately-invalid.json'
        bad.write_bytes(b'{}')
        snapshots = workspace/'snapshots'
        snapshots.mkdir()
        with ledger.open('x', encoding='utf-8', newline='\n') as stream, ThreadPoolExecutor(4) as pool:
            while cycles == 0 or time.perf_counter()-began < seconds:
                cycle_start = time.perf_counter()
                cycles += 1
                archive = snapshots/f'cycle-{cycles:05d}.zip'
                parent = randomizer.choice(rows)['run_id']
                alias = randomizer.choice(sorted(aliases))
                def valid():
                    return ingest(database, pin, parent, paths[parent])
                def rejected():
                    try:
                        ingest(database, pin, parent, bad)
                    except ValueError:
                        return {'status': 'invalid_payload_rejected'}
                    raise ValueError('Invalid fixture was accepted')
                tasks = [('valid', valid), ('invalid', rejected),
                         ('alias', lambda: ingest(database, pin, alias, paths[aliases[alias]])),
                         ('crash', lambda: abrupt_writer(database, cycles)),
                         ('export', lambda: export_snapshot(database, pin, archive))]
                randomizer.shuffle(tasks)
                pending = {name: pool.submit(action) for name, action in tasks}
                results = {name: future.result(timeout=90) for name, future in pending.items()}
                added += results['valid']['independent_trajectories_added']
                restored = snapshots/f'restored-{cycles:05d}'
                receipt = restore_snapshot(archive, digest(archive), pin, restored)
                if receipt['logical_identity'] != results['export']['logical_identity']:
                    raise ValueError('Logical snapshot identity changed during reconstruction')
                source = verify_catalog(database, pin)
                recovered = verify_catalog(restored/'catalog.sqlite', pin)
                source_by_id = {row['row']['run_id']: row for row in source['records']}
                if (any(source_by_id[row['row']['run_id']] != row for row in recovered['records']) or
                        source['attempts'][:len(recovered['attempts'])] != recovered['attempts'] or
                        any(attempt['run_id'].startswith('crash-') for attempt in source['attempts']) or
                        len(source['records']) != added or len(source['attempts']) != 5+3*cycles):
                    raise ValueError('Concurrent import/history accounting differs from an independent prefix oracle')
                if not all(source['aliases'].get(key) == value for key, value in recovered['aliases'].items()):
                    raise ValueError('Recovered aliases do not refer to the original physical parents')
                expected_orphans = {'uncommitted-crash-'+str(index) for index in range(16, cycles+1, 16)}
                if (set(source['unreferenced_objects']) != expected_orphans or
                        not set(recovered['unreferenced_objects']) <= expected_orphans or
                        any((restored/'catalog.sqlite.objects'/name).read_bytes() !=
                            (Path(str(database)+'.objects')/name).read_bytes()
                            for name in recovered['unreferenced_objects'])):
                    raise ValueError('Interrupted object bytes or orphan visibility changed')
                before = digest(database)
                # Reading/reconstructing the snapshot must not mutate the source.
                verify_catalog(restored/'catalog.sqlite', pin)
                if digest(database) != before:
                    raise ValueError('Source database changed during isolated recovery verification')
                row = {'cycle': cycles, 'elapsed_seconds': time.perf_counter()-began,
                       'cycle_seconds': time.perf_counter()-cycle_start, 'task_submission_order': [name for name, _ in tasks],
                       'source_physical_observations': len(source['records']), 'source_attempts': len(source['attempts']),
                       'snapshot_physical_observations': len(recovered['records']),
                       'snapshot_attempts': len(recovered['attempts']), 'archive_sha256': digest(archive),
                       'logical_identity': receipt['logical_identity'], 'resources': resources(),
                       'previous_ledger_sha256': previous, 'status': 'passed'}
                previous = identity(row)
                stream.write(canonical({**row, 'ledger_sha256': previous})+'\n')
                stream.flush()
                os.fsync(stream.fileno())
                progress = {'cycles': cycles, 'elapsed_seconds': time.perf_counter()-began,
                            'last_ledger_sha256': previous, 'status': 'running'}
                (workspace/'progress.json').write_text(json.dumps(progress)+'\n', encoding='utf-8')
                if cycles > 2:
                    retire_successful_fixture(snapshots, cycles-1)
        for name, expected in source_files.items():
            if digest(ROOT/name) != expected:
                raise ValueError('Soak source changed while running: '+name)
        final = verify_catalog(database, pin)
        acceptance = {'schema': 'phase3-catalog-recovery-soak-v1', 'status': 'passed',
                      'started_utc': started.isoformat(), 'completed_utc': datetime.now(timezone.utc).isoformat(),
                      'requested_seconds': seconds, 'elapsed_seconds': time.perf_counter()-began, 'cycles': cycles,
                      'fixture_seed': fixture_seed, 'source_files': source_files, 'manifest_sha256': pin,
                      'physical_observations': len(final['records']), 'aliases': len(final['aliases']),
                      'attempts': len(final['attempts']), 'forced_uncommitted_exits': cycles,
                      'snapshots_restored_and_verified': cycles, 'invalid_payloads_rejected': cycles,
                      'unreferenced_crash_objects_preserved': len(final['unreferenced_objects']),
                      'synthetic_snapshot_retention': 'First and latest successful cycles, all failed cycles; ledger keeps every cycle hash',
                      'ledger_sha256': digest(ledger), 'last_ledger_sha256': previous,
                      'runtime': sys.version, 'platform': sys.platform,
                      'scope': 'Bounded local concurrency/recovery stress with fabricated counts; not power-loss/provider qualification',
                      'research_model_executions': 0, 'final_test_accessed': False, 'final_dispatchable': False}
        create_output(output/'acceptance.json', acceptance)
        return acceptance
    except BaseException as exc:
        create_output(output/'failure.json', {'status': 'failed_attempt_retained', 'exception': type(exc).__name__,
                      'message': str(exc), 'completed_cycles': cycles, 'last_ledger_sha256': previous,
                      'elapsed_seconds': time.perf_counter()-began, 'final_test_accessed': False, 'final_dispatchable': False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--fixture-seed', type=int, default=20261026)
    args = parser.parse_args()
    result = qualify(args.output, args.workspace, args.seconds, args.fixture_seed)
    print({name: result[name] for name in ('status', 'cycles', 'elapsed_seconds', 'forced_uncommitted_exits')})


if __name__ == '__main__':
    main()
