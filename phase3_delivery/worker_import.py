"""Verify a downloaded worker export before transactional count ingestion."""
import argparse
import hashlib
import io
import tempfile
import zipfile
from pathlib import Path

import numpy as np

from kaggle_worker.artifacts import references, valid_name
from kaggle_worker.contracts import SourceBindings, validate_procedure, validate_runtime
from kaggle_worker.handoff import inspect
from scripts.audit_phase3_endpoints import require
from src.phase3.common import array_identity, canonical, identity
from src.phase3.common import ROOT, read_json
from src.phase3_v2.checkpoint import strict_json
from src.phase3_v2.data import BASE_DEV

from .archive_policy import check_archive_npz
from .catalog import bound_manifest, connect, create_output, ingest
from .io import MAX_JSON_BYTES, copy_verified_archive
from .import_counts import import_counts


def archive_json(archive, name):
    require(archive.getinfo(name).file_size <= MAX_JSON_BYTES, 'Archived JSON exceeds the byte limit')
    return strict_json(archive.read(name).decode('utf-8'))


def validate_evaluation_binding(archive, job_prefix, metrics_path, row):
    require(valid_name(job_prefix) and valid_name(metrics_path) and metrics_path.endswith('/metrics.json'),
            'Unsafe job or evaluation mapping')
    prefix = job_prefix+'/'
    procedure = archive_json(archive, prefix+'job.json')
    settings = validate_procedure(procedure)
    require(canonical(procedure['settings']) == canonical(row['settings']) and
            canonical(procedure['execution']) == canonical(row['execution']), 'Export job differs from import registry')
    require(archive.getinfo(metrics_path).file_size <= MAX_JSON_BYTES, 'Metric JSON exceeds byte limit')
    payload = archive.read(metrics_path)
    require(hashlib.sha256(payload).hexdigest() == row['metric_sha256'], 'Export metric payload differs from registry')
    metrics = archive_json(archive, metrics_path)
    metric_prefix = metrics_path[:-len('metrics.json')]
    commit = archive_json(archive, metric_prefix+'evaluation.commit.json')
    expected = {'metrics.json'} | {f'E{stage}-predictions.npz' for stage in range(1, 5)}
    require(set(commit) == {'schema', 'job_manifest_sha256', 'development_manifest_sha256',
                           'evaluation_runtime_identity', 'files'} and
            commit['schema'] == 'kaggle-evaluation-commit-v1' and set(commit['files']) == expected,
            'Missing or incompatible committed evaluation')
    require(commit['job_manifest_sha256'] == hashlib.sha256(archive.read(prefix+'job.json')).hexdigest() and
            commit['development_manifest_sha256'] == BASE_DEV and
            metrics['development_manifest_sha256'] == BASE_DEV, 'Evaluation input/job identity differs')
    validate_runtime(metrics['evaluation_runtime'], SourceBindings.local())
    require(metrics['evaluation_runtime']['device_type'] == 'cpu' and
            commit['evaluation_runtime_identity'] == identity(metrics['evaluation_runtime']),
            'Evaluation runtime differs from the common CPU policy')
    for name, sha in commit['files'].items():
        require(hashlib.sha256(archive.read(metric_prefix+name)).hexdigest() == sha, 'Committed evaluation payload changed')
    refs = references([name[len(prefix):] for name in archive.namelist() if name.startswith(prefix)],
                      settings.rounds, complete=True)
    models, slots_by_stage = {}, {}
    for ref in refs:
        if ref.round != settings.rounds:
            continue
        with np.load(io.BytesIO(archive.read(prefix+ref.payload)), allow_pickle=False) as checkpoint:
            metadata = strict_json(str(checkpoint['metadata']))
            slots = metadata['slots']
            expected_shapes = {'backbone.0.weight': (128, 74), 'backbone.0.bias': (128,),
                               'backbone.3.weight': (64, 128), 'backbone.3.bias': (64,),
                               'classifier.weight': (len(slots), 64), 'classifier.bias': (len(slots),)}
            tensors = {name[6:]: checkpoint[name] for name in checkpoint.files if name.startswith('model.')}
            require(set(tensors) == set(expected_shapes) and
                    all(value.shape == expected_shapes[name] and value.dtype == np.dtype('<f4') and
                        np.isfinite(value).all() for name, value in tensors.items()),
                    'Committed model tensor schema differs from the frozen architecture')
            weights = {name: array_identity(value) for name, value in tensors.items()}
            slots_by_stage[ref.stage] = slots
            models[ref.stage] = identity({'slots': metadata['slots'], 'weights': weights})
    require([stage['stage'] for stage in metrics['stages']] == [1, 2, 3, 4] and
            all(stage['model_sha256'] == models[stage['stage']] and
                canonical(stage['source_codes_in_slot_order']) == canonical(slots_by_stage[stage['stage']]) and
                type(stage['head_width']) is int and stage['head_width'] == len(slots_by_stage[stage['stage']])
                for stage in metrics['stages']),
            'Reported metrics refer to a different stage model')
    return payload


