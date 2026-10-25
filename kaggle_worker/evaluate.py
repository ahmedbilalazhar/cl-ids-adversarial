"""Separate development-only evaluator for complete notebook qualification jobs."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from .runtime import configure, safe_output

import numpy as np
import torch

from src.phase3.common import array_identity, canonical, digest, identity, read_json, write_json
from src.phase3.evaluate import ratio
from src.phase3.model import ReferenceMLP
from src.phase3.reference import model_identity
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.data import BASE_DEV, verify_files
from src.phase3_v2.evaluate import stage_counts
from .contracts import validate_procedure
from .artifacts import HistoryValidator, discover


def stage_snapshots(job, execution, rounds, learner=None):
    """Verify all transactions while retaining only four small model snapshots."""
    snapshots, history = {}, HistoryValidator(rounds, learner)
    for ref in discover(job, rounds, complete=True):
        meta, arrays, marker = read_transaction(job/ref.payload, execution)
        history.accept(meta, marker, ref)
        stage, row = ref.stage, ref.round
        stage_end = row == rounds
        if stage_end:
            model_state = {key[6:]: value for key, value in arrays.items() if key.startswith('model.')}
            if any(value.dtype != np.dtype('<f4') or not np.isfinite(value).all() for value in model_state.values()):
                raise ValueError('Expected finite FP32 model tensors')
            snapshots[stage] = {'slots': meta['slots'], 'model': model_state}
        # Replay buffers and optimizer/importance state are verified then released.
        del arrays
    return snapshots


def verify_completed(job, development, output, runtime):
    marker = read_json(output/'evaluation.commit.json')
    expected = {'metrics.json'} | {f'E{stage}-predictions.npz' for stage in range(1, 5)}
    if (set(marker) != {'schema', 'job_manifest_sha256', 'development_manifest_sha256',
                       'evaluation_runtime_identity', 'files'} or
            marker['schema'] != 'kaggle-evaluation-commit-v1' or
            marker['job_manifest_sha256'] != digest(job/'job.json') or
            marker['development_manifest_sha256'] != BASE_DEV or
            digest(development/'manifest.json') != BASE_DEV or
            marker['evaluation_runtime_identity'] != identity(runtime) or
            set(marker['files']) != expected):
        raise ValueError('Evaluation commit identity differs')
    paths = {path.relative_to(output).as_posix(): path for path in output.rglob('*') if path.is_file()}
    if (set(paths) != expected | {'evaluation.commit.json'} or
            any(path.is_symlink() or not path.resolve().is_relative_to(output.resolve()) for path in paths.values()) or
            any(digest(output/name) != sha for name, sha in marker['files'].items())):
        raise ValueError('Evaluation artifact inventory or hashes differ')
    procedure, metrics = read_json(job/'job.json'), read_json(output/'metrics.json')
    settings = validate_procedure(procedure)
    if (metrics['schema'] != 'kaggle-qualification-development-metrics-v1' or
            metrics['status'] != 'valid_development_only' or metrics['final_test_accessed'] is not False or
            metrics['final_dispatchable'] is not False or
            canonical(metrics['execution']) != canonical(procedure['execution']) or
            canonical(metrics['settings']) != canonical(procedure['settings']) or
            canonical(metrics['evaluation_runtime']) != canonical(runtime) or
            [stage['stage'] for stage in metrics['stages']] != [1, 2, 3, 4]):
        raise ValueError('Evaluation metadata differs')
    snapshots = stage_snapshots(job, procedure['execution'], settings.rounds, settings.learner)
    for stage in metrics['stages']:
        state = snapshots[stage['stage']]
        model_hash = identity({'slots': state['slots'],
                               'weights': {key: array_identity(value) for key, value in state['model'].items()}})
        if stage['model_sha256'] != model_hash or stage['source_codes_in_slot_order'] != state['slots']:
            raise ValueError('Evaluation model differs from committed stage state')
    return {'status': 'existing_evaluation_verified', 'new_inference': False, 'metrics_sha256': digest(output/'metrics.json')}


def evaluate(job, development, output, verify_existing=False):
    started = time.perf_counter()
    runtime = configure('cpu')  # One declared evaluation device for every arm.
    output = safe_output(output)
    if output.exists():
        if verify_existing:
            return verify_completed(job, development, output, runtime)
        raise FileExistsError(output)
    procedure = read_json(job/'job.json')
    execution = procedure['execution']
    settings = validate_procedure(procedure)
    if digest(development/'manifest.json') != BASE_DEV:
        raise ValueError('Only the immutable development bank is accepted; final inference is sealed')
    manifest = read_json(development/'manifest.json')
    if manifest['role'] != 'development_only':
        raise ValueError('Not a development bank')
    verify_files(development, manifest['files'], {f'{k}.npy' for k in ('x', 'y', 'ids', 'cohort', 'attempted')})
    snapshots = stage_snapshots(job, execution, settings.rounds, settings.learner)
    data = {k: np.load(development/f'{k}.npy', allow_pickle=False, mmap_mode='r') for k in ('x', 'y', 'ids', 'cohort', 'attempted')}
    output.mkdir(parents=True)
    stages, trajectory = [], [[None]*4 for _ in range(4)]
    for stage in range(1, 5):
        slots = snapshots[stage]['slots']
        model = ReferenceMLP(len(slots), settings.seed).eval()
        model.load_state_dict({key: torch.from_numpy(value) for key, value in snapshots[stage]['model'].items()}, strict=True)
        indexes = np.flatnonzero(np.asarray(manifest['arrival'])[data['y']] <= stage)
        predicted_slots = np.empty(len(indexes), dtype=np.uint8)
        with torch.no_grad():
            for start in range(0, len(indexes), 2048):
                logits = model(torch.from_numpy(data['x'][indexes[start:start+2048]].copy()))
                if not torch.isfinite(logits).all():
                    raise FloatingPointError('Nonfinite development logits')
                predicted_slots[start:start+2048] = logits.argmax(dim=1).numpy().astype(np.uint8)
        predicted = np.asarray(slots)[predicted_slots]
        counts = stage_counts(stage, slots, data['y'][indexes], predicted, manifest['eligible_codes'],
                              manifest['families'], manifest['arrival'], data['cohort'][indexes], data['attempted'][indexes])
        counts.update({'model_sha256': model_identity(model, slots), 'bank_ids_sha256': array_identity(data['ids'][indexes])})
        stages.append(counts)
        for cell in counts['cohort_counts']:
            trajectory[stage-1][cell['cohort']-1] = ratio(cell['correct'], cell['total'])
        np.savez(output/f'E{stage}-predictions.npz', ids=data['ids'][indexes], predicted_slots=predicted_slots,
                 source_codes_in_slot_order=np.asarray(slots, dtype=np.int16))
    final = trajectory[3]
    result = {'schema': 'kaggle-qualification-development-metrics-v1', 'status': 'valid_development_only',
              'execution': execution, 'evaluation_runtime': runtime, 'settings': procedure['settings'],
              'stages': stages, 'R_accuracy_by_stage_and_arrival_cohort': trajectory,
              'equal_stage_ACC4': float(np.mean(final)),
              'BWT4': float(np.mean([final[j]-trajectory[j][j] for j in range(3)])),
              'forgetting4': float(np.mean([max(trajectory[t][j] for t in range(j, 4))-final[j] for j in range(3)])),
              'A': float(np.mean([r['untargeted_new_annotated_class_f1'] for r in stages[1:]])),
              'development_manifest_sha256': BASE_DEV, 'evaluation_seconds': time.perf_counter()-started,
              'final_test_accessed': False, 'final_dispatchable': False}
    write_json(output/'metrics.json', result)
    files = {'metrics.json'} | {f'E{stage}-predictions.npz' for stage in range(1, 5)}
    write_json(output/'evaluation.commit.json', {'schema': 'kaggle-evaluation-commit-v1',
               'job_manifest_sha256': digest(job/'job.json'), 'development_manifest_sha256': BASE_DEV,
               'evaluation_runtime_identity': identity(runtime),
               'files': {name: digest(output/name) for name in sorted(files)}})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', type=Path, required=True)
    parser.add_argument('--development-package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verify-existing', action='store_true')
    args = parser.parse_args()
    result = evaluate(args.job, args.development_package, args.output, args.verify_existing)
    print({key: result[key] for key in ('status', 'evaluation_seconds', 'new_inference') if key in result})


if __name__ == '__main__':
    main()
