"""Repo-root-relative path helpers.

Single source of truth for locating configs, data, and results regardless of
the caller's working directory (repo root, old ``cl-ids-adversarial/`` shim,
or anywhere else).
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

CONFIG_DIR = REPO_ROOT / "configs"
RESULTS_DIR = REPO_ROOT / "results"
RUNS_DIR = RESULTS_DIR / "runs"
DATA_DIR = REPO_ROOT / "data"


def resolve_repo_path(p: Path) -> Path:
    """Resolve a config-relative path against the repo root.

    A CWD-relative path wins if it exists (backward compatible with runs
    launched from the old ``cl-ids-adversarial/`` subdirectory); otherwise
    fall back to the repo root.
    """
    if p.is_absolute() or p.exists():
        return p
    rooted = REPO_ROOT / p
    return rooted if rooted.exists() else p


def find_config(name: str) -> Path:
    """Locate ``<name>.yaml`` under ``configs/`` (families live in subdirs).

    Raises FileNotFoundError when missing, RuntimeError when ambiguous.
    """
    direct = CONFIG_DIR / f"{name}.yaml"
    if direct.exists():
        return direct
    hits = sorted(CONFIG_DIR.rglob(f"{name}.yaml"))
    if not hits:
        raise FileNotFoundError(f"config not found: {name}")
    if len(hits) > 1:
        rel = [str(h.relative_to(CONFIG_DIR)) for h in hits]
        raise RuntimeError(f"ambiguous config name {name!r}: {rel}")
    return hits[0]


def runs_dir() -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return RUNS_DIR
