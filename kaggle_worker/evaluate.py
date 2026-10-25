"""Separate development-only evaluator for complete notebook qualification jobs."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from .runtime import configure

import numpy as np
import torch

from src.phase3.common import array_identity, digest, read_json, write_json
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


def evaluate(job, development, output):
    started = time.perf_counter()
    runtime = configure('cpu')  # One declared evaluation device for every arm.
    if output.exists():
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
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', type=Path, required=True)
    parser.add_argument('--development-package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.job, args.development_package, args.output)
    print({'status': result['status'], 'evaluation_seconds': result['evaluation_seconds']})


if __name__ == '__main__':
    main()
