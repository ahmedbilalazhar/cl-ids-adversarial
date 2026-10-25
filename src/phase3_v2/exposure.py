"""Evaluator-only joins of immutable reference annotations to learner ledgers."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from src.phase3.common import digest, read_json, write_json

from .checkpoint import read_transaction


def exposure(package: Path, run_dir: Path, output: Path):
    if output.exists():
        raise FileExistsError(output)
    preparation = read_json(package / 'preparation.json')
    run = read_json(run_dir / 'run.json')
    if run['execution']['train_manifest_sha256'] != preparation['train_manifest_sha256']:
        raise ValueError('Exposure reference does not match learner package')
    for name, sha in preparation['files'].items():
        if digest(package / name) != sha:
            raise ValueError('Audit package hash mismatch')
    poison, references, records = set(), {}, []
    for stage in range(1, 5):
        with np.load(package / f'audit/E{stage}-reference.npz', allow_pickle=False) as f:
            ids, clean, flags = f['ids'], f['reference_y'], f['poison']
        poison.update(str(int(r)) for r in ids[flags])
        references.update({str(int(r)): int(y) for r, y in zip(ids, clean)})
    for row in run['checkpoints']:
        if not row['stage_end']:
            continue
        meta, arrays, _ = read_transaction(run_dir / row['file'], run['execution'])
        stage = row['stage']
        with np.load(package / f'audit/E{stage}-reference.npz', allow_pickle=False) as f:
            ids, owners = f['ids'], f['owner']
        admission = next(r for r in meta['ledger'] if r['kind'] == 'admission' and r['stage'] == stage)
        for i, client in enumerate(meta['clients']):
            accepted = arrays[f'client{i}.accepted']
            selected = {str(int(r)) for r in ids[accepted]}
            local = {str(int(r)) for r in ids[owners == i]}
            admitted_poison = len(selected & poison)
            rejected_poison = len((local-selected) & poison)
            memory_ids = set()
            if client['replay'] is not None:
                memory_ids = {str(int(r)) for r in arrays[f'client{i}.replay.ids'][:client['replay']['size']]}
            samples = client['importance_samples'].get(str(stage), {}).get('ids', [])
            records.append({'stage': stage, 'client': i, 'raw': len(local), 'admitted': len(selected),
                            'honest_admitted': len(selected)-admitted_poison, 'poison_admitted': admitted_poison,
                            'honest_rejected': len(local-selected)-rejected_poison, 'poison_rejected': rejected_poison,
                            'poison_current_exposures_this_stage': admitted_poison*run['settings']['rounds']*run['settings']['epochs'],
                            'cumulative_poison_replay_exposures': sum(n for rid, n in client['replay_counts'].items() if rid in poison),
                            'retained_poison_records': len(memory_ids & poison), 'importance_sample_poison': len(set(samples) & poison),
                            'importance_sample_reference_counts': {str(code): sum(references[rid] == code for rid in samples) for code in sorted({references[rid] for rid in samples})},
                            'admission_ledger_matches': admission['clients'][i]['admitted'] == len(selected)})
    result = {'status': 'evaluator_only_exposure', 'run_manifest_sha256': digest(run_dir / 'run.json'),
              'package_preparation_sha256': digest(package / 'preparation.json'), 'poison_ids_count': len(poison),
              'records': records, 'clean_dose_poison_ratios': None if not poison else 'derive from integer cells; no zero-denominator success claim'}
    write_json(output, result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    exposure(a.package, a.run, a.output)


if __name__ == '__main__':
    main()
