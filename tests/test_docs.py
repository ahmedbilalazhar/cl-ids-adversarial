"""Docs consistency guards: numbering discipline and spec contract."""
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_decisions_log_stays_sequential():
    text = (ROOT / "docs" / "decisions_log.md").read_text(encoding="utf-8")
    nums = [int(m.group(1)) for m in re.finditer(r"(?m)^(\d+)\. 2026", text)]
    assert nums, "no dated entries found"
    assert len(set(nums)) == len(nums), "duplicate decision numbers"
    assert all(b == a + 1 for a, b in itertools.pairwise(nums)), "entries out of order"


def test_analysis_spec_contract():
    spec = json.loads((ROOT / "docs" / "analysis_spec.json").read_text(encoding="utf-8"))
    assert spec["n_families"] == 27 and spec["n_pairs"] == 200
    assert sum(f["n_pairs"] for f in spec["families"]) == 200
