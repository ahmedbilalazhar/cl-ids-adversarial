"""Versioned CPU-only training and exact committed-round recovery."""
from __future__ import annotations

import argparse
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from src.phase3.common import ROOT, canonical, digest, identity, read_json, write_json
from src.phase3.model import ReferenceMLP
from src.phase3.reference import model_identity, snapshot

from .checkpoint import read_transaction, unpack, write_transaction
from .data import load_stage, verify_train
from .learning import (
    admit,
    aggregate,
    client_state,
    commit_importance,
    expand_importance,
    train_client,
)
from .protocol import PROTOCOL, Settings, code_identity, configure_runtime


class Simulator:
    def __init__(self, settings, stage_loader, execution):
        self.settings = settings.validate()
        self.stage_loader = stage_loader
        self.execution = execution

    def execute(self, output: Path, resume=None, stop_after_commits=None):
        if output.exists():
            raise FileExistsError('Outputs are immutable; choose a fresh directory')
        if stop_after_commits is not None and stop_after_commits <= 0:
            raise ValueError('Commit limit must be positive')
        settings = self.settings
        if resume is not None:
            metadata, arrays, marker = read_transaction(Path(resume), self.execution)
            model, clients, meta = unpack(metadata, arrays, settings, self.stage_loader)
            previous = (meta['stage']-1, settings.rounds) if meta['round'] == 1 else (meta['stage'], meta['round']-1)
            if (marker['stage'], marker['round']) != previous or marker['stage_end'] != (previous[1] == settings.rounds):
                raise ValueError('Commit marker is not the declared previous boundary')
            if meta['stage'] == 5:
                raise ValueError('Completed trajectory has no continuation')
        else:
            model = None
            clients = [client_state(settings, i) for i in range(5)]
            meta = {'schema': 'phase3-round-v2', 'execution': self.execution, 'slots': [], 'stage': 1,
                    'round': 1, 'admission_stage': 0, 'ledger': [], 'commits': 0}
        output.mkdir(parents=True)
        write_json(output / 'settings.json', asdict(settings))
        timings, checkpoints = [], []
        started = time.perf_counter()
        try:
            while meta['stage'] <= 4:
                stage, round_id = meta['stage'], meta['round']
                data = self.stage_loader(stage)
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
                            expand_importance(client, model)
                    began = time.perf_counter()
                    scores = admit(model, data, meta['slots'], set(new_codes), clients, settings, meta['ledger'])
                    components['admission_seconds'] = time.perf_counter()-began
                    np.savez(output / f'E{stage}-admission.npz', ids=data.ids, scores=scores,
                             **{f'client{i}_accepted_ids': data.ids[c.accepted] for i, c in enumerate(clients)})
                    meta['admission_stage'] = stage
                broadcast = snapshot(model)
                before = model_identity(model, meta['slots'])
                updates, rows = [], []
                began = time.perf_counter()
                for i, client in enumerate(clients):
                    update, row = train_client(broadcast, model, client, data, meta['slots'], settings, round_id, i)
                    updates.append(update)
                    rows.append(row)
                components['training_seconds'] = time.perf_counter()-began
                if model_identity(model, meta['slots']) != before:
                    raise RuntimeError('Clients mutated immutable broadcast')
                combined, weights = aggregate(broadcast, updates, [len(c.accepted) for c in clients])
                model.load_state_dict(combined)
                shared = model_identity(model, meta['slots'])
                meta['ledger'].append({'kind': 'round', 'stage': stage, 'round': round_id,
                                       'broadcast_sha256': before, 'aggregate_sha256': shared,
                                       'weights_fp32': weights, 'clients': rows})
                stage_end = round_id == settings.rounds
                if stage_end and settings.learner == 'EI':
                    began = time.perf_counter()
                    commit_importance(model, clients, data, meta['slots'], settings, meta['ledger'])
                    components['importance_seconds'] = time.perf_counter()-began
                meta['commits'] += 1
                meta['stage'], meta['round'] = (stage+1, 1) if stage_end else (stage, round_id+1)
                began = time.perf_counter()
                row = write_transaction(output / f'E{stage}-R{round_id}.npz', model, clients, meta, stage, round_id, stage_end)
                components['checkpoint_seconds'] = time.perf_counter()-began
                timings.append(components)
                checkpoints.append(row)
                print(canonical({'stage': stage, 'round': round_id, 'learner': settings.learner, 'elapsed_seconds': time.perf_counter()-started}), flush=True)
                if stop_after_commits is not None and len(checkpoints) >= stop_after_commits:
                    break
        except Exception as exc:
            write_json(output / 'failure.json', {'status': 'failed_uncommitted_round_rolled_back',
                       'exception': type(exc).__name__, 'message': str(exc), 'execution': self.execution,
                       'committed_checkpoints': checkpoints, 'timings': timings, 'elapsed_seconds': time.perf_counter()-started,
                       'failure_disposition': 'investigate software/input/infrastructure versus scientific numerical instability; no metric imputation'})
            raise
        result = {'schema': 'phase3-run-v2', 'status': 'complete' if meta['stage'] == 5 else 'stopped_at_committed_boundary',
                  'execution': self.execution, 'settings': asdict(settings), 'checkpoints': checkpoints, 'ledger': meta['ledger'],
                  'resumed_from': None if resume is None else str(Path(resume).resolve()), 'independent_replicate': resume is None,
                  'final_test_accessed': False, 'gpu_grid_launched': False, 'total_commits': meta['commits'],
                  'next_cursor': [meta['stage'], meta['round']], 'final_model_sha256': model_identity(model, meta['slots']),
                  'elapsed_seconds': time.perf_counter()-started, 'timings': timings}
        write_json(output / 'run.json', result)
        return result