def prepare_mapping(manifest, rows, existing, mapping):
    """Validate all map entries, then place physical parents before their aliases."""
    require(type(mapping) is list and bool(mapping), 'Explicit export-to-registry mapping required')
    require(manifest['kind'] == 'development', 'Worker import accepts development exports only')
    copied, ids = [], set()
    for item in mapping:
        require(type(item) is dict and set(item) == {'run_id', 'job_prefix', 'metrics_path'},
                'Unexpected import mapping fields')
        run_id = item['run_id']
        require(type(run_id) is str and run_id and run_id not in ids, 'Invalid or duplicate mapped run ID')
        require(valid_name(item['job_prefix']) and valid_name(item['metrics_path']) and
                item['metrics_path'].endswith('/metrics.json'), 'Unsafe job or evaluation mapping')
        parent = manifest['aliases'].get(run_id, run_id)
        require(parent in rows and rows[parent]['execution']['study_revision'] == 'kaggle-qualification-v5',
                'Only a registered v5 development job may use this import path')
        copied.append(dict(item))
        ids.add(run_id)
    require(all(manifest['aliases'][run_id] in ids | existing for run_id in ids if run_id in manifest['aliases']),
            'Mapped alias needs its physical parent in the batch or catalog')
    return sorted(copied, key=lambda item: item['run_id'] in manifest['aliases'])


def ingest_export(database, manifest_sha256, archive_path, archive_sha256, mapping):
    with connect(database) as connection:
        manifest, rows = bound_manifest(connection, manifest_sha256)
        existing = {row[0] for row in connection.execute('SELECT run_id FROM observations')}
    mapping = prepare_mapping(manifest, rows, existing, mapping)
    with tempfile.TemporaryDirectory(prefix='verified-worker-export-') as directory:
        root = Path(directory)
        snapshot = root/'worker-output.zip'
        copied = copy_verified_archive(archive_path, snapshot, archive_sha256)
        envelope = check_archive_npz(snapshot)
        handoff = inspect(snapshot, archive_sha256)
        jobs = {job['job']: job for job in handoff['jobs']}
        planned, seen_ids, seen_conditions = [], set(), set()
        with zipfile.ZipFile(snapshot) as archive:
            for index, item in enumerate(mapping):
                job = jobs.get(item['job_prefix']+'/')
                require(job is not None and job['status'] == 'complete', 'Job is incomplete, unreceipted or has extra commits')
                parent = manifest['aliases'].get(item['run_id'], item['run_id'])
                payload = validate_evaluation_binding(archive, item['job_prefix'], item['metrics_path'], rows[parent])
                metrics = root/f'metrics-{index:04d}.json'
                metrics.write_bytes(payload)
                if parent not in seen_ids:
                    import_counts(metrics, rows[parent]['metric_sha256'], rows[parent]['settings'],
                                  rows[parent]['execution'], read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes'],
                                  kind='development', run_id=parent, seen_ids=seen_ids, seen_conditions=seen_conditions)
                planned.append((item['run_id'], metrics))
        # Every mapped job/evaluation is checked before the first database write.
        # Each observation is independently transactional; retries are idempotent.
        accepted = []
        try:
            for run_id, metric in planned:
                accepted.append({'run_id': run_id, **ingest(database, manifest_sha256, run_id, metric)})
        except Exception as exc:
            raise RuntimeError('Batch stopped after verified rows '+str([r['run_id'] for r in accepted])) from exc
        return {'schema': 'phase3-verified-worker-import-v1', 'status': 'passed',
                'archive_sha256': archive_sha256, 'snapshot_bytes': copied, 'envelope': envelope,
                'manifest_sha256': manifest_sha256, 'rows': accepted, 'handoff': handoff,
                'independent_trajectories_added': sum(r['independent_trajectories_added'] for r in accepted),
                'final_test_accessed': False, 'final_dispatchable': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--archive-sha256', required=True)
    parser.add_argument('--mapping', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    try:
        with args.mapping.open('rb') as stream:
            payload = stream.read(MAX_JSON_BYTES+1)
        require(len(payload) <= MAX_JSON_BYTES, 'Import mapping exceeds the JSON byte limit')
        mapping = strict_json(payload.decode('utf-8'))
        result = ingest_export(args.database, args.manifest_sha256, args.archive, args.archive_sha256, mapping)
    except Exception as exc:
        create_output(args.output, {'status': 'failed_attempt_retained', 'exception': type(exc).__name__,
                                   'message': str(exc), 'final_dispatchable': False})
        raise
    create_output(args.output, result)
    print({'status': result['status'], 'independent_trajectories_added': result['independent_trajectories_added']})


if __name__ == '__main__':
    main()
