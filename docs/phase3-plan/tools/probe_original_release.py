"""Bounded public acquisition-route probe; submits no form or personal data."""
import concurrent.futures
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URLS = [
    "https://cicresearch.ca/CICDataset/CIC-IDS-2017/Dataset/GeneratedLabelledFlows.zip",
    "https://cicresearch.ca/CICDataset/CIC-IDS-2017/Dataset/GeneratedLabelledFlows.md5",
    "https://huggingface.co/datasets/Mireu-Lab/CIC-IDS/resolve/ab4a10050a2a5c3a9b36c126a409f1898a589059/ZIP/GeneratedLabelledFlows.zip",
    "https://huggingface.co/api/datasets/bencorn/CICIDS2017/tree/main",
]


def probe(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20) as response:
            return {"url": url, "status": response.status, "length": response.headers.get("Content-Length"),
                    "content_type": response.headers.get("Content-Type"), "etag": response.headers.get("ETag")}
    except Exception as exc:
        return {"url": url, "error": str(exc)}


with concurrent.futures.ThreadPoolExecutor(4) as pool:
    rows = list(pool.map(probe, URLS))
result = {"scope": "HEAD requests only; no form submission or archive authenticity claim", "completed_utc": datetime.now(timezone.utc).isoformat(), "routes": rows}
output = Path(__file__).resolve().parents[1] / "original-release-route-probe.json"
output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2))
