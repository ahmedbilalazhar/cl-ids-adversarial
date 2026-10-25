"""Assemble a verified full logical trajectory from prefix/suffix transactions.

This packages existing immutable states; it never trains or changes a model.
The resulting collection has explicit recovery lineage and adds no replicate.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np

from src.phase3.common import array_identity, digest, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction, unpack
from src.phase3_v2.data import load_stage, verify_train
from src.phase3_v3.protocol import Settings, code_identity, configure_runtime


def assemble(prefix: Path, suffix: Path, train: Path, expected_manifest: str, output: Path):
    if output.exists():
        raise FileExistsError(output)
    configure_runtime()
    parent, continuation = read_json(prefix/'run.json'), read_json(suffix/'run.json')
    if parent['schema'] != 'phase3-run-v2' or continuation['schema'] != 'phase3-run-v2' or continuation['status'] != 'complete':
        raise ValueError('A valid prefix and completed continuation are required')
    if not continuation['resumed_from'] or parent['execution'] != continuation['execution'] or parent['settings'] != continuation['settings']:
        raise ValueError('Recovery settings/execution lineage differs')
    if parent['execution']['code_identity'] != code_identity():
        raise ValueError('Incompatible current code')
    values = dict(parent['settings'])
    values['dose'] = tuple(values['dose'])
    settings = Settings(**values).validate()
    verify_train(train, settings, expected_manifest)
    if parent['execution']['train_manifest_sha256'] != expected_manifest:
        raise ValueError('Expected training identity differs')
    resume = Path(continuation['resumed_from'])
    if resume.resolve().parent != prefix.resolve():
        raise ValueError('Continuation does not refer to the supplied prefix')
    matches = [i for i, row in enumerate(parent['checkpoints']) if row['file'] == resume.name]
    if len(matches) != 1:
        raise ValueError('Resume boundary not in prefix inventory')
    cutoff = matches[0]+1
    before = parent['checkpoints'][:cutoff]
    after = continuation['checkpoints']
    rows = before+after
    expected = [(s, r) for s in range(1, 5) for r in range(1, settings.rounds+1)]
    if [(r['stage'], r['round']) for r in rows] != expected or continuation['next_cursor'] != [5, 1]:
        raise ValueError('Incomplete or noncontiguous recovery collection')
    start_meta, _, resume_commit = read_transaction(resume, parent['execution'])
    if start_meta['ledger'] != continuation['ledger'][:len(start_meta['ledger'])]:
        raise ValueError('Continuation did not retain the exact prefix ledger')
    copies, last_ledger = [], []
    for source, row in [(prefix, row) for row in before]+[(suffix, row) for row in after]:
        path = source/row['file']
        meta, arrays, marker = read_transaction(path, parent['execution'])
        if marker != row or marker['stage_end'] != (marker['round'] == settings.rounds):
            raise ValueError('Transaction marker/inventory differs')
        unpack(meta, arrays, settings, lambda stage: load_stage(train, stage))
        if meta['ledger'][:len(last_ledger)] != last_ledger:
            raise ValueError('Transaction history diverged')
        last_ledger = meta['ledger']
        copies.extend([path, path.with_suffix('.commit.json')])
    if last_ledger != continuation['ledger']:
        raise ValueError('Final continuation ledger differs')
    for stage in range(1, 5):
        source = prefix if stage <= start_meta['admission_stage'] else suffix
        path = source/f'E{stage}-admission.npz'
        admission = next(r for r in last_ledger if r['kind'] == 'admission' and r['stage'] == stage)
        with np.load(path, allow_pickle=False) as f:
            if set(f.files) != {'ids', 'scores'} | {f'client{i}_accepted_ids' for i in range(5)}:
                raise ValueError('Admission artifact schema differs')
            if array_identity(f['ids']) != admission['score_ids_sha256'] or array_identity(f['scores']) != admission['scores_sha256']:
                raise ValueError('Frozen scores/IDs differ')
            for i in range(5):
                if array_identity(f[f'client{i}_accepted_ids']) != admission['clients'][i]['admitted_ids_sha256']:
                    raise ValueError('Frozen admitted IDs differ')
        copies.append(path)
    # All checks finish before creating the destination. Each payload is copied
    # unchanged and its original commit marker still covers its exact bytes.
    output.mkdir(parents=True)
    for source in copies:
        shutil.copyfile(source, output/source.name)
    for name in ('runtime.json', 'settings.json'):
        shutil.copyfile(suffix/name, output/name)
    collection = {**continuation, 'checkpoints': rows, 'independent_replicate': False,
                  'artifact_kind': 'verified_recovered_trajectory_collection_v1',
                  # This is a complete collection, not a suffix-only execution.
                  # The actual resume path is retained explicitly in lineage.
                  'resumed_from': None, 'elapsed_seconds': None,
                  'timings': parent['timings'][:cutoff]+continuation['timings'],
                  'recovery_lineage': {'prefix_run_sha256': digest(prefix/'run.json'),
                     'suffix_run_sha256': digest(suffix/'run.json'), 'original_resume_path': str(resume.resolve()),
                     'resume_payload_sha256': resume_commit['file_sha256'], 'resume_state_identity': resume_commit['state_identity'],
                     'assembly_script_sha256': digest(Path(__file__)),
                     'prefix_physical_elapsed_seconds': parent['elapsed_seconds'],
                     'suffix_physical_elapsed_seconds': continuation['elapsed_seconds'],
                     'logical_loop_cost': 'unavailable; no fabricated cost or extra replicate'}}
    write_json(output/'run.json', collection)
    return collection


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prefix', type=Path, required=True)
    p.add_argument('--suffix', type=Path, required=True)
    p.add_argument('--train-package', type=Path, required=True)
    p.add_argument('--train-manifest-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assemble(args.prefix, args.suffix, args.train_package, args.train_manifest_sha256, args.output)


if __name__ == '__main__':
    main()
