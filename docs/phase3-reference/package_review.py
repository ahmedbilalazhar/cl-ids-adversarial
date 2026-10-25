"""Package a repository review overlay; never include data arrays/checkpoints."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/"output/phase3-reference74-review.zip"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    paths = [ROOT/"README.md", ROOT/".gitignore", ROOT/"src/__init__.py",
             ROOT/"submissions/phase3-methodology-amendment.md", ROOT/"submissions/phase2-with-claude.tex"]
    for folder in ["src/phase3", "configs/phase3", "docs/phase3-reference", "docs/phase3-plan"]:
        paths.extend(p for p in (ROOT/folder).rglob("*") if p.is_file() and p.suffix in
                     {".py", ".md", ".json", ".lock", ".txt", ".svg", ".png"})
    paths = sorted(set(paths))
    manifest = {"scope": "Repository review overlay with source/configuration/small evidence; requires local source data and audit caches to rebuild",
                "excludes": ["raw data", "prepared feature arrays", "replay-containing checkpoints", "virtual environments"],
                "files": {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr("review-bundle-manifest.json", json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    with zipfile.ZipFile(OUT) as archive:
        for path, expected in manifest["files"].items():
            if hashlib.sha256(archive.read(path)).hexdigest() != expected:
                raise RuntimeError(f"Packaged byte mismatch: {path}")
    result = {"bundle": OUT.name, "bytes": OUT.stat().st_size, "sha256": sha(OUT),
              "source_files": len(paths), "all_packaged_hashes_verified": True, "gpu_grid_launched": False}
    (OUT.parent/"phase3-reference74-delivery.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
