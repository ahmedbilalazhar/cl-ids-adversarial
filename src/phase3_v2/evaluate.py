"""Independent development evaluator; only the immutable development bank is accepted."""
from __future__ import annotations

import argparse
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
import torch

from src.phase3.common import ROOT, array_identity, digest, identity, read_json, write_json
from src.phase3.evaluate import counts_for, ratio
from src.phase3.model import ReferenceMLP
from src.phase3.reference import model_identity

from .checkpoint import read_transaction
from .data import BASE_DEV, verify_files
from .protocol import PROTOCOL, code_identity, configure_runtime


def rational_macro(classes):
    if any(row['support'] == 0 for row in classes) or not classes:
        raise ValueError('Fixed eligible class lacks support')
    return sum((Fraction(2*r['tp'], 2*r['tp']+r['fp']+r['fn']) for r in classes), Fraction()) / len(classes)


def stage_counts(stage, slots, y, predicted, eligible, names, arrival, cohorts, attempted):
    if not slots or slots[0] != 0 or len(set(slots)) != len(slots) or not np.isin(predicted, slots).all() or not np.isin(y, slots).all():
        raise ValueError('Invalid registered prediction space')
    full_matrix, full_classes = counts_for(y, predicted, slots, names)
    seen = [c for c in eligible if arrival[c] <= stage]
    mask = np.isin(y, seen)
    matrix, classes = counts_for(y[mask], predicted[mask], seen, names)
    macro = rational_macro(classes)
    benign, alert = y == 0, predicted != 0
    tp, fp = int((~benign & alert).sum()), int((benign & alert).sum())
    fn, tn = int((~benign & ~alert).sum()), int((benign & ~alert).sum())
    hulk = y == 4
    source = {'support': int(hulk.sum()), 'predicted_benign': int((hulk & ~alert).sum()),
              'predicted_hulk': int((hulk & (predicted == 4)).sum()),
              'predicted_other_attack': int((hulk & alert & (predicted != 4)).sum())}
    acquisition = [r for r in classes if r['code'] not in (0, 4) and arrival[r['code']] == stage]
    a = None if stage == 1 else rational_macro(acquisition)
    cohort_counts = []
    for j in range(1, stage + 1):
        cohort = mask & (cohorts == j)
        cohort_counts.append({'cohort': j, 'correct': int((predicted[cohort] == y[cohort]).sum()), 'total': int(cohort.sum())})
    provenance = []
    for flag, name in ((False, 'original_background'), (True, 'remapped_attempted')):
        subgroup = benign & (attempted == flag)
        provenance.append({'group': name, 'benign_rows': int(subgroup.sum()), 'alerts': int((subgroup & alert).sum()),
                           'error_rate': ratio(int((subgroup & alert).sum()), int(subgroup.sum()))})
    return {'stage': stage, 'head_width': len(slots), 'source_codes_in_slot_order': slots,
            'full_seen_bank_rows': len(y), 'full_seen_confusion_source_code_order': full_matrix,
            'full_seen_classes': full_classes, 'eligible_seen_bank_rows': int(mask.sum()),
            'eligible_codes': seen, 'eligible_confusion_source_code_order': matrix, 'eligible_classes': classes,
            'eligible_macro_f1': float(macro), 'eligible_macro_f1_exact': [str(macro.numerator), str(macro.denominator)],
            'eligible_pooled_accuracy': ratio(int((predicted[mask] == y[mask]).sum()), int(mask.sum())),
            'untargeted_new_annotated_class_f1': None if a is None else float(a),
            'binary_full_seen': {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'attack_precision': ratio(tp, tp+fp),
                                 'attack_recall': ratio(tp, tp+fn), 'f1': ratio(2*tp, 2*tp+fp+fn),
                                 'benign_far': ratio(fp, fp+tn), 'attack_miss_rate': ratio(fn, tp+fn)},
            'benign_provenance_descriptive': provenance, 'hulk_partition': source, 'cohort_counts': cohort_counts}


def evaluate(development_package: Path, run_dir: Path, output: Path):
    runtime = configure_runtime()
    run = read_json(run_dir / 'run.json')
    if output.exists():
        raise FileExistsError(output)
    if run['schema'] != 'phase3-run-v2' or run['status'] != 'complete' or run['resumed_from'] is not None:
        raise ValueError('A complete from-start trajectory is required; a suffix is not an independent run')
    execution = run['execution']
    if execution['code_identity'] != code_identity() or execution['protocol_sha256'] != digest(PROTOCOL) or execution['runtime_identity'] != identity(runtime):
        raise ValueError('Incompatible model code/protocol/runtime')
    if execution['taxonomy_sha256'] != digest(ROOT/'configs/phase3/taxonomy-v1.json') or execution['decisions_sha256'] != digest(ROOT/'docs/phase3-cpu-v2/decisions-2026-10-24.md'):
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
    result = {'schema': 'phase3-development-metrics-v2', 'status': 'valid_development_only',
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
