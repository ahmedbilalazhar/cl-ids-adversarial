"""Locked E1 acquisition probes; separate from the frozen v2 study engine."""
from __future__ import annotations

import argparse
import copy
import time
import unittest
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from src.phase3.common import (
    ROOT,
    array_identity,
    canonical,
    digest,
    identity,
    read_json,
    rng,
    write_json,
)
from src.phase3.model import ReferenceMLP
from src.phase3.reference import snapshot
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.data import BASE_DEV, load_stage, verify_files, verify_train
from src.phase3_v2.learning import aggregate, client_state
from src.phase3_v2.protocol import Settings, code_identity, configure_runtime

CONFIG = ROOT/'configs/phase3/acquisition-diagnostic-v1.json'
PLAN = ROOT/'docs/phase3-acquisition-diagnostic-v1/plan-2026-10-24.md'
SLOTS = [0, 7, 12]


def diagnostic_identity():
    files = [Path(__file__), CONFIG, PLAN, ROOT/'tests/test_phase3_acquisition.py']
    return identity({'parent_code_identity': code_identity(), 'files': {p.relative_to(ROOT).as_posix(): digest(p) for p in files}})


def validate_config(config):
    if config['parent_code_identity'] != code_identity():
        raise ValueError('Frozen parent source changed')
    if (config['seeds'] != [101, 102, 103] or config['stage'] != 1 or config['learner'] != 'FT' or
            config['admission'] != 'NONE' or config['learning_rate'] != .001 or config['epochs_per_round'] != 1 or
            config['rounds'] != 12 or config['readout_rounds'] != [3, 12] or config['objectives'] != ['natural', 'equal_class'] or
            config['training_batch_size'] != 128 or config['final_test_access'] or config['gpu_dispatchable']):
        raise ValueError('Only the locked exploratory E1 matrix is executable')


def class_weights(targets, width):
    counts = np.bincount(targets, minlength=width)
    if len(counts) != width or np.any(counts == 0):
        raise ValueError('Every registered E1 class must have supplied support')
    return torch.tensor(len(targets)/(width*counts), dtype=torch.float32)


def objective_loss(logits, targets, weights=None):
    if weights is None:
        return F.cross_entropy(logits, targets)
    return (F.cross_entropy(logits, targets, reduction='none')*weights[targets]).mean()


def local_update(template, data, seed, client_id, round_id, dropout, weights=None):
    """Independent FT loop; natural path must exactly reproduce frozen v2."""
    indexes = np.flatnonzero(data.owner == client_id)
    if not len(indexes):
        return None, dropout.copy(), {'inactive': True, 'optimizer_updates': 0, 'current_exposures': 0}
    local = copy.deepcopy(template)
    optimizer = torch.optim.Adam(local.parameters(), lr=.001, betas=(.9, .999), eps=1e-8,
                                 weight_decay=0, amsgrad=False, foreach=False, fused=False)
    targets = data.targets(SLOTS)
    order = rng(6, seed, client_id, 1, round_id, 1).permutation(indexes)
    loss_sum, updates = 0., 0
    with torch.random.fork_rng(devices=[]):
        torch.set_rng_state(torch.from_numpy(dropout.copy()))
        local.train()
        for start in range(0, len(order), 128):
            selected = order[start:start+128]
            x = torch.from_numpy(data.x[selected].copy())
            y = torch.from_numpy(targets[selected])
            optimizer.zero_grad(set_to_none=True)
            loss = objective_loss(local(x), y, weights)
            if not torch.isfinite(loss):
                raise FloatingPointError('Nonfinite exploratory objective')
            loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in local.parameters()):
                raise FloatingPointError('Nonfinite exploratory gradient')
            optimizer.step()
            loss_sum += float(loss.detach())
            updates += 1
        next_dropout = torch.get_rng_state().numpy().copy()
    if any(not torch.isfinite(p).all() for p in local.parameters()) or any(
            not torch.isfinite(v).all() for s in optimizer.state.values() for v in s.values() if isinstance(v, torch.Tensor)):
        raise FloatingPointError('Nonfinite exploratory optimizer/model state')
    return local, next_dropout, {'inactive': False, 'optimizer_updates': updates,
                                'current_exposures': len(order), 'mean_optimizer_batch_objective': loss_sum/updates}


