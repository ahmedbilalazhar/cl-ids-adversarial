from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile

root = Path.cwd()
docs = root / "docs/phase3-plan"
pdf = root / "output/pdf/phase3-research-implementation-plan.pdf"
pdfs = [pdf, root / "output/pdf/phase3-implementation-evaluation-gap-audit.pdf"]
figures = sorted((root / "output/figures/phase3-audit").glob("*"))
archive_path = root / "output/phase3-research-plan.zip"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = sorted(p for p in docs.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != "delivery-manifest.json") + pdfs + [p for p in figures if p.is_file()]
manifest = {
    "kind": "reviewed_planning_package_not_experimental_results",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "reference_repository_head": "fac09ec0d908dc696cc4a250e95d170be9d49fa9",
    "reference_methodology": "submissions/phase2-with-claude.tex",
    "reference_methodology_sha256": sha(root / "submissions/phase2-with-claude.tex"),
    "experiments_executed": False,
    "publication_guarantee": False,
    "formal_external_preregistration_claimed": False,
    "files": [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in files],
    "note": "Manifest excludes its own hash; ZIP hash is recorded in the external output delivery record."
}
manifest_path = docs / "delivery-manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    archive.writestr("START-HERE.txt", "Start with output/pdf/phase3-implementation-evaluation-gap-audit.pdf or docs/phase3-plan/audit-executive-summary.md. The updated main plan is output/pdf/phase3-research-implementation-plan.pdf.\nThis package contains a reviewed research plan, evidence and proposed interfaces. It contains no completed model experiments or trained weights.\n")
    for p in files + [manifest_path]:
        archive.write(p, p.relative_to(root).as_posix())
with zipfile.ZipFile(archive_path) as archive:
    corrupt = archive.testzip()
    count = len(archive.namelist())
    for item in manifest["files"]:
        if hashlib.sha256(archive.read(item["path"])).hexdigest() != item["sha256"]:
            raise RuntimeError("Packaged digest mismatch: " + item["path"])
if corrupt:
    raise RuntimeError("Archive integrity failure: " + corrupt)
delivery = {"archive": archive_path.relative_to(root).as_posix(), "archive_bytes": archive_path.stat().st_size, "archive_sha256": sha(archive_path), "archive_entries": count, "pdf": pdf.relative_to(root).as_posix(), "pdf_sha256": sha(pdf), "pdfs": [{"path": p.relative_to(root).as_posix(), "sha256": sha(p)} for p in pdfs], "raw_data_included": False, "planning_consistency": json.loads((docs / "planning-validation.json").read_text())["passed"], "pdf_visual_review": json.loads((docs / "pdf-review.json").read_text())["result"], "scope": "Document/archive integrity only; no model implementation tests."}
(root / "output/phase3-plan-delivery.json").write_text(json.dumps(delivery, indent=2) + "\n", encoding="utf-8")
print(json.dumps(delivery, indent=2))
