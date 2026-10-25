"""Read-only counts, learning curves and controlled development comparisons."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
import torch

from src.phase3.common import ROOT, canonical, digest, read_json, write_json
from src.phase3.evaluate import counts_for
from src.phase3.model import ReferenceMLP
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.data import verify_train
from src.phase3_v2.protocol import Settings, code_identity, configure_runtime


def main():
    configure_runtime()
    base = ROOT/'results/phase3-cpu-v2'
    inventory = read_json(base/'development/completion.json')
    records, groups, data_cache = [], defaultdict(list), {}
    for row in inventory['rows']:
        if row['status'] != 'valid' or not row['physical_execution']:
            continue
        run_dir = Path(row['run'])
        run = read_json(run_dir/'run.json')
        if run['execution']['code_identity'] != code_identity():
            raise ValueError('Source version differs')
        seed = row['settings']['seed']
        package = ROOT/f'data/processed/phase3-cpu-v2/s{seed}-p000/train'
        if digest(package/'manifest.json') != run['execution']['train_manifest_sha256']:
            raise ValueError('Training annotation view differs')
        if seed not in data_cache:
            verify_train(package, Settings(seed=seed), run['execution']['train_manifest_sha256'])
            data_cache[seed] = {k: np.load(package/f'E1/{k}.npy', allow_pickle=False, mmap_mode='r') for k in ('x', 'y', 'ids')}
        data = data_cache[seed]
        checkpoint = next(c for c in run['checkpoints'] if c['stage'] == 1 and c['stage_end'])
        meta, arrays, _ = read_transaction(run_dir/checkpoint['file'], run['execution'])
        model = ReferenceMLP(len(meta['slots']), seed)
        model.load_state_dict({k[6:]: torch.from_numpy(v) for k, v in arrays.items() if k.startswith('model.')})
        model.eval()
        predicted = np.empty(len(data['y']), dtype=np.int64)
        with torch.no_grad():
            for start in range(0, len(predicted), 2048):
                logits = model(torch.from_numpy(data['x'][start:start+2048].copy()))
                if not torch.isfinite(logits).all():
                    raise FloatingPointError('Nonfinite diagnostic logits')
                predicted[start:start+2048] = np.asarray(meta['slots'])[logits.argmax(dim=1).numpy()]
        train_matrix, train_classes = counts_for(data['y'], predicted, meta['slots'], [str(i) for i in range(16)])
        metric = read_json(Path(row['metrics']))
        curves = []
        for transition in run['ledger']:
            if transition['kind'] != 'round':
                continue
            updates = sum(c['optimizer_updates'] for c in transition['clients'])
            losses = [sum(c['mean_losses'][i]*c['optimizer_updates'] for c in transition['clients'] if not c['inactive'])/updates for i in range(4)]
            curves.append({'stage': transition['stage'], 'round': transition['round'], 'optimizer_updates': updates,
                           'mean_optimizer_batch_losses_current_replay_dark_EI': losses,
                           'current_exposures': sum(c.get('current_exposures', 0) for c in transition['clients']),
                           'replay_exposures': sum(c.get('replay_exposures', 0) for c in transition['clients'])})
        cells = []
        for code in (7, 12):
            training = next(c for c in train_classes if c['code'] == code)
            development = next(c for c in metric['stages'][0]['eligible_classes'] if c['code'] == code)
            matrix = metric['stages'][0]['full_seen_confusion_source_code_order']
            cells.append({'source_code': code, 'training_support': training['support'], 'training_recall': training['recall'],
                          'development_support': development['support'], 'development_recall': development['recall'],
                          'development_predicted_benign': matrix[code][0],
                          'development_predicted_other_attack': sum(matrix[code])-matrix[code][code]-matrix[code][0]})
        record = {'row_id': row['row_id'], 'group': row['group'], 'settings': row['settings'],
                  'E1_training_confusion': train_matrix, 'E1_training_classes': train_classes, 'E1_anchor_comparison': cells,
                  'macro_f1_by_stage': [s['eligible_macro_f1'] for s in metric['stages']],
                  'benign_far_by_stage': [s['binary_full_seen']['benign_far'] for s in metric['stages']],
                  'hulk_partition_by_stage': [s['hulk_partition'] for s in metric['stages']], 'round_curves': curves}
        records.append(record)
    # Config-level learning-rate comparisons include aliases as logical rows,
    # but each endpoint retains the original physical execution and seed.
    for row in inventory['rows']:
        if row['group'] != 'tuning' or row['status'] != 'valid':
            continue
        key = {k: v for k, v in row['settings'].items() if k not in ('seed', 'learning_rate')}
        groups[canonical(key)].append(row)
    comparisons = []
    for key, rows in groups.items():
        pairs = []
        for seed in (101, 102, 103):
            selected = {r['settings']['learning_rate']: r for r in rows if r['settings']['seed'] == seed}
            if set(selected) != {.0001, .001}:
                continue
            low, high = selected[.0001], selected[.001]
            a, b = Fraction(*map(int, low['score_exact'])), Fraction(*map(int, high['score_exact']))
            pairs.append({'seed': seed, 'low_row': low['row_id'], 'high_row': high['row_id'],
                          'high_minus_low_equal_stage_macro_f1': float(b-a)})
        comparisons.append({'matched_settings': __import__('json').loads(key), 'pairs': pairs,
                            'mean_high_minus_low': None if len(pairs) != 3 else sum(p['high_minus_low_equal_stage_macro_f1'] for p in pairs)/3})
    counts = []
    source = ROOT/'data/processed/phase3-cpu-v2/s101-p000/train'
    for stage in range(1, 5):
        y = np.load(source/f'E{stage}/y.npy', allow_pickle=False)
        counts.append({'stage': stage, 'rows': len(y), 'source_counts': np.bincount(y, minlength=16).tolist()})
    dev_y = np.load(ROOT/'data/processed/phase3-reference74-v1/development/y.npy', allow_pickle=False)
    result = {'status': 'read_only_post_selection_diagnostics', 'code_identity': code_identity(), 'physical_rows': records,
              'controlled_learning_rate_comparisons': comparisons, 'training_inventory': counts,
              'fixed_development_inventory': np.bincount(dev_y, minlength=16).tolist(),
              'interpretation': ['Training/development anchor confusion separates observed acquisition and generalization gaps; it does not identify their cause.',
                                 'Schedule comparisons jointly vary synchronization and Adam resets.',
                                 'Retention coefficients and learning rates are controlled development comparisons within the declared grid; no new seed or threat is selected.',
                                 'Class/prevalence skew and forgetting are hypotheses to investigate; no split, transform, label inventory, support floor or bank was changed.'],
              'final_test_accessed': False, 'training_models_modified': False}
    output = base/'learning-diagnostics.json'
    if output.exists():
        raise FileExistsError(output)
    write_json(output, result)
    print(len(records), 'physical E1 training/development comparisons exported')


if __name__ == '__main__':
    main()
