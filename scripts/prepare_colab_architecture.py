"""Bundle the exact code, configs, and processed CICIDS task file for Colab."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "architecture_colab_bundle.zip"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    files = sorted((ROOT / "src").rglob("*.py"))
    files += sorted((ROOT / "configs" / "arch").glob("ar_*.yaml"))
    files += [
        ROOT / "requirements.txt",
        ROOT / "data/processed/tasks_chrono.npz",
        ROOT / "data/processed/tasks_chrono.json",
    ]
    assert len(list((ROOT / "configs" / "arch").glob("ar_*.yaml"))) == 12
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(path)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            payload = path.read_bytes()
            hashes[rel] = sha256(payload)
            zf.writestr(rel, payload)
        zf.writestr("bundle_manifest.json", json.dumps({"files_sha256": hashes}, indent=2))
    print(f"Created {OUT} ({OUT.stat().st_size / 1e6:.1f} MB; {len(files)} files)")
    print(f"SHA-256 {sha256(OUT.read_bytes())}")


if __name__ == "__main__":
    main()
