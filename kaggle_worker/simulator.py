"""Bounded notebook execution with immutable round transactions and lineage."""
from __future__ import annotations

import time
from dataclasses import asdict

import numpy as np

from src.phase3.common import write_json
from src.phase3.model import ReferenceMLP
from src.phase3.reference import model_identity, snapshot
from src.phase3_v2 import learning

from . import checkpoint
from .backends import backend_for
from .contracts import TimeBudget, parse_settings
from .runtime import synchronize


def execute(settings, loader, execution, output, device='cpu', resume=None,
            stop_after_commits=None, budget_seconds=3600, reserve_seconds=120,
            transition_bound_seconds=600, emulate_accelerator=False):
    settings = parse_settings(asdict(settings))
    if output.exists():
        raise FileExistsError('Outputs are immutable')
    if (stop_after_commits is not None and (type(stop_after_commits) is not int or stop_after_commits < 1)):
        raise ValueError('Invalid commit limit')
    budget = TimeBudget(budget_seconds, reserve_seconds, transition_bound_seconds)
    backend = backend_for(device, emulate_accelerator)
    if resume is not None:
        model, clients, meta, _ = checkpoint.restore(resume, execution, settings, loader, device)
        if meta['stage'] == 5:
            raise ValueError('Completed trajectory has no continuation')
    else:
        model = None
        clients = [learning.client_state(settings, i) for i in range(5)]
        backend.initialize_clients(clients, settings)
        meta = {'schema': 'phase3-round-v2', 'execution': execution, 'slots': [], 'stage': 1,
                'round': 1, 'admission_stage': 0, 'ledger': [], 'commits': 0}
    output.mkdir(parents=True)
    write_json(output/'settings.json', asdict(settings))
    started = time.perf_counter()
    timings, checkpoints = [], []
    upper = transition_bound_seconds
    try:
        while meta['stage'] <= 4:
            if not budget.permits(time.perf_counter()-started, upper):
                break
            synchronize(device)
            round_start = time.perf_counter()
            stage, round_id = meta['stage'], meta['round']
            data = loader(stage)
            components = {'stage': stage, 'round': round_id}
            if meta['admission_stage'] != stage:
                new_codes = [code for code in sorted(set(map(int, data.y))) if code not in meta['slots']]
                meta['slots'].extend(new_codes)
                if not meta['slots'] or meta['slots'][0] != 0:
                    raise ValueError('Benign must be slot zero')
                if model is None:
                    model = ReferenceMLP(len(meta['slots']), settings.seed)
                elif new_codes:
                    model.expand(len(meta['slots']), stage, settings.seed)
                if settings.learner == 'EI':
                    for client in clients:
                        learning.expand_importance(client, model)
                began = time.perf_counter()
                scores = backend.admit(model, data, meta['slots'], set(new_codes), clients, settings, meta['ledger'])
                synchronize(device)
                components['admission_seconds'] = time.perf_counter()-began
                np.savez(output/f'E{stage}-admission.npz', ids=data.ids, scores=scores,
                         **{f'client{i}_accepted_ids': data.ids[c.accepted] for i, c in enumerate(clients)})
                meta['admission_stage'] = stage
            broadcast = snapshot(model)
            before = model_identity(model, meta['slots'])
            began = time.perf_counter()
            updates, rows = [], []
            for i, client in enumerate(clients):
                update, row = backend.train_client(broadcast, model, client, data, meta['slots'], settings, round_id, i)
                updates.append(update)
                rows.append(row)
            synchronize(device)
            components['training_seconds'] = time.perf_counter()-began
            if model_identity(model, meta['slots']) != before:
                raise RuntimeError('Clients mutated broadcast')
            combined, weights = learning.aggregate(broadcast, updates, [len(c.accepted) for c in clients])
            model.load_state_dict(combined)
            meta['ledger'].append({'kind': 'round', 'stage': stage, 'round': round_id,
                                   'broadcast_sha256': before, 'aggregate_sha256': model_identity(model, meta['slots']),
                                   'weights_fp32': weights, 'clients': rows})
            stage_end = round_id == settings.rounds
            if stage_end and settings.learner == 'EI':
                began = time.perf_counter()
                backend.importance(model, clients, data, meta['slots'], settings, meta['ledger'])
                synchronize(device)
                components['importance_seconds'] = time.perf_counter()-began
            meta['commits'] += 1
            meta['stage'], meta['round'] = (stage+1, 1) if stage_end else (stage, round_id+1)
            began = time.perf_counter()
            row = checkpoint.write(output/f'E{stage}-R{round_id}.npz', model, clients, meta, stage, round_id, stage_end, device)
            components['checkpoint_seconds'] = time.perf_counter()-began
            components['whole_transition_seconds'] = time.perf_counter()-round_start
            upper = max(upper, 1.5*components['whole_transition_seconds'])
            timings.append(components)
            checkpoints.append(row)
            print({'stage': stage, 'round': round_id, 'learner': settings.learner,
                   'commits': meta['commits'], 'device': str(device)}, flush=True)
            if stop_after_commits is not None and len(checkpoints) >= stop_after_commits:
                break
    except Exception as exc:
        write_json(output/'failure.json', {'status': 'failed_attempt_retained', 'message': str(exc),
                   'exception': type(exc).__name__, 'execution': execution, 'checkpoints': checkpoints,
                   'timings': timings, 'elapsed_seconds': time.perf_counter()-started})
        raise
    result = {'schema': 'kaggle-qualification-run-v1', 'status': 'complete' if meta['stage'] == 5 else 'stopped_at_committed_boundary',
              'execution': execution, 'settings': asdict(settings), 'checkpoints': checkpoints,
              'ledger': meta['ledger'], 'total_commits': meta['commits'], 'next_cursor': [meta['stage'], meta['round']],
              'resumed_from': None if resume is None else str(resume.resolve()),
              'segment_is_independent_replicate': False, 'trajectory_is_qualification_only': True,
              'final_model_sha256': None if model is None else model_identity(model, meta['slots']),
              'elapsed_seconds': time.perf_counter()-started, 'timings': timings,
              'scheduling_bound_is_guarantee': False, 'final_test_accessed': False, 'final_dispatchable': False}
    write_json(output/'run.json', result)
    return result
