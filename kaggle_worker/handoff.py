"""Read-only verification of downloaded notebook outputs; no model execution."""
from __future__ import annotations

import argparse
import hashlib
import io
import zipfile
from pathlib import Path

import numpy as np

from src.phase3.common import digest, identity, state_identity, write_json
from src.phase3_v2.checkpoint import strict_json

from .artifacts import HistoryValidator, references, valid_name, validate_receipt
from .contracts import SourceBindings, validate_procedure, validate_runtime
from .runtime import FROZEN, source_files


def inspect(path, expected_sha256):
    if digest(path) != expected_sha256:
        raise ValueError('Downloaded archive digest differs from the notebook export')
    result = {'schema': 'kaggle-handoff-integrity-v1', 'status': 'passed', 'archive_sha256': expected_sha256,
              'jobs': [], 'final_dispatchable': False, 'actual_GPU_release_qualified': False,
              'scope': 'Archive/receipt/checkpoint integrity and lineage only. No inference, data reconstruction or statistical analysis.'}
    with zipfile.ZipFile(path) as archive:
        files = [i for i in archive.infolist() if not i.is_dir()]
        names = [i.filename for i in files]
        name_set = set(names)
        if len(names) != len(set(names)) or any(not valid_name(n) for n in names):
            raise ValueError('Unsafe or duplicate downloaded output path')
        if sum(i.file_size for i in files) > 4*1024**3:
            raise ValueError('Unexpected output bundle size')
        def json_file(name):
            return strict_json(archive.read(name).decode('utf-8'))
        acceptance = json_file('synthetic-acceptance.json')
        bindings = SourceBindings.local()
        validate_runtime(acceptance['runtime'], bindings)
        if (acceptance['status'] != 'passed' or acceptance['runtime']['frozen_code_identity'] != FROZEN or
                acceptance['runtime']['worker_source_identity'] != identity(source_files()) or
                acceptance['final_dispatchable'] is not False or not acceptance.get('checks') or
                any(row['status'] != 'passed' for row in acceptance['checks'])):
            raise ValueError('Fixture evidence is missing, failed or incompatible')
        result['actual_CUDA_fixtures_passed'] = acceptance['actual_CUDA_fixtures_passed']
        if acceptance['actual_CUDA_fixtures_passed'] is not (acceptance['runtime']['device_type'] == 'cuda'):
            raise ValueError('Fixture device claim differs from runtime')
        result['runtime'] = acceptance['runtime']
        for name in sorted(n for n in names if n.endswith('/job.json')):
            prefix = name[:-len('job.json')]
            procedure = json_file(name)
            execution = procedure['execution']
            settings = validate_procedure(procedure, bindings)
            if procedure['runtime'] != acceptance['runtime']:
                raise ValueError('Job execution is incompatible with returned fixture/runtime evidence')
            receipts = sorted(n for n in names if n.startswith(prefix+'invocation-') and n.endswith('.json'))
            actual_refs = references([name[len(prefix):] for name in names if name.startswith(prefix)], settings.rounds)
            if not receipts:
                result['jobs'].append({'job': prefix, 'status': 'no_receipt_retained_attempt',
                                       'unverified_commit_markers': [ref.marker for ref in actual_refs],
                                       'independent_seeds_added': 0})
                continue
            latest = json_file(receipts[-1])
            recorded = validate_receipt(latest, execution, settings.rounds)
            if tuple(ref.payload for ref in recorded) != tuple(ref.payload for ref in actual_refs[:len(recorded)]):
                raise ValueError('Receipt is not the actual committed prefix')
            segment_files = {name[len(prefix):] for name in names if name.startswith(prefix+'segment-')}
            if latest['status'] == 'complete' and (len(recorded) != len(actual_refs) or segment_files != set(latest['files'])):
                raise ValueError('Complete receipt ignores unexpected committed artifacts')
            for relative, expected in latest['files'].items():
                if not valid_name(relative) or prefix+relative not in name_set:
                    raise ValueError('Missing/unsafe receipt path')
                if hashlib.sha256(archive.read(prefix+relative)).hexdigest() != expected:
                    raise ValueError('Receipt payload mismatch: '+relative)
            history = HistoryValidator(settings.rounds, settings.learner)
            for ref, row in zip(recorded, latest['checkpoints']):
                relative = row['path']
                if not valid_name(relative) or relative not in latest['files']:
                    raise ValueError('Checkpoint absent from receipt hashes')
                payload = archive.read(prefix+relative)
                marker_name = prefix+relative[:-4]+'.commit.json'
                marker = json_file(marker_name)
                if marker != {k: v for k, v in row.items() if k != 'path'}:
                    raise ValueError('Receipt and commit marker differ')
                if hashlib.sha256(payload).hexdigest() != marker['file_sha256']:
                    raise ValueError('Checkpoint file digest differs')
                with np.load(io.BytesIO(payload), allow_pickle=False) as arrays:
                    meta = strict_json(str(arrays['metadata']))
                    values = {k: arrays[k] for k in arrays.files if k != 'metadata'}
                    if len(arrays.files) != len(set(arrays.files)) or state_identity(meta, values) != marker['state_identity']:
                        raise ValueError('Checkpoint typed-state identity differs')
                if meta['execution'] != execution:
                    raise ValueError('Checkpoint execution differs')
                history.accept(meta, marker, ref)
            extra_refs = actual_refs[len(recorded):]
            result['jobs'].append({'job': prefix,
                                   'status': 'unreceipted_commits_retained' if extra_refs else latest['status'],
                                   'receipt_status': latest['status'], 'commits_verified': history.count,
                                   'unverified_commit_markers': [ref.marker for ref in extra_refs],
                                   'seed': settings.seed, 'learner': settings.learner,
                                   'qualification_trajectories': 1, 'independent_final_seeds_added': 0})
        for name in names:
            if name.startswith('command-') and name.endswith('.json'):
                command = json_file(name)
                log = name[:-5]+'.log'
                if log not in names or hashlib.sha256(archive.read(log)).hexdigest() != command['log_sha256']:
                    raise ValueError('Command log missing or corrupted')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--archive-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = inspect(args.archive, args.archive_sha256)
    write_json(args.output, result)
    print({'status': result['status'], 'jobs': len(result['jobs']), 'final_dispatchable': False})


if __name__ == '__main__':
    main()
