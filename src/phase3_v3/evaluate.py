"""Independent v3 development evaluator using unchanged count/bank arithmetic."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import torch

from src.phase3.common import ROOT, array_identity, digest, identity, read_json, write_json
from src.phase3.evaluate import ratio
from src.phase3.model import ReferenceMLP
from src.phase3.reference import model_identity
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.data import BASE_DEV, verify_files
from src.phase3_v2.evaluate import stage_counts
from src.phase3_v2.protocol import code_identity as parent_identity

from .protocol import PROTOCOL, code_identity, configure_runtime


def evaluate(development_package: Path, run_dir: Path, output: Path):
    runtime = configure_runtime()
    run = read_json(run_dir / 'run.json')
    if output.exists():
        raise FileExistsError(output)
    if run['schema'] != 'phase3-run-v2' or run['status'] != 'complete' or run['resumed_from'] is not None:
        raise ValueError('A complete from-start trajectory is required; a suffix is not an independent run')
    execution = run['execution']
    if execution.get('study_revision') != 'cpu-v3' or execution.get('parent_code_identity') != parent_identity():
        raise ValueError('Not a compatible v3 study execution')
    if execution['code_identity'] != code_identity() or execution['protocol_sha256'] != digest(PROTOCOL) or execution['runtime_identity'] != identity(runtime):
        raise ValueError('Incompatible model code/protocol/runtime')
    if execution['taxonomy_sha256'] != digest(ROOT/'configs/phase3/taxonomy-v1.json') or execution['decisions_sha256'] != digest(ROOT/'docs/phase3-cpu-v3/decisions-2026-10-24.md'):
        raise ValueError('Taxonomy/decision identity differs')
    if digest(development_package / 'manifest.json') != BASE_DEV:
        raise ValueError('Only the pinned development bank is accepted; final-test inference is sealed')
    manifest = read_json(development_package / 'manifest.json')
    verify_files(development_package, manifest['files'], {f'{k}.npy' for k in ('x', 'y', 'ids', 'cohort', 'attempted')})
    if manifest['role'] != 'development_only':
        raise ValueError('Not a development bank')
    data = {k: np.load(development_package / f'{k}.npy', allow_pickle=False, mmap_mode='r') for k in ('x', 'y', 'ids', 'cohort', 'attempted')}
    rounds = run['settings']['rounds']
    expected = [(s, r) for s in range(1, 5) for r in range(1, rounds+1)]
    if [(row['stage'], row['round']) for row in run['checkpoints']] != expected or run['total_commits'] != 4*rounds or run['next_cursor'] != [5, 1]:
        raise ValueError('Incomplete checkpoint inventory')
    output.mkdir(parents=True)
    started = time.perf_counter()
    stages, trajectory = [], [[None]*4 for _ in range(4)]
    for row in run['checkpoints']:
        meta, arrays, commit = read_transaction(run_dir / row['file'], execution)
        if row != commit:
            raise ValueError('Run and transaction markers differ')
        if not row['stage_end']:
            continue
        stage, slots = row['stage'], meta['slots']
        if meta['stage'] != stage+1 or meta['round'] != 1:
            raise ValueError('Not a completed-stage transition')
        model = ReferenceMLP(len(slots), run['settings']['seed'])
        model.load_state_dict({k[6:]: torch.from_numpy(v) for k, v in arrays.items() if k.startswith('model.')}, strict=True)
        model.eval()
        # Bank membership uses frozen arrivals, never admission or corrupted labels.
        indexes = np.flatnonzero(np.asarray(manifest['arrival'])[data['y']] <= stage)
        predicted_slots = np.empty(len(indexes), dtype=np.uint8)
        with torch.no_grad():
            for start in range(0, len(indexes), 2048):
                logits = model(torch.from_numpy(data['x'][indexes[start:start+2048]].copy()))
                if not torch.isfinite(logits).all():
                    raise FloatingPointError('Nonfinite evaluation logits')
                predicted_slots[start:start+2048] = logits.argmax(dim=1).numpy().astype(np.uint8)
        predicted = np.asarray(slots)[predicted_slots]
        y = data['y'][indexes]
        row_counts = stage_counts(stage, slots, y, predicted, manifest['eligible_codes'], manifest['families'],
                                  manifest['arrival'], data['cohort'][indexes], data['attempted'][indexes])
        row_counts.update({'model_sha256': model_identity(model, slots), 'bank_ids_sha256': array_identity(data['ids'][indexes])})
        np.savez(output / f'E{stage}-predictions.npz', ids=data['ids'][indexes], predicted_slots=predicted_slots,
                 source_codes_in_slot_order=np.asarray(slots, dtype=np.int16))
        for cell in row_counts['cohort_counts']:
            trajectory[stage-1][cell['cohort']-1] = ratio(cell['correct'], cell['total'])
        stages.append(row_counts)
    if len(stages) != 4 or any(v is None for v in trajectory[3]):
        raise ValueError('Incomplete stage/cohort evaluation')
    final = trajectory[3]
    result = {'schema': 'phase3-development-metrics-v3', 'status': 'valid_development_only',
              'run_manifest_sha256': digest(run_dir / 'run.json'), 'development_manifest_sha256': BASE_DEV,
              'settings': run['settings'], 'stages': stages, 'R_accuracy_by_stage_and_arrival_cohort': trajectory,
              'equal_stage_ACC4': float(np.mean(final)),
              'BWT4': float(np.mean([final[j]-trajectory[j][j] for j in range(3)])),
              'forgetting4': float(np.mean([max(trajectory[t][j] for t in range(j, 4))-final[j] for j in range(3)])),
              'A': float(np.mean([r['untargeted_new_annotated_class_f1'] for r in stages[1:]])),
              'final_test_accessed': False, 'evaluation_seconds': time.perf_counter()-started,
              'limitations': ['Development-only benchmark; no final inference or comparative publication claim.',
                             'Fixed cross-period benign mixture; all registered rare outputs remain active.',
                             'Scenario annotation acquisition does not establish zero-day/technique novelty.']}
    write_json(output / 'metrics.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--development-package', type=Path, default=ROOT / 'data/processed/phase3-reference74-v1/development')
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.development_package, args.run, args.output)
    print({'macro_f1': [s['eligible_macro_f1'] for s in result['stages']], 'A': result['A']})


if __name__ == '__main__':
    main()
