"""Diagnostic scripts must run from any working directory."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = [
    "scripts/compare_discovery_cap.py",
    "scripts/audit_discovery_threshold.py",
    "scripts/run_e4_diagnostics.py",
    "scripts/summarize_e4_diagnostics.py",
    "scripts/audit_family_scores.py",
    "scripts/snapshot_runtime.py",
]


def test_diagnostic_entrypoints_work_off_root(tmp_path):
    env = dict(os.environ, CL_THREADS="2")
    for script in SCRIPTS:
        # check=False intentionally: the returncode assertion below reports
        # the script's stderr on failure instead of a bare CalledProcessError.
        proc = subprocess.run(  # noqa: PLW1510
            [sys.executable, str(ROOT / script), "--help"],
            cwd=str(tmp_path), env=env, capture_output=True, text=True,
        )
        assert proc.returncode == 0, f"{script}: {proc.stderr[-500:]}"
        assert "usage:" in proc.stdout, script