def readout(model, x, y):
    """Eval-only bank; no outputs feed local_update or class_weights."""
    previous = model.training
    model.eval()
    logits = []
    with torch.no_grad():
        for start in range(0, len(y), 2048):
            logits.append(model(torch.from_numpy(x[start:start+2048].copy())))
    model.train(previous)
    values = torch.cat(logits)
    if not torch.isfinite(values).all():
        raise FloatingPointError('Nonfinite exploratory readout')
    targets = torch.from_numpy(np.asarray([{c: i for i, c in enumerate(SLOTS)}[int(v)] for v in y], dtype=np.int64))
    predictions = values.argmax(dim=1).numpy()
    losses = F.cross_entropy(values, targets, reduction='none').numpy()
    probabilities = values.softmax(dim=1)[torch.arange(len(y)), targets].numpy()
    true = values[torch.arange(len(y)), targets]
    other = values.clone()
    other[torch.arange(len(y)), targets] = -torch.inf
    margins = (true-other.max(dim=1).values).numpy()
    matrix = np.zeros((3, 3), dtype=np.int64)
    np.add.at(matrix, (targets.numpy(), predictions), 1)
    classes = []
    for slot, code in enumerate(SLOTS):
        selected = y == code
        support, correct = int(selected.sum()), int(matrix[slot, slot])
        classes.append({'source_code': code, 'support': support, 'correct': correct,
                        'recall': None if support == 0 else correct/support,
                        'mean_natural_CE': None if support == 0 else float(losses[selected].mean(dtype=np.float64)),
                        'mean_true_probability': None if support == 0 else float(probabilities[selected].mean(dtype=np.float64)),
                        'true_minus_best_other_logit_quantiles_0_50_100': None if support == 0 else np.quantile(margins[selected], [0, .5, 1]).tolist()})
    tp = np.diag(matrix)
    denominators = matrix.sum(axis=0)+matrix.sum(axis=1)
    macro = float(np.mean(np.divide(2*tp, denominators, out=np.zeros(3, dtype=float), where=denominators != 0)))
    benign_count = int(matrix[0].sum())
    return {'rows': len(y), 'source_codes_in_matrix_order': SLOTS, 'confusion': matrix.tolist(), 'classes': classes,
            'macro_f1': macro, 'benign_far': None if benign_count == 0 else int(matrix[0, 1:].sum())/benign_count}


