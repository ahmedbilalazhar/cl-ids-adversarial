"""Lightweight regression tests — no dataset or GPU required."""
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import average_accuracy, backward_transfer, forgetting, summarize


def test_metrics_on_identity_matrix():
    R = np.eye(3)
    assert average_accuracy(R) == 1 / 3
    s = summarize(R)
    assert set(s) == {"acc", "bwt", "fwt", "forgetting"}
    assert forgetting(R) >= 0.0


def test_bwt_zero_without_forgetting():
    R = np.ones((3, 3))
    assert backward_transfer(R) == 0.0


def test_configs_parse():
    cfgs = sorted((ROOT / "configs").rglob("*.yaml"))
    assert len(cfgs) > 100, "expected the full experiment config set"
    for path in cfgs[:20]:  # sample to keep the test fast
        with open(path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        assert isinstance(cfg, dict), path.name


def test_layout_contract():
    for d in ["src", "configs", "scripts", "docs", "data", "results", "notebooks", "tests"]:
        assert (ROOT / d).is_dir(), f"missing top-level dir: {d}"
    assert (ROOT / "README.md").exists()
    assert (ROOT / "pyproject.toml").exists()
    # Phase-A index docs — every major folder must be self-describing
    for doc in ["configs/README.md", "scripts/README.md", "docs/README.md", "data/README.md",
                "results/README.md", "docs/papers/README.md", "reports/README.md"]:
        assert (ROOT / doc).exists(), f"missing index doc: {doc}"
