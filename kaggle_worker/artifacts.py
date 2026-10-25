"""Shared artifact indexing, history and receipt rules; no training or inference."""
from __future__ import annotations

import re
import math
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from src.phase3.common import digest

from .contracts import exact_keys, sha256_value

MARKER_KEYS = {'schema', 'stage', 'round', 'stage_end', 'file', 'file_sha256', 'state_identity',
               'head_width', 'source_codes_in_slot_order'}
RECEIPT_KEYS = {'schema', 'status', 'execution', 'commits_verified', 'trajectory_count',
                'segment_count_is_not_replicate_count', 'runtime_identity', 'whole_invocation_seconds',
                'stage_cache_loads', 'whole_invocation_excludes_imports', 'resources',
                'recovered_completion_receipt', 'checkpoints', 'files', 'final_test_accessed', 'final_dispatchable'}


def valid_name(name):
    if type(name) is not str or not name or '\x00' in name:
        return False
    path = PurePosixPath(name)
    return not (path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name or str(path) != name)


@dataclass(frozen=True, slots=True)
class CheckpointRef:
    marker: str
    stage: int
    round: int
    ordinal: int

    @property
    def payload(self):
        return self.marker[:-len('.commit.json')]+'.npz'


def reference(name, rounds):
    if type(rounds) is not int or rounds < 1:
        raise ValueError('Expected a positive integer round budget')
    match = re.fullmatch(r'segment-[0-9]{4,}/E([1-4])-R([1-9][0-9]*)\.commit\.json', name) if valid_name(name) else None
    if match is None:
        raise ValueError('Invalid committed artifact path')
    stage, row = map(int, match.groups())
    if not 1 <= row <= rounds:
        raise ValueError('Commit round exceeds declared budget')
    return CheckpointRef(name, stage, row, (stage-1)*rounds+row)


def references(names, rounds, complete=False):
    rows = {}
    for name in names:
        if name.startswith('segment-') and name.endswith('.commit.json'):
            ref = reference(name, rounds)
            if ref.ordinal in rows:
                raise ValueError('Duplicate committed boundary; preserve and investigate the branch')
            rows[ref.ordinal] = ref
    if sorted(rows) != list(range(1, len(rows)+1)) or complete and len(rows) != 4*rounds:
        raise ValueError('Missing committed prefix or incomplete collection')
    return tuple(rows[index] for index in sorted(rows))


def discover(root, rounds, complete=False):
    root = Path(root).resolve()
    names = []
    for path in root.glob('segment-*/*.commit.json'):
        if not path.resolve().is_relative_to(root):
            raise ValueError('Checkpoint escapes its job directory')
        names.append(path.relative_to(root).as_posix())
    return references(names, rounds, complete)


class HistoryValidator:
    def __init__(self, rounds, learner=None):
        self.rounds, self.learner, self.previous, self.count = rounds, learner, [], 0

    def accept(self, metadata, marker, ref):
        exact_keys(marker, MARKER_KEYS, 'commit marker')
        ended = ref.round == self.rounds
        cursor = (ref.stage+1, 1) if ended else (ref.stage, ref.round+1)
        if (marker['schema'] != 'phase3-commit-v2' or
                any(type(marker[key]) is not int for key in ('stage', 'round', 'head_width')) or
                type(marker['stage_end']) is not bool or
                (marker['stage'], marker['round'], marker['stage_end']) != (ref.stage, ref.round, ended) or
                marker['file'] != PurePosixPath(ref.payload).name):
            raise ValueError('Commit marker differs from canonical location')
        slots = metadata['slots']
        if (type(slots) is not list or not slots or slots[0] != 0 or len(set(slots)) != len(slots) or
                any(type(code) is not int or not 0 <= code < 16 for code in slots) or
                marker['head_width'] != len(slots) or marker['source_codes_in_slot_order'] != slots):
            raise ValueError('Commit registry differs')
        if (metadata.get('schema') != 'phase3-round-v2' or
                any(type(metadata[key]) is not int for key in ('commits', 'stage', 'round', 'admission_stage')) or
                metadata['commits'] != ref.ordinal or ref.ordinal != self.count+1 or
                (metadata['stage'], metadata['round']) != cursor or metadata['admission_stage'] != ref.stage):
            raise ValueError('Committed cursor/count differs')
        ledger = metadata['ledger']
        if (type(ledger) is not list or any(type(row) is not dict or row.get('kind') not in
                {'round', 'admission', 'importance'} for row in ledger) or ledger[:len(self.previous)] != self.previous or
                sum(row['kind'] == 'round' for row in ledger) != ref.ordinal or
                sum(row['kind'] == 'admission' for row in ledger) != ref.stage):
            raise ValueError('Committed history diverged or is incomplete')
        if self.learner is not None:
            expected = metadata['stage']-1 if self.learner == 'EI' else 0
            if sum(row['kind'] == 'importance' for row in ledger) != expected:
                raise ValueError('Importance transition count differs')
        self.previous, self.count = ledger, ref.ordinal