def feature_audit(data):
    rows = []
    for code in SLOTS:
        values = data.x[data.y == code].astype(np.float64)
        rows.append({'source_code': code, 'rows': len(values),
                     'absolute_value_quantiles_0_50_90_99_100': np.quantile(np.abs(values), [0, .5, .9, .99, 1]).tolist(),
                     'row_L2_quantiles_0_50_90_99_100': np.quantile(np.linalg.norm(values, axis=1), [0, .5, .9, .99, 1]).tolist(),
                     'constant_features_within_class': int(np.count_nonzero(np.ptp(values, axis=0) == 0)),
                     'exact_zero_fraction': float(np.count_nonzero(values == 0)/values.size)})
    _, inverse = np.unique(data.x, axis=0, return_inverse=True)
    memberships = np.zeros((int(inverse.max())+1, 3), dtype=np.int64)
    for slot, code in enumerate(SLOTS):
        np.add.at(memberships[:, slot], inverse[data.y == code], 1)
    mixed = (memberships > 0).sum(axis=1) > 1
    # For exact feature vectors, any deterministic feature-only classifier can
    # get at most the largest label count per vector correct on this inventory.
    unavoidable = int((memberships.sum(axis=1)-memberships.max(axis=1)).sum())
    return {'classes': rows, 'distinct_feature_vectors': len(memberships), 'mixed_label_feature_vectors': int(mixed.sum()),
            'rows_in_mixed_feature_vectors_by_class': memberships[mixed].sum(axis=0).tolist(),
            'unavoidable_training_errors_from_exact_feature_collisions': unavoidable,
            'interpretation': 'FP32 feature equality on this inventory only; no labels or records are removed and no generalization claim follows'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/phase3-acquisition-diagnostic-v1')
    args = parser.parse_args()
    output = args.output
    if output.exists():
        raise FileExistsError('Choose a fresh diagnostic output directory')
    config = read_json(CONFIG)
    validate_config(config)
    runtime = configure_runtime()
    execution = {'diagnostic_identity': diagnostic_identity(), 'parent_code_identity': code_identity(),
                 'config_sha256': digest(CONFIG), 'plan_sha256': digest(PLAN), 'runtime_identity': identity(runtime)}
    output.mkdir(parents=True)
    write_json(output/'execution.json', {**execution, 'runtime': runtime, 'scope': config['scope']})
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'), pattern='test_phase3_acquisition.py')
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    write_json(output/'acceptance.json', {'status': 'passed' if result.wasSuccessful() else 'failed',
               'tests_run': result.testsRun, 'failures': [(str(t), message) for t, message in result.failures+result.errors], **execution})
    if not result.wasSuccessful():
        raise AssertionError('Acquisition probe acceptance failed')
    dev = ROOT/'data/processed/phase3-reference74-v1/development'
    if digest(dev/'manifest.json') != BASE_DEV:
        raise ValueError('Only pinned development is allowed')
    manifest = read_json(dev/'manifest.json')
    verify_files(dev, manifest['files'], {f'{k}.npy' for k in ('x', 'y', 'ids', 'cohort', 'attempted')})
    dev_y = np.load(dev/'y.npy', allow_pickle=False)
    use = np.asarray(manifest['arrival'])[dev_y] <= 1
    dx, dy = np.load(dev/'x.npy', allow_pickle=False)[use], dev_y[use]
    if sorted(set(map(int, dy))) != SLOTS:
        raise ValueError('Unexpected E1 development registry')
    inventory_path = ROOT/'results/phase3-cpu-v2/development/completion.json'
    inventory = read_json(inventory_path)
    data, baseline, packages = {}, {}, {}
    for seed in config['seeds']:
        package = ROOT/f'data/processed/phase3-cpu-v2/s{seed}-p000/train'
        row = next(r for r in inventory['rows'] if r['group'] == 'tuning' and r['settings']['learner'] == 'FT' and
                   r['settings']['seed'] == seed and r['settings']['learning_rate'] == .001)
        if row['status'] != 'valid':
            raise ValueError('All original seed baselines required')
        baseline[seed] = Path(row['run'])
        run = read_json(baseline[seed]/'run.json')
        if run['execution']['code_identity'] != code_identity() or run['settings']['rounds'] != 3 or run['settings']['epochs'] != 1:
            raise ValueError('Incompatible baseline trajectory')
        verify_train(package, Settings(learner='FT', seed=seed), run['execution']['train_manifest_sha256'])
        packages[seed] = {'train_manifest_sha256': digest(package/'manifest.json'), 'baseline_run_sha256': digest(baseline[seed]/'run.json')}
        data[seed] = load_stage(package, 1)
        if sorted(set(map(int, data[seed].y))) != SLOTS:
            raise ValueError('Only adopted clean E1 classes allowed')
    write_json(output/'inputs.json', {'packages_by_seed': packages, 'original_inventory_sha256': digest(inventory_path),
               'development_manifest_sha256': BASE_DEV, 'E1_development_ids_sha256': array_identity(np.load(dev/'ids.npy', allow_pickle=False)[use]),
               'features': feature_audit(data[101])})
    trajectories, parity = [], []
    try:
        for objective in config['objectives']:
            for seed in config['seeds']:
                started = time.perf_counter()
                current = data[seed]
                weights = None if objective == 'natural' else class_weights(current.targets(SLOTS), 3)
                folder = output/f'{objective}-s{seed}'
                folder.mkdir()
                model = ReferenceMLP(3, seed)
                dropout = [client_state(Settings(learner='FT', seed=seed), i).dropout for i in range(5)]
                counts = [int(np.count_nonzero(current.owner == i)) for i in range(5)]
                ownership = [{'client': i, 'records': counts[i], 'class_counts': [int(np.count_nonzero((current.owner == i) & (current.y == c))) for c in SLOTS],
                              'aggregation_weight_fp32': float(np.float32(counts[i]/len(current.y)))} for i in range(5)]
                curves = [{'round': 0, 'train': readout(model, current.x, current.y), 'development': readout(model, dx, dy)}]
                cumulative_updates = [0]*5
                for round_id in range(1, config['rounds']+1):
                    round_start = time.perf_counter()
                    updates, locals_readout, losses = [], [], []
                    for client in range(5):
                        local, next_rng, accounting = local_update(model, current, seed, client, round_id, dropout[client], weights)
                        dropout[client] = next_rng
                        updates.append(None if local is None else snapshot(local))
                        cumulative_updates[client] += accounting['optimizer_updates']
                        losses.append({'client': client, **accounting})
                        if round_id in config['readout_rounds'] and local is not None:
                            own = current.owner == client
                            locals_readout.append({'client': client, 'own_train': readout(local, current.x[own], current.y[own]),
                                                   'development': readout(local, dx, dy)})
                    state, _ = aggregate(snapshot(model), updates, counts)
                    model.load_state_dict(state)
                    if objective == 'natural' and round_id <= 3:
                        meta, arrays, marker = read_transaction(baseline[seed]/f'E1-R{round_id}.npz')
                        expected_model = {k[6:]: v for k, v in arrays.items() if k.startswith('model.')}
                        exact = set(expected_model) == set(state) and all(np.array_equal(expected_model[k], state[k].numpy()) for k in state)
                        exact = exact and all(np.array_equal(dropout[i], arrays[f'client{i}.dropout']) for i in range(5))
                        exact = exact and all(meta['clients'][i]['updates'] == cumulative_updates[i] and
                                             meta['clients'][i]['current_exposures'] == counts[i]*round_id for i in range(5))
                        parity.append({'seed': seed, 'round': round_id, 'state_dropout_counters_exact': exact,
                                       'original_state_identity': marker['state_identity']})
                        if not exact:
                            raise AssertionError('Independent natural E1 loop differs from frozen v2')
                    record = {'round': round_id, 'train': readout(model, current.x, current.y), 'development': readout(model, dx, dy),
                              'clients': losses, 'locals_before_aggregation': locals_readout, 'seconds_including_readouts': time.perf_counter()-round_start}
                    curves.append(record)
                    if round_id in config['readout_rounds']:
                        metadata = {'schema': 'phase3-exploratory-E1-model-v1', **execution, 'objective': objective, 'seed': seed,
                                    'round': round_id, 'slots': SLOTS, 'complete_four_stage_candidate': False}
                        np.savez(folder/f'E1-R{round_id}-model.npz', metadata=np.array(canonical(metadata)),
                                 **{k: v.numpy() for k, v in state.items()})
                    print({'objective': objective, 'seed': seed, 'round': round_id,
                           'dev_FTP_SSH_recall': [record['development']['classes'][i]['recall'] for i in (1, 2)]}, flush=True)
                trajectory = {'objective': objective, 'seed': seed, 'global_class_weights': None if weights is None else weights.tolist(),
                              'ownership': ownership, 'curves': curves, 'elapsed_seconds_including_readouts': time.perf_counter()-started,
                              'model_artifacts': {p.name: digest(p) for p in folder.glob('*.npz')}}
                write_json(folder/'trajectory.json', trajectory)
                trajectories.append(trajectory)
                write_json(output/'progress.json', {'completed_physical_E1_trajectories': len(trajectories), 'required': 6, 'baseline_checks': parity})
    except Exception as error:
        write_json(output/'failure.json', {'status': 'failed', 'type': type(error).__name__, 'message': str(error), 'baseline_checks': parity,
                   'completed_physical_E1_trajectories': len(trajectories), 'no_invalid_or_missing_cell_imputation': True})
        raise
    cells = []
    for objective in config['objectives']:
        for round_id in config['readout_rounds']:
            selected = [t for t in trajectories if t['objective'] == objective]
            per_seed = [{'seed': t['seed'], 'train': t['curves'][round_id]['train'], 'development': t['curves'][round_id]['development']} for t in selected]
            means = {bank: {str(code): float(np.mean([r[bank]['classes'][slot]['recall'] for r in per_seed])) for slot, code in enumerate(SLOTS)}
                     for bank in ('train', 'development')}
            cells.append({'objective': objective, 'rounds': round_id, 'per_seed': per_seed, 'mean_recall': means,
                          'E1_development_anchor_context_passed': all(means['development'][str(code)] >= .5 for code in (7, 12)),
                          'complete_clean_gate_passed': False, 'E2_Hulk_status': 'not_exercised'})
    summary = {'status': 'completed_exploratory_E1_diagnostic', **execution, 'physical_E1_trajectories': 6, 'logical_E1_cells': 12,
               'paired_development_seeds': [101, 102, 103], 'additional_complete_study_replicates': 0,
               'baseline_exact_checks': parity, 'cells': cells, 'final_test_accessed': False, 'gpu_dispatchable': False,
               'E1_total_current_exposures': sum(sum(c['current_exposures'] for c in r['clients']) for t in trajectories for r in t['curves'][1:]),
               'E1_total_optimizer_updates': sum(sum(c['optimizer_updates'] for c in r['clients']) for t in trajectories for r in t['curves'][1:]),
               'elapsed_seconds_including_readouts': sum(t['elapsed_seconds_including_readouts'] for t in trajectories),
               'limits': ['Development evidence was already visible when this plan was written.', 'Only FT E1 is exercised; no EI/DR/replay, E2 Hulk, later retention or corruption claim.',
                          'Longer schedules jointly change exposure/synchronization/Adam resets.', 'No adaptive extension, favorable seed selection, threshold change or final dispatch.']}
    write_json(output/'summary.json', summary)
    write_json(output/'artifact-index.json', {'files': {p.relative_to(output).as_posix(): digest(p) for p in sorted(output.rglob('*')) if p.is_file()}})
    print({'status': summary['status'], 'baseline_exact_checks': len(parity), 'physical_E1_trajectories': 6})


if __name__ == '__main__':
    main()
