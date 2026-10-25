"""CPU-compatible state plus separately validated CUDA dropout byte streams."""
from __future__ import annotations

import numpy as np
import torch

from src.phase3.common import digest, save_state, state_identity, write_json
from src.phase3_v2.checkpoint import pack, read_transaction, unpack


def write(path, model, clients, meta, stage, round_id, stage_end, device):
    metadata, arrays = pack(model, clients, meta)
    if torch.device(device).type == 'cuda':
        for i, client in enumerate(clients):
            arrays[f'cuda.client{i}.dropout'] = client.cuda_dropout.copy()
    if path.exists() or path.with_suffix('.commit.json').exists():
        raise FileExistsError('Refusing checkpoint overwrite')
    save_state(path, metadata, arrays)
    row = {'schema': 'phase3-commit-v2', 'stage': stage, 'round': round_id, 'stage_end': stage_end,
           'file': path.name, 'file_sha256': digest(path), 'state_identity': state_identity(metadata, arrays),
           'head_width': len(meta['slots']), 'source_codes_in_slot_order': meta['slots'].copy()}
    write_json(path.with_suffix('.commit.json'), row)
    return row


def restore(path, execution, settings, loader, device):
    metadata, arrays, marker = read_transaction(path, execution)
    extras = {k: arrays.pop(k) for k in list(arrays) if k.startswith('cuda.')}
    cuda = torch.device(device).type == 'cuda'
    expected = {f'cuda.client{i}.dropout' for i in range(5)} if cuda else set()
    if set(extras) != expected:
        raise ValueError('CUDA RNG inventory differs from backend')
    model, clients, meta = unpack(metadata, arrays, settings, loader)
    for i, client in enumerate(clients):
        if cuda:
            value = extras[f'cuda.client{i}.dropout']
            generator = torch.Generator(device=device)
            if value.dtype != np.uint8 or value.shape != generator.get_state().numpy().shape:
                raise ValueError('Invalid CUDA RNG byte state')
            generator.set_state(torch.from_numpy(value.copy()))
            client.cuda_dropout = value.copy()
    previous = (meta['stage']-1, settings.rounds) if meta['round'] == 1 else (meta['stage'], meta['round']-1)
    if (marker['stage'], marker['round']) != previous or marker['stage_end'] != (previous[1] == settings.rounds):
        raise ValueError('Commit marker is not the previous completed boundary')
    return model, clients, meta, marker
