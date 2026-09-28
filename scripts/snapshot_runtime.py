"""Preserve dirty-worktree runtime bytes referenced by v3 seed manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path

from src.reporting import source_commit, source_tree_hash

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/source_snapshots"))
    args = parser.parse_args()
    code_hash = source_tree_hash()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"runtime_{code_hash}.zip"
    manifest_path = output_dir / f"runtime_{code_hash}.json"
    files = [*sorted((ROOT / "src").rglob("*.py")),
             *sorted((ROOT / "configs" / "novelty").glob("*.yaml")),
             ROOT / "requirements.txt"]
    records = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in files]
    if archive.exists() or manifest_path.exists():
        raise FileExistsError(f"source snapshot already exists for {code_hash}")
    fd, temporary = tempfile.mkstemp(prefix=".runtime.", suffix=".zip", dir=output_dir)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in files:
                bundle.write(path, path.relative_to(ROOT).as_posix())
        if source_tree_hash() != code_hash:
            raise RuntimeError("runtime sources changed during snapshot")
        os.replace(temporary, archive)
    finally:
        Path(temporary).unlink(missing_ok=True)
    manifest = {
        "source_commit": source_commit(), "source_tree_hash": code_hash,
        "archive_sha256": sha256(archive), "files": records,
        "note": "Preserves dirty runtime source for exploratory E4 manifest-v3 seeds; config/task hashes remain in each seed manifest.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {archive} ({len(records)} files)")


if __name__ == "__main__":
    main()
