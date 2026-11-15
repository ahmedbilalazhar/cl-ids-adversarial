"""Execute the preread CPU supplement with immutable identities and complete-pair checks.

No final-test path is read. Default: 21 required trajectories, then 36 additional
DR trajectories only if estimated completion fits the compute deadline.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'phase3-implementation/src'))
import p3intervention as L


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def canonical(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def atomic(path, obj):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(obj, indent=2, allow_nan=False), encoding='utf-8')
    os.replace(temp, path)


def validate_result(r):
    assert r['device'] == 'cpu'
    assert len(r['stages']) == (1 if r.get('study_kind') == 'pooled' else 4)
    for st in r['stages']:
        c = np.asarray(st['confusion'])
        assert c.shape == (16, 16) and (c >= 0).all() and c.sum() > 0
        for name in ('accuracy', 'macro_f1', 'benign_far'):
            assert np.isfinite(st[name]) and 0 <= st[name] <= 1
    if r['cfg']['intervention'] != 'none':
        assert len(r['interventions']) == 5
        assert all(x['before'] - x['after'] == x['removed'] for x in r['interventions'])
        if r['cfg']['intervention'] == 'oracle_purge':
            assert all(x['poison_remaining'] == 0 for x in r['interventions'])


def pooled(cfg, stages, dev, tax):
    """Offline future-aware reference: 12 shuffled full-inventory passes."""
    torch.set_num_threads(1); torch.manual_seed(cfg.sd)
    start = time.perf_counter()
    x = torch.from_numpy(np.concatenate([s['x'] for s in stages]))
    y = torch.from_numpy(np.concatenate([s['y'] for s in stages]))
    model = L.Net(16, p=cfg.dropout)
    opt = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    for ep in range(12):
        idx = np.random.default_rng([cfg.sd, 772, ep]).permutation(len(y))
        model.train()
        for i in range(0, len(idx), cfg.batch):
            bt = idx[i:i + cfg.batch]
            opt.zero_grad(); loss = F.cross_entropy(model(x[bt]), y[bt]); loss.backward(); opt.step()
    m = L.stage_metrics(model, list(range(16)), dev, torch.from_numpy(dev['x']), tax, 4, torch.device('cpu'))
    return dict(cfg=asdict(cfg), tag='POOLED-s' + str(cfg.seed), study_kind='pooled', device='cpu',
                stages=[m], interventions=[], cost=dict(seconds=time.perf_counter() - start,
                model_bytes=4 * L.n_params(model), comm_bytes_total=0, buffer_bytes_total=0),
                caveat='Future-aware pooled training; continuous Adam; unrestricted historical access; not memory-matched.')


def assert_parity(reference, intervention):
    assert reference['pre_intervention_sha256'] == intervention['pre_intervention_sha256'], 'E2 state parity failure'
    assert reference['stages'][:2] == intervention['stages'][:2], 'E2 predictions/metrics differ'
    assert reference['admission'][:2] == intervention['admission'][:2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, default=ROOT / 'results/phase3-cpu-supplement')
    p.add_argument('--compute-hours', type=float, default=3.25)
    p.add_argument('--required-only', action='store_true')
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    runs = args.output / 'runs'; runs.mkdir(exist_ok=True)
    start = time.monotonic(); deadline = start + args.compute_hours * 3600
    sources = {str(Path(x).relative_to(ROOT)): digest(x) for x in [Path(__file__), Path(L.__file__)]}
    tax_path = ROOT / 'configs/phase3/taxonomy-v1.json'
    dev_dir = ROOT / 'data/processed/phase3-reference74-v1/development'
    paths = [tax_path] + list(dev_dir.glob('*.npy')) + [dev_dir / 'manifest.json']
    # Verify current training identities against the original immutable manifests.
    packages = {}
    for seed in (101, 102, 103):
        train = ROOT / f'data/processed/phase3-cpu-v2/s{seed}-p000/train'
        manifest = json.loads((train / 'manifest.json').read_text())
        for relative, expected in manifest['files'].items():
            assert digest(train / relative) == expected, f'Package hash mismatch: {train / relative}'
            paths.append(train / relative)
        paths.append(train / 'manifest.json'); packages[seed] = train
    inputs = {str(x.relative_to(ROOT)): digest(x) for x in paths}
    env = dict(python=sys.version, torch=torch.__version__, numpy=np.__version__,
               platform=platform.platform(), processor=platform.processor(), threads=1,
               device='cpu', workers=1, start_utc=datetime.now(timezone.utc).isoformat())
    identity = dict(schema='phase3-cpu-supplement-v1', sources=sources, inputs=inputs,
                    runtime={k: env[k] for k in ('python', 'torch', 'numpy', 'device', 'threads', 'workers')})
    identity_hash = canonical(identity)
    atomic(args.output / 'identity.json', dict(**identity, sha256=identity_hash))
    atomic(args.output / 'environment.json', env)
    tax = L.load_taxonomy(tax_path); dev = L.load_dev(dev_dir)
    completed = []; seconds = []; stage_cache = {}

    def execute(cfg, kind='federated'):
        for rel, expected in sources.items(): assert digest(ROOT / rel) == expected, 'Source changed during study'
        tag = cfg.tag() if kind == 'federated' else 'POOLED-s' + str(cfg.seed)
        path = runs / (tag + '.json')
        run_identity = canonical(dict(study=identity_hash, cfg=asdict(cfg), kind=kind))
        if path.exists():
            result = json.loads(path.read_text())
            assert result['run_identity'] == run_identity, f'Stale result; use a separate output directory: {path}'
            validate_result(result)
            print('RESUME validated', tag, flush=True)
        else:
            if time.monotonic() >= deadline: raise TimeoutError('CPU compute deadline reached')
            if cfg.seed not in stage_cache:
                stage_cache.clear(); L._UPLOADS.clear()
                stage_cache[cfg.seed] = L.load_stages(packages[cfg.seed])
            stages = stage_cache[cfg.seed]
            ok, messages = L.check_data(stages, dev, tax); assert ok, messages
            print('START', tag, flush=True)
            if kind == 'pooled': result = pooled(cfg, stages, dev, tax)
            else:
                result = L.run(cfg, stages, dev, tax, threads=1, device='cpu',
                    progress=lambda t, sec: print(f'  E{t} complete, {sec:.1f}s', flush=True))
            result.update(run_identity=run_identity, study_identity=identity_hash, study_kind=kind,
                          finished_utc=datetime.now(timezone.utc).isoformat())
            validate_result(result); atomic(path, result)
            print('DONE', tag, round(result['cost']['seconds'], 1), 's', flush=True)
        seconds.append(result['cost']['seconds']); completed.append(path.name)
        atomic(args.output / 'progress.json', dict(completed=len(completed), files=completed,
            elapsed_seconds=time.monotonic() - start, latest=tag))
        return result

    def mechanism(seed, rep):
        common = dict(learner='DR', n_att=5, seed=seed, rep=rep)
        execute(L.Cfg(**common, dose=0))
        ref = execute(L.Cfg(**common, dose=.5))
        for mode in ('oracle_purge', 'random_delete'):
            arm = execute(L.Cfg(**common, dose=.5, intervention=mode)); assert_parity(ref, arm)
        return ref

    # Required 12 + 6 + 3 trajectories.
    for seed in (101, 102, 103): mechanism(seed, 0)
    for seed in (101, 102, 103):
        for dose in (0., .5): execute(L.Cfg(learner='DR', admission='DQ', n_att=5, seed=seed, dose=dose))
    for seed in (101, 102, 103): execute(L.Cfg(seed=seed), kind='pooled')
    required_complete = True
    remaining_estimate = 36 * max(seconds) * 1.25
    expand = not args.required_only and time.monotonic() + remaining_estimate < deadline
    print('EXPANSION', expand, 'conservative estimate seconds', round(remaining_estimate), flush=True)
    if expand:
        for rep in (1, 2, 3):
            for seed in (101, 102, 103): mechanism(seed, rep)
    atomic(args.output / 'completion.json', dict(required_complete=required_complete,
        expanded_complete=expand, count=len(completed), files=completed,
        run_hashes={f: digest(runs / f) for f in completed}, study_identity=identity_hash,
        elapsed_seconds=time.monotonic() - start, expansion_estimate_seconds=remaining_estimate))
    print('STUDY COMPLETE', len(completed), 'validated CPU trajectories', flush=True)


if __name__ == '__main__': main()
