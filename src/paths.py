"""Repo-root-relative path helpers.

Single source of truth for locating configs, data, and results. Resolution
order is explicit: an absolute path is used as-is; otherwise the artifact
root (``$ARTIFACT_ROOT`` when set, else the repo root) wins. A same-named
file in the caller's working directory is NEVER silently preferred — the old
CWD-shadowing behavior hid which bytes a run actually consumed.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def artifact_root() -> Path:
    override = os.environ.get("ARTIFACT_ROOT")
    if override:
        root = Path(override)
        if not root.is_absolute():
            raise ValueError("ARTIFACT_ROOT must be an absolute path")
        return root
    return REPO_ROOT

CONFIG_DIR = REPO_ROOT / "configs"
RESULTS_DIR = artifact_root() / "results"
RUNS_DIR = RESULTS_DIR / "runs"
DATA_DIR = artifact_root() / "data"


def resolve_repo_path(p: Path) -> Path:
    """Resolve a config-relative path against the explicit artifact root.

    No CWD probing: the returned path is deterministic for a given
    environment, and callers check existence / fall back explicitly.
    """
    if p.is_absolute():
        return p
    return artifact_root() / p


def find_config(name: str) -> Path:
    """Locate ``<name>.yaml`` under ``configs/`` (families live in subdirs).

    Raises FileNotFoundError when missing, RuntimeError when ambiguous.
    """
    direct = CONFIG_DIR / f"{name}.yaml"
    if direct.exists():
        return direct
    hits = sorted(CONFIG_DIR.rglob(f"{name}.yaml"))
    if not hits:
        # One historical filename uses `05pct` while its display name uses
        # `0.5pct`. Result readers must resolve the name written by the runner.
        import yaml

        hits = [p for p in sorted(CONFIG_DIR.rglob("*.yaml"))
                if (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("name") == name]
        if not hits:
            raise FileNotFoundError(f"config not found: {name}")
    if len(hits) > 1:
        rel = [str(h.relative_to(CONFIG_DIR)) for h in hits]
        raise RuntimeError(f"ambiguous config name {name!r}: {rel}")
    return hits[0]


def runs_dir() -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return RUNS_DIR
