"""Import the published CPU delivery using Git-bound receipts, without inference."""
import argparse
import hashlib
import subprocess
from pathlib import Path

from scripts.audit_phase3_endpoints import require
from src.phase3.common import ROOT, digest, identity, read_json

from .assemble import assemble
from .catalog import create_output, initialize, ingest, validate_manifest, verify_catalog

BASELINE = 'b77a7bbf11c1e4ae7cc06f79e5d7d7d452dbf932'


def published(path):
    relative = path.relative_to(ROOT).as_posix()
    payload = subprocess.check_output(['git', 'show', BASELINE+':'+relative], cwd=ROOT)
    require(hashlib.sha256(payload).hexdigest() == digest(path), 'Published evidence changed: '+relative)
    return read_json(path)


def build_manifest():
    base = ROOT/'results/phase3-cpu-v3/development'
    completion = published(base/'completion.json')
    rows, aliases, sources = [], {}, {}
    for row in completion['rows']:
        require(row['status'] == 'valid', 'Unexpected invalid delivery row')
        receipt = published(base/'receipts'/(row['row_id']+'.json'))
        require(receipt['row'] == row, 'Receipt differs from completion ledger')
        if row['alias_of'] is not None:
            aliases[row['row_id']] = row['alias_of']
            continue
        metric, run = receipt_path(row['metrics']), receipt_path(row['run'])/'run.json'
        execution_root = base/'executions'/row['row_id']
        require(metric.is_relative_to(execution_root) and run.is_relative_to(execution_root),
                'Receipt paths escape their physical execution')
        for path in (metric, run):
            relative = path.relative_to(execution_root).as_posix()
            require(receipt['artifact_files'][relative] == digest(path), 'Receipt payload hash mismatch')
        run_value = read_json(run)
        settings = row['settings']
        rows.append({'run_id': row['row_id'], 'arm': settings['learner'] if settings['admission'] == 'NONE'
                     else settings['admission'], 'settings': settings, 'execution': run_value['execution'],
                     'metric_sha256': digest(metric), 'run_manifest_sha256': digest(run)})
        sources[row['row_id']] = (metric, run)
    manifest = {'schema': 'phase3-count-registry-v1', 'kind': 'development',
                'taxonomy_sha256': digest(ROOT/'configs/phase3/taxonomy-v1.json'),
                'final_dispatchable': False, 'rows': rows, 'aliases': aliases}
    validate_manifest(manifest)
    return manifest, sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.database.exists():
        raise FileExistsError('Use fresh catalog and evidence destinations')
    args.output.mkdir(parents=True)
    try:
        manifest, sources = build_manifest()
        manifest_path = args.output/'import-manifest.json'
        create_output(manifest_path, manifest)
        sha = digest(manifest_path)
        initialize(args.database, manifest_path, sha)
        for row in manifest['rows']:
            metric, run = sources[row['run_id']]
            ingest(args.database, sha, row['run_id'], metric, run)
        for alias, parent in manifest['aliases'].items():
            metric, run = sources[parent]
            ingest(args.database, sha, alias, metric, run)
        verified = verify_catalog(args.database, sha)
        create_output(args.output/'catalog-verification.json', verified)
        create_output(args.output/'development-endpoints.json', assemble(verified))
        create_output(args.output/'acceptance.json', {'status': 'passed', 'baseline_commit': BASELINE,
                      'manifest_sha256': sha, 'physical_observations': len(verified['records']),
                      'aliases': len(verified['aliases']), 'attempts': len(verified['attempts']),
                      'unreferenced_objects': verified['unreferenced_objects'],
                      'delivery_source_identity': identity({p.name: digest(p) for p in sorted((ROOT/'phase3_delivery').glob('*.py'))}),
                      'models_executed': 0, 'final_test_accessed': False, 'final_dispatchable': False})
    except Exception as exc:
        create_output(args.output/'failure.json', {'status': 'failed_attempt_retained',
                      'exception': type(exc).__name__, 'message': str(exc)})
        raise
    print({'status': 'passed', 'physical_observations': len(verified['records']),
           'aliases': len(verified['aliases']), 'models_executed': 0})


def receipt_path(value):
    """Relocate historical Windows receipt paths without trusting their prefix."""
    normalized = '/'+str(value).replace('\\', '/').lstrip('/')
    marker = '/results/phase3-cpu-v3/development/'
    require(normalized.count(marker) == 1, 'Not a CPU development artifact path')
    suffix = normalized.split(marker, 1)[1]
    base = ROOT/'results/phase3-cpu-v3/development'
    result = (base/suffix).resolve()
    require(result.is_relative_to(base), 'Receipt path escapes the development tree')
    return result


if __name__ == '__main__':
    main()
