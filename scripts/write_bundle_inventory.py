"""Inventory git-ignored preservation artifacts for release bundling.

Usage: python scripts/write_bundle_inventory.py [--output docs/release_bundle_contents.md]
Walks results/_archive, data/_archive, and artifacts/source_snapshots and
records each archive manifest's reason, file count, and hash alongside each
runtime snapshot's code hash. Reads only manifests/sidecars, never result
payloads, so it cannot validate or invalidate any scientific claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="docs/release_bundle_contents.md")
    args = ap.parse_args()

    archives = []
    for base in (ROOT / "results" / "_archive", ROOT / "data" / "_archive"):
        if not base.is_dir():
            continue
        for manifest in sorted(base.glob("*/manifest.json")):
            try:
                meta = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(meta, list):
                # Older manifests record the file list without an envelope.
                meta = {"n_files": len(meta), "superseded_by": "(legacy list manifest)",
                        "created_utc": ""}
            if not isinstance(meta, dict):
                continue
            archives.append({
                "dir": manifest.parent.relative_to(ROOT).as_posix(),
                "manifest_sha256": sha256(manifest),
                "n_files": meta.get("n_files"),
                "reason": meta.get("superseded_by", ""),
                "created_utc": meta.get("created_utc", ""),
                "complete": meta.get("complete", True),
                "error": meta.get("error", ""),
            })

    snapshots = []
    snap_dir = ROOT / "artifacts" / "source_snapshots"
    if snap_dir.is_dir():
        for sidecar in sorted(snap_dir.glob("runtime_*.json")):
            try:
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            code_hash = meta.get("source_tree_hash", sidecar.stem.replace("runtime_", ""))
            zipped = sidecar.with_suffix(".zip")
            snapshots.append({
                "file": zipped.relative_to(ROOT).as_posix() if zipped.is_file() else None,
                "sidecar": sidecar.relative_to(ROOT).as_posix(),
                "source_tree_hash": code_hash,
                "source_commit": meta.get("source_commit", ""),
                "zip_present": zipped.is_file(),
                "zip_sha256": sha256(zipped) if zipped.is_file() else None,
                "note": meta.get("note", ""),
            })

    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                                         text=True).strip()
    except Exception:
        commit = "unknown"

    lines = ["# Release bundle contents — git-ignored preservation artifacts", "",
             f"Generated {datetime.now(UTC).isoformat()} at commit `{commit}` by",
             "`python scripts/write_bundle_inventory.py`. Every path below is",
             "git-ignored and MUST be copied explicitly into any release bundle;",
             "a bundle without them is incomplete. Hashes are of the manifests",
             "and snapshot zips as found on this host.", "",
             "## Result/data archives", ""]
    for entry in archives:
        lines += [f"### `{entry['dir']}`", "",
                  f"- files: {entry['n_files']}",
                  f"- manifest sha256: `{entry['manifest_sha256']}`",
                  f"- created: {entry['created_utc']}",
                  f"- complete: {entry['complete']}",
                  f"- reason: {entry['reason']}", ""]
        if entry["error"]:
            lines += [f"- INTERRUPTED ARCHIVE, recovery required: {entry['error']}", ""]
    lines += ["## Runtime source snapshots", ""]
    for entry in snapshots:
        lines += [f"### `{entry['sidecar']}`", "",
                  f"- source_tree_hash: `{entry['source_tree_hash']}`",
                  f"- source_commit: `{entry['source_commit']}`",
                  f"- zip: `{entry['file']}` (present: {entry['zip_present']})",
                  f"- zip sha256: `{entry['zip_sha256']}`",
                  f"- note: {entry['note']}", ""]
    lines += ["## Verify on the bundling host", "",
              "```powershell",
              "python scripts/write_bundle_inventory.py",
              "git status --short  # confirm no archive or snapshot path is missing",
              "```", ""]
    out = ROOT / args.output
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}: {len(archives)} archives, {len(snapshots)} snapshots")


if __name__ == "__main__":
    main()
