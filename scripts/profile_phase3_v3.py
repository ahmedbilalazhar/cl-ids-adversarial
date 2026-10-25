"""Fresh-process full CPU worker profiles; logical serialization is not a network."""
from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import subprocess
import sys
import time
import unittest
from pathlib import Path


def peak_working_set():
    if os.name != 'nt':
        return {'status': 'unavailable', 'reason': 'This measurement wrapper is qualified only for Windows working-set counters'}
    import ctypes
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)]+[(n, ctypes.c_size_t) for n in
            ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage',
             'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    get_handle = ctypes.windll.kernel32.GetCurrentProcess
    get_handle.restype = wintypes.HANDLE
    get_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_info.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
    get_info.restype = wintypes.BOOL
    if not get_info(get_handle(), ctypes.byref(counters), counters.cb):
        return {'status': 'unavailable', 'reason': 'GetProcessMemoryInfo failed'}
    return {'status': 'measured', 'peak_working_set_bytes': int(counters.PeakWorkingSetSize),
            'working_set_bytes_at_readout': int(counters.WorkingSetSize),
            'definition': 'OS process peak resident working set since this fresh worker started, including imports/training/evaluation'}


def model_message(arrays, metadata):
    import numpy as np

    if not arrays or any(not isinstance(a, np.ndarray) or a.dtype != np.dtype('<f4') or not np.isfinite(a).all() for a in arrays.values()):
        raise ValueError('Logical model messages require nonempty finite FP32 arrays')
    payload = io.BytesIO()
    np.savez(payload, metadata=np.array(json.dumps(metadata, sort_keys=True, separators=(',', ':'), allow_nan=False)), **arrays)
    return sum(a.nbytes for a in arrays.values()), payload.getvalue()


def communication(run_dir):
    from src.phase3.common import read_json
    from src.phase3_v2.checkpoint import read_transaction

    run = read_json(run_dir/'run.json')
    rows = []
    totals = dict.fromkeys(('active_only_downlink_raw', 'all_five_downlink_raw', 'active_uplink_raw',
                           'active_only_downlink_serialized', 'all_five_downlink_serialized', 'active_uplink_serialized',
                           'potential_EI_final_anchor_downlink_raw', 'potential_EI_final_anchor_downlink_serialized'), 0)
    for stage in range(1, 5):
        final = next(r for r in run['checkpoints'] if r['stage'] == stage and r['stage_end'])
        meta, all_arrays, _ = read_transaction(run_dir/final['file'])
        arrays = {k: v for k, v in all_arrays.items() if k.startswith('model.')}
        raw = sum(a.nbytes for a in arrays.values())
        updates = [r for r in run['ledger'] if r['kind'] == 'round' and r['stage'] == stage]
        active = sum(not c['inactive'] for r in updates for c in r['clients'])
        stage_totals = dict.fromkeys(totals, 0)
        for row in updates:
            for client in row['clients']:
                metadata = {'schema': 'phase3-logical-model-message-v1', 'stage': stage, 'round': row['round'],
                            'client': client['client'], 'slots': meta['slots'], 'direction': 'broadcast'}
                _, serialized = model_message(arrays, metadata)
                stage_totals['all_five_downlink_serialized'] += len(serialized)
                if not client['inactive']:
                    stage_totals['active_only_downlink_serialized'] += len(serialized)
                    _, serialized = model_message(arrays, {**metadata, 'direction': 'client_update'})
                    stage_totals['active_uplink_serialized'] += len(serialized)
        stage_totals['active_only_downlink_raw'] = stage_totals['active_uplink_raw'] = active*raw
        stage_totals['all_five_downlink_raw'] = 5*len(updates)*raw
        if run['settings']['learner'] == 'EI':
            for client in range(5):
                _, payload = model_message(arrays, {'schema': 'phase3-logical-model-message-v1', 'stage': stage,
                                                  'client': client, 'slots': meta['slots'], 'direction': 'final_anchor'})
                stage_totals['potential_EI_final_anchor_downlink_serialized'] += len(payload)
            stage_totals['potential_EI_final_anchor_downlink_raw'] = 5*raw
        for name in totals:
            totals[name] += stage_totals[name]
        rows.append({'stage': stage, 'head_width': len(meta['slots']), 'parameter_bytes': raw,
                     'rounds': len(updates), 'active_client_updates': active, **stage_totals})
    return {'stages': rows, 'totals': totals,
            'scope': 'Logical FP32 payload and concrete uncompressed NPZ template sizes, not measured network traffic. Template values use same-shaped final aggregate arrays; uncompressed size depends on schema/shapes, not parameter values.',
            'EI_note': 'Dedicated final-shared-model downlink is a separate upper accounting scenario; it could be piggybacked in a real protocol. Retained client replay/importance stays local.',
            'network_latency_and_remote_uploads': 'unmeasured; sequential simulator has no transport'}


def worker(request_path):
    started = time.perf_counter()
    import zipfile

    import numpy as np
    import torch

    from src.phase3.common import ROOT, array_identity, digest, read_json, write_json
    from src.phase3.model import ReferenceMLP
    from src.phase3_v2.checkpoint import read_transaction
    from src.phase3_v3.evaluate import evaluate
    from src.phase3_v3.protocol import Settings, code_identity
    from src.phase3_v3.train import run

    cold_import_seconds = time.perf_counter()-started
    request = read_json(request_path)
    output = request_path.parent
    settings = Settings(**{**request['settings'], 'dose': tuple(request['settings']['dose'])}).validate()
    source = Path(request['source_run'])
    prior = read_json(source/'run.json')
    if prior['execution']['code_identity'] != code_identity():
        raise ValueError('Source code differs from profiling condition')
    package = ROOT/f'data/processed/phase3-cpu-v2/s{settings.seed}-p000/train'
    before = time.perf_counter()
    trained = run(package, output/'train', settings, digest(package/'manifest.json'))
    run_seconds = time.perf_counter()-before
    before = time.perf_counter()
    metric = evaluate(ROOT/'data/processed/phase3-reference74-v1/development', output/'train', output/'evaluation')
    evaluation_seconds = time.perf_counter()-before
    equality = []
    for row in trained['checkpoints']:
        a, aa, am = read_transaction(source/row['file'])
        b, bb, bm = read_transaction(output/'train'/row['file'])
        equal = set(aa) == set(bb) and all(aa[k].dtype == bb[k].dtype and np.array_equal(aa[k], bb[k]) for k in aa)
        equality.append({'file': row['file'], 'exact': a == b and equal and am['state_identity'] == bm['state_identity']})
    stages_equal = metric['stages'] == read_json(Path(request['source_metrics']))['stages']
    if not all(c['exact'] for c in equality) or trained['ledger'] != prior['ledger'] or not stages_equal:
        write_json(output/'failure.json', {'status': 'profile_condition_changed_state_or_counts', 'checks': equality, 'evaluation_stages_exact': stages_equal})
        raise AssertionError('Profile is not equivalent work')
    peak_after_job = peak_working_set()
    last = trained['checkpoints'][-1]
    meta, arrays, _ = read_transaction(output/'train'/last['file'])
    model = ReferenceMLP(len(meta['slots']), settings.seed)
    model.load_state_dict({k[6:]: torch.from_numpy(v) for k, v in arrays.items() if k.startswith('model.')})
    model.eval()
    dev = ROOT/'data/processed/phase3-reference74-v1/development'
    x = np.load(dev/'x.npy', mmap_mode='r', allow_pickle=False)
    ids = np.load(dev/'ids.npy', mmap_mode='r', allow_pickle=False)
    latency = []
    with torch.no_grad():
        for batch in (1, 256):
            values = torch.from_numpy(x[:batch].copy())
            tick = time.perf_counter_ns()
            model(values)
            cold_call = (time.perf_counter_ns()-tick)/1e9
            for _ in range(20):
                model(values)
            calls = []
            for _ in range(100):
                tick = time.perf_counter_ns()
                model(values)
                calls.append((time.perf_counter_ns()-tick)/1e9)
            latency.append({'batch_size': batch, 'feature_ids_sha256': array_identity(ids[:batch]),
                            'first_shape_call_seconds': cold_call, 'warmups': 20, 'calls_seconds': calls,
                            'mean_seconds': statistics.mean(calls), 'median_seconds': statistics.median(calls),
                            'p95_seconds_linear': float(np.quantile(calls, .95, method='linear'))})
    before = time.perf_counter()
    communication_report = communication(output/'train')
    serialization_seconds = time.perf_counter()-before
    write_json(output/'communication.json', communication_report)
    before = time.perf_counter()
    bundle = output/'local-worker-output.zip'
    files = sorted(p for folder in ('train', 'evaluation') for p in (output/folder).rglob('*') if p.is_file())
    with zipfile.ZipFile(bundle, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            archive.write(path, path.relative_to(output).as_posix())
    sha = digest(bundle)
    export_seconds = time.perf_counter()-before
    write_json(output/'profile.json', {'status': 'passed_equivalent_CPU_worker_profile', 'code_identity': code_identity(),
               'settings': trained['settings'], 'source_run_sha256': digest(source/'run.json'), 'source_metrics_sha256': digest(Path(request['source_metrics'])),
               'cold_library_import_seconds': cold_import_seconds, 'run_seconds_including_input_validation': run_seconds,
               'training_loop_seconds': trained['elapsed_seconds'], 'component_timings': trained['timings'],
               'evaluation_seconds': evaluation_seconds, 'serialization_accounting_seconds': serialization_seconds,
               'local_bundle_export_hash_seconds': export_seconds, 'local_bundle_bytes': bundle.stat().st_size, 'local_bundle_sha256': sha,
               'checkpoint_and_run_file_bytes': sum(p.stat().st_size for p in (output/'train').rglob('*') if p.is_file()),
               'prediction_and_metrics_bytes': sum(p.stat().st_size for p in (output/'evaluation').rglob('*') if p.is_file()),
               'peak_after_training_and_evaluation': peak_after_job, 'peak_after_all_probes': peak_working_set(),
               'inference_latency': latency, 'exact_state_checks': equality, 'evaluation_stages_exact': stages_equal,
               'worker_seconds_excluding_interpreter_startup': time.perf_counter()-started,
               'additional_physical_training_executions': 1, 'additional_independent_replicates': 0,
               'unmeasured': ['Dependency installation', 'Fresh source reconstruction', 'Remote transfers/network transport', 'GPU runtime/workload'],
               'final_test_accessed': False, 'gpu_dispatchable': False})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    p.add_argument('--development', type=Path, default=root/'results/phase3-cpu-v3/development')
    p.add_argument('--selection', type=Path, default=root/'results/phase3-cpu-v3/cost-correction/selection.json')
    p.add_argument('--output', type=Path, default=root/'results/phase3-cpu-v3/profiling')
    p.add_argument('--worker-request', type=Path)
    args = p.parse_args()
    if args.worker_request is not None:
        worker(args.worker_request)
        return
    from src.phase3.common import digest, read_json, write_json

    completion, selection = read_json(args.development/'completion.json'), read_json(args.selection)
    if selection['status'] != 'complete':
        raise ValueError('Resolved source selection required')
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    capture = io.StringIO()
    tests = unittest.TextTestRunner(stream=capture, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('tests.test_phase3_profile'))
    write_json(args.output/'acceptance.json', {'status': 'passed' if tests.wasSuccessful() else 'failed', 'tests_run': tests.testsRun,
               'script_sha256': digest(Path(__file__)), 'test_source_sha256': digest(root/'tests/test_phase3_profile.py'),
               'plan_sha256': digest(root/'docs/phase3-cpu-v3/profile-plan.md'),
               'scope': 'FP32 serialization/rejection, logical message arithmetic and explicit OS memory availability',
               'unittest_output': capture.getvalue()})
    if not tests.wasSuccessful():
        raise AssertionError('Worker profile fixtures failed')
    jobs = []
    for learner in ('FT', 'EI', 'DR'):
        selected = selection['learners'][learner]['selected']
        members = [r for r in completion['rows'] if r['status'] == 'valid' and r['settings']['seed'] == 101 and r['settings']['learner'] == learner]
        source = next(r for r in members if r['row_id'] in selected['rows']) if selected else next(
            r for r in members if r['group'] == 'pilot' and [r['settings']['rounds'], r['settings']['epochs']] == completion['selected_budget'])
        output = args.output/learner
        output.mkdir()
        request = output/'request.json'
        write_json(request, {'settings': source['settings'], 'source_run': source['run'], 'source_metrics': source['metrics'],
                            'scope': 'selected_feasible_condition' if selected else 'fixed_unqualified_pilot_defaults',
                            'plan_sha256': digest(root/'docs/phase3-cpu-v3/profile-plan.md')})
        started = time.perf_counter()
        subprocess.run([sys.executable, '-m', 'scripts.profile_phase3_v3', '--worker-request', str(request)], cwd=root, check=True)
        profile = read_json(output/'profile.json')
        jobs.append({'learner': learner, 'process_end_to_end_seconds': time.perf_counter()-started,
                     'profile_sha256': digest(output/'profile.json'), 'scope': read_json(request)['scope'],
                     'status': profile['status'], 'source_row_id': source['row_id']})
    write_json(args.output/'jobs.json', {'status': 'passed', 'jobs': jobs, 'additional_physical_training_executions': 3,
               'additional_independent_replicates': 0, 'final_test_accessed': False, 'gpu_dispatchable': False})


if __name__ == '__main__':
    main()
