"""Generate a credential-free private qualification notebook pinned to a bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
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
WORK = Path('/kaggle/working/phase3-v5')
DEVICE = 'cpu'  # Change to 'cuda:0' for the separate CUDA qualification candidate.
RUN_FULL_DATA = False  # Selected clean development settings; seed 101 only.
SESSION_REMAINING_SECONDS = 7200  # Set the remaining allowance shown by the actual session UI.
SESSION_STARTED = time.monotonic()
EXPORT_RESERVE_SECONDS = 240  # Operational estimate; qualify actual export cost.
MINIMUM_FREE_BYTES = 2*1024**3  # Conservative local reservation, not a measured job size.

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
    environment = '''# The notebook kernel orchestrates standard-library helpers only.
# Scientific commands run in the separate pinned environment.
from kaggle_worker.session import SessionBudget, run_logged, export_outputs
SESSION = SessionBudget(SESSION_REMAINING_SECONDS, EXPORT_RESERVE_SECONDS, SESSION_STARTED)
OUTPUT = Path('/kaggle/working/phase3-results-v5')/DEVICE.replace(':', '-')
OUTPUT.mkdir(parents=True, exist_ok=True)
_COMMAND_FAILED = False

def save_outputs(reason):
    print('Saving retained outputs:', reason, flush=True)
    exported = export_outputs(OUTPUT, Path('/kaggle/working'))
    print('Export:', exported['archive'], 'SHA256:', exported['archive_sha256'], flush=True)
    return exported

def run(module, *args, interpreter=None, process_env=None, minimum=1):
    global _COMMAND_FAILED
    _COMMAND_FAILED = False
    command = [interpreter or PYTHON, '-m', module, *map(str, args)]
    try:
        remaining = SESSION.job_seconds(minimum)
        if remaining == 0:
            raise RuntimeError('Session allowance exhausted; preserve outputs and resume in a fresh session')
        receipt = run_logged(command, module, OUTPUT, PROJECT,
                             process_env if process_env is not None else ENV, remaining)
        print(receipt, flush=True)
        return receipt
    except BaseException:
        _COMMAND_FAILED = True
        try:
            save_outputs('command failed or session allowance exhausted')
        except Exception as export_error:
            print('Export failed; original working files remain:', type(export_error).__name__, flush=True)
        raise

ENVIRONMENT = '/kaggle/working/phase3-env-v5-'+DEVICE.replace(':', '-')
setup_started = time.perf_counter()
run('kaggle_worker.bootstrap', '--device', 'cuda' if DEVICE.startswith('cuda') else 'cpu',
    '--output', ENVIRONMENT, interpreter=sys.executable, process_env=os.environ.copy())
PYTHON = ENVIRONMENT+'/bin/python'
ENV = {**os.environ, 'CUBLAS_WORKSPACE_CONFIG': ':4096:8', 'OMP_NUM_THREADS': '1',
       'MKL_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'PYTHONPATH': str(PROJECT)}
import shutil
environment_receipt = Path(ENVIRONMENT)/'.phase3-environment.json'
if (OUTPUT/'environment-lock.json').exists():
    if sha(OUTPUT/'environment-lock.json') != sha(environment_receipt):
        raise ValueError('Returned environment lock changed')
else:
    shutil.copyfile(environment_receipt, OUTPUT/'environment-lock.json')
setup_receipt = OUTPUT/'setup-cost.json'
if not setup_receipt.exists():
    setup_receipt.write_text(json.dumps({'environment_setup_seconds': time.perf_counter()-setup_started,
                                        'device_candidate': DEVICE}, indent=2))
preflight = OUTPUT/f'preflight-{time.time_ns()}.json'
run('kaggle_worker.preflight', '--device', DEVICE, '--output', preflight,
    '--session-seconds', max(1., SESSION_REMAINING_SECONDS-(time.monotonic()-SESSION_STARTED)),
    '--minimum-free-bytes', MINIMUM_FREE_BYTES)
acceptance = OUTPUT/'synthetic-acceptance.json'
run('kaggle_worker.checks', '--device', DEVICE, '--output', acceptance, '--verify-existing')
'''
    definitions, setup = environment.split('ENVIRONMENT =', 1)
    environment = definitions+'try:\n'+textwrap.indent('ENVIRONMENT ='+setup, '    ')+'''except BaseException:
    if not _COMMAND_FAILED:
        try:
            save_outputs('environment setup or integrity check failed')
        except Exception as export_error:
            print('Export failed; original working files remain:', type(export_error).__name__, flush=True)
    raise
'''
    jobs = '''# Fresh jobs or compatible committed continuations. No final seed CLI exists.
# The receipt covers train validation, stage/round work, importance and saving.
# Evaluation uses the same pinned CPU device for every condition.
if RUN_FULL_DATA:
    for learner in ('FT', 'EI', 'DR'):
        remaining = SESSION.job_seconds(1080)
        if remaining == 0:
            print('Session allowance reserved for export; continue the fixed job order in a fresh session.')
            break
        job = OUTPUT/learner
        run('kaggle_worker.worker', '--device', DEVICE, '--learner', learner,
            '--train-package', PROJECT/'inputs/train',
            '--train-manifest-sha256', manifest['train_manifest_sha256'],
            '--output', job, '--budget-seconds', remaining,
            '--reserve-seconds', 180, '--transition-bound-seconds', 900)
        receipts = sorted(job.glob('invocation-*.json'))
        if not receipts or json.loads(receipts[-1].read_text())['status'] != 'complete':
            print(learner, 'stopped at a committed boundary; save outputs and resume this job.')
            break
        if SESSION.job_seconds(60) == 0:
            print('Evaluation deferred; complete training state is retained for the next session.')
            break
        metrics = OUTPUT/(learner+'-development')
        attempt = 1
        while metrics.exists() and not (metrics/'evaluation.commit.json').exists():
            metrics = OUTPUT/(learner+f'-development-attempt-{attempt:04d}')
            attempt += 1
        run('kaggle_worker.evaluate', '--job', job, '--verify-existing',
            '--development-package', PROJECT/'inputs/development', '--output', metrics)
else:
    print('Full-data confirmations are disabled. Enable RUN_FULL_DATA after inspecting fixture evidence.')
'''
    export = '''# Save Version / Run All, then download the ZIP and adjacent export receipt.
# A local archive is not proof of provider durability. Failed command attempts
# also trigger this export path after the child process stops.
exported = save_outputs('notebook reached its export cell')
print('Final-study dispatch remains sealed; inspect the retained qualification receipts.')
'''
    cells = [cell('markdown', '# Phase 3 Kaggle qualification\n\nPrivate development-only worker. Start with CPU, then use a separate CUDA run and environment for comparison. All five federated clients stay inside one job. Each contributor operates their own account.\n\nNo final-test bank, final seeds, AMP, TF32, DDP or automatic account operation. Actual Kaggle GPU qualification and full-data confirmations remain necessary.\n'),
             cell('code', extraction), cell('markdown', '## Install and verify\n\nThe notebook image is not the experiment environment. The setup cell creates Python 3.12.14, NumPy 2.3.5 and Torch 2.7.0 in a separate environment. CUDA uses the cu126 build; CPU uses the CPU build.\n'),
             cell('code', environment), cell('markdown', '## Representative complete worker costs\n\nThese jobs read the SHA256-bound CPU v3 selection record: 12 rounds, 1 epoch, EI lambda_E=100 and DR lambda_z=0.1. Record the complete receipt times and evaluate all three learners. Afterwards confirm the selected clean settings on seeds 101-103 on the eventual runtime.\n'),
             cell('code', jobs), cell('code', export)]
    notebook = {'nbformat': 4, 'nbformat_minor': 5,
                'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                             'language_info': {'name': 'python'}, 'phase3': {'final_dispatchable': False,
                                                                         'bundle_sha256': expected}}, 'cells': cells}
    output.mkdir(parents=True)
    path = output/'phase3-qualification.ipynb'
    path.write_text(json.dumps(notebook, indent=2)+'\n', encoding='utf-8')
    metadata = {'id': 'YOUR-USERNAME/phase3-qualification-v5', 'title': 'Phase 3 development qualification v5',
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
