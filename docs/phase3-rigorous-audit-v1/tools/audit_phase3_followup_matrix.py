"""Independent integrity and metric audit for the 74-feature follow-up matrix.

Read-only except for its JSON audit output. It checks the primary 240 cells,
DQ, clean confirmations, 48 replay-loss cells, 96 quota cells, duplicate copies,
stage checkpoints, and parity with the report metric ledger.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from src.phase3.common import array_identity, identity

RUN_ROOT = ROOT / 'results/phase3-followup-ablation'
OUT = ROOT / 'results/phase3-rigorous-audit-v1/followup-independent-audit.json'
METRICS = ROOT / 'results/phase3-rigorous-audit-v1/trajectory-metrics.csv'
FROZEN_SOURCE_ARCHIVE = ROOT / 'submissions/phase3-final/23I-2568_23I-2581.zip'
SEEDS = tuple(range(1, 12)) + (42,)
DOSES = ((0, 1), (1, 10), (3, 10), (1, 2))
AB_DOSES = ((0, 1), (1, 2))
METHODS = ('FT', 'EI', 'DR', 'DM', 'DC')


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(ok: bool, message: str):
    if not ok:
        raise AssertionError(message)


def metric_matrix(matrix, codes):
    support = {c: sum(matrix[c]) for c in codes}
    active = [c for c in codes if support[c] > 0]
    require(bool(active) and 0 in active, 'No active classes or benign support')
    f1, precision, recall = {}, {}, {}
    for c in active:
        tp = matrix[c][c]
        predicted = sum(matrix[r][c] for r in codes)
        f1[c] = 2 * tp / (support[c] + predicted) if support[c] + predicted else 0.0
        precision[c] = tp / predicted if predicted else 0.0
        recall[c] = tp / support[c]
    total = sum(support.values())
    tn = matrix[0][0]
    fp = sum(matrix[0][1:])
    fn = sum(matrix[r][0] for r in codes if r != 0)
    binary_tp = sum(sum(matrix[r][1:]) for r in codes if r != 0)
    bprec = binary_tp / (binary_tp + fp) if binary_tp + fp else 0.0
    brec = binary_tp / (binary_tp + fn) if binary_tp + fn else 0.0
    bf1 = 2 * binary_tp / (2 * binary_tp + fp + fn) if 2 * binary_tp + fp + fn else 0.0
    return {
        'f1': f1, 'recall': recall,
        'macro_f1': sum(f1.values()) / len(active),
        'macro_precision': sum(precision.values()) / len(active),
        'macro_recall': sum(recall.values()) / len(active),
        'accuracy': sum(matrix[c][c] for c in active) / total,
        'benign_far': 1 - tn / support[0],
        'binary_precision': bprec, 'binary_recall': brec, 'binary_f1': bf1,
    }


def rescore(result, eligible, arrival):
    stages = []
    for t, stage in enumerate(result['stages'], 1):
        matrix = stage['confusion']
        require(len(matrix) == 16 and all(len(row) == 16 for row in matrix), 'Non-16x16 confusion matrix')
        require(all(type(x) is int and x >= 0 for row in matrix for x in row), 'Invalid confusion count')
        stages.append(metric_matrix(matrix, [c for c in eligible if arrival[c] <= t]))
    A = []
    for t in (2, 3, 4):
        codes = [c for c in eligible if arrival[c] == t and c != 4]
        require(bool(codes), f'No eligible acquisition class at stage {t}')
        A.append(sum(stages[t - 1]['f1'][c] for c in codes) / len(codes))
    e2 = stages[1]['recall'][4]
    e3m, e4m = result['stages'][2]['confusion'], result['stages'][3]['confusion']
    e3 = e3m[4][0] / sum(e3m[4])
    e4 = e4m[4][0] / sum(e4m[4])
    final = stages[3]
    return {
        'A': sum(A) / 3, 'e2_recall': e2, 'e3_asr': e3, 'e4_asr': e4,
        'macro_f1': final['macro_f1'], 'macro_precision': final['macro_precision'],
        'macro_recall': final['macro_recall'], 'accuracy': final['accuracy'],
        'benign_far': final['benign_far'], 'binary_precision': final['binary_precision'],
        'binary_recall': final['binary_recall'], 'binary_f1': final['binary_f1'],
        'hulk_recall': stages[3]['recall'][4], 'hulk_asr': e4,
    }


def run_id(path: Path) -> str:
    return path.parent.name


def main():
    completion = json.loads((RUN_ROOT / 'completion-followup.json').read_text(encoding='utf-8'))
    study = json.loads((RUN_ROOT / 'identity.json').read_text(encoding='utf-8'))
    require(completion['status'] == 'complete', 'Follow-up completion status is not complete')
    require(completion['final_test_accessed'] is False, 'Follow-up record says final test was accessed')
    require(study.get('final_test_accessed') is False, 'Study identity does not preserve sealed-test status')

    source_mismatches = []
    for rel, expected in study['source'].items():
        path = ROOT / rel
        if not path.is_file() or sha(path) != expected:
            source_mismatches.append(rel)
    with zipfile.ZipFile(FROZEN_SOURCE_ARCHIVE, 'r') as frozen_archive:
        require(frozen_archive.testzip() is None, 'Frozen-source archive CRC failure')
        inventory_name = next((n for n in frozen_archive.namelist()
                               if n.endswith('/UPLOAD_INVENTORY.json')), None)
        require(inventory_name is not None, 'Frozen-source archive lacks its upload inventory')
        frozen_inventory = json.loads(frozen_archive.read(inventory_name))['files']
        source_snapshot_mismatches = []
        archive_names = frozen_archive.namelist()
        for rel, expected in study['source'].items():
            matches = [n for n in archive_names if n.endswith('/' + rel)]
            if len(matches) != 1:
                source_snapshot_mismatches.append(rel)
                continue
            name = matches[0]
            inventory_rel = name.split('/', 1)[1]
            actual = hashlib.sha256(frozen_archive.read(name)).hexdigest()
            if actual != expected or frozen_inventory.get(inventory_rel) != expected:
                source_snapshot_mismatches.append(rel)
    require(not source_snapshot_mismatches,
            f'{len(source_snapshot_mismatches)} frozen source hashes fail in the archived source snapshot')

    inventory_bad = []
    for rel, expected in completion['files'].items():
        path = RUN_ROOT / rel
        if not path.is_file() or sha(path) != expected:
            inventory_bad.append(rel)
    require(not inventory_bad, f'{len(inventory_bad)} result hashes fail completion inventory')

    paths = sorted(RUN_ROOT.glob('runs/*/result.json'))
    nested = sorted(RUN_ROOT.glob('runs/runs/*/result.json'))
    require(len(paths) == 417, f'Expected 417 unique path records, got {len(paths)}')
    require(len(nested) == 273, f'Expected 273 cross-directory copies, got {len(nested)}')
    by_id = {run_id(p): p for p in paths}
    require(len(by_id) == len(paths), 'Duplicate run IDs in primary result directory')
    copy_mismatches = []
    for p in nested:
        original = by_id.get(run_id(p))
        if original is None or sha(original) != sha(p):
            copy_mismatches.append(str(p.relative_to(ROOT)))
            continue
        for stage in range(1, 5):
            a, b = original.parent / f'E{stage}-weights.npz', p.parent / f'E{stage}-weights.npz'
            if not a.is_file() or not b.is_file() or sha(a) != sha(b):
                copy_mismatches.append(str(b.relative_to(ROOT)))
        for stage in (3, 4):
            a = original.parent / 'oracle-label-repair' / f'E{stage}-weights.npz'
            b = p.parent / 'oracle-label-repair' / f'E{stage}-weights.npz'
            if a.exists() != b.exists() or (a.exists() and sha(a) != sha(b)):
                copy_mismatches.append(str(b.relative_to(ROOT)))
    require(not copy_mismatches, f'{len(copy_mismatches)} cross-directory result/checkpoint copies differ')

    taxonomy = json.loads((ROOT / 'configs/phase3/taxonomy-v1.json').read_text(encoding='utf-8'))
    eligible = [int(x['source_code']) for x in taxonomy['classes'] if x['scoring_eligible']]
    arrival = {int(x['source_code']): int(x['arrival_stage']) for x in taxonomy['classes']}
    results = {}
    block_counts = Counter()
    input_hash_mismatches = []
    checkpoint_bad = []
    verified_stage_weights = 0
    verified_oracle_weights = 0
    oracle_cells = set()
    for p in paths:
        result = json.loads(p.read_text(encoding='utf-8'))
        s = result['settings']
        block = s['block']
        block_counts[block] += 1
        require(result['status'] == 'complete', f'Incomplete result: {p}')
        require(result['final_test_accessed'] is False, f'Final test flag true: {p}')
        require(result['study_identity'] == study['sha256'], f'Study identity mismatch: {p}')
        require(len(result['stages']) == 4, f'Missing stage results: {p}')
        key = (block, s['learner'], s['admission'], int(s['seed']), tuple(s['dose']),
               float(s['q']), float(s['lambda_y']), float(s['lambda_z']))
        require(key not in results, f'Duplicate scientific cell: {key}')
        results[key] = (p, result)
        for stage_i, stage in enumerate(result['stages'], 1):
            wf = p.parent / f'E{stage_i}-weights.npz'
            if not wf.is_file():
                checkpoint_bad.append(str(wf.relative_to(ROOT)))
                continue
            try:
                with np.load(wf, allow_pickle=False) as z:
                    arrays = {k: z[k] for k in z.files}
                slots = arrays.pop('source_codes').tolist()
                model_hash = identity({'slots': slots,
                                       'weights': {k: array_identity(v) for k, v in arrays.items()}})
                if model_hash != stage['model_sha256']:
                    checkpoint_bad.append(str(wf.relative_to(ROOT)))
                else:
                    verified_stage_weights += 1
            except Exception:
                checkpoint_bad.append(str(wf.relative_to(ROOT)))
        oracle = result.get('oracle_label_repair')
        if oracle is not None:
            require(oracle['nonlabel_state_unchanged'] and not oracle['independent_replicate'],
                    f'Oracle continuation is not an exact intervention: {p}')
            require(s['dose'] == [1, 2] and s['learner'] == 'DR' and s['admission'] in ('NONE', 'DC'),
                    f'Unexpected oracle arm: {p}')
            oracle_cells.add((s['learner'], s['admission'], int(s['seed'])))
            for stage in oracle['stages']:
                st = int(stage['stage'])
                wf = p.parent / 'oracle-label-repair' / f'E{st}-weights.npz'
                if not wf.is_file():
                    checkpoint_bad.append(str(wf.relative_to(ROOT)))
                    continue
                try:
                    with np.load(wf, allow_pickle=False) as z:
                        arrays = {k: z[k] for k in z.files}
                    slots = arrays.pop('source_codes').tolist()
                    model_hash = identity({'slots': slots,
                                           'weights': {k: array_identity(v) for k, v in arrays.items()}})
                    if model_hash != stage['model_sha256']:
                        checkpoint_bad.append(str(wf.relative_to(ROOT)))
                    else:
                        verified_oracle_weights += 1
                except Exception:
                    checkpoint_bad.append(str(wf.relative_to(ROOT)))
        rec = result['input_identity']['arrays']
        if not result['input_identity']['whole_component_ownership']:
            input_hash_mismatches.append(str(p.relative_to(ROOT)))

    core = [(k, v) for k, v in results.items() if k[0] == 'core']
    actual_core = {(k[1] if k[2] == 'NONE' else k[2], k[3], k[4]) for k, _ in core}
    expected_core = {(m, seed, dose) for m in METHODS for seed in SEEDS for dose in DOSES}
    require(len(core) == 240 and actual_core == expected_core, 'Primary core cell coverage mismatch')
    dq = [(k, v) for k, v in results.items() if k[0] == 'matched-random']
    require(len(dq) == 24 and {(k[3], k[4]) for k, _ in dq} ==
            {(seed, dose) for seed in SEEDS for dose in AB_DOSES}, 'DQ cell coverage mismatch')
    loss = [(k, v) for k, v in results.items() if k[0] == 'replay-loss']
    expected_loss = {(seed, dose, ly, lz) for seed in SEEDS for dose in AB_DOSES
                     for ly, lz in ((1.0, 0.0), (0.0, 0.1))}
    actual_loss = {(k[3], k[4], k[6], k[7]) for k, _ in loss}
    require(len(loss) == 48 and actual_loss == expected_loss, 'Replay-loss ablation coverage mismatch')
    quota = [(k, v) for k, v in results.items() if k[0] == 'quota']
    expected_quota = {(method, seed, dose, q) for method in ('DM', 'DC') for seed in SEEDS
                       for dose in AB_DOSES for q in (0.5, 0.9)}
    actual_quota = {(k[2], k[3], k[4], k[5]) for k, _ in quota}
    require(len(quota) == 96 and actual_quota == expected_quota, 'Quota ablation coverage mismatch')
    clean = [(k, v) for k, v in results.items() if k[0] == 'clean-confirmation']
    require(len(clean) == 9 and {(k[1], k[3]) for k, _ in clean} ==
            {(m, seed) for m in ('FT', 'EI', 'DR') for seed in (101, 102, 103)},
            'Fresh clean confirmation coverage mismatch')
    require(not checkpoint_bad, f'{len(checkpoint_bad)} result/checkpoint identity failures')
    expected_oracles = {('DR', 'NONE', seed) for seed in SEEDS} | {('DR', 'DC', seed) for seed in SEEDS}
    require(oracle_cells == expected_oracles and verified_oracle_weights == 48,
            'Oracle suffix coverage/checkpoint inventory mismatch')
    require(not input_hash_mismatches, f'{len(input_hash_mismatches)} runs lack component ownership proof')

    # Paired method attack IDs and E1 states across dose for the 240-cell core.
    coremap = {(k[1] if k[2] == 'NONE' else k[2], k[3], k[4]): r for k, (_, r) in core}
    for seed in SEEDS:
        for dose in DOSES:
            poison_sets = {tuple(coremap[(m, seed, dose)]['attack']['poison_ids']) for m in METHODS}
            require(len(poison_sets) == 1, f'Core attack IDs differ for seed={seed}, dose={dose}')
        for method in METHODS:
            hashes = {coremap[(method, seed, dose)]['stages'][0]['model_sha256'] for dose in DOSES}
            require(len(hashes) == 1, f'Core E1 prefix differs across doses for {method}, seed={seed}')

    # Loss and quota controls use the same source data, ownership, attack IDs,
    # training schedule and paired seed/dose as the q=.75 DC/DM reference.
    core_refs = {(k[1] if k[2] == 'NONE' else k[2], k[3], k[4]): r for k, (_, r) in core}
    for k, (_, r) in loss:
        s = r['settings']; ref = core_refs[('DC', k[3], k[4])]
        require(r['input_identity'] == ref['input_identity'], f'Loss ablation input mismatch: {k}')
        require(r['attack']['poison_ids'] == ref['attack']['poison_ids'], f'Loss attack IDs mismatch: {k}')
        require((s['rounds'], s['epochs'], s['learning_rate'], s['q']) ==
                (ref['settings']['rounds'], ref['settings']['epochs'], ref['settings']['learning_rate'], .75),
                f'Loss ablation protocol mismatch: {k}')
    for k, (_, r) in quota:
        method = k[2]; s = r['settings']; ref = core_refs[(method, k[3], k[4])]
        require(r['input_identity'] == ref['input_identity'], f'Quota input mismatch: {k}')
        require(r['attack']['poison_ids'] == ref['attack']['poison_ids'], f'Quota attack IDs mismatch: {k}')
        require((s['rounds'], s['epochs'], s['learning_rate']) ==
                (ref['settings']['rounds'], ref['settings']['epochs'], ref['settings']['learning_rate']),
                f'Quota protocol mismatch: {k}')
    # At each changed quota the DM/DC admissions must remain volume matched.
    quota_by = {(k[3], k[4], k[5], k[2]): r for k, (_, r) in quota}
    for seed in SEEDS:
        for dose in AB_DOSES:
            for q in (.5, .9):
                dm = quota_by[(seed, dose, q, 'DM')]
                dc = quota_by[(seed, dose, q, 'DC')]
                dml = [x for x in dm['ledger'] if x['kind'] == 'admission']
                dcl = [x for x in dc['ledger'] if x['kind'] == 'admission']
                require(len(dml) == len(dcl), f'DM/DC admission stages differ at q={q}, seed={seed}')
                for a, b in zip(dml, dcl):
                    require([x['admitted'] for x in a['clients']] == [x['admitted'] for x in b['clients']],
                            f'DM/DC client quotas differ at q={q}, seed={seed}, dose={dose}')

    # Recompute all listed scalar metrics from integer confusion matrices.
    summary = {}
    by_result_hash = {}
    for p, result in [(v[0], v[1]) for v in results.values()]:
        record = (p, result, rescore(result, eligible, arrival))
        summary[p.relative_to(ROOT).as_posix()] = record
        by_result_hash[sha(p)] = record
    metric_rows = list(csv.DictReader(METRICS.open(newline='', encoding='utf-8')))
    require(len(metric_rows) == 417, 'Trajectory metric ledger is not the 417-run unique matrix')
    metric_bad = []
    row_result = {}
    for row in metric_rows:
        record = by_result_hash.get(row['sha256'])
        if record is None:
            metric_bad.append({'path': row['path'], 'reason': 'missing raw result hash'})
            continue
        path, result, values = record
        row_result[row['sha256']] = (result, values)
        if result['settings']['block'] != row['block']:
            metric_bad.append({'path': row['path'], 'reason': 'block label differs from raw result'})
        if result['settings']['seed'] != int(row['seed']) or result['settings']['dose'][0] / result['settings']['dose'][1] != float(row['dose']):
            metric_bad.append({'path': row['path'], 'reason': 'seed/dose differs from raw result'})
        for field, expected in values.items():
            if field not in row:
                continue
            actual = float(row[field])
            if abs(actual - expected) > 1e-10:
                metric_bad.append({'path': row['path'], 'field': field, 'actual': actual, 'rescored': expected})
    require(not metric_bad, f'{len(metric_bad)} metric-ledger/raw-confusion discrepancies')

    # Recompute paired H and immediate E2 recall change within the full setting key.
    lookup = {}
    for key, (path, result) in results.items():
        s = result['settings']
        lookup[(key[0], s['learner'], s['admission'], int(s['seed']), float(s['q']),
                float(s['lambda_y']), float(s['lambda_z']), tuple(s['dose']))] = (path, result)
    pair_bad = []
    for row in metric_rows:
        paired_result = row_result.get(row['sha256'])
        if paired_result is None:
            continue
        result, values = paired_result
        s = result['settings']; dose = tuple(s['dose'])
        if dose == (0, 1):
            exp_h = exp_d = 0.0
        else:
            clean_key = (s['block'], s['learner'], s['admission'], int(s['seed']), float(s['q']),
                         float(s['lambda_y']), float(s['lambda_z']), (0, 1))
            clean_pair = lookup.get(clean_key)
            if clean_pair is None:
                pair_bad.append({'path': row['path'], 'reason': 'no matched clean twin'})
                continue
            _, clean_result = clean_pair
            cleanv = rescore(clean_result, eligible, arrival)
            exp_h = ((values['e3_asr'] - cleanv['e3_asr']) + (values['e4_asr'] - cleanv['e4_asr'])) / 2
            exp_d = values['e2_recall'] - cleanv['e2_recall']
        if abs(float(row['H']) - exp_h) > 1e-10:
            pair_bad.append({'path': row['path'], 'field': 'H', 'actual': float(row['H']), 'rescored': exp_h})
        if abs(float(row['delta_recall']) - exp_d) > 1e-10:
            pair_bad.append({'path': row['path'], 'field': 'delta_recall', 'actual': float(row['delta_recall']), 'rescored': exp_d})
    require(not pair_bad, f'{len(pair_bad)} paired H/E2 recall discrepancies')

    summary_out = {
        'schema': 'phase3-followup-independent-audit-v1',
        'status': 'passed',
        'study_identity_sha256': study['sha256'],
        'completion_inventory_result_files': len(completion['files']),
        'completion_inventory_hashes_valid': len(inventory_bad) == 0,
        'unique_full_runs': len(paths),
        'duplicate_cross_directory_copies': len(nested),
        'duplicate_results_and_stage_weights_identical': len(copy_mismatches) == 0,
        'unique_run_blocks': dict(sorted(block_counts.items())),
        'cells': {'primary_core': len(core), 'DQ': len(dq), 'replay_loss': len(loss),
                  'quota': len(quota), 'clean_confirmation': len(clean)},
        'matched_attack_ids_and_e1_dose_prefixes': 'passed',
        'loss_and_quota_input_protocol_parity': 'passed',
        'changed_quota_DM_DC_per_client_admission_parity': 'passed',
        'serialized_checkpoint_to_stage_model_hashes': 'passed',
        'unique_stage_checkpoint_model_hashes': verified_stage_weights,
        'paired_oracle_checkpoint_model_hashes': verified_oracle_weights,
        'raw_confusion_to_trajectory_metrics_rows': len(metric_rows),
        'raw_confusion_metric_discrepancies': 0,
        'paired_H_and_immediate_recall_discrepancies': 0,
        'final_test_accessed': False,
        'followup_elapsed_seconds': completion['elapsed_seconds'],
        'followup_elapsed_hours': completion['elapsed_seconds'] / 3600,
        'planned_single_worker_cap_hours': 6,
        'cap_exceeded': completion['elapsed_seconds'] > 6 * 3600,
        'frozen_study_source_files': len(study['source']),
        'frozen_source_archive_files_verified': len(study['source']) - len(source_snapshot_mismatches),
        'current_worktree_source_hash_mismatches': source_mismatches,
        'limitations': [
            'FIFO and class-balanced eviction 96-cell matched block remains unrun.',
            'DG is not supplied by DQ; historical DG belongs to a noncomparable engine.',
            'Development-bank outcomes are not independent held-out confirmation.',
            'Three source files differ from the frozen study identity in the current worktree; the frozen source snapshot is retained in the validated baseline archive.'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary_out, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(summary_out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
