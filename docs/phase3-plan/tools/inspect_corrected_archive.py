"""Bounded read-only inspection of a public research dataset archive."""
import io
import json
import csv
from pathlib import Path
from datetime import datetime, timezone
import urllib.request
import zipfile

URL = "https://intrusion-detection.distrinet-research.be/CNS2022/Datasets/CICIDS2017_improved.zip"
MAX_TRANSFER = 2 * 1024 * 1024


class RemoteArchive(io.RawIOBase):
    def __init__(self, url):
        self.url = url
        self.position = 0
        self.transferred = 0
        self.requests = 0
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=25) as response:
            self.size = int(response.headers["Content-Length"])
            self.accept_ranges = response.headers.get("Accept-Ranges")

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        if self.position < 0:
            raise ValueError("negative seek")
        return self.position

    def read(self, count=-1):
        count = self.size - self.position if count < 0 else min(count, self.size - self.position)
        if count <= 0:
            return b""
        if self.transferred + count > MAX_TRANSFER:
            raise RuntimeError("bounded transfer allowance exceeded")
        end = self.position + count - 1
        request = urllib.request.Request(self.url, headers={"Range": f"bytes={self.position}-{end}"})
        with urllib.request.urlopen(request, timeout=25) as response:
            if response.status != 206:
                raise RuntimeError(f"server did not honor range request: {response.status}")
            expected = f"bytes {self.position}-{end}/"
            if not response.headers.get("Content-Range", "").startswith(expected):
                raise RuntimeError("unexpected content range")
            data = response.read(count + 1)
        if len(data) != count:
            raise RuntimeError("unexpected range length")
        self.position += len(data)
        self.transferred += len(data)
        self.requests += 1
        return data


remote = RemoteArchive(URL)
with zipfile.ZipFile(remote) as archive:
    entries = [{"name": x.filename, "bytes": x.file_size, "compressed_bytes": x.compress_size} for x in archive.infolist()]
    samples = []
    for item in archive.infolist():
        if item.filename.lower().endswith(".csv"):
            with archive.open(item) as stream:
                sample = stream.read(4096).decode("utf-8-sig", errors="replace")
            lines = sample.splitlines()
            header = next(csv.reader([lines[0]]))
            first_rows = list(csv.reader(lines[1:3]))
            samples.append({"name": item.filename, "header": header, "column_count": len(header), "sample_timestamps": [r[header.index("Timestamp")] for r in first_rows]})
result = {"source": URL, "archive_bytes": remote.size, "accept_ranges": remote.accept_ranges, "transferred_bytes": remote.transferred, "range_requests": remote.requests, "entries": entries, "samples": samples, "scope": "Partial archive/header inspection only; not a full data/support audit."}
result["inspected_utc"] = datetime.now(timezone.utc).isoformat()
result["full_archive_downloaded"] = False
result["full_file_hashes_or_crc_verified"] = False
Path("docs/phase3-plan/data-acquisition-evidence.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"archive_bytes": remote.size, "transferred_bytes": remote.transferred, "headers": [{"file": s["name"], "columns": s["column_count"]} for s in samples], "metadata_fields_present": ["Src IP", "Src Port", "Dst IP", "Dst Port", "Protocol", "Timestamp"], "annotation_fields_to_exclude_from_features": ["Label", "Attempted Category"], "evidence": "docs/phase3-plan/data-acquisition-evidence.json"}, indent=2))
