"""Export reviewable analysis acceptance from fabricated count fixtures only."""
import argparse
import copy
import tempfile
from pathlib import Path

from phase3_delivery.assemble import assemble
from phase3_delivery.catalog import create_output, validate_manifest
from phase3_delivery.import_counts import import_counts
from src.phase3.common import ROOT, digest, identity, read_json
from tests.test_delivery_catalog import fixture_row, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        with tempfile.TemporaryDirectory(prefix='fabricated-counts-') as directory:
            folder = Path(directory)
            rows, records, ids, conditions = [], [], set(), set()
            classes = read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes']
            for arm in ('FT', 'EI', 'DR', 'DM', 'DC'):
                for dose in ((0, 1), (1, 10), (3, 10), (1, 2)):
                    for seed in list(range(1, 12))+[42]:
                        run_id = f'{arm}-{dose[0]}-{dose[1]}-{seed}'
                        row, path = fixture_row(folder, run_id, arm, seed, dose)
                        result = import_counts(path, row['metric_sha256'], row['settings'], row['execution'],
                                               classes, kind='synthetic', run_id=run_id,
                                               seen_ids=ids, seen_conditions=conditions)
                        rows.append(row)
                        records.append({'row': row, 'counts': result})
            spec, _, sha = manifest(folder, rows, {'alias': rows[0]['run_id']})
            validate_manifest(spec)
            catalog = {'status': 'passed', 'kind': 'synthetic', 'manifest_sha256': sha,
                       'records': records, 'aliases': spec['aliases'], 'missing_run_ids': [],
                       'final_test_accessed': False, 'final_dispatchable': False}
            complete = assemble(catalog)
            assert len(complete['analysis']['rows']) == 29
            assert all(r['available_pairs'] == 12 and r['raw_p']['value'] == 1
                       for r in complete['analysis']['rows'])
            create_output(args.output/'analysis-complete.json', complete)
            partial = copy.deepcopy(catalog)
            partial['records'] = [r for r in records if r['row']['run_id'] != 'FT-0-1-42']
            partial['missing_run_ids'] = ['FT-0-1-42']
            missing = assemble(partial)
            unavailable = [r for r in missing['analysis']['rows'] if r['raw_p'] is None]
            assert len(unavailable) == 12 and all(r['missing_seeds'] == [42] for r in unavailable)
            create_output(args.output/'analysis-missing-clean.json', missing)
            create_output(args.output/'acceptance.json', {'status': 'passed', 'fabricated_trajectories': 240,
                          'complete_contrasts': 29, 'missing_clean_unavailable_contrasts': len(unavailable),
                          'delivery_source_identity': identity({p.name: digest(p) for p in sorted((ROOT/'phase3_delivery').glob('*.py'))}),
                          'test_fixture_source_sha256': digest(ROOT/'tests/test_delivery_catalog.py'),
                          'model_executions': 0, 'final_test_accessed': False, 'final_dispatchable': False,
                          'scope': 'Fabricated integer counts; independent reviewable analysis artifact, not a model study'})
    except Exception as exc:
        create_output(args.output/'failure.json', {'status': 'failed_attempt_retained',
                      'exception': type(exc).__name__, 'message': str(exc)})
        raise
    print({'status': 'passed', 'fabricated_trajectories': 240, 'complete_contrasts': 29})


if __name__ == '__main__':
    main()
