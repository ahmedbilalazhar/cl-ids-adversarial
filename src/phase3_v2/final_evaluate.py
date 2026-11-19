"""One-shot final-role evaluator, deliberately separate from development scoring.

This module refuses all inputs until a separately frozen final-test release
manifest is supplied. It contains no training, tuning, or model-selection API.
The manifest contract is intentionally stricter than the development evaluator.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch

from src.phase3.common import digest, read_json, write_json, array_identity, identity
from src.phase3.evaluate import counts_for, ratio
from src.phase3.model import ReferenceMLP
from src.phase3.reference import model_identity
from .checkpoint import read_transaction
from .data import verify_files
from .protocol import configure_runtime
from .evaluate import rational_macro


FINAL_FILES = {f'{k}.npy' for k in ('x', 'y', 'ids', 'cohort', 'attempted', 'component_ids')}
REQUIRED_MANIFEST = {
    'schema', 'role', 'release_id', 'files', 'eligible_codes', 'families',
    'arrival', 'component_ids_sha256', 'development_manifest_sha256',
    'protocol_sha256', 'frozen_checkpoint_inventory_sha256', 'analysis_sha256',
    'support_min_rows', 'support_min_components', 'benign_cohort_count',
    'train_component_ids_sha256', 'development_component_ids_sha256',
}


def final_stage_counts(stage, slots, y, predicted, eligible, names, arrival, cohorts, attempted):
    """Score every final row, including classes that have not arrived yet."""
    if (not slots or slots[0] != 0 or len(set(slots)) != len(slots) or
            not np.isin(predicted, slots).all() or not np.isin(y, range(16)).all()):
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
        cohort_counts.append({'cohort': j, 'correct': int((predicted[cohort] == y[cohort]).sum()),
                              'total': int(cohort.sum())})
    provenance = []
    for flag, name in ((False, 'original_background'), (True, 'remapped_attempted')):
        subgroup = benign & (attempted == flag)
        errors = int((subgroup & alert).sum())
        provenance.append({'group': name, 'benign_rows': int(subgroup.sum()), 'alerts': errors,
                           'error_rate': ratio(errors, int(subgroup.sum()))})
    return {'stage': stage, 'head_width': len(slots), 'source_codes_in_slot_order': slots,
            'full_seen_bank_rows': len(y), 'full_seen_confusion_source_code_order': full_matrix,
            'full_seen_classes': full_classes, 'eligible_seen_bank_rows': int(mask.sum()),
            'eligible_codes': seen, 'eligible_confusion_source_code_order': matrix,
            'eligible_classes': classes, 'eligible_macro_f1': float(macro),
            'eligible_macro_f1_exact': [str(macro.numerator), str(macro.denominator)],
            'eligible_pooled_accuracy': ratio(int((predicted[mask] == y[mask]).sum()), int(mask.sum())),
            'untargeted_new_annotated_class_f1': None if a is None else float(a),
            'binary_full_seen': {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
                                 'attack_precision': ratio(tp, tp + fp),
                                 'attack_recall': ratio(tp, tp + fn),
                                 'f1': ratio(2 * tp, 2 * tp + fp + fn),
                                 'benign_far': ratio(fp, fp + tn),
                                 'attack_miss_rate': ratio(fn, tp + fn)},
            'benign_provenance_descriptive': provenance, 'hulk_partition': source,
            'cohort_counts': cohort_counts}


def validate_final_package(package: Path, frozen: dict) -> dict:
    manifest_path = package / 'manifest.json'
    manifest = read_json(manifest_path)
    if set(manifest) != REQUIRED_MANIFEST:
        raise ValueError('Final manifest schema mismatch; no fallback to development role')
    if manifest['schema'] != 'phase3-final-test-v1' or manifest['role'] != 'final_test':
        raise ValueError('Package is not explicitly designated final_test')
    if not manifest['release_id'] or manifest['development_manifest_sha256'] != frozen['development_manifest_sha256']:
        raise ValueError('Final release or development split lineage differs from freeze')
    for field in ('protocol_sha256', 'frozen_checkpoint_inventory_sha256', 'analysis_sha256'):
        if manifest[field] != frozen[field]:
            raise ValueError(f'Frozen {field} mismatch')
    if digest(manifest_path) != frozen['final_manifest_sha256']:
        raise ValueError('Final manifest hash differs from one-shot freeze')
    verify_files(package, manifest['files'], FINAL_FILES)
    arrays = {name[:-4]: np.load(package / name, allow_pickle=False, mmap_mode='r') for name in FINAL_FILES}
    x, y, ids = arrays['x'], arrays['y'], arrays['ids']
    n = len(y)
    if x.dtype != np.dtype('<f4') or x.shape != (n, 74) or not np.isfinite(x).all():
        raise ValueError('Final feature matrix violates frozen FP32 schema')
    if y.dtype != np.dtype('<i8') or ids.dtype != np.dtype('<u8') or len(np.unique(ids)) != n:
        raise ValueError('Final labels/IDs invalid or duplicated')
    # Keep every registered taxonomy class in the final bank, including rare
    # classes excluded from the eligible macro-F1 set.  The full-inventory
    # confusion matrix is descriptive; only the frozen eligible inventory is
    # used for the confirmatory supported-class macro metric.
    if not np.isin(y, range(16)).all():
        raise ValueError('Final package contains labels outside the frozen taxonomy')
    if len(arrays['cohort']) != n or len(arrays['attempted']) != n:
        raise ValueError('Final evaluator metadata row count mismatch')
    if arrays['cohort'].dtype != np.dtype('uint8') or arrays['attempted'].dtype != np.dtype('bool'):
        raise ValueError('Final cohort/provenance metadata dtype mismatch')
    components = arrays['component_ids']
    if components.shape != (n,) or components.dtype != np.dtype('<u8'):
        raise ValueError('Final component ID inventory invalid')
    if array_identity(components) != manifest['component_ids_sha256']:
        raise ValueError('Final component identity mismatch')
    if manifest['component_ids_sha256'] in {manifest['train_component_ids_sha256'], manifest['development_component_ids_sha256']}:
        raise ValueError('Final component inventory aliases a development role')
    if not np.isin(arrays['cohort'], (1, 2, 3, 4)).all():
        raise ValueError('Invalid benign cohort assignment')
    if not np.isin(manifest['eligible_codes'], range(16)).all() or len(set(manifest['eligible_codes'])) != len(manifest['eligible_codes']):
        raise ValueError('Invalid fixed eligible class inventory')
    if not np.isin(y, range(16)).all() or len(manifest['families']) != 16 or len(manifest['arrival']) != 16:
        raise ValueError('Invalid frozen taxonomy')
    if 0 not in manifest['eligible_codes']:
        raise ValueError('Benign class is absent from the eligible metric inventory')
    if int((y == 0).sum()) == 0:
        raise ValueError('Final benign denominator is empty')
    benign_cohorts = np.unique(arrays['cohort'][y == 0])
    if len(benign_cohorts) != manifest['benign_cohort_count']:
        raise ValueError('Final benign cohort count differs from the frozen analysis')
    if (not isinstance(manifest['support_min_rows'], int) or manifest['support_min_rows'] < 1 or
            not isinstance(manifest['support_min_components'], int) or manifest['support_min_components'] < 1):
        raise ValueError('Frozen support thresholds must be positive integers')
    for code in manifest['eligible_codes']:
        if int((y == code).sum()) < manifest['support_min_rows']:
            raise ValueError(f'Final eligible class {code} below frozen row support')
        if len(np.unique(components[y == code])) < manifest['support_min_components']:
            raise ValueError(f'Final eligible class {code} below frozen component support')
    return manifest


def validate_checkpoint_matrix(run: dict, expected_run_hash: str, expected_inventory_hash: str) -> None:
    if run.get('schema') != 'phase3-run-v2' or run.get('status') != 'complete' or run.get('resumed_from') is not None:
        raise ValueError('Only complete from-start trajectories are eligible')
    if run.get('final_test_accessed') is not False or run.get('gpu_grid_launched') is not False:
        raise ValueError('Unexpected prior held-out access or execution mode')
    rows = run.get('checkpoints', [])
    expected = [(stage, rnd) for stage in range(1, 5) for rnd in range(1, run['settings']['rounds'] + 1)]
    if [(r.get('stage'), r.get('round')) for r in rows] != expected:
        raise ValueError('Checkpoint matrix is incomplete, duplicated, or out of order')
    if len({r.get('file') for r in rows}) != len(rows) or any(r.get('stage_end') != (r.get('round') == run['settings']['rounds']) for r in rows):
        raise ValueError('Checkpoint file reuse or stage-end marker mismatch')
    if run.get('total_commits') != len(expected) or run.get('next_cursor') != [5, 1]:
        raise ValueError('Run completion cursor disagrees with checkpoint matrix')
    inventory = [{'file': r['file'], 'sha256': r['file_sha256'], 'stage': r['stage'], 'round': r['round'],
                  'stage_end': r['stage_end']} for r in rows]
    if identity(inventory) != expected_inventory_hash:
        raise ValueError('Checkpoint inventory differs from freeze')


def evaluate_final(package: Path, run_dirs: list[Path], freeze_path: Path, output: Path):
    configure_runtime()
    freeze = read_json(freeze_path)
    if set(freeze) != {'schema', 'status', 'development_manifest_sha256', 'protocol_sha256',
                       'frozen_checkpoint_inventory_sha256', 'analysis_sha256',
                       'final_manifest_sha256', 'run_manifest_sha256',
                       'checkpoint_inventory_sha256','settings'}:
        raise ValueError('Freeze manifest schema mismatch')
    if freeze['schema'] != 'phase3-final-freeze-v1' or freeze['status'] != 'authorized_one_shot':
        raise ValueError('Final evaluation has not passed its explicit freeze gate')
    manifest = validate_final_package(package, freeze)
    if len(run_dirs) != len(freeze['run_manifest_sha256']):
        raise ValueError('Checkpoint matrix differs from freeze')
    if not (len(run_dirs) == len(freeze['settings']) == len(freeze['checkpoint_inventory_sha256'])):
        raise ValueError('Frozen run/settings/checkpoint inventories differ in length')
    if output.exists():
        raise FileExistsError(output)
    prepared = []
    for i, (run_dir, expected_sha) in enumerate(zip(run_dirs, freeze['run_manifest_sha256'])):
        run_path = run_dir / 'run.json'
        if digest(run_path) != expected_sha:
            raise ValueError('Run manifest changed after freeze')
        run = read_json(run_path)
        validate_checkpoint_matrix(run, expected_sha, freeze['checkpoint_inventory_sha256'][i])
        if run.get('execution', {}).get('protocol_sha256') != freeze['protocol_sha256']:
            raise ValueError('Run protocol differs from the final evaluation freeze')
        if run['settings'] != freeze['settings'][i]:
            raise ValueError('Run settings differ from frozen analysis matrix')
        for row in run['checkpoints']:
            checkpoint_path = run_dir / row['file']
            if not checkpoint_path.is_file() or digest(checkpoint_path) != row['file_sha256']:
                raise ValueError('Checkpoint payload missing or hash mismatch')
        prepared.append(run)
    # Exclusive durable lock prevents concurrent/repeated scoring. Claim is
    # retained after any post-claim failure, requiring a versioned new release.
    receipt = output.with_name(output.name + '.one-shot-claimed.json')
    fd = os.open(receipt, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        stream.write(json.dumps({'status':'claimed','manifest_sha256':freeze['final_manifest_sha256']}, sort_keys=True))
        stream.flush(); os.fsync(stream.fileno())
    output.mkdir(parents=True)
    result_runs = []
    for run_index, (run_dir, expected_sha) in enumerate(zip(run_dirs, freeze['run_manifest_sha256'])):
        run = prepared[run_index]
        inventory_hash = identity([{'file':r['file'],'sha256':r['file_sha256'],'stage':r['stage'],'round':r['round'],'stage_end':r['stage_end']} for r in run.get('checkpoints',[])])
        inv_expected = freeze['checkpoint_inventory_sha256'][run_index]
        if inventory_hash != inv_expected: raise ValueError('Checkpoint inventory differs from freeze')
        stages = []
        for checkpoint in run['checkpoints']:
            meta, arrays_ckpt, commit = read_transaction(run_dir / checkpoint['file'], run['execution'])
            if checkpoint != commit:
                continue
            if not checkpoint['stage_end']: continue
            stage, slots = checkpoint['stage'], meta['slots']
            model = ReferenceMLP(len(slots), run['settings']['seed'])
            model.load_state_dict({k[6:]: torch.from_numpy(v) for k,v in arrays_ckpt.items() if k.startswith('model.')}, strict=True)
            model.eval()
            predicted_slots = np.empty(len(np.load(package/'y.npy',allow_pickle=False,mmap_mode='r')), dtype=np.uint8)
            x = np.load(package/'x.npy',allow_pickle=False,mmap_mode='r')
            y = np.load(package/'y.npy',allow_pickle=False,mmap_mode='r')
            cohort = np.load(package/'cohort.npy',allow_pickle=False,mmap_mode='r')
            attempted = np.load(package/'attempted.npy',allow_pickle=False,mmap_mode='r')
            with torch.no_grad():
                for start in range(0,len(y),2048):
                    logits=model(torch.from_numpy(x[start:start+2048].copy()))
                    if not torch.isfinite(logits).all(): raise FloatingPointError('Nonfinite final logits')
                    predicted_slots[start:start+2048]=logits.argmax(1).numpy().astype(np.uint8)
            if not np.isin(predicted_slots, range(len(slots))).all(): raise ValueError('Prediction slot outside head')
            predicted=np.asarray(slots,dtype=np.int16)[predicted_slots]
            counts=final_stage_counts(stage,slots,y,predicted,manifest['eligible_codes'],manifest['families'],manifest['arrival'],cohort,attempted)
            counts.update({'model_sha256':model_identity(model,slots),'bank_ids_sha256':array_identity(np.load(package/'ids.npy',allow_pickle=False,mmap_mode='r'))})
            prediction_name = f'run-{run_index + 1:03d}-stage-{stage:02d}-predictions.npy'
            prediction_path = output / prediction_name
            # These row-aligned labels and the package ID hash make every
            # aggregate denominator independently auditable without saving
            # sensitive feature vectors into the results directory.
            np.save(prediction_path, predicted.astype('<i2', copy=False), allow_pickle=False)
            counts.update({'predictions_file': prediction_name,
                           'predictions_sha256': digest(prediction_path),
                           'row_ids_sha256': array_identity(np.load(package/'ids.npy',allow_pickle=False,mmap_mode='r'))})
            stages.append(counts)
        if len(stages)!=4: raise ValueError('All four frozen checkpoints required')
        result_runs.append({'run_manifest_sha256':expected_sha,'settings':run['settings'],'stages':stages})
    write_json(output/'metrics.json',{'schema':'phase3-final-test-metrics-v1','status':'one_shot_final_test_complete',
      'final_manifest_sha256':freeze['final_manifest_sha256'],'freeze_manifest_sha256':digest(freeze_path),
      'runs':result_runs,'final_test_accessed':True,'training_or_tuning_performed':False})
    receipt.write_text(json.dumps({'status':'complete','manifest_sha256':freeze['final_manifest_sha256'],'metrics_sha256':digest(output/'metrics.json')},sort_keys=True)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--freeze',type=Path,required=True)
    parser.add_argument('--run-dir',type=Path,nargs='+',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    evaluate_final(args.package,args.run_dir,args.freeze,args.output)


if __name__=='__main__': main()
