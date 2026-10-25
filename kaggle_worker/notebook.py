"""Generate a credential-free private qualification notebook pinned to a bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from src.phase3.common import read_json, write_json


def cell(kind, text):
    value = {'cell_type': kind, 'id': hashlib.sha256(text.encode()).hexdigest()[:12],
             'metadata': {}, 'source': text.splitlines(keepends=True)}
    if kind == 'code':
        value.update({'execution_count': None, 'outputs': []})
    return value


def generate(receipt, output):
    if output.exists():
        raise FileExistsError(output)
    expected = receipt['archive_sha256']
    extraction = f'''from pathlib import Path, PurePosixPath
import hashlib, json, zipfile, os, subprocess, sys, time

# Attach the private dataset containing qualification.zip, then set its path.
BUNDLE = Path('/kaggle/input/CHANGE-TO-YOUR-PRIVATE-DATASET/qualification.zip')
EXPECTED_SHA256 = {expected!r}
WORK = Path('/kaggle/working/phase3-v3')
DEVICE = 'cpu'  # Change to 'cuda:0' for the separate CUDA qualification candidate.
RUN_FULL_DATA = False  # Enable after synthetic checks; development seed 101 only.

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024**2), b''):
            h.update(block)
    return h.hexdigest()

assert BUNDLE.is_file(), 'Attach the private bundle dataset and set BUNDLE'
assert sha(BUNDLE) == EXPECTED_SHA256, 'Wrong bundle bytes'
WORK.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(BUNDLE) as archive:
    manifest = json.loads(archive.read('SNAPSHOT.json'))
    assert not manifest['final_dispatchable'] and not manifest['final_test_accessed']
    assert set(archive.namelist()) == set(manifest['files']) | {{'SNAPSHOT.json'}}
    assert len(archive.namelist()) == len(set(archive.namelist()))
    for name, expected in manifest['files'].items():
        p = PurePosixPath(name)
        assert not p.is_absolute() and '..' not in p.parts and '\\\\' not in name and ':' not in name
        target = WORK/name
        assert target.resolve().is_relative_to(WORK.resolve())
        if target.exists():
            assert sha(target) == expected, 'Existing source/input changed: '+name
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(name) as source, target.open('xb') as dest:
                import shutil
                shutil.copyfileobj(source, dest, 8*1024**2)
            assert sha(target) == expected
PROJECT = WORK/'project'
os.chdir(PROJECT)
print('Verified frozen source, worker source and train/development input bytes.')
'''
    environment = '''# Enable Internet for setup. The candidate uses its own pinned environment.
ENVIRONMENT = '/kaggle/working/phase3-env-v3-'+DEVICE.replace(':', '-')
setup_started = time.perf_counter()
subprocess.run([sys.executable, '-m', 'kaggle_worker.bootstrap',
                '--device', 'cuda' if DEVICE.startswith('cuda') else 'cpu',
                '--output', ENVIRONMENT], check=True)
PYTHON = ENVIRONMENT+'/bin/python'
ENV = {**os.environ, 'CUBLAS_WORKSPACE_CONFIG': ':4096:8', 'OMP_NUM_THREADS': '1',
       'MKL_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'PYTHONPATH': str(PROJECT)}
OUTPUT = Path('/kaggle/working/phase3-results-v3')/DEVICE.replace(':', '-')
OUTPUT.mkdir(parents=True, exist_ok=True)
import shutil
shutil.copyfile(Path(ENVIRONMENT)/'.phase3-environment.json', OUTPUT/'environment-lock.json')
setup_receipt = OUTPUT/'setup-cost.json'
if not setup_receipt.exists():
    setup_receipt.write_text(json.dumps({'environment_setup_seconds': time.perf_counter()-setup_started,
                                        'device_candidate': DEVICE}, indent=2))

def run(module, *args):
    index = 1
    while (OUTPUT/f'command-{index:04d}.json').exists() or (OUTPUT/f'command-{index:04d}.log').exists():
        index += 1
    log = OUTPUT/f'command-{index:04d}.log'
    command = [PYTHON, '-m', module, *map(str, args)]
    print('Running', module, 'log:', log, flush=True)
    began = time.perf_counter()
    with log.open('x') as stream:
        result = subprocess.run(command, cwd=PROJECT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
    receipt = {'module': module, 'argv': command, 'returncode': result.returncode,
               'subprocess_wall_seconds': time.perf_counter()-began,
               'scope': 'Includes cold interpreter imports, input verification, execution and saving; excludes setup',
               'log_sha256': sha(log)}
    (OUTPUT/f'command-{index:04d}.json').write_text(json.dumps(receipt, indent=2))
    print(receipt)
    print('\\n'.join(log.read_text().splitlines()[-8:]))
    result.check_returncode()

acceptance = OUTPUT/'synthetic-acceptance.json'
run('kaggle_worker.checks', '--device', DEVICE, '--output', acceptance, '--verify-existing')
'''
    jobs = '''# Fresh jobs or compatible committed continuations. No final seed CLI exists.
# The receipt covers train validation, stage/round work, importance and saving.
# Evaluation uses the same pinned CPU device for every condition.
if RUN_FULL_DATA:
    for learner in ('FT', 'EI', 'DR'):
        job = OUTPUT/learner
        run('kaggle_worker.worker', '--device', DEVICE, '--learner', learner,
            '--train-package', PROJECT/'inputs/train',
            '--train-manifest-sha256', manifest['train_manifest_sha256'],
            '--output', job, '--budget-seconds', 7200,
            '--reserve-seconds', 180, '--transition-bound-seconds', 900)
        receipts = sorted(job.glob('invocation-*.json'))
        if not receipts or json.loads(receipts[-1].read_text())['status'] != 'complete':
            print(learner, 'stopped at a committed boundary; save outputs and resume this job.')
            continue
        metrics = OUTPUT/(learner+'-development')
        if not metrics.exists():
            run('kaggle_worker.evaluate', '--job', job,
                '--development-package', PROJECT/'inputs/development', '--output', metrics)
else:
    print('Full-data confirmations are disabled. Enable RUN_FULL_DATA after inspecting fixture evidence.')
'''
    export = '''# Save Version / Run All, wait for success, and download these saved outputs.
# /kaggle/working is the output location; a checkpoint only in a live session is
# not a durable handoff. Keep failed logs and immutable segments in the export.
import shutil
index = 1
export = Path(f'/kaggle/working/phase3-qualification-output-{index:04d}.zip')
while export.exists():
    index += 1
    export = Path(f'/kaggle/working/phase3-qualification-output-{index:04d}.zip')
shutil.make_archive(str(export.with_suffix('')), 'zip', OUTPUT)
print('Output archive:', export, 'SHA256:', sha(export))
print('These results qualify development execution only; final-study dispatch is still sealed.')
'''
    cells = [cell('markdown', '# Phase 3 Kaggle qualification\n\nPrivate development-only worker. Start with CPU, then use a separate CUDA run and environment for comparison. All five federated clients stay inside one job. Each contributor operates their own account.\n\nNo final-test bank, final seeds, AMP, TF32, DDP or automatic account operation. Actual Kaggle GPU qualification and full-data confirmations remain necessary.\n'),
             cell('code', extraction), cell('markdown', '## Install and verify\n\nThe notebook image is not the experiment environment. The setup cell creates Python 3.12.14, NumPy 2.3.5 and Torch 2.7.0 in a separate environment. CUDA uses the cu126 build; CPU uses the CPU build.\n'),
             cell('code', environment), cell('markdown', '## Representative complete worker costs\n\nThese pilot defaults benchmark execution, not final selected settings. Record the complete receipt times and evaluate all three learners. Afterwards confirm the selected clean settings on seeds 101–103 on the eventual runtime.\n'),
             cell('code', jobs), cell('code', export)]
    notebook = {'nbformat': 4, 'nbformat_minor': 5,
                'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                             'language_info': {'name': 'python'}, 'phase3': {'final_dispatchable': False,
                                                                         'bundle_sha256': expected}}, 'cells': cells}
    output.mkdir(parents=True)
    path = output/'phase3-qualification.ipynb'
    path.write_text(json.dumps(notebook, indent=2)+'\n', encoding='utf-8')
    metadata = {'id': 'YOUR-USERNAME/phase3-qualification-v3', 'title': 'Phase 3 development qualification v3',
                'code_file': path.name, 'language': 'python', 'kernel_type': 'notebook',
                'is_private': True, 'enable_gpu': False, 'enable_internet': True,
                'dataset_sources': [], 'competition_sources': [], 'kernel_sources': [], 'model_sources': []}
    write_json(output/'kernel-metadata.json', metadata)
    for value in cells:
        if value['cell_type'] == 'code':
            compile(''.join(value['source']), str(path), 'exec')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle-receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(generate(read_json(args.bundle_receipt), args.output))


if __name__ == '__main__':
    main()
