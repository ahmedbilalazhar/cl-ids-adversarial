"""Archive superseded local artifacts with hashes and a reason.

Usage: python scripts/archive_artifacts.py results/_archive/reason --reason TEXT FILE...
All paths are resolved from the repository root. The destination must be under
data/_archive or results/_archive. Existing archives are never replaced.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def root_path(raw: str) -> Path:
    path = Path(raw)
    return (path if path.is_absolute() else ROOT / path).resolve()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("destination")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--glob", action="append", default=[], help="repo-root-relative file glob")
    ap.add_argument("--reason", required=True)
    args = ap.parse_args()
    dest = root_path(args.destination)
    allowed = [(ROOT / "data" / "_archive").resolve(),
               (ROOT / "results" / "_archive").resolve()]
    if not any(dest.is_relative_to(parent) and dest != parent for parent in allowed):
        raise ValueError(f"archive destination must be under data/_archive or results/_archive: {dest}")
    if dest.exists():
        raise FileExistsError(f"archive already exists: {dest}")
    sources = [root_path(raw) for raw in args.files]
    for pattern in args.glob:
        sources.extend(sorted((ROOT / pattern).parent.glob(Path(pattern).name)))
    if not sources:
        raise ValueError("no source files matched")
    if len({p.name for p in sources}) != len(sources):
        raise ValueError("source basenames must be unique within an archive")
    for path in sources:
        if not path.is_relative_to(ROOT) or not path.is_file() or path.is_relative_to(dest):
            raise ValueError(f"source must be an existing file inside the repository: {path}")
    records = [{"source": str(p.relative_to(ROOT)).replace("\\", "/"),
                "file": p.name, "sha256": sha256(p)} for p in sources]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dest.mkdir(parents=True)
    for path, rec in zip(sources, records):
        target = dest / path.name
        shutil.move(str(path), str(target))
        if sha256(target) != rec["sha256"]:
            raise OSError(f"archive copy failed checksum verification: {target}")
    manifest = {"superseded_by": args.reason, "source_commit": commit,
                "created_utc": datetime.now(UTC).isoformat(), "n_files": len(records),
                "files": records}
    fd, tmp = tempfile.mkstemp(dir=dest, prefix=".manifest.", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, dest / "manifest.json")
    finally:
        Path(tmp).unlink(missing_ok=True)
    print(f"Archived {len(records)} files to {dest}")


if __name__ == "__main__":
    main()
