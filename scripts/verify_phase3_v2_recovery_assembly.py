"""Check full recovered collections and independent development predictions."""
from __future__ import annotations

from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_v2.evaluate import evaluate

from .assemble_phase3_v2_recovery import assemble


def main():
    base = ROOT/'results/phase3-cpu-v2'
    train = ROOT/'data/processed/phase3-cpu-v2/s101-p000/train'
    dev = ROOT/'data/processed/phase3-reference74-v1/development'
    expected = digest(train/'manifest.json')
    checks = []
    sources = {'DR': base/'integration/DC', 'EI': base/'development/executions/pilot-13-EI-s101-r3e1/train'}
    for learner, prefix in sources.items():
        suffix = base/f'full-data-{learner}-recovered'
        collection = base/f'full-data-{learner}-recovery-collection'
        manifest = assemble(prefix, suffix, train, expected, collection)
        result = evaluate(dev, collection, base/f'full-data-{learner}-recovery-evaluation')
        original_path = base/'integration/DC-evaluation' if learner == 'DR' else prefix.parent/'evaluation'
        original = read_json(original_path/'metrics.json')
        checks.append({'learner': learner, 'check': 'all_stage_counts_and_metrics', 'passed': result['stages'] == original['stages']})
        for key in ('A', 'equal_stage_ACC4', 'BWT4', 'forgetting4', 'R_accuracy_by_stage_and_arrival_cohort'):
            checks.append({'learner': learner, 'check': key, 'passed': result[key] == original[key]})
        for stage in range(1, 5):
            name = f'E{stage}-predictions.npz'
            # NPZ writer timestamps are not model content; compare typed arrays.
            import numpy as np
            with np.load(original_path/name, allow_pickle=False) as a, np.load(base/f'full-data-{learner}-recovery-evaluation'/name, allow_pickle=False) as b:
                equal = set(a.files) == set(b.files) and all(np.array_equal(a[k], b[k]) and a[k].dtype == b[k].dtype for k in a.files)
            checks.append({'learner': learner, 'check': name, 'passed': equal})
        checks.append({'learner': learner, 'check': 'complete_inventory_and_explicit_lineage',
                       'passed': len(manifest['checkpoints']) == 12 and not manifest['independent_replicate'] and
                       manifest['recovery_lineage']['original_resume_path'] == str((prefix/'E1-R2.npz').resolve())})
    for label, prefix, suffix, sha in (
        ('mismatched_learner', sources['DR'], base/'full-data-EI-recovered', expected),
        ('wrong_expected_manifest', sources['DR'], base/'full-data-DR-recovered', '0'*64),
    ):
        output = base/f'rejected-recovery-assembly-{label}'
        rejected = False
        try:
            assemble(prefix, suffix, train, sha, output)
        except ValueError:
            rejected = not output.exists()
        checks.append({'check': label, 'passed': rejected})
    passed = all(c['passed'] for c in checks)
    write_json(base/'recovery-assembly-acceptance.json', {'status': 'passed' if passed else 'failed', 'checks': checks,
               'independent_replicates_added': 0, 'scope': 'Existing exact transactions packaged into complete collections; independent full development prediction arrays and counts compared, no final inference',
               'assembly_script_sha256': digest(ROOT/'scripts/assemble_phase3_v2_recovery.py'),
               'verification_script_sha256': digest(ROOT/'scripts/verify_phase3_v2_recovery_assembly.py')})
    if not passed:
        raise AssertionError('Recovery collection verification failed')
    print({'status': 'passed', 'checks': len(checks)})


if __name__ == '__main__':
    main()
