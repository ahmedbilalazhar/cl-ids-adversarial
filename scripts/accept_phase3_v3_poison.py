"""Capture extended-budget corruption interaction fixtures, no new study condition."""
from __future__ import annotations

import argparse
import contextlib
import io
import unittest
from pathlib import Path

from src.phase3.common import ROOT, digest, write_json
from src.phase3_v3.protocol import code_identity


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'results/phase3-cpu-v3/poison-acceptance.json')
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    capture, trace = io.StringIO(), io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_phase3_v3_poison')
    with contextlib.redirect_stdout(trace):
        result = unittest.TextTestRunner(stream=capture, verbosity=2).run(suite)
    write_json(args.output, {'status': 'passed' if result.wasSuccessful() else 'failed', 'tests_run': result.testsRun,
               'code_identity': code_identity(), 'test_source_sha256': digest(ROOT/'tests/test_phase3_v3_poison.py'),
               'scope': 'Tiny supplied-label poison interactions at both new budgets: unfiltered DR/EI pairing and recovery, matched DM/DC/DQ work/streams; no efficacy claim',
               'unittest_output': capture.getvalue(), 'final_test_accessed': False, 'gpu_dispatchable': False})
    args.output.with_suffix('.log').write_text(trace.getvalue(), encoding='utf-8')
    print(capture.getvalue())
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == '__main__':
    main()
