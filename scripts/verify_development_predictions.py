"""Audit published CPU development predictions without features or new inference."""
import argparse
import time
from pathlib import Path

from phase3_delivery.archive_policy import MAX_CHECKPOINT_BYTES
from phase3_delivery.catalog import create_output
from phase3_delivery.development import BASELINE, build_manifest, published
from phase3_delivery.io import read_verified_bytes
from phase3_delivery.prediction_integrity import validate_predictions
from src.phase3.common import ROOT, digest
from src.phase3_v2.checkpoint import strict_json


def verify(output):
    if output.exists():
        raise FileExistsError(output)
    started = time.perf_counter()
    try:
        manifest, sources = build_manifest()
        records, total_bytes = [], 0
        base = ROOT/'results/phase3-cpu-v3/development'
        for row in manifest['rows']:
            run_id = row['run_id']
            metric_path, _ = sources[run_id]
            metric = strict_json(read_verified_bytes(metric_path, row['metric_sha256']).decode('utf-8'))
            receipt = published(base/'receipts'/(run_id+'.json'))
            execution_root = base/'executions'/run_id
            for stage in metric['stages']:
                path = metric_path.parent/f"E{stage['stage']}-predictions.npz"
                expected = receipt['artifact_files'][path.relative_to(execution_root).as_posix()]
                payload = read_verified_bytes(path, expected, max_bytes=MAX_CHECKPOINT_BYTES)
                result = validate_predictions(payload, stage)
                total_bytes += len(payload)
                records.append({'run_id': run_id, 'stage': stage['stage'], 'prediction_file_sha256': expected,
                                'metric_sha256': row['metric_sha256'], **result})
        result = {'schema': 'phase3-published-development-prediction-audit-v1', 'status': 'passed',
                  'published_commit': BASELINE, 'physical_observations': len(manifest['rows']),
                  'aliases_not_reexecuted': len(manifest['aliases']), 'prediction_files_verified': len(records),
                  'prediction_bytes_verified': total_bytes, 'records': records,
                  'elapsed_seconds': time.perf_counter()-started,
                  'validator_sources': {name: digest(ROOT/name) for name in
                                        ('phase3_delivery/prediction_integrity.py', 'phase3_delivery/archive_policy.py',
                                         'phase3_delivery/io.py', 'phase3_delivery/development.py',
                                         'scripts/verify_development_predictions.py')},
                  'scope': 'Git-bound saved prediction structure, bank identity and confusion-column marginals only',
                  'reference_labels_accessed': False, 'features_accessed': False, 'new_inference': False,
                  'final_test_accessed': False, 'final_dispatchable': False}
        create_output(output, result)
        return result
    except Exception as exc:
        create_output(output, {'status': 'failed_attempt_retained', 'exception': type(exc).__name__,
                      'message': str(exc), 'final_test_accessed': False, 'final_dispatchable': False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.output)
    print({key: result[key] for key in ('status', 'physical_observations', 'prediction_files_verified', 'elapsed_seconds')})


if __name__ == '__main__':
    main()
