"""Generator determinism: same inputs always yield same spec/inventory."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_generator(script: str, output: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / script), "--output", str(output)],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr


def _scrub_timestamps(text: str) -> str:
    text = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(\+\d{2}:\d{2}|Z)?", "<ts>", text)
    return text


def test_analysis_spec_regenerates_deterministically(tmp_path):
    a = tmp_path / "spec_a.json"
    b = tmp_path / "spec_b.json"
    _run_generator("scripts/write_analysis_spec.py", a)
    _run_generator("scripts/write_analysis_spec.py", b)
    sa = json.loads(a.read_text(encoding="utf-8"))
    sb = json.loads(b.read_text(encoding="utf-8"))
    for spec in (sa, sb):
        del spec["created_utc"]
    assert sa == sb
    assert sa["n_families"] == 27 and sa["n_pairs"] == 200


def test_bundle_inventory_regenerates_deterministically(tmp_path):
    a = tmp_path / "bundle_a.md"
    b = tmp_path / "bundle_b.md"
    _run_generator("scripts/write_bundle_inventory.py", a)
    _run_generator("scripts/write_bundle_inventory.py", b)
    assert _scrub_timestamps(a.read_text(encoding="utf-8")) == \
        _scrub_timestamps(b.read_text(encoding="utf-8"))
    text = a.read_text(encoding="utf-8")
    assert "discovery_prefedcontrols_20260928" in text
    assert "order_rev_benign_dup_20260928" in text
