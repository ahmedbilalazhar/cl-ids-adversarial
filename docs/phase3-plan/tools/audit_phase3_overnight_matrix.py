"""Independent read-only integrity and cell-coverage audit for the CPU extension."""
from __future__ import annotations

import hashlib
import csv
import json
from collections import defaultdict
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'results/phase3-overnight'
REPORT = ROOT / 'submissions/phase3-overnight'
SEEDS = list(range(1, 12)) + [42]
DOSES = [(0, 1), (1, 10), (3, 10), (1, 2)]
METHODS = ('FT', 'EI', 'DR', 'DM', 'DC')


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def method_of(settings):
    return settings['learner'] if settings['admission'] == 'NONE' else settings['admission']


def metrics_from_matrix(confusion, codes):
    support = {c: sum(confusion[c]) for c in codes}
    active = [c for c in codes if support[c] > 0]
    if not active or 0 not in active:
        raise AssertionError('Frozen scoring bank has no active classes or benign support')
    f1, precision, recall = {}, {}, {}
    for c in active:
        tp = confusion[c][c]
        predicted = sum(confusion[r][c] for r in codes)
        f1[c] = 2 * tp / (support[c] + predicted) if support[c] + predicted else 0.0
        precision[c] = tp / predicted if predicted else 0.0
        recall[c] = tp / support[c]
    total = sum(support.values())
    tn = confusion[0][0]
    fp = sum(confusion[0][1:])
    fn = sum(confusion[r][0] for r in codes if r != 0)
    binary_tp = sum(sum(confusion[r][1:]) for r in codes if r != 0)
    binary = {
        'precision': binary_tp / (binary_tp + fp) if binary_tp + fp else 0.0,
        'recall': binary_tp / (binary_tp + fn) if binary_tp + fn else 0.0,
        'f1': 2 * binary_tp / (2 * binary_tp + fp + fn) if 2 * binary_tp + fp + fn else 0.0,
    }
    return {'macro_f1': sum(f1.values()) / len(active),
            'macro_precision': sum(precision.values()) / len(active),
            'macro_recall': sum(recall.values()) / len(active),
            'accuracy': sum(confusion[c][c] for c in active) / total,
            'benign_far': 1 - tn / support[0], 'binary': binary,
            'f1': f1, 'recall': recall}


def rescore(row, eligible, arrival):
    stage_metrics = []
    for stage, record in enumerate(row['stages'], 1):
        codes = [c for c in eligible if arrival[c] <= stage]
        stage_metrics.append(metrics_from_matrix(record['confusion'], codes))
    acquisition = []
    for stage in (2, 3, 4):
        codes = [c for c in eligible if arrival[c] == stage and c != 4]
        acquisition.append(sum(stage_metrics[stage - 1]['f1'][c] for c in codes) / len(codes))
    full = metrics_from_matrix(row['stages'][3]['confusion'], list(range(16)))
    final = stage_metrics[3]
    return {
        'macro_f1': final['macro_f1'], 'macro_precision': final['macro_precision'],
        'macro_recall': final['macro_recall'], 'accuracy': final['accuracy'],
        'benign_far': final['benign_far'], 'binary_precision': final['binary']['precision'],
        'binary_recall': final['binary']['recall'], 'binary_f1': final['binary']['f1'],
        'full_inventory_binary_precision': full['binary']['precision'],
        'full_inventory_binary_recall': full['binary']['recall'],
        'full_inventory_binary_f1': full['binary']['f1'],
        'full_inventory_accuracy': full['accuracy'], 'A': sum(acquisition) / 3,
        'e2_recall': stage_metrics[1]['recall'][4],
        'e3_asr': row['stages'][2]['confusion'][4][0] / sum(row['stages'][2]['confusion'][4]),
        'e4_asr': row['stages'][3]['confusion'][4][0] / sum(row['stages'][3]['confusion'][4]),
        'elapsed_seconds': row['elapsed_seconds'],
    }


