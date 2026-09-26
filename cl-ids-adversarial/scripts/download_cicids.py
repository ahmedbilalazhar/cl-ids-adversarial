from __future__ import annotations

import ssl
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

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

MIRRORS = [
    "https://cicresearch.ca/CICDataset/CIC-IDS-2017/Dataset/MachineLearningCSV",
    "http://cicresearch.ca/CICDataset/CIC-IDS-2017/Dataset/MachineLearningCSV",
    "http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/MachineLearningCSV",
    "https://huggingface.co/datasets/c01dsnap/CIC-IDS2017/resolve/main",
]

ctx = ssl._create_unverified_context()


def already(name: str) -> bool:
    p = OUT / name
    return p.exists() and p.stat().st_size > 1_000_000


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
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
                        pct = 100 * done / total
                        print(f"\r  {done // (1<<20)}MB / {total // (1<<20)}MB ({pct:.1f}%)", end="")
            print()
            if tmp.stat().st_size < 1_000_000:
                tmp.unlink(missing_ok=True)
                return False
            tmp.replace(dest)
            return True
    except Exception as e:
        print(f"\n  fail: {type(e).__name__}: {e}")
        return False


def main():
    for name in FILES:
        dest = OUT / name
        if already(name):
            print(f"skip {name} ({dest.stat().st_size // (1<<20)}MB)")
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
            return 1
    print("ALL DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
