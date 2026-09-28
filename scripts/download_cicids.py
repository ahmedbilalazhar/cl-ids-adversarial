"""CICIDS2017 raw-CSV downloader (fail-closed).

Security contract (Phase-2):
- TLS is verified with the platform default context (no unverified contexts).
- Only HTTPS mirrors are attempted; the old plaintext-HTTP mirrors and the
  bare-IP fallback are removed (downgrade/MITM surface).
- Every file must match a checked-in SHA-256 reference hash before acceptance.
  The hashes came from this project's existing copies, not vendor signatures;
  verified HTTPS authenticates the server connection. A missing pin or hash
  mismatch fails closed. SHA256SUMS records locally accepted files.
- A CSV-header sanity check (comma-separated header containing a label-like
  column) rejects truncated/error pages before acceptance.
"""
from __future__ import annotations

import hashlib
import json
import ssl
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import artifact_root

OUT = artifact_root() / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)
SUMS = OUT / "SHA256SUMS"

FILES = [
    "Monday-WorkingHours.pcap_ISCX.csv",
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
]
EXPECTED = json.loads(Path(__file__).with_name("cicids2017_sha256.json").read_text(
    encoding="utf-8"))["files"]
if set(EXPECTED) != set(FILES):
    raise ValueError("CICIDS2017 checksum manifest does not cover the eight CSVs")

MIRRORS = [
    "https://cicresearch.ca/CICDataset/CIC-IDS-2017/Dataset/MachineLearningCSV",
    "https://huggingface.co/datasets/c01dsnap/CIC-IDS2017/resolve/main",
]
assert all(m.startswith("https://") for m in MIRRORS), "HTTPS-only mirrors"

CTX = ssl.create_default_context()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def recorded() -> dict[str, str]:
    if not SUMS.exists():
        return {}
    out = {}
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) == 2:
            out[parts[1]] = parts[0]
    return out


def record(name: str, digest: str) -> None:
    sums = recorded()
    sums[name] = digest
    SUMS.write_text("".join(f"{v}  {k}\n" for k, v in sorted(sums.items())), encoding="utf-8")


def already(name: str) -> bool:
    p = OUT / name
    if not (p.exists() and p.stat().st_size > 1_000_000):
        return False
    if sha256(p) != EXPECTED[name]:
        raise ValueError(f"checksum mismatch on existing {name}: refusing to replace it")
    return True


def sane_csv(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            head = f.read(1 << 20).decode("utf-8", errors="replace")
        first = head.splitlines()[0]
        return "," in first and any(k in first for k in ("Label", "label", "Destination"))
    except Exception:
        return False


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            total = int(r.headers.get("Content-Length") or 0)
            tmp = dest.with_suffix(".part")
            done = 0
            with open(tmp, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        print(f"\r  {done // (1<<20)}MB / {total // (1<<20)}MB ({100*done/total:.1f}%)", end="")
            print()
            if tmp.stat().st_size < 1_000_000 or not sane_csv(tmp):
                tmp.unlink(missing_ok=True)
                return False
            digest = sha256(tmp)
            if digest != EXPECTED[dest.name]:
                print(f"  checksum mismatch for {dest.name}: failing closed")
                tmp.unlink(missing_ok=True)
                return False
            tmp.replace(dest)
            record(dest.name, digest)
            return True
    except Exception as e:
        print(f"\n  fail: {type(e).__name__}: {e}")
        return False


def main():
    failed = []
    for name in FILES:
        dest = OUT / name
        if already(name):
            print(f"skip {name} ({dest.stat().st_size // (1<<20)}MB, checksum ok)")
            continue
        print(f"get {name}")
        ok = False
        for base in MIRRORS:
            url = f"{base.rstrip('/')}/{name}"
            print(f"  try {url}")
            if download(url, dest):
                print(f"  ok {dest.stat().st_size // (1<<20)}MB")
                ok = True
                break
        if not ok:
            print(f"FAILED {name}")
            failed.append(name)
    if failed:
        print(f"FAILED FILES: {failed}")
        return 1
    print("ALL DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
