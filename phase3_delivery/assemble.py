"""Join validated clean/poison count records; final analysis remains sealed."""
import argparse
from fractions import Fraction
from pathlib import Path

from scripts.audit_phase3_endpoints import require
from src.phase3_analysis.statistics import analyze_family, contrast_differences, hulk_endpoints

from .analysis import seed_summary
from .catalog import create_output, verify_catalog
from .import_counts import FINAL_SEEDS


def assemble(catalog):
    require(catalog['status'] == 'passed' and catalog['kind'] in ('development', 'synthetic') and
            catalog['final_dispatchable'] is False, 'Only verified non-final catalogs are accepted')
    if catalog['kind'] == 'development':
        # Development contains pilots and tuning profiles; never pool them as seeds.
        return {'schema': 'phase3-development-count-summary-v1', 'status': 'development_only',
                'rows': [{'run_id': record['row']['run_id'], 'arm': record['row']['arm'],
                          'settings': record['row']['settings'], 'endpoints': record['counts']['endpoints']}
                         for record in catalog['records']],
                'missing_run_ids': catalog['missing_run_ids'], 'confirmatory_analysis_run': False,
                'final_test_accessed': False, 'final_dispatchable': False}
    by_key, seed_profiles, inputs = {}, {}, {}
    bank = None
    for record in catalog['records']:
        row = record['row']
        settings = row['settings']
        key = (row['arm'], Fraction(*settings['dose']), settings['seed'])
        require(key not in by_key, 'Multiple settings/runtime profiles cannot be pooled as one paired seed')
        if bank is None:
            bank = record['counts']['banks']
        require(record['counts']['banks'] == bank, 'Comparisons require one fixed evaluation bank')
        profile = {k: v for k, v in row['execution'].items()
                   if k not in ('settings_identity', 'train_manifest_sha256')}
        seed_profiles.setdefault(key[2], profile)
        require(seed_profiles[key[2]] == profile, 'Mixed execution profiles within a paired seed')
        input_key = (key[1], key[2])
        inputs.setdefault(input_key, row['execution']['train_manifest_sha256'])
        require(inputs[input_key] == row['execution']['train_manifest_sha256'], 'Paired arms use different training data')
        by_key[key] = record
    endpoints, unavailable = {}, []
    for key, record in by_key.items():
        arm, dose, seed = key
        counts = record['counts']
        own = dict(counts['endpoints'])
        clean = by_key.get((arm, Fraction(), seed))
        if clean is None:
            unavailable.append({'run_id': record['row']['run_id'], 'reason': 'matching_clean_reference_missing'})
        else:
            require(counts['banks'] == clean['counts']['banks'], 'Clean/poison banks or fixed denominators differ')
            left, right = record['row'], clean['row']
            # Dose is the only consumed-setting difference within each pair.
            paired = {k: v for k, v in left['settings'].items() if k != 'dose'}
            reference = {k: v for k, v in right['settings'].items() if k != 'dose'}
            require(paired == reference, 'Clean/poison settings differ beyond dose')
            own.update(hulk_endpoints(clean['counts']['hulk'], counts['hulk']))
        endpoints[key] = own
    differences = contrast_differences(endpoints)
    analysis = analyze_family(differences)
    summaries = []
    for arm, dose in sorted({(a, d) for a, d, _ in endpoints}):
        for endpoint in ('acquisition_A', 'benign_FAR_E4', 'H', 'source_recall_change_E2'):
            values = {seed: endpoints.get((arm, dose, seed), {}).get(endpoint) for seed in FINAL_SEEDS}
            summaries.append({'arm': arm, 'dose': [dose.numerator, dose.denominator], 'endpoint': endpoint,
                              **seed_summary(values)})
    return {'schema': 'phase3-synthetic-analysis-validation-v1', 'status': 'synthetic_only',
            'manifest_sha256': catalog['manifest_sha256'], 'physical_trajectories': len(by_key),
            'aliases_counted_as_replicates': 0, 'missing_run_ids': catalog['missing_run_ids'],
            'unavailable_security_endpoints': unavailable, 'summaries': summaries, 'analysis': analysis,
            'final_test_accessed': False, 'final_dispatchable': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    try:
        result = assemble(verify_catalog(args.database, args.manifest_sha256))
    except Exception as exc:
        create_output(args.output, {'status': 'failed_attempt_retained', 'exception': type(exc).__name__,
                                   'message': str(exc), 'final_dispatchable': False})
        raise
    create_output(args.output, result)
    print({'status': result['status'], 'final_dispatchable': False})


if __name__ == '__main__':
    main()
