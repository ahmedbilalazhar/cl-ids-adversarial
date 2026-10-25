"""Sequential FP32 learner semantics with explicit retained client state."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

import numpy as np
import torch
from torch.nn import functional as F

from src.phase3.common import array_identity, encode_rng, rng, torch_seed
from src.phase3.reference import insert_batch, model_identity, new_client, snapshot

from .data import StageInput
from .protocol import Settings


@dataclass
class ClientState:
    accepted: np.ndarray
    dropout: np.ndarray
    replay: dict | None = None
    importance: dict[str, torch.Tensor] = field(default_factory=dict)
    anchor: dict[str, torch.Tensor] = field(default_factory=dict)
    importance_samples: dict = field(default_factory=dict)
    replay_counts: dict[str, int] = field(default_factory=dict)
    updates: int = 0
    current_exposures: int = 0
    replay_exposures: int = 0


def client_state(settings, client):
    generator = torch.Generator().manual_seed(torch_seed(10, settings.seed, client))
    replay = None
    if settings.learner == 'DR':
        replay = new_client(settings.seed, client)
        for key in ('dropout', 'accepted', 'updates', 'current_exposures', 'replay_exposures'):
            replay.pop(key)
    return ClientState(np.empty(0, dtype='<i8'), generator.get_state().numpy().copy(), replay)


def expand_importance(client, model):
    """Old-coordinate state survives; new coordinates have no prior penalty."""
    for name, value in model.named_parameters():
        prior = client.importance.get(name)
        anchor = client.anchor.get(name)
        updated = torch.zeros_like(value)
        anchored = value.detach().clone()
        if prior is not None:
            region = tuple(slice(0, size) for size in prior.shape)
            updated[region] = prior
            anchored[region] = anchor
        client.importance[name], client.anchor[name] = updated, anchored


def importance_reference(model, x, targets):
    """Independent single-record autograd implementation, used only for acceptance."""
    parameters = dict(model.named_parameters())
    totals = {name: torch.zeros_like(p) for name, p in parameters.items()}
    mode = model.training
    model.eval()
    try:
        for record, label in zip(x, targets):
            log_probability = model(record.unsqueeze(0)).log_softmax(dim=1)[0, label]
            gradients = torch.autograd.grad(log_probability, tuple(parameters.values()))
            for (name, _), gradient in zip(parameters.items(), gradients):
                totals[name].add_(gradient.detach() * gradient.detach())
        return {name: value / len(targets) for name, value in totals.items()}
    finally:
        model.train(mode)


def empirical_importance(model, x, targets, chunk=64):
    """torch.func per-example gradients, squared before FP32 averaging."""
    if len(targets) == 0:
        raise ValueError('An active importance sample cannot be empty')
    parameters = {k: v.detach() for k, v in model.named_parameters()}
    buffers = dict(model.named_buffers())
    totals = {name: torch.zeros_like(p) for name, p in parameters.items()}
    mode = model.training
    model.eval()

    def single_loss(params, record, label):
        logits = torch.func.functional_call(model, (params, buffers), (record.unsqueeze(0),))
        return F.cross_entropy(logits, label.unsqueeze(0))

    differentiate = torch.func.vmap(torch.func.grad(single_loss), in_dims=(None, 0, 0), randomness='error')
    try:
        for start in range(0, len(targets), chunk):
            gradients = differentiate(parameters, x[start:start+chunk], targets[start:start+chunk])
            for name, gradient in gradients.items():
                totals[name].add_(gradient.square().sum(dim=0))
        result = {name: value / len(targets) for name, value in totals.items()}
        if any(not torch.isfinite(v).all() for v in result.values()):
            raise FloatingPointError('Nonfinite empirical importance')
        return result
    finally:
        model.train(mode)


def commit_importance(model, clients, data, slots, settings, ledger):
    targets = data.targets(slots)
    shared = snapshot(model)
    rows = []
    for i, client in enumerate(clients):
        if len(client.accepted):
            stream = rng(9, settings.seed, i, data.stage)
            selected = stream.choice(client.accepted, min(1024, len(client.accepted)), replace=False)
            increments = empirical_importance(model, torch.from_numpy(data.x[selected].copy()),
                                             torch.from_numpy(targets[selected]))
            for name, value in increments.items():
                client.importance[name].add_(value)
                if not torch.isfinite(client.importance[name]).all():
                    raise FloatingPointError('Nonfinite accumulated importance')
            sample = {'ids': [str(int(v)) for v in data.ids[selected]], 'rng': encode_rng(stream)}
            client.importance_samples[str(data.stage)] = sample
            row = {'client': i, 'count': len(selected), 'sample_ids_sha256': array_identity(data.ids[selected]),
                   'increment_sum_by_parameter': {k: float(v.sum()) for k, v in increments.items()}}
        else:
            row = {'client': i, 'count': 0, 'status': 'inactive_importance_preserved'}
        # Every client receives the same final aggregate anchor, including inactive.
        client.anchor = {k: v.clone() for k, v in shared.items()}
        rows.append(row)
    ledger.append({'kind': 'importance', 'stage': data.stage, 'aggregate_sha256': model_identity(model, slots), 'clients': rows})


def quotas(labels, new_codes, stage):
    result = []
    for code in np.unique(labels):
        n = int(np.count_nonzero(labels == code))
        protected = stage == 1 or int(code) in new_codes or n < 20
        result.append({'source_code': int(code), 'raw': n, 'admitted': n if protected else (3*n+3)//4,
                       'protected': protected})
    return result


def choose_admission(data, scores, new_codes, settings):
    if scores.shape != (len(data.y),) or not np.isfinite(scores).all():
        raise FloatingPointError('Invalid admission scores')
    accepted, rows = [], []
    for i in range(5):
        indexes = np.flatnonzero(data.owner == i)
        cells = quotas(data.y[indexes], new_codes, data.stage)
        if settings.admission == 'NONE' or data.stage == 1:
            chosen = indexes
        elif settings.admission == 'DM':
            rank = np.lexsort((data.ids[indexes], scores[indexes]))
            chosen = indexes[rank[:sum(c['admitted'] for c in cells)]]
        else:
            groups = []
            priority = rng(11, settings.seed, i, data.stage)
            for cell in cells:
                group = indexes[data.y[indexes] == cell['source_code']]
                # Base order is canonical ID order by StageInput validation.
                rank = priority.permutation(len(group)) if settings.admission == 'DQ' else np.lexsort((data.ids[group], scores[group]))
                groups.extend(group[rank[:cell['admitted']]].tolist())
            chosen = np.asarray(groups, dtype=np.int64)
        chosen = np.sort(chosen).astype('<i8')
        accepted.append(chosen)
        rows.append({'client': i, 'raw': len(indexes), 'admitted': len(chosen), 'quotas': cells,
                     'admitted_ids_sha256': array_identity(data.ids[chosen])})
    if not any(len(a) for a in accepted):
        raise ValueError('All-inactive stage')
    return accepted, rows


def admit(model, data, slots, new_codes, clients, settings, ledger):
    model.eval()
    targets = data.targets(slots)
    scores = np.empty(len(data.y), dtype=np.float32)
    with torch.no_grad():
        for start in range(0, len(targets), 2048):
            end = start + 2048
            scores[start:end] = F.cross_entropy(model(torch.from_numpy(data.x[start:end].copy())),
                                               torch.from_numpy(targets[start:end]), reduction='none').numpy()
    selected, rows = choose_admission(data, scores, new_codes, settings)
    for client, indexes in zip(clients, selected):
        client.accepted = indexes.copy()
    ledger.append({'kind': 'admission', 'stage': data.stage, 'expanded_head_width': len(slots),
                   'scorer_model_sha256': model_identity(model, slots), 'score_ids_sha256': array_identity(data.ids),
                   'scores_sha256': array_identity(scores), 'clients': rows})
    return scores


def dark_loss(predicted, teachers, widths):
    if len(widths) == 0 or torch.any(widths <= 0) or torch.any(widths > predicted.shape[1]):
        raise ValueError('Invalid observed replay width')
    mask = torch.arange(predicted.shape[1])[None, :] < widths[:, None]
    difference = torch.where(mask, predicted - teachers[:, :predicted.shape[1]], 0.)
    return (difference.square().sum(dim=1) / widths).mean()


def penalty(model, client, coefficient):
    value = torch.zeros((), dtype=torch.float32)
    for name, parameter in model.named_parameters():
        value = value + (client.importance[name] * (parameter - client.anchor[name]).square()).sum()
    return value * (coefficient / 2)


def current_order(data, accepted, seed, client, round_id, epoch):
    raw = np.flatnonzero(data.owner == client)
    permutation = rng(6, seed, client, data.stage, round_id, epoch).permutation(raw)
    mask = np.zeros(len(data.y), dtype=bool)
    mask[accepted] = True
    return permutation[mask[permutation]]


def train_client(broadcast, template, client: ClientState, data: StageInput, slots, settings: Settings, round_id, client_id):
    if not len(client.accepted):
        return None, {'client': client_id, 'admitted': 0, 'optimizer_updates': 0, 'inactive': True}
    local = copy.deepcopy(template)
    local.load_state_dict(broadcast)
    optimizer = torch.optim.Adam(local.parameters(), lr=settings.learning_rate, betas=(.9, .999), eps=1e-8,
                                 weight_decay=0, amsgrad=False, foreach=False, fused=False)
    if optimizer.state:
        raise RuntimeError('Adam did not reset')
    targets = data.targets(slots)
    mapping = {code: slot for slot, code in enumerate(slots)}
    memory = client.replay
    seen = 0 if memory is None else memory['seen']
    updates = current_exposures = replay_exposures = short_replay = 0
    loss_sums = np.zeros(4, dtype=np.float64)
    with torch.random.fork_rng(devices=[]):
        torch.set_rng_state(torch.from_numpy(client.dropout.copy()))
        for epoch in range(1, settings.epochs + 1):
            order = current_order(data, client.accepted, settings.seed, client_id, round_id, epoch)
            for start in range(0, len(order), 128):
                current = order[start:start+128]
                x, y = torch.from_numpy(data.x[current].copy()), torch.from_numpy(targets[current])
                first_pass = memory is not None and round_id == 1 and epoch == 1
                teachers = None
                if first_pass:
                    local.eval()
                    with torch.no_grad():
                        teachers = local(x).numpy().copy()
                    if not np.isfinite(teachers).all():
                        raise FloatingPointError('Nonfinite pre-update teachers')
                replay = None
                if memory is not None and memory['size']:
                    draw = memory['draw'].choice(memory['size'], min(128, memory['size']), replace=False)
                    replay = {k: memory[k][draw].copy() for k in ('x', 'y', 'z', 'width', 'ids')}
                    for rid in replay['ids']:
                        key = str(int(rid))
                        client.replay_counts[key] = client.replay_counts.get(key, 0) + 1
                optimizer.zero_grad(set_to_none=True)
                local.train()
                ce = F.cross_entropy(local(x), y)
                total = ce
                replay_ce = dark = regularizer = torch.zeros((), dtype=torch.float32)
                if replay is not None:
                    rx = torch.from_numpy(replay['x'])
                    ry = torch.tensor([mapping[int(v)] for v in replay['y']], dtype=torch.int64)
                    replay_ce = F.cross_entropy(local(rx), ry)
                    local.eval()
                    dark = dark_loss(local(rx), torch.from_numpy(replay['z']), torch.from_numpy(replay['width'].astype(np.int64)))
                    local.train()
                    total = total + settings.lambda_y * replay_ce + settings.lambda_z * dark
                    short_replay += int(len(current) < 128 and len(replay['y']) == 128)
                if settings.learner == 'EI':
                    regularizer = penalty(local, client, settings.lambda_E)
                    total = total + regularizer
                if not torch.isfinite(total):
                    raise FloatingPointError('Nonfinite objective')
                total.backward()
                if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in local.parameters()):
                    raise FloatingPointError('Nonfinite gradient')
                optimizer.step()
                if any(not torch.isfinite(p).all() for p in local.parameters()) or any(
                    not torch.isfinite(v).all() for state in optimizer.state.values() for v in state.values() if isinstance(v, torch.Tensor)):
                    raise FloatingPointError('Nonfinite optimizer/weight state')
                if first_pass:
                    insert_batch(memory, data.x[current], data.y[current], data.ids[current], teachers, len(slots))
                updates += 1
                current_exposures += len(current)
                replay_exposures += 0 if replay is None else len(replay['y'])
                loss_sums += [float(v.detach()) for v in (ce, replay_ce, dark, regularizer)]
        client.dropout = torch.get_rng_state().numpy().copy()
    proposals = 0 if memory is None else memory['seen'] - seen
    expected = len(client.accepted) if memory is not None and round_id == 1 else 0
    if proposals != expected:
        raise RuntimeError('Reservoir proposals repeated or missing')
    client.updates += updates
    client.current_exposures += current_exposures
    client.replay_exposures += replay_exposures
    return snapshot(local), {'client': client_id, 'admitted': len(client.accepted), 'inactive': False,
            'start_model_sha256': model_identity(template, slots), 'adam_reset': True,
            'optimizer_updates': updates, 'current_exposures': current_exposures, 'replay_exposures': replay_exposures,
            'proposals': proposals, 'full_replay_with_short_current_batches': short_replay,
            'buffer_occupancy': 0 if memory is None else memory['size'], 'mean_losses': (loss_sums/updates).tolist()}


def aggregate(broadcast, updates, counts):
    total = sum(counts)
    if not total or any((update is None) != (n == 0) for update, n in zip(updates, counts)):
        raise ValueError('Invalid active-client aggregation')
    combined = {key: torch.zeros_like(value) for key, value in broadcast.items()}
    weights = []
    for count, update in zip(counts, updates):
        weight = float(np.float32(count / total))
        weights.append(weight)
        if count:
            for key, value in combined.items():
                value.add_(update[key] * weight)
    if any(not torch.isfinite(v).all() for v in combined.values()):
        raise FloatingPointError('Nonfinite aggregate')
    return combined, weights
