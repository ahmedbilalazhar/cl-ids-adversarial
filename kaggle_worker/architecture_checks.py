"""Contract and artifact fault tests; never trains or executes a model."""
from __future__ import annotations

import argparse
import copy
import json
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from .runtime import FROZEN_FILES, configure

import numpy as np

from src.phase3.common import digest, identity, save_state, state_identity, write_json
from src.phase3_v2 import learning
from src.phase3_v3.protocol import Settings

from .artifacts import HistoryValidator, references, validate_receipt
from .backends import CPUBackend, backend_for
from .contracts import SourceBindings, TimeBudget, make_procedure, parse_settings, validate_procedure
from .handoff import inspect
from .data import StageCache


def run():
    runtime = configure('cpu')
    bindings = SourceBindings.local()
    settings = Settings('FT', rounds=3, epochs=4)
    valid = make_procedure(settings, runtime, '0'*64, bindings)
    reports = []
    def rejected(name, action):
        try:
            action()
        except (ValueError, KeyError, TypeError):
            reports.append({'check': name, 'status': 'passed', 'invalid_fixture_rejected': True})
        else:
            raise AssertionError('Invalid architecture fixture accepted: '+name)
    assert validate_procedure(valid, bindings) == settings
    with patch('kaggle_worker.runtime.code_identity', return_value='1'*64):
        rejected('ingestion-rejects-changed-frozen-engine', SourceBindings.local)
    for name in FROZEN_FILES:
        def changed_binding(path, name=name):
            return '0'*64 if str(path).replace('\\', '/').endswith('/'+name) else digest(path)
        with patch('kaggle_worker.runtime.digest', side_effect=changed_binding):
            rejected('ingestion-rejects-changed-binding-'+name, SourceBindings.local)
    for field, value in [('seed', 101.), ('seed', True), ('seed', 1), ('seed', 42),
                         ('rounds', 3.), ('epochs', True), ('dose', [True, 2]), ('dose', [1, 0]),
                         ('learning_rate', True), ('lambda_E', float('nan'))]:
        data = asdict(settings)
        data[field] = value
        rejected(f'settings-{field}-{value}', lambda data=data: parse_settings(data))
    for field, value in [('study_revision', 'final'), ('protocol_sha256', '1'*64),
                         ('decisions_sha256', '1'*64), ('taxonomy_sha256', '1'*64),
                         ('worker_source_identity', '1'*64), ('settings_identity', '1'*64),
                         ('runtime_identity', '1'*64), ('train_manifest_sha256', '../features'),
                         ('final_dispatchable', True), ('final_dispatchable', 0)]:
        data = copy.deepcopy(valid)
        data['execution'][field] = value
        rejected('execution-'+field, lambda data=data: validate_procedure(data, bindings))
    for field, value in [('amp', True), ('tf32', True), ('dtype', 'float16'), ('threads', True),
                         ('threads', 8), ('deterministic_algorithms', 1), ('device_type', 'cuda'),
                         ('worker_source_identity', '1'*64), ('python', '3.11.0')]:
        data = copy.deepcopy(valid)
        data['runtime'][field] = value
        data['execution']['runtime_identity'] = identity(data['runtime'])
        rejected('runtime-'+field, lambda data=data: validate_procedure(data, bindings))
    data = copy.deepcopy(valid)
    data['runtime']['packages']['torch'] = 'another-build'
    data['execution']['runtime_identity'] = identity(data['runtime'])
    rejected('runtime-installed-package-mismatch', lambda: validate_procedure(data, bindings))
    for extra in ('job', 'execution', 'runtime', 'settings'):
        data = copy.deepcopy(valid)
        target = data if extra == 'job' else data[extra]
        target['unknown_field'] = True
        rejected('unknown-field-'+extra, lambda data=data: validate_procedure(data, bindings))
    budget = TimeBudget(1000, 100, 200)
    assert budget.permits(700, 200) and not budget.permits(700.001, 200)
    for args in ((True, 1, 1), (100, 100, 10), (float('inf'), 1, 1), (1000, -1, 100)):
        rejected('invalid-budget-'+str(args), lambda args=args: TimeBudget(*args))
    rejected('unsupported-device-port', lambda: backend_for('mps'))
    assert CPUBackend.admit is learning.admit and CPUBackend.train_client is learning.train_client
    assert CPUBackend.importance is learning.commit_importance
    reports.append({'check': 'CPU-port-delegates-to-frozen-numerical-functions', 'status': 'passed'})
    calls = []
    cache = StageCache(lambda stage: None, lambda: calls.append('verified'))
    cache.verify_integrity()
    assert calls == ['verified']
    reports.append({'check': 'data-adapter-owns-publication-integrity-capability', 'status': 'passed'})
    def fail_integrity():
        raise ValueError('synthetic changed input')
    rejected('changed-input-publication-capability', StageCache(lambda stage: None, fail_integrity).verify_integrity)
    for names in (['segment-0001/E1-R2.commit.json'], ['segment-0001/E1-R1.commit.json', 'segment-0002/E1-R1.commit.json'],
                  ['segment-0001/E1-R4.commit.json'], ['segment-0001/../../E1-R1.commit.json']):
        rejected('invalid-collection-'+str(names), lambda names=names: references(names, 3))
    with tempfile.TemporaryDirectory(prefix='phase3-contracts-no-model-') as temporary:
        folder = Path(temporary)
        meta = {'schema': 'phase3-round-v2', 'execution': valid['execution'], 'slots': [0],
                'stage': 1, 'round': 2, 'admission_stage': 1, 'commits': 1,
                'ledger': [{'kind': 'admission'}, {'kind': 'round'}]}
        files, rows = {}, []
        for row_id in (1, 2):
            value = copy.deepcopy(meta)
            value['commits'], value['round'] = row_id, row_id+1
            value['ledger'] += [{'kind': 'round'}]*(row_id-1)
            name = f'segment-0001/E1-R{row_id}.npz'
            # Intentionally minimal synthetic typed state for hash/lineage tests.
            # No learner, feature bank, optimizer or inference is executed.
            arrays = {'synthetic.state': np.asarray([row_id], dtype=np.int64)}
            path = folder/name
            save_state(path, value, arrays)
            marker = {'schema': 'phase3-commit-v2', 'stage': 1, 'round': row_id, 'stage_end': False,
                      'file': path.name, 'file_sha256': digest(path), 'state_identity': state_identity(value, arrays),
                      'head_width': 1, 'source_codes_in_slot_order': [0]}
            write_json(path.with_suffix('.commit.json'), marker)
            files[name] = digest(path)
            files[name[:-4]+'.commit.json'] = digest(path.with_suffix('.commit.json'))
            rows.append({'path': name, **marker})
        first_files = {key: value for key, value in files.items() if 'R1.' in key}
        receipt = {'schema': 'kaggle-worker-receipt-v1', 'status': 'stopped_at_committed_boundary',
                   'execution': valid['execution'], 'commits_verified': 1, 'trajectory_count': 1,
                   'segment_count_is_not_replicate_count': True, 'runtime_identity': identity(runtime),
                   'whole_invocation_seconds': 1., 'stage_cache_loads': 1, 'whole_invocation_excludes_imports': True,
                   'resources': {}, 'recovered_completion_receipt': False,
                   'checkpoints': [rows[0]], 'files': first_files, 'final_test_accessed': False, 'final_dispatchable': False}
        recorded = validate_receipt(receipt, valid['execution'], 3)
        history = HistoryValidator(3, 'FT')
        history.accept(meta, {k: v for k, v in rows[0].items() if k != 'path'}, recorded[0])
        bad_meta = {**meta, 'round': 2.}
        rejected('typed-cursor-float', lambda: HistoryValidator(3).accept(bad_meta,
                 {k: v for k, v in rows[0].items() if k != 'path'}, recorded[0]))
        for field, value in [('trajectory_count', 2), ('commits_verified', True), ('final_dispatchable', 0),
                             ('status', 'complete'), ('whole_invocation_seconds', float('nan'))]:
            data = copy.deepcopy(receipt)
            data[field] = value
            rejected('receipt-'+field, lambda data=data: validate_receipt(data, valid['execution'], 3))
        data = copy.deepcopy(receipt)
        data['files'].pop(recorded[0].marker)
        rejected('receipt-marker-not-hash-bound', lambda: validate_receipt(data, valid['execution'], 3))
        evidence = {'status': 'passed', 'runtime': runtime, 'final_dispatchable': False,
                    'actual_CUDA_fixtures_passed': False, 'checks': [{'status': 'passed', 'check': 'synthetic-only'}]}
        path = folder/'handoff.zip'
        with zipfile.ZipFile(path, 'x') as archive:
            archive.writestr('synthetic-acceptance.json', json.dumps(evidence))
            archive.writestr('FT/job.json', json.dumps(valid))
            archive.writestr('FT/invocation-0001.json', json.dumps(receipt))
            for name in files:
                archive.write(folder/name, 'FT/'+name)
        returned = inspect(path, digest(path))
        actual_job = returned['jobs'][0]
        assert actual_job['status'] == 'unreceipted_commits_retained'
        assert actual_job['commits_verified'] == 1 and len(actual_job['unverified_commit_markers']) == 1
        reports.append({'check': 'unreceipted-checkpoints-visible-without-claiming-verification', 'status': 'passed'})
    return {'status': 'passed', 'schema': 'kaggle-architecture-v3', 'runtime': runtime, 'checks': reports,
            'model_executions': 0, 'scope': 'Strict contracts, lineage and artifact boundaries; no numerical training/inference',
            'final_test_accessed': False, 'final_dispatchable': False}


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
    print({'status': result['status'], 'checks': len(result['checks']), 'model_executions': 0})


if __name__ == '__main__':
    main()
