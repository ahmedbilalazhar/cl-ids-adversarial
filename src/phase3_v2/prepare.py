"""Derive development-only supplied-label packages from the pinned audited cache."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np

from src.phase3.common import (
    ROOT,
    array_identity,
    digest,
    encode_rng,
    identity,
    read_json,
    rng,
    write_json,
)
from src.phase3.prepare import allocate

from .data import BASE_DEV, BASE_TRAIN
from .protocol import PROTOCOL


def corrupt(labels, ids, owners, seed, stage, dose):
    """Builder-only function. Learner receives only its returned supplied labels."""
    num, den = dose
    if (num, den) not in {(0, 1), (1, 10), (3, 10), (1, 2)}:
        raise ValueError('Undeclared rational dose')
    supplied = labels.copy()
    info = {'stage': stage, 'dose': list(dose), 'poison_ids': [], 'eligible_clients': [], 'attacked_client': None}
    if stage != 2:
        return supplied, info
    counts = np.bincount(owners[labels == 4], minlength=5)
    eligible = np.flatnonzero(counts >= 10)
    if not len(eligible):
        raise ValueError('No client with ten eligible Hulk rows')
    selector = rng(2, seed)
    attacked = int(selector.choice(eligible))
    source = np.flatnonzero((owners == attacked) & (labels == 4))
    source = source[np.argsort(ids[source], kind='stable')]
    order_rng = rng(3, seed, attacked)
    prefix = order_rng.permutation(source)
    q = num * len(source) // den
    chosen = prefix[:q]
    supplied[chosen] = 0
    info.update({'eligible_clients': eligible.tolist(), 'attacked_client': attacked,
                 'eligible_hulk': len(source), 'poison_ids': [str(int(v)) for v in ids[chosen]],
                 'full_source_order_sha256': array_identity(ids[prefix]),
                 'selector_rng': encode_rng(selector), 'source_order_rng': encode_rng(order_rng),
                 'realized_poison_count': q})
    return supplied, info


def prepare(output: Path, seed: int, dose: tuple[int, int]):
    if seed not in {101, 102, 103}:
        raise ValueError('Final seeds sealed')
    if output.exists():
        raise FileExistsError(output)
    base = ROOT / 'data/processed/phase3-reference74-v1'
    fixed = read_json(ROOT / 'docs/phase3-reference/evidence/preparation-rebuild.json')['files']
    for name, expected in fixed.items():
        if digest(base / name) != expected:
            raise ValueError('Pinned preparation changed: ' + name)
    if digest(base / 'train/manifest.json') != BASE_TRAIN or digest(base / 'development/manifest.json') != BASE_DEV:
        raise ValueError('Base package identity changed')
    adoption = read_json(ROOT / 'docs/phase3-reference/adoption.json')
    for name, sha in adoption['data_preparation']['source_assets'].items():
        if digest(ROOT / name) != sha:
            raise ValueError('Audited source/cache changed')
    if digest(ROOT / 'data/raw/phase3-feasibility-corrected/CICIDS2017_improved.zip') != read_json(ROOT / 'configs/phase3/reference74-v1.json')['data']['archive_sha256']:
        raise ValueError('Source archive changed')
    with np.load(base / 'builder/ownership.npz', allow_pickle=False) as f:
        positions, components = f['source_positions'], f['canonical_components']
    with np.load(ROOT / 'data/raw/phase3-feasibility-corrected/no-headers-74/conditional-components-120.npz', allow_pickle=False) as f:
        source_ids, labels = f['row_ids'][positions], f['labels'][positions].astype(np.int64)
    owners, allocation = allocate(components, labels, seed)
    canonical = np.argsort(source_ids, kind='stable')
    output.mkdir(parents=True)
    worker, audit = output / 'train', output / 'audit'
    worker.mkdir()
    audit.mkdir()
    component_owner_check = np.unique(np.stack([components, owners.astype(np.uint64)], axis=1), axis=0)
    if len(component_owner_check) != len(np.unique(components)):
        raise ValueError('Component has multiple owners')
    np.savez(audit / 'ownership.npz', ids=source_ids, canonical_components=components, owners=owners,
             **{k: v for k, v in allocation.items() if isinstance(v, np.ndarray)})
    corrections = []
    for stage in range(1, 5):
        source = base / f'train/E{stage}'
        ids = np.load(source / 'ids.npy', allow_pickle=False)
        clean = np.load(source / 'y.npy', allow_pickle=False)
        indexes = canonical[np.searchsorted(source_ids[canonical], ids)]
        if not np.array_equal(source_ids[indexes], ids) or not np.array_equal(labels[indexes], clean):
            raise ValueError('Component/reference alignment differs')
        stage_owners = owners[indexes]
        supplied, correction = corrupt(clean, ids, stage_owners, seed, stage, dose)
        corrections.append(correction)
        target = worker / f'E{stage}'
        target.mkdir()
        for name in ('x.npy', 'ids.npy'):
            shutil.copyfile(source / name, target / name)
        np.save(target / 'y.npy', supplied, allow_pickle=False)
        np.save(target / 'owner.npy', stage_owners, allow_pickle=False)
        np.savez(audit / f'E{stage}-reference.npz', ids=ids, reference_y=clean, owner=stage_owners,
                 components=components[indexes], poison=clean != supplied)
        if seed == 101 and not np.array_equal(stage_owners, np.load(source / 'owner.npy', allow_pickle=False)):
            raise ValueError('Seed101 ownership does not reproduce v1')
    manifest = {'schema': 'phase3-train-v2', 'base_train_manifest_sha256': BASE_TRAIN,
                'protocol_sha256': digest(PROTOCOL), 'seed': seed, 'dose': list(dose),
                'files': {p.relative_to(worker).as_posix(): digest(p) for p in sorted(worker.rglob('*.npy'))}}
    write_json(worker / 'manifest.json', manifest)
    write_json(audit / 'corruption.json', corrections)
    summary = {'schema': 'phase3-preparation-v2', 'seed': seed, 'dose': list(dose),
               'train_manifest_sha256': digest(worker / 'manifest.json'), 'scientific_identity': identity(manifest),
               'development_manifest_sha256': BASE_DEV, 'source_assets': adoption['data_preparation']['source_assets'],
               'base_preparation_report_sha256': digest(base / 'preparation-report.json'),
               'ownership_sha256': digest(audit / 'ownership.npz'), 'ownership_objective': allocation['objective'],
               'reconstruction': 'Audited-cache reuse; source/archive/split/transform verified via pinned v1 identities; ownership rebuilt',
               'files': {p.relative_to(output).as_posix(): digest(p) for p in sorted(output.rglob('*')) if p.is_file()},
               'training_rows': len(source_ids), 'development_feature_rows_in_train': 0, 'test_rows_exported': 0,
               'whole_component_owners': True}
    write_json(output / 'preparation.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=101)
    parser.add_argument('--dose', type=int, nargs=2, default=(0, 1))
    args = parser.parse_args()
    result = prepare(args.output, args.seed, tuple(args.dose))
    print(result['train_manifest_sha256'], flush=True)


if __name__ == '__main__':
    main()
