"""Strict, complete, pickle-free round transactions and commit validation."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import torch

from src.phase3.common import (
    array_identity,
    decode_rng,
    digest,
    encode_rng,
    read_json,
    rng,
    save_state,
    state_identity,
    write_json,
)
from src.phase3.model import ReferenceMLP

from .learning import client_state

META_KEYS = {'schema', 'execution', 'slots', 'stage', 'round', 'admission_stage', 'ledger', 'commits', 'clients'}
CLIENT_KEYS = {'updates', 'current_exposures', 'replay_exposures', 'replay_counts', 'importance_samples', 'replay'}
REPLAY_ARRAYS = {'x', 'y', 'ids', 'z', 'width'}


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate checkpoint JSON key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Nonfinite checkpoint JSON')
    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid)


def restore_rng(info):
    if set(info) != {'bit_generator', 'state', 'has_uint32', 'uinteger'} or info['bit_generator'] != 'PCG64' or set(info['state']) != {'state', 'inc'}:
        raise ValueError('Unexpected RNG schema')
    for value in info['state'].values():
        if not isinstance(value, str) or not value.isascii() or not value.isdigit() or str(int(value)) != value or not 0 <= int(value) < 2**128:
            raise ValueError('RNG requires bounded canonical decimal strings')
    if type(info['has_uint32']) is not int or info['has_uint32'] not in (0, 1) or type(info['uinteger']) is not int or not 0 <= info['uinteger'] < 2**32:
        raise ValueError('Invalid PCG64 cache')
    return decode_rng(info)


def pack(model, clients, metadata):
    arrays = {'model.' + k: v.detach().numpy().copy() for k, v in model.state_dict().items()}
    meta = copy.deepcopy(metadata)
    meta['clients'] = []
    for i, client in enumerate(clients):
        prefix = f'client{i}.'
        arrays[prefix + 'accepted'] = client.accepted.copy()
        arrays[prefix + 'dropout'] = client.dropout.copy()
        row = {k: copy.deepcopy(getattr(client, k)) for k in ('updates', 'current_exposures', 'replay_exposures', 'replay_counts', 'importance_samples')}
        row['replay'] = None
        if client.replay is not None:
            row['replay'] = {'size': client.replay['size'], 'seen': client.replay['seen'],
                             'draw': encode_rng(client.replay['draw']), 'insert': encode_rng(client.replay['insert'])}
            if 'order' in client.replay:
                row['replay'].update(policy=client.replay['policy'], next_order=client.replay['next_order'])
                arrays[prefix + 'replay.order'] = client.replay['order'].copy()
            for name in REPLAY_ARRAYS:
                arrays[prefix + 'replay.' + name] = client.replay[name].copy()
        for name, value in client.importance.items():
            arrays[prefix + 'importance.' + name] = value.numpy().copy()
        for name, value in client.anchor.items():
            arrays[prefix + 'anchor.' + name] = value.numpy().copy()
        meta['clients'].append(row)
    return meta, arrays


def unpack(meta, arrays, settings, stage_loader):
    if set(meta) != META_KEYS or meta['schema'] != 'phase3-round-v2' or len(meta['clients']) != 5:
        raise ValueError('Checkpoint metadata schema mismatch')
    slots = meta['slots']
    if not slots or slots[0] != 0 or len(slots) != len(set(slots)) or any(type(v) is not int or not 0 <= v < 16 for v in slots):
        raise ValueError('Invalid output registry')
    stage, round_id = meta['stage'], meta['round']
    if type(stage) is not int or stage not in range(1, 6) or type(round_id) is not int or not 1 <= round_id <= settings.rounds:
        raise ValueError('Illegal next cursor')
    expected_commits = (stage-1)*settings.rounds + round_id-1
    if stage == 5 and round_id != 1 or meta['commits'] != expected_commits or meta['commits'] <= 0:
        raise ValueError('Inconsistent checkpoint cursor/count')
    last_stage = stage if round_id > 1 else stage - 1
    if meta['admission_stage'] != last_stage:
        raise ValueError('Incomplete admission boundary')
    if sum(row['kind'] == 'round' for row in meta['ledger']) != meta['commits'] or sum(row['kind'] == 'admission' for row in meta['ledger']) != last_stage:
        raise ValueError('Incomplete ledger')
    completed_stages = stage - 1
    if sum(row['kind'] == 'importance' for row in meta['ledger']) != (completed_stages if settings.learner == 'EI' else 0):
        raise ValueError('Importance not committed exactly once per completed stage')
    observed = []
    for s in range(1, last_stage + 1):
        observed.extend(code for code in sorted(set(map(int, stage_loader(s).y))) if code not in observed)
    if observed != slots:
        raise ValueError('Registry differs from supplied-label-only history')
    model = ReferenceMLP(len(slots), settings.seed)
    expected = {'model.' + k: v.numpy() for k, v in model.state_dict().items()}
    clients = []
    data = stage_loader(last_stage)
    admission = next(row for row in meta['ledger'] if row['kind'] == 'admission' and row['stage'] == last_stage)
    for i, info in enumerate(meta['clients']):
        if set(info) != CLIENT_KEYS:
            raise ValueError('Unexpected client metadata')
        client = client_state(settings, i)
        prefix = f'client{i}.'
        for field in ('updates', 'current_exposures', 'replay_exposures'):
            if type(info[field]) is not int or info[field] < 0:
                raise ValueError('Invalid client counters')
            setattr(client, field, info[field])
        accepted = arrays[prefix + 'accepted']
        if accepted.dtype != np.dtype('<i8') or accepted.ndim != 1 or np.any(accepted < 0) or np.any(accepted >= len(data.y)) or len(np.unique(accepted)) != len(accepted) or np.any(data.owner[accepted] != i):
            raise ValueError('Invalid locked admission')
        if len(accepted) > 1 and not np.all(accepted[1:] > accepted[:-1]):
            raise ValueError('Admission is not in canonical order')
        client.accepted = accepted.copy()
        if len(accepted) != admission['clients'][i]['admitted'] or array_identity(data.ids[accepted]) != admission['clients'][i]['admitted_ids_sha256']:
            raise ValueError('Locked admission differs from committed ledger')
        for field, ledger_key in (('updates', 'optimizer_updates'), ('current_exposures', 'current_exposures'), ('replay_exposures', 'replay_exposures')):
            if getattr(client, field) != sum(r['clients'][i].get(ledger_key, 0) for r in meta['ledger'] if r['kind'] == 'round'):
                raise ValueError('Client counters differ from round ledger')
        expected[prefix + 'accepted'] = accepted
        expected[prefix + 'dropout'] = client.dropout
        client.dropout = arrays[prefix + 'dropout'].copy()
        torch.Generator().set_state(torch.from_numpy(client.dropout))
        client.replay_counts = info['replay_counts']
        if any(not isinstance(k, str) or not k.isdigit() or str(int(k)) != k or not 0 <= int(k) < 2**64 or type(v) is not int or v <= 0 for k, v in client.replay_counts.items()):
            raise ValueError('Invalid replay exposure record')
        if sum(client.replay_counts.values()) != client.replay_exposures:
            raise ValueError('Replay accounting mismatch')
        client.importance_samples = info['importance_samples']
        if settings.learner == 'DR':
            replay = info['replay']
            policy = getattr(settings, 'eviction_policy', 'reservoir')
            expected_replay_keys = {'size', 'seen', 'draw', 'insert'} if policy == 'reservoir' else {'size', 'seen', 'draw', 'insert', 'policy', 'next_order'}
            if not isinstance(replay, dict) or set(replay) != expected_replay_keys or type(replay['seen']) is not int or replay['seen'] < 0 or replay['size'] != min(500, replay['seen']):
                raise ValueError('Invalid replay occupancy/counter')
            if policy != 'reservoir':
                if replay['policy'] != policy or type(replay['next_order']) is not int or replay['next_order'] < 0:
                    raise ValueError('Eviction policy/counter differs from run settings')
                order_name = prefix + 'replay.order'
                order = arrays[order_name]
                if order.dtype != np.dtype('<u8') or order.shape != (500,):
                    raise ValueError('Invalid replay insertion-order array')
                expected[order_name] = client.replay['order']
                client.replay['order'] = order.copy()
                client.replay['policy'] = policy
                client.replay['next_order'] = replay['next_order']
            for key in REPLAY_ARRAYS:
                name = prefix + 'replay.' + key
                expected[name] = client.replay[key]
                client.replay[key] = arrays[name].copy()
            size = replay['size']
            width = client.replay['width'][:size]
            if np.any(width <= 0) or np.any(width > len(slots)) or not np.isin(client.replay['y'][:size], slots).all() or len(np.unique(client.replay['ids'][:size])) != size:
                raise ValueError('Invalid retained replay tuples')
            for key in ('draw', 'insert'):
                client.replay[key] = restore_rng(replay[key])
            client.replay['size'], client.replay['seen'] = size, replay['seen']
            proposals = sum(r['clients'][i].get('proposals', 0) for r in meta['ledger'] if r['kind'] == 'round')
            if replay['seen'] != proposals:
                raise ValueError('Replay stream count differs from committed proposals')
            if policy == 'reservoir':
                if 'order' in arrays or 'next_order' in replay:
                    raise ValueError('Reservoir checkpoint contains eviction-only state')
            else:
                valid_order = client.replay['order'][:size]
                if replay['next_order'] != proposals or np.any(valid_order >= replay['next_order']) or len(np.unique(valid_order)) != size:
                    raise ValueError('Insertion order differs from committed proposal history')
                if size < 500 and not np.array_equal(valid_order, np.arange(size, dtype='<u8')):
                    raise ValueError('Unfilled buffer insertion order is not canonical')
        elif info['replay'] is not None or client.replay_exposures:
            raise ValueError('Unexpected replay in non-DR state')
        if settings.learner == 'EI':
            for kind in ('importance', 'anchor'):
                for key, value in model.state_dict().items():
                    name = prefix + kind + '.' + key
                    expected[name] = value.numpy()
                    tensor = torch.from_numpy(arrays[name].copy())
                    if kind == 'importance' and torch.any(tensor < 0):
                        raise ValueError('Negative empirical importance')
                    getattr(client, kind)[key] = tensor
            if set(client.importance_samples) != {str(s) for s in range(1, completed_stages+1) if any(
                    row['clients'][i]['count'] for row in meta['ledger'] if row['kind'] == 'importance' and row['stage'] == s)}:
                raise ValueError('Missing importance samples')
            for key, sample in client.importance_samples.items():
                restore_rng(sample['rng'])
                ids = sample['ids']
                if len(ids) != len(set(ids)) or not 0 < len(ids) <= 1024 or any(not v.isdigit() or not 0 <= int(v) < 2**64 for v in ids):
                    raise ValueError('Invalid importance sample IDs')
                source = stage_loader(int(key))
                active = np.flatnonzero(source.owner == i)
                stream = rng(9, settings.seed, i, int(key))
                selected = stream.choice(active, min(1024, len(active)), replace=False)
                if ids != [str(int(v)) for v in source.ids[selected]] or encode_rng(stream) != sample['rng']:
                    raise ValueError('Importance sample/stream differs from the declared supplied-label pool')
        elif client.importance_samples:
            raise ValueError('Unexpected importance state')
        clients.append(client)
    if set(arrays) != set(expected):
        raise ValueError('Missing or extra checkpoint arrays')
    for key, shape_template in expected.items():
        value = arrays[key]
        if value.shape != shape_template.shape or value.dtype != shape_template.dtype or value.dtype.kind == 'O' or (value.dtype.kind == 'f' and not np.isfinite(value).all()):
            raise ValueError('Invalid checkpoint array: ' + key)
    model.load_state_dict({k[6:]: torch.from_numpy(v) for k, v in arrays.items() if k.startswith('model.')}, strict=True)
    if settings.learner == 'EI':
        if any(not torch.equal(c.anchor[k], clients[0].anchor[k]) for c in clients for k in c.anchor):
            raise ValueError('EI clients must share one stage anchor')
        if round_id == 1 and any(not torch.equal(c.anchor[k], value) for c in clients for k, value in model.state_dict().items()):
            raise ValueError('Stage-end EI anchor is not the final shared aggregate')
    return model, clients, {k: v for k, v in meta.items() if k != 'clients'}


def read_transaction(path: Path, execution=None):
    commit = read_json(path.with_suffix('.commit.json'))
    if set(commit) != {'schema', 'stage', 'round', 'stage_end', 'file', 'file_sha256', 'state_identity', 'head_width', 'source_codes_in_slot_order'} or commit['schema'] != 'phase3-commit-v2' or commit['file'] != path.name:
        raise ValueError('Invalid commit marker schema')
    if digest(path) != commit['file_sha256']:
        raise ValueError('Checkpoint payload hash mismatch')
    with np.load(path, allow_pickle=False) as f:
        if len(f.files) != len(set(f.files)) or 'metadata' not in f.files or f['metadata'].ndim != 0 or f['metadata'].dtype.kind != 'U':
            raise ValueError('Invalid transaction envelope')
        meta = strict_json(str(f['metadata']))
        arrays = {k: f[k].copy() for k in f.files if k != 'metadata'}
    if state_identity(meta, arrays) != commit['state_identity']:
        raise ValueError('Checkpoint logical hash mismatch')
    if execution is not None and meta['execution'] != execution:
        raise ValueError('Checkpoint code/data/protocol/runtime/settings identity mismatch')
    if commit['head_width'] != len(meta['slots']) or commit['source_codes_in_slot_order'] != meta['slots']:
        raise ValueError('Commit/registry mismatch')
    return meta, arrays, commit


def write_transaction(path, model, clients, meta, stage, round_id, stage_end):
    metadata, arrays = pack(model, clients, meta)
    if path.exists() or path.with_suffix('.commit.json').exists():
        raise FileExistsError('Refusing checkpoint overwrite')
    save_state(path, metadata, arrays)
    row = {'schema': 'phase3-commit-v2', 'stage': stage, 'round': round_id, 'stage_end': stage_end,
           'file': path.name, 'file_sha256': digest(path), 'state_identity': state_identity(metadata, arrays),
           'head_width': len(meta['slots']), 'source_codes_in_slot_order': meta['slots'].copy()}
    write_json(path.with_suffix('.commit.json'), row)
    return row