def main():
    frozen = read(OUT / 'identity.json')
    completion = read(OUT / 'completion.json')
    checks = {}
    source_bad = [rel for rel, expected in frozen['source'].items()
                  if not (ROOT / rel).is_file() or sha(ROOT / rel) != expected]
    input_bad, absent_inputs = [], []
    for rel, expected in frozen['inputs'].items():
        path = ROOT / rel
        if not path.is_file():
            absent_inputs.append(rel)
        elif sha(path) != expected:
            input_bad.append(rel)
    checks['frozen_source_hashes_match_in_worktree'] = not source_bad
    checks['worktree_source_hash_mismatches'] = source_bad
    checks['present_input_hashes_match'] = not input_bad
    checks['absent_frozen_inputs'] = absent_inputs

    declared_files = completion['files']
    result_paths = sorted((OUT / 'runs').glob('*/result.json'))
    result_hash_bad = []
    records = []
    for path in result_paths:
        rel = path.relative_to(OUT).as_posix()
        if rel not in declared_files or sha(path) != declared_files.get(rel):
            result_hash_bad.append(rel)
        row = read(path)
        settings = row['settings']
        if (row['status'] != 'complete' or row['final_test_accessed'] is not False or
                row['study_identity'] != frozen['sha256']):
            raise AssertionError(f'Invalid run status/identity: {rel}')
        records.append((path, row))
    if set(declared_files) != {p.relative_to(OUT).as_posix() for p in result_paths}:
        result_hash_bad.append('completion inventory does not equal current result-file inventory')
    checks['result_hashes_match'] = not result_hash_bad
    checks['result_hash_mismatches'] = result_hash_bad

    by_block = defaultdict(list)
    for path, row in records:
        by_block[row['settings']['block']].append((path, row))
    checks['run_counts_by_block'] = {k: len(v) for k, v in sorted(by_block.items())}
    if len(by_block['core']) != 240:
        raise AssertionError('Core block does not contain exactly 240 run records')

    core = {}
    for path, row in by_block['core']:
        s = row['settings']
        key = (method_of(s), int(s['seed']), tuple(s['dose']))
        if key in core:
            raise AssertionError(f'Duplicate core cell: {key}')
        if key[0] not in METHODS or key[1] not in SEEDS or key[2] not in DOSES:
            raise AssertionError(f'Unexpected core cell: {key}')
        if s['rounds'] != 12 or s['epochs'] != 1 or float(s['learning_rate']) != .001:
            raise AssertionError(f'Unexpected training budget in {path}')
        if float(s['q']) != 0.75:
            raise AssertionError(f'Unexpected quota in {path}')
        if float(s['lambda_E']) != 100.0 or float(s['lambda_y']) != 1.0 or float(s['lambda_z']) != 0.1:
            raise AssertionError(f'Unexpected replay coefficients in {path}')
        if (not row['input_identity']['whole_component_ownership'] or
                row['attack']['stage'] != 2 or row['attack']['dose'] != s['dose']):
            raise AssertionError(f'Attack or ownership contract mismatch in {path}')
        if len(row['stages']) != 4:
            raise AssertionError(f'Missing stage metric in {path}')
        for stage, stage_row in enumerate(row['stages'], 1):
            matrix = stage_row['confusion']
            if (len(matrix) != 16 or any(len(r) != 16 for r in matrix) or
                    any(type(v) is not int or v < 0 for r in matrix for v in r)):
                raise AssertionError(f'Invalid stage confusion matrix in {path}, E{stage}')
        core[key] = (path, row)
    expected_core = {(m, seed, dose) for m in METHODS for seed in SEEDS for dose in DOSES}
    if set(core) != expected_core:
        raise AssertionError(f'Core design coverage mismatch: missing={expected_core-set(core)}, extra={set(core)-expected_core}')
    checks['core_cells_complete'] = True
    checks['core_unique_cells'] = len(core)
    checks['core_seeds'] = SEEDS
    checks['core_doses'] = [x[0] / x[1] for x in DOSES]
    checks['core_methods'] = list(METHODS)
    checks['core_replay_coefficients'] = {'lambda_y': 1.0, 'lambda_z': 0.1}
    checks['execution_settings'] = {'rounds_per_stage': 12, 'local_epochs': 1,
                                   'batch_size': 128, 'learning_rate': 0.001,
                                   'EI_lambda_E': 100.0, 'q': 0.75}

    for seed in SEEDS:
        for dose in DOSES:
            paired = [core[(m, seed, dose)][1] for m in METHODS]
            poison_ids = {tuple(r['attack']['poison_ids']) for r in paired}
            if len(poison_ids) != 1:
                raise AssertionError(f'Attack ID set differs between paired methods: seed={seed}, dose={dose}')
        for method in METHODS:
            e1_hashes = {core[(method, seed, dose)][1]['stages'][0]['model_sha256'] for dose in DOSES}
            if len(e1_hashes) != 1:
                raise AssertionError(f'E1 checkpoint differs across doses: {method}, seed={seed}')
    checks['paired_attack_ids_and_clean_e1_prefixes'] = 'verified across all core seeds/methods/doses'

    dqs = by_block['matched-random']
    dq_cells = set()
    for path, row in dqs:
        s = row['settings']
        key = (int(s['seed']), tuple(s['dose']))
        if key in dq_cells or key[0] not in SEEDS or key[1] not in ((0, 1), (1, 2)) or float(s['q']) != .75:
            raise AssertionError(f'Invalid/duplicate DQ cell: {key}')
        dq_cells.add(key)
    expected_dq = {(seed, dose) for seed in SEEDS for dose in ((0, 1), (1, 2))}
    if dq_cells != expected_dq:
        raise AssertionError('Matched-random DQ coverage mismatch')
    checks['matched_random_dq_cells_complete'] = len(dq_cells)

    clean = by_block['clean-confirmation']
    clean_cells = {(row['settings']['learner'], row['settings']['seed'])
                   for _, row in clean}
    expected_clean = {(method, seed) for method in ('FT', 'EI', 'DR')
                      for seed in (101, 102, 103)}
    if len(clean) != 9 or clean_cells != expected_clean or read(OUT / 'clean-gates.json')['passed'] is not True:
        raise AssertionError('Fresh clean-gate inventory is incomplete or failed')
    checks['fresh_clean_gate_cells'] = len(clean)
    checks['fresh_clean_gate_passed'] = True

    oracle = [(key, row['oracle_label_repair']) for key, (_, row) in core.items()
              if row['oracle_label_repair'] is not None]
    oracle_keys = {key for key, _ in oracle}
    expected_oracle = {(method, seed, (1, 2)) for method in ('DR', 'DC') for seed in SEEDS}
    if oracle_keys != expected_oracle or any(
            not x['nonlabel_state_unchanged'] or x['independent_replicate'] for _, x in oracle):
        raise AssertionError('Oracle suffix inventory or paired-state contract mismatch')
    checks['oracle_paired_suffixes'] = len(oracle)

    taxonomy = read(ROOT / 'configs/phase3/taxonomy-v1.json')
    eligible = [r['source_code'] for r in taxonomy['classes'] if r['scoring_eligible']]
    arrival = {r['source_code']: r['arrival_stage'] for r in taxonomy['classes']}
    with (REPORT / 'trajectory-metrics.csv').open(newline='', encoding='utf-8') as stream:
        metric_rows = list(csv.DictReader(stream))
    metric_by_key = {}
    rescored = {}
    for record in metric_rows:
        key = (record['block'], record['method'], int(record['seed']), float(record['dose']))
        if key in metric_by_key:
            raise AssertionError(f'Duplicate summary metric row: {key}')
        metric_by_key[key] = record
    if len(metric_rows) != len(records):
        raise AssertionError('Metric summary row count differs from raw result inventory')
    fields = ('macro_f1', 'macro_precision', 'macro_recall', 'accuracy', 'benign_far',
              'binary_precision', 'binary_recall', 'binary_f1',
              'full_inventory_binary_precision', 'full_inventory_binary_recall',
              'full_inventory_binary_f1', 'full_inventory_accuracy', 'A',
              'e2_recall', 'e3_asr', 'e4_asr', 'elapsed_seconds')
    run_for_key = {}
    for path, row in records:
        s = row['settings']
        key = (s['block'], method_of(s), int(s['seed']),
               s['dose'][0] / s['dose'][1])
        rescored[key] = rescore(row, eligible, arrival)
        run_for_key[key] = row
    for key, recomputed in rescored.items():
        stored = metric_by_key[key]
        for field in fields:
            if abs(float(stored[field]) - recomputed[field]) > 1e-10:
                raise AssertionError(f'Raw confusion matrix rescore mismatch: {key}, {field}')
    for key, values in rescored.items():
        block, method, seed, dose = key
        row = run_for_key[key]
        s = row['settings']
        clean_key = (block, method, seed, 0.0)
        if clean_key not in rescored:
            continue
        clean_row = run_for_key[clean_key]['settings']
        if (float(s['q']) != float(clean_row['q']) or
                float(s['lambda_y']) != float(clean_row['lambda_y']) or
                float(s['lambda_z']) != float(clean_row['lambda_z'])):
            continue
        expected_h = .5 * ((values['e3_asr'] - rescored[clean_key]['e3_asr']) +
                           (values['e4_asr'] - rescored[clean_key]['e4_asr']))
        expected_recall = values['e2_recall'] - rescored[clean_key]['e2_recall']
        stored = metric_by_key[key]
        if abs(float(stored['H']) - expected_h) > 1e-10 or abs(float(stored['delta_recall']) - expected_recall) > 1e-10:
            raise AssertionError(f'Paired H/recall effect mismatch: {key}')
    checks['raw_confusion_to_summary_metric_parity'] = len(metric_rows)

    weight_files = {}
    weight_bad = []
    for path, row in records:
        sizes = row['serialized_stage_weight_bytes']
        for name in (f'E{s}-weights.npz' for s in range(1, 5)):
            artifact = path.parent / name
            rel = artifact.relative_to(ROOT).as_posix()
            if not artifact.is_file() or artifact.stat().st_size != sizes.get(name):
                weight_bad.append(rel)
            else:
                weight_files[rel] = {'bytes': artifact.stat().st_size, 'sha256': sha(artifact)}
    if weight_bad:
        raise AssertionError(f'Missing/size-mismatched stage weights: {weight_bad[:5]}')
    checks['stage_weight_files'] = len(weight_files)
    checks['stage_weight_hashes'] = weight_files

    validation = read(REPORT / 'validation.json')
    checks['finalizer_validation_claims'] = {
        'source_hashes_valid': validation['source_hashes_valid'],
        'present_input_hashes_valid': validation['present_input_hashes_valid'],
        'complete_core': validation['complete_core'],
        'trajectory_count': validation['trajectory_count'],
        'oracle_suffixes': validation['oracle_suffixes'],
        'final_test_accessed': validation['final_test_accessed'],
    }
    if (not validation['source_hashes_valid'] or not validation['present_input_hashes_valid'] or
            not validation['complete_core'] or validation['trajectory_count'] != len(records) or
            validation['oracle_suffixes'] != len(oracle) or validation['final_test_accessed']):
        raise AssertionError('Existing independent finalizer validation conflicts with current audit')

    upload_validation = read(REPORT / 'upload-validation.json')
    archive_path = Path(upload_validation['path'])
    if not archive_path.is_absolute():
        archive_path = ROOT / archive_path
    if not archive_path.is_file() or sha(archive_path) != upload_validation['sha256']:
        raise AssertionError('Final submission archive does not match its recorded digest')
    missing_packaged_source, mismatched_packaged_source = [], []
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if archive.testzip() is not None:
            raise AssertionError('Final submission ZIP CRC check failed')
        for rel, expected in frozen['source'].items():
            match = next((name for name in names if name.endswith('/' + rel) or name == rel), None)
            if match is None:
                missing_packaged_source.append(rel)
            elif hashlib.sha256(archive.read(match)).hexdigest() != expected:
                mismatched_packaged_source.append(rel)
    if missing_packaged_source or mismatched_packaged_source:
        raise AssertionError('Frozen experiment source is not intact in the submitted archive')
    checks['frozen_source_hashes_match_in_submission_archive'] = True
    checks['submission_archive_sha256'] = upload_validation['sha256']
    checks['submission_archive_file_count'] = upload_validation['files']

    checks.update({
        'schema': 'phase3-overnight-independent-cell-audit-v1',
        'status': 'complete_frozen_core_dq_oracle_cell_parity_and_packaged_source_identity',
        'study_identity_sha256': frozen['sha256'],
        'completion_elapsed_seconds': completion['elapsed_seconds'],
        'final_test_accessed': False,
        'known_omissions': {
            'replay_loss_cells': 'not_started_runtime_budget',
            'quota_cells': 'not_started_runtime_budget',
            'DG_global_filter_control': 'not_run',
            'FIFO_class_balanced_matched_cells': 'not_run; only one-seed smoke diagnostics',
            'final_test_package_and_scores': 'not_available_and_not_accessed',
        },
        'source_hash_mismatches': source_bad,
        'input_hash_mismatches': input_bad,
    })
    target = ROOT / 'docs/phase3-plan/phase3-overnight-independent-audit.json'
    target.write_text(json.dumps(checks, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in checks.items() if k != 'stage_weight_hashes'}, indent=2))


if __name__ == '__main__':
    main()
