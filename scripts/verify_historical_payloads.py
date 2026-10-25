"""Recheck preserved CPU evidence bytes without training or inference."""
import argparse
import ast
import hashlib
import json
import subprocess
import time
import zipfile
from pathlib import Path

from phase3_delivery.catalog import create_output
from src.phase3.common import ROOT, digest

BASE = ROOT/'results/phase3-cpu-v3'
PUBLISHED = 'b77a7bbf11c1e4ae7cc06f79e5d7d7d452dbf932'


def published_json(name):
    payload = subprocess.check_output(['git', 'show', PUBLISHED+':'+name], cwd=ROOT)
    if (ROOT/name).read_bytes() != payload:
        raise ValueError('Published evidence bytes changed: '+name)
    return json.loads(payload)


def verify(output):
    started = time.perf_counter()
    grid = published_json('results/phase3-cpu-v3/development/completion.json')
    count, size, aliases = 0, 0, 0
    for row in grid['rows']:
        receipt_name = 'results/phase3-cpu-v3/development/receipts/'+row['row_id']+'.json'
        receipt = published_json(receipt_name)
        if receipt['row'] != row:
            raise ValueError('Receipt row changed')
        if not row['physical_execution']:
            if receipt['artifact_files']:
                raise ValueError('Alias acquired physical artifacts')
            aliases += 1
            continue
        folder = BASE/'development/executions'/row['row_id']
        files = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
        if files != set(receipt['artifact_files']):
            raise ValueError('Historical trajectory inventory changed')
        for name, expected in receipt['artifact_files'].items():
            if digest(folder/name) != expected:
                raise ValueError('Historical trajectory payload changed: '+name)
            size += (folder/name).stat().st_size
            count += 1
    if len(grid['rows']) != 81 or aliases != 9 or count != 7200:
        raise ValueError('Historical row/payload accounting changed')
    acceptance_counts = {}
    for name, expected in (('integration', 559), ('controls', 1080), ('recovery', 104)):
        value = published_json(f'results/phase3-cpu-v3/{name}/acceptance.json')
        if value['status'] != 'passed' or len(value['checks']) != expected or not all(c['passed'] for c in value['checks']):
            raise ValueError('Historical acceptance changed')
        acceptance_counts[name] = expected
    bundle = ROOT/'results/phase3-source-bundle-v1/CPU-delivery'
    manifest = published_json('results/phase3-source-bundle-v1/CPU-delivery/source-manifest.json')
    acceptance = published_json('results/phase3-source-bundle-v1/CPU-delivery/acceptance.json')
    if digest(bundle/'cpu-source.zip') != acceptance['archive_sha256'] or len(manifest['files']) != 287:
        raise ValueError('Historical source bundle changed')
    with zipfile.ZipFile(bundle/'cpu-source.zip') as archive:
        if set(archive.namelist()) != set(manifest['files']) | {'SOURCE-MANIFEST.json'} or len(archive.namelist()) != 288:
            raise ValueError('Historical source inventory changed')
        for name, expected in manifest['files'].items():
            payload = archive.read(name)
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError('Archived source payload changed')
            if name.endswith('.py'):
                ast.parse(payload.decode('utf-8-sig'))
    create_output(output, {'schema': 'phase3-historical-payload-preservation-v1', 'status': 'passed',
                  'published_commit': PUBLISHED, 'logical_rows': 81, 'aliases': aliases,
                  'physical_row_payloads_verified': count, 'physical_row_bytes_verified': size,
                  'source_bundle_payloads_verified': 287, 'historical_acceptance_groups': acceptance_counts,
                  'elapsed_seconds': time.perf_counter()-started,
                  'scope': 'Fresh hash/inventory audit of original evidence; historical model tests not re-executed',
                  'new_research_trajectories': 0, 'final_test_accessed': False, 'final_dispatchable': False})
    print({'status': 'passed', 'physical_row_payloads_verified': count, 'aliases': aliases})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    verify(parser.parse_args().output)


if __name__ == '__main__':
    main()
