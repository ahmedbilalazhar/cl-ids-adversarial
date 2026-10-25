"""V3 execution identity around the unchanged sequential v2 simulator."""
from __future__ import annotations

import argparse
from pathlib import Path

from src.phase3.common import ROOT, digest, identity, read_json, write_json
from src.phase3_v2.data import load_stage, verify_train
from src.phase3_v2.protocol import code_identity as parent_identity
from src.phase3_v2.train import Simulator

from .protocol import DECISIONS, PROTOCOL, Settings, code_identity, configure_runtime


def execution_identity(settings, expected_manifest, runtime):
    return {'study_revision': 'cpu-v3', 'protocol_sha256': digest(PROTOCOL), 'train_manifest_sha256': expected_manifest,
                 'code_identity': code_identity(), 'parent_code_identity': parent_identity(), 'runtime_identity': identity(runtime),
                 'decisions_sha256': digest(DECISIONS), 'taxonomy_sha256': digest(ROOT/'configs/phase3/taxonomy-v1.json'),
                 'settings_identity': identity(settings.scientific())}


def run(train_package, output, settings, expected_manifest, resume=None, stop_after_commits=None):
    settings.validate()
    runtime = configure_runtime()
    verify_train(train_package, settings, expected_manifest)
    if digest(ROOT/'configs/phase3/taxonomy-v1.json') != read_json(PROTOCOL)['taxonomy_sha256']:
        raise ValueError('Frozen taxonomy identity differs')
    execution = execution_identity(settings, expected_manifest, runtime)
    # phase3-run-v2 / phase3-round-v2 are retained serialization formats. Their
    # execution identity unambiguously binds this v3 study; old resumes mismatch.
    result = Simulator(settings, lambda stage: load_stage(train_package, stage), execution).execute(
        output, resume, stop_after_commits)
    write_json(output/'runtime.json', runtime)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--train-package', type=Path, required=True)
    p.add_argument('--train-manifest-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--learner', choices=['FT', 'EI', 'DR'], default='DR')
    p.add_argument('--admission', choices=['NONE', 'DM', 'DC', 'DQ'], default='NONE')
    p.add_argument('--seed', type=int, default=101)
    p.add_argument('--rounds', type=int, default=3)
    p.add_argument('--epochs', type=int, default=4)
    p.add_argument('--learning-rate', type=float, default=.001)
    p.add_argument('--lambda-E', type=float, default=10.)
    p.add_argument('--lambda-y', type=float, default=1.)
    p.add_argument('--lambda-z', type=float, default=.5)
    p.add_argument('--dose', type=int, nargs=2, default=(0, 1))
    p.add_argument('--resume', type=Path)
    p.add_argument('--stop-after-commits', type=int)
    a = p.parse_args()
    settings = Settings(a.learner, a.admission, a.seed, a.rounds, a.epochs, a.learning_rate,
                        a.lambda_E, a.lambda_y, a.lambda_z, tuple(a.dose))
    run(a.train_package, a.output, settings, a.train_manifest_sha256, a.resume, a.stop_after_commits)


if __name__ == '__main__':
    main()