def run(train_package, output, settings, expected_manifest, resume=None, stop_after_commits=None):
    settings.validate()
    runtime = configure_runtime()
    verify_train(train_package, settings, expected_manifest)
    if digest(ROOT / 'configs/phase3/taxonomy-v1.json') != read_json(PROTOCOL)['taxonomy_sha256']:
        raise ValueError('Frozen support/taxonomy identity differs')
    execution = {'protocol_sha256': digest(PROTOCOL), 'train_manifest_sha256': expected_manifest,
                 'code_identity': code_identity(), 'runtime_identity': identity(runtime),
                 'decisions_sha256': digest(ROOT / 'docs/phase3-cpu-v2/decisions-2026-10-24.md'),
                 'taxonomy_sha256': digest(ROOT / 'configs/phase3/taxonomy-v1.json'),
                 'settings_identity': identity(settings.scientific())}
    result = Simulator(settings, lambda stage: load_stage(train_package, stage), execution).execute(output, resume, stop_after_commits)
    write_json(output / 'runtime.json', runtime)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train-package', type=Path, required=True)
    parser.add_argument('--train-manifest-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--learner', choices=['FT', 'EI', 'DR'], default='DR')
    parser.add_argument('--admission', choices=['NONE', 'DM', 'DC', 'DQ'], default='NONE')
    parser.add_argument('--seed', type=int, default=101)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--epochs', type=int, default=1)
    parser.add_argument('--learning-rate', type=float, default=.001)
    parser.add_argument('--lambda-E', type=float, default=10.)
    parser.add_argument('--lambda-y', type=float, default=1.)
    parser.add_argument('--lambda-z', type=float, default=.5)
    parser.add_argument('--dose', type=int, nargs=2, default=(0, 1))
    parser.add_argument('--resume', type=Path)
    parser.add_argument('--stop-after-commits', type=int)
    args = parser.parse_args()
    settings = Settings(args.learner, args.admission, args.seed, args.rounds, args.epochs,
                        args.learning_rate, args.lambda_E, args.lambda_y, args.lambda_z, tuple(args.dose))
    run(args.train_package, args.output, settings, args.train_manifest_sha256, args.resume, args.stop_after_commits)


if __name__ == '__main__':
    main()
