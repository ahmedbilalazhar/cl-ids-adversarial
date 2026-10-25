"""Qualify analysis code on synthetic arithmetic only; cannot read final data."""
from __future__ import annotations

import argparse
import contextlib
import io
import unittest
from fractions import Fraction
from pathlib import Path

from src.phase3.common import ROOT, digest, write_json
from src.phase3_analysis.statistics import analysis_identity, analyze_family, specification


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'results/phase3-analysis-v1')
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    capture = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_phase3_analysis')
    with contextlib.redirect_stdout(capture):
        result = unittest.TextTestRunner(stream=capture, verbosity=2).run(suite)
    report = {'status': 'passed' if result.wasSuccessful() else 'failed', 'tests_run': result.testsRun,
              'analysis_identity': analysis_identity(), 'test_source_sha256': digest(ROOT/'tests/test_phase3_analysis.py'),
              'scope': 'Synthetic count/rank/tie/zero/missingness/contrast/bootstrap fixtures only',
              'final_data_accessed': False, 'real_research_results': False, 'unittest_output': capture.getvalue()}
    write_json(args.output/'acceptance.json', report)
    print(capture.getvalue())
    if not result.wasSuccessful():
        raise SystemExit(1)
    _, spec = specification()
    example = {c['id']: [Fraction()]*12 for c in spec['contrasts']}
    example['C1_01'] = [Fraction(1, 10), Fraction(-1, 10)]+[Fraction()]*10
    example['C2_FAR_clean'][-1] = None
    output = analyze_family(example)
    output.update({'role': 'synthetic_acceptance_only', 'real_research_results': False, 'final_data_accessed': False})
    write_json(args.output/'synthetic-family-example.json', output)
    write_json(args.output/'artifact-index.json', {'files': {p.name: digest(p) for p in sorted(args.output.glob('*.json'))}})


if __name__ == '__main__':
    main()