def validate_receipt(receipt, execution, rounds):
    exact_keys(receipt, RECEIPT_KEYS, 'receipt')
    if (receipt['schema'] != 'kaggle-worker-receipt-v1' or receipt['execution'] != execution or
            receipt['runtime_identity'] != execution['runtime_identity'] or
            receipt['status'] not in ('complete', 'stopped_at_committed_boundary') or
            receipt['final_dispatchable'] is not False or receipt['final_test_accessed'] is not False or
            type(receipt['trajectory_count']) is not int or receipt['trajectory_count'] != 1 or
            receipt['segment_count_is_not_replicate_count'] is not True or
            type(receipt['recovered_completion_receipt']) is not bool):
        raise ValueError('Receipt execution/status/replicate contract differs')
    count = receipt['commits_verified']
    if (type(count) is not int or not 0 <= count <= 4*rounds or type(receipt['checkpoints']) is not list or
            count != len(receipt['checkpoints']) or type(receipt['files']) is not dict or
            (receipt['status'] == 'complete') != (count == 4*rounds)):
        raise ValueError('Receipt completion count differs')
    if (type(receipt['whole_invocation_seconds']) not in (int, float) or
            not math.isfinite(receipt['whole_invocation_seconds']) or receipt['whole_invocation_seconds'] < 0 or
            type(receipt['stage_cache_loads']) is not int or not 0 <= receipt['stage_cache_loads'] <= 4 or
            receipt['whole_invocation_excludes_imports'] is not True or type(receipt['resources']) is not dict):
        raise ValueError('Receipt timing/resource metadata differs')
    for name, expected in receipt['files'].items():
        if not valid_name(name) or not name.startswith('segment-'):
            raise ValueError('Unsafe receipt artifact path')
        sha256_value(expected, 'receipt file')
    refs = []
    for count, row in enumerate(receipt['checkpoints'], 1):
        exact_keys(row, MARKER_KEYS | {'path'}, 'receipt checkpoint')
        name = row['path']
        if not valid_name(name) or not name.endswith('.npz'):
            raise ValueError('Invalid receipt checkpoint path')
        ref = reference(name[:-4]+'.commit.json', rounds)
        if ref.ordinal != count or name not in receipt['files'] or ref.marker not in receipt['files']:
            raise ValueError('Unbound or noncontiguous receipt checkpoint')
        if receipt['files'][name] != row['file_sha256']:
            raise ValueError('Receipt checkpoint file hashes differ')
        sha256_value(row['state_identity'], 'typed state')
        refs.append(ref)
    return tuple(refs)


def verify_local_files(root, files, exact=False):
    root = Path(root).resolve()
    if exact:
        actual = {path.relative_to(root).as_posix() for path in root.glob('segment-*/*') if path.is_file()}
        if set(files) != actual:
            raise ValueError('Completed receipt artifact inventory changed')
    for name, expected in files.items():
        if not valid_name(name):
            raise ValueError('Unsafe receipt artifact path')
        path = (root/name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or digest(path) != expected:
            raise ValueError('Completed receipt payload changed: '+name)
