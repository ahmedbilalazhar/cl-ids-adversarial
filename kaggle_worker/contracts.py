"""One strict contract shared by job creation, evaluation and result import."""
from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, fields

from src.phase3.common import ROOT, digest, identity
from src.phase3_v3.protocol import DECISIONS, PROTOCOL, Settings, code_identity

from .runtime import FROZEN, source_files

REVISION = 'kaggle-qualification-v3'
EXECUTION_KEYS = {'study_revision', 'frozen_code_identity', 'worker_source_identity', 'protocol_sha256',
                  'decisions_sha256', 'taxonomy_sha256', 'settings_identity', 'runtime_identity',
                  'train_manifest_sha256', 'final_dispatchable'}
RUNTIME_KEYS = {'schema', 'python', 'torch', 'numpy', 'cuda', 'cudnn', 'torch_build', 'system', 'machine',
                'processor', 'CPU_capability', 'device_type', 'gpu', 'threads', 'interop_threads',
                'dtype', 'amp', 'tf32', 'deterministic_algorithms', 'cublas_workspace', 'packages',
                'worker_source_identity', 'frozen_code_identity'}


def sha256_value(value, field):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('Expected lowercase SHA256 for '+field)
    return value


def exact_keys(value, keys, label):
    if type(value) is not dict or set(value) != keys:
        raise ValueError('Unexpected '+label+' fields')


def parse_settings(value):
    exact_keys(value, {field.name for field in fields(Settings)}, 'settings')
    for name in ('seed', 'rounds', 'epochs'):
        if type(value[name]) is not int:
            raise ValueError('Expected integer '+name)
    if type(value['dose']) not in (list, tuple) or len(value['dose']) != 2 or any(type(v) is not int for v in value['dose']):
        raise ValueError('Expected an integer numerator/denominator dose')
    for name in ('learning_rate', 'lambda_E', 'lambda_y', 'lambda_z'):
        if type(value[name]) not in (int, float) or not math.isfinite(value[name]):
            raise ValueError('Expected finite numerical '+name)
    if type(value['learner']) is not str or type(value['admission']) is not str:
        raise ValueError('Expected learner/admission names')
    return Settings(**{**value, 'dose': tuple(value['dose'])}).validate()


@dataclass(frozen=True, slots=True)
class SourceBindings:
    worker: str
    protocol: str
    decisions: str
    taxonomy: str

    @classmethod
    def local(cls):
        if code_identity() != FROZEN:
            raise ValueError('Frozen scientific source differs from the accepted numerical engine')
        return cls(identity(source_files()), digest(PROTOCOL), digest(DECISIONS),
                   digest(ROOT/'configs/phase3/taxonomy-v1.json'))


@dataclass(frozen=True, slots=True)
class TimeBudget:
    seconds: float
    reserve: float = 120
    transition: float = 600

    def __post_init__(self):
        if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0
               for v in (self.seconds, self.reserve, self.transition)):
            raise ValueError('Positive finite scheduling bounds required')
        if self.seconds <= self.reserve+self.transition:
            raise ValueError('Session budget cannot safely start one transition')

    def permits(self, elapsed, observed_bound):
        return elapsed+self.reserve+max(self.transition, observed_bound) <= self.seconds


def validate_runtime(runtime, bindings):
    exact_keys(runtime, RUNTIME_KEYS, 'runtime')
    if (runtime['schema'] != 'kaggle-qualification-runtime-v1' or runtime['python'] != '3.12.14' or
            runtime['numpy'] != '2.3.5' or runtime['torch'] not in ('2.7.0+cpu', '2.7.0+cu126') or
            runtime['worker_source_identity'] != bindings.worker or runtime['frozen_code_identity'] != FROZEN):
        raise ValueError('Incompatible runtime/source contract')
    for name in ('threads', 'interop_threads'):
        if type(runtime[name]) is not int or runtime[name] != 1:
            raise ValueError('Unexpected thread policy')
    if (runtime['dtype'] != 'float32' or runtime['amp'] is not False or runtime['tf32'] is not False or
            runtime['deterministic_algorithms'] is not True or runtime['cublas_workspace'] != ':4096:8'):
        raise ValueError('Unexpected precision/determinism policy')
    packages = runtime['packages']
    if (type(packages) is not dict or any(type(k) is not str or type(v) is not str or not v for k, v in packages.items()) or
            packages.get('torch') != runtime['torch'] or packages.get('numpy') != runtime['numpy']):
        raise ValueError('Installed package fingerprint differs from runtime')
    if runtime['torch'] == '2.7.0+cpu' and runtime['cuda'] is not None:
        raise ValueError('CPU build reports CUDA')
    if runtime['torch'] == '2.7.0+cu126' and runtime['cuda'] != '12.6':
        raise ValueError('Unexpected CUDA build')
    if runtime['device_type'] == 'cpu':
        if runtime['gpu'] is not None:
            raise ValueError('CPU execution must not report a GPU device')
    elif runtime['device_type'] == 'cuda':
        gpu = runtime['gpu']
        exact_keys(gpu, {'name', 'capability', 'memory_bytes', 'driver_versions'}, 'GPU')
        if (runtime['torch'] != '2.7.0+cu126' or type(gpu['name']) is not str or not gpu['name'] or
                type(gpu['memory_bytes']) is not int or gpu['memory_bytes'] <= 0 or
                type(gpu['capability']) is not list or len(gpu['capability']) != 2 or
                any(type(v) is not int or v < 0 for v in gpu['capability']) or
                type(gpu['driver_versions']) is not list or not gpu['driver_versions'] or
                any(type(v) is not str or not v for v in gpu['driver_versions'])):
            raise ValueError('Actual GPU fingerprint required')
    else:
        raise ValueError('Unsupported execution device')


def make_procedure(settings, runtime, train_manifest, bindings=None):
    bindings = SourceBindings.local() if bindings is None else bindings
    settings = parse_settings(asdict(settings))
    validate_runtime(runtime, bindings)
    execution = {'study_revision': REVISION, 'frozen_code_identity': FROZEN,
                 'worker_source_identity': bindings.worker, 'protocol_sha256': bindings.protocol,
                 'decisions_sha256': bindings.decisions, 'taxonomy_sha256': bindings.taxonomy,
                 'settings_identity': identity(settings.scientific()), 'runtime_identity': identity(runtime),
                 'train_manifest_sha256': sha256_value(train_manifest, 'training manifest'), 'final_dispatchable': False}
    return {'schema': 'kaggle-qualification-job-v1', 'execution': execution,
            'settings': asdict(settings), 'runtime': runtime}


def validate_procedure(procedure, bindings=None):
    bindings = SourceBindings.local() if bindings is None else bindings
    exact_keys(procedure, {'schema', 'execution', 'settings', 'runtime'}, 'job')
    if procedure['schema'] != 'kaggle-qualification-job-v1':
        raise ValueError('Unsupported job schema')
    settings = parse_settings(procedure['settings'])
    runtime, execution = procedure['runtime'], procedure['execution']
    validate_runtime(runtime, bindings)
    exact_keys(execution, EXECUTION_KEYS, 'execution')
    expected = make_procedure(settings, runtime, execution['train_manifest_sha256'], bindings)
    if execution != expected['execution'] or execution['final_dispatchable'] is not False:
        raise ValueError('Job code/config/runtime/settings identity mismatch')
    return settings
