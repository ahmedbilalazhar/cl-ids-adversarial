"""FP32 CUDA candidate; server aggregation and reservoir RNG stay on CPU.

This is an unqualified backend until actual-device checks and development
confirmations pass. CPU emulation is tested against the frozen implementation.
"""
from __future__ import annotations

import copy

import numpy as np
import torch
from torch.nn import functional as F

from src.phase3.common import array_identity, encode_rng, rng, torch_seed
from src.phase3.reference import insert_batch, model_identity, snapshot
from src.phase3_v2.learning import choose_admission, current_order, empirical_importance

from .data import DeviceCache


def finite(values):
    # One host synchronization per validation boundary, retaining every check.
    return bool(torch.stack([torch.isfinite(v).all() for v in values]).all())


def dark_loss(predicted, teachers, widths):
    if not len(widths) or bool(torch.any(widths <= 0) | torch.any(widths > predicted.shape[1])):
        raise ValueError('Invalid observed replay width')
    mask = torch.arange(predicted.shape[1], device=predicted.device)[None, :] < widths[:, None]
    difference = torch.where(mask, predicted-teachers[:, :predicted.shape[1]], 0.)
    return (difference.square().sum(dim=1)/widths).mean()


class Accelerator:
    def __init__(self, device):
        self.device = torch.device(device)
        self.cache = DeviceCache(device)

    def initialize_clients(self, clients, settings):
        if self.device.type == 'cuda':
            for i, client in enumerate(clients):
                generator = torch.Generator(device=self.device).manual_seed(torch_seed(10, settings.seed, i))
                client.cuda_dropout = generator.get_state().numpy().copy()

    def admit(self, model, data, slots, new_codes, clients, settings, ledger):
        local = copy.deepcopy(model).to(self.device).eval()
        x, targets = self.cache.get(data, slots)
        scores = np.empty(len(data.y), dtype=np.float32)
        with torch.no_grad():
            for start in range(0, len(targets), 2048):
                end = start+2048
                scores[start:end] = F.cross_entropy(local(x[start:end]), targets[start:end], reduction='none').cpu().numpy()
        selected, rows = choose_admission(data, scores, new_codes, settings)
        for client, indexes in zip(clients, selected):
            client.accepted = indexes.copy()
        ledger.append({'kind': 'admission', 'stage': data.stage, 'expanded_head_width': len(slots),
                       'scorer_model_sha256': model_identity(model, slots), 'score_ids_sha256': array_identity(data.ids),
                       'scores_sha256': array_identity(scores), 'clients': rows})
        return scores

    def importance(self, model, clients, data, slots, settings, ledger):
        local = copy.deepcopy(model).to(self.device)
        x, targets = self.cache.get(data, slots)
        shared, rows = snapshot(model), []
        for i, client in enumerate(clients):
            if len(client.accepted):
                stream = rng(9, settings.seed, i, data.stage)
                selected = stream.choice(client.accepted, min(1024, len(client.accepted)), replace=False)
                index = torch.from_numpy(selected).to(self.device)
                increments = empirical_importance(local, x[index], targets[index])
                increments = {k: v.cpu() for k, v in increments.items()}
                for name, value in increments.items():
                    client.importance[name].add_(value)
                    if not torch.isfinite(client.importance[name]).all():
                        raise FloatingPointError('Nonfinite accumulated importance')
                client.importance_samples[str(data.stage)] = {
                    'ids': [str(int(v)) for v in data.ids[selected]], 'rng': encode_rng(stream)}
                rows.append({'client': i, 'count': len(selected), 'sample_ids_sha256': array_identity(data.ids[selected]),
                             'increment_sum_by_parameter': {k: float(v.sum()) for k, v in increments.items()}})
            else:
                rows.append({'client': i, 'count': 0, 'status': 'inactive_importance_preserved'})
            client.anchor = {k: v.clone() for k, v in shared.items()}
        ledger.append({'kind': 'importance', 'stage': data.stage,
                       'aggregate_sha256': model_identity(model, slots), 'clients': rows})

    def train_client(self, broadcast, template, client, data, slots, settings, round_id, client_id):
        if not len(client.accepted):
            return None, {'client': client_id, 'admitted': 0, 'optimizer_updates': 0, 'inactive': True}
        local = copy.deepcopy(template)
        local.load_state_dict(broadcast)
        local = local.to(self.device)
        optimizer = torch.optim.Adam(local.parameters(), lr=settings.learning_rate, betas=(.9, .999),
                                     eps=1e-8, weight_decay=0, amsgrad=False, foreach=False, fused=False)
        if optimizer.state:
            raise RuntimeError('Adam did not reset')
        x_all, y_all = self.cache.get(data, slots)
        prior = {k: v.to(self.device) for k, v in client.importance.items()}
        anchors = {k: v.to(self.device) for k, v in client.anchor.items()}
        mapping = {code: slot for slot, code in enumerate(slots)}
        memory = client.replay
        seen = 0 if memory is None else memory['seen']
        updates = current_exposures = replay_exposures = short_replay = 0
        loss_sums = np.zeros(4, dtype=np.float64)
        cuda = self.device.type == 'cuda'
        devices = [self.device.index if self.device.index is not None else torch.cuda.current_device()] if cuda else []
        with torch.random.fork_rng(devices=devices):
            if cuda:
                torch.cuda.set_rng_state(torch.from_numpy(client.cuda_dropout.copy()), self.device)
            else:
                torch.set_rng_state(torch.from_numpy(client.dropout.copy()))
            for epoch in range(1, settings.epochs+1):
                order = current_order(data, client.accepted, settings.seed, client_id, round_id, epoch)
                device_order = torch.from_numpy(order).to(self.device)
                for start in range(0, len(order), 128):
                    current = order[start:start+128]
                    index = device_order[start:start+128]
                    x, y = x_all[index], y_all[index]
                    first_pass = memory is not None and round_id == 1 and epoch == 1
                    teachers = None
                    if first_pass:
                        local.eval()
                        with torch.no_grad():
                            teachers = local(x).cpu().numpy().copy()
                        if not np.isfinite(teachers).all():
                            raise FloatingPointError('Nonfinite pre-update teachers')
                    replay = None
                    if memory is not None and memory['size']:
                        draw = memory['draw'].choice(memory['size'], min(128, memory['size']), replace=False)
                        replay = {k: memory[k][draw].copy() for k in ('x', 'y', 'z', 'width', 'ids')}
                        for rid in replay['ids']:
                            key = str(int(rid))
                            client.replay_counts[key] = client.replay_counts.get(key, 0)+1
                    optimizer.zero_grad(set_to_none=True)
                    local.train()
                    ce = F.cross_entropy(local(x), y)
                    total = ce
                    replay_ce = dark = regularizer = torch.zeros((), dtype=torch.float32, device=self.device)
                    if replay is not None:
                        rx = torch.from_numpy(replay['x']).to(self.device)
                        ry = torch.tensor([mapping[int(v)] for v in replay['y']], dtype=torch.int64, device=self.device)
                        replay_ce = F.cross_entropy(local(rx), ry)
                        local.eval()
                        dark = dark_loss(local(rx), torch.from_numpy(replay['z']).to(self.device),
                                         torch.from_numpy(replay['width'].astype(np.int64)).to(self.device))
                        local.train()
                        total = total+settings.lambda_y*replay_ce+settings.lambda_z*dark
                        short_replay += int(len(current) < 128 and len(replay['y']) == 128)
                    if settings.learner == 'EI':
                        for name, parameter in local.named_parameters():
                            regularizer = regularizer+(prior[name]*(parameter-anchors[name]).square()).sum()
                        regularizer = regularizer*(settings.lambda_E/2)
                        total = total+regularizer
                    if not bool(torch.isfinite(total)):
                        raise FloatingPointError('Nonfinite objective')
                    total.backward()
                    if not finite([p.grad for p in local.parameters() if p.grad is not None]):
                        raise FloatingPointError('Nonfinite gradient')
                    optimizer.step()
                    values = list(local.parameters())+[v for state in optimizer.state.values()
                                                       for v in state.values() if isinstance(v, torch.Tensor)]
                    # Adam step counters may be CPU tensors; validate per device.
                    for device in {v.device for v in values}:
                        if not finite([v for v in values if v.device == device]):
                            raise FloatingPointError('Nonfinite optimizer/weight state')
                    if first_pass:
                        insert_batch(memory, data.x[current], data.y[current], data.ids[current], teachers, len(slots))
                    updates += 1
                    current_exposures += len(current)
                    replay_exposures += 0 if replay is None else len(replay['y'])
                    loss_sums += torch.stack([v.detach() for v in (ce, replay_ce, dark, regularizer)]).cpu().numpy().astype(np.float64)
            if cuda:
                client.cuda_dropout = torch.cuda.get_rng_state(self.device).numpy().copy()
            else:
                client.dropout = torch.get_rng_state().numpy().copy()
        proposals = 0 if memory is None else memory['seen']-seen
        expected = len(client.accepted) if memory is not None and round_id == 1 else 0
        if proposals != expected:
            raise RuntimeError('Reservoir proposals repeated or missing')
        client.updates += updates
        client.current_exposures += current_exposures
        client.replay_exposures += replay_exposures
        # Fixed-order FP32 aggregation remains the frozen CPU operation.
        update = {k: v.detach().cpu().clone() for k, v in local.state_dict().items()}
        return update, {'client': client_id, 'admitted': len(client.accepted), 'inactive': False,
                        'start_model_sha256': model_identity(template, slots), 'adam_reset': True,
                        'optimizer_updates': updates, 'current_exposures': current_exposures,
                        'replay_exposures': replay_exposures, 'proposals': proposals,
                        'full_replay_with_short_current_batches': short_replay,
                        'buffer_occupancy': 0 if memory is None else memory['size'],
                        'mean_losses': (loss_sums/updates).tolist()}
