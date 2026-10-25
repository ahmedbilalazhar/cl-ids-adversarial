"""Fail-closed development/synthetic count import; final results remain sealed."""
import copy
from fractions import Fraction

from scripts.audit_phase3_endpoints import reconstruct, require
from src.phase3.common import digest
from src.phase3_v2.checkpoint import strict_json

FINAL_SEEDS = tuple(range(1, 12))+(42,)


def import_counts(path, expected_sha256, expected_settings, expected_execution,
                  classes, *, kind, run_id, seen_ids, seen_conditions, run_manifest=None):
    """Caller supplies the prospective registry, never identities read from the result.

    Each record is one completed trajectory, not a segment or alias. Mutate the
    caller registry only after every validation succeeds. This API never reads
    features, checkpoints or final outcomes and has no final release switch.
    """
    require(kind in ('synthetic', 'development'), 'Final import is sealed')
    require(isinstance(run_id, str) and bool(run_id) and run_id not in seen_ids, 'Duplicate/invalid run ID')
    require(digest(path) == expected_sha256, 'Metric payload hash mismatch')
    metric = strict_json(path.read_text(encoding='utf-8'))
    require(metric['settings'] == expected_settings, 'Unexpected configuration')
    if metric['schema'] == 'phase3-development-metrics-v3':
        require(run_manifest is not None, 'CPU metric requires its hash-bound run manifest')
        require(digest(run_manifest) == metric['run_manifest_sha256'], 'CPU run manifest hash mismatch')
        run = strict_json(run_manifest.read_text(encoding='utf-8'))
        require(run['status'] == 'complete' and run['resumed_from'] is None,
                'CPU import must be a complete from-start trajectory')
        require(run['settings'] == expected_settings, 'CPU run settings differ')
        execution = run['execution']
    else:
        execution = metric['execution']
    require(execution == expected_execution, 'Unexpected source/protocol/data/runtime binding')
    require(metric['final_test_accessed'] is False, 'Final outcomes are sealed')
    seed = metric['settings']['seed']
    require(type(seed) is int and seed in (FINAL_SEEDS if kind == 'synthetic' else (101, 102, 103)),
            'Wrong seed set')
    # Scientific settings identity excludes irrelevant coefficients. Runtime and
    # retry segmentation cannot manufacture another observation of this condition.
    condition = (seed, expected_execution['settings_identity'], expected_execution['train_manifest_sha256'])
    require(condition not in seen_conditions, 'Alias/retry counted as independent trajectory')
    require(metric['schema'] in ('phase3-development-metrics-v3',
                                'kaggle-qualification-development-metrics-v1'), 'Unknown metric schema')
    translated = copy.deepcopy(metric)
    translated['schema'] = 'phase3-development-metrics-v3'
    result = reconstruct(translated, classes)
    matrix = metric['R_accuracy_by_stage_and_arrival_cohort']
    require(type(matrix) is list and len(matrix) == 4 and all(type(r) is list and len(r) == 4 for r in matrix),
            'Incomplete continual accuracy matrix')
    for t, stage in enumerate(metric['stages']):
        for j in range(4):
            value = matrix[t][j]
            if j > t:
                require(value is None, 'Future accuracy cell must be unavailable')
            else:
                c = stage['cohort_counts'][j]
                require(type(value) in (int, float) and value == float(Fraction(c['correct'], c['total'])),
                        'Accuracy matrix disagrees with cohort counts')
    benign = [b['benign_support'] for b in result['banks']]
    require(len(set(benign)) == 1, 'Fixed benign denominator changed')
    require(len({r['support'] for r in result['hulk']}) == 1, 'Fixed Hulk denominator changed')
    seen_ids.add(run_id)
    seen_conditions.add(condition)
    return result
