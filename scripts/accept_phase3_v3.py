"""Execute focused semantics and emit strict machine-readable unittest evidence."""
import argparse
import contextlib
import io
import time
import unittest
from pathlib import Path

from src.phase3.common import ROOT, digest, write_json
from src.phase3_v3.protocol import code_files, code_identity


class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({'test': test.id(), 'status': 'passed'})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({'test': test.id(), 'status': 'failed', 'traceback': self._exc_info_to_string(err, test)})

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({'test': test.id(), 'status': 'error', 'traceback': self._exc_info_to_string(err, test)})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    started = time.perf_counter()
    stream, trace = io.StringIO(), io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_phase3_v3')
    with contextlib.redirect_stdout(trace):
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
    report = {'schema': 'phase3-acceptance-v3', 'status': 'passed' if result.wasSuccessful() else 'failed',
              'tests_run': result.testsRun, 'checks': result.records, 'elapsed_seconds': time.perf_counter()-started,
              'code_identity': code_identity(), 'code_files': code_files(),
              'test_source_sha256': digest(ROOT/'tests/test_phase3_v3.py'),
              'numerical_comparison': {'EI_FP32_rtol': 2e-5, 'EI_FP32_atol': 2e-7, 'CPU_same_engine_recovery': 'exact logical metadata and typed states'},
              'scope': 'Extended-budget counts/first-pass/EI commits and exact continuation for six pipelines at both v3 budgets; old-budget parity and orchestration interruption/receipts/locks. Parent 33-test semantics retained by immutable dependency hash; no CUDA/final qualification',
              'unittest_output': stream.getvalue()}
    write_json(args.output, report)
    args.output.with_suffix('.log').write_text(trace.getvalue(), encoding='utf-8')
    print(stream.getvalue())
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == '__main__':
    main()
