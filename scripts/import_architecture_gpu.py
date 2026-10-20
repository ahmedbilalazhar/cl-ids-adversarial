"""Verify and import the 12-config, 12-seed Colab architecture bundle.

The CPU artifacts being replaced are hashed and archived. Per-seed GPU
completion manifests are imported last, so an interrupted import cannot
make a partial seed appear complete.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.reporting import (
    _atomic_write_bytes,
    check_artifact,
    config_hash,
    source_tree_hash,
    validate_R,
    validate_summary,
)

SEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 42]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_completion_manifest(completion: dict, *, cfg: dict, task_hash: str,
                              source_commit: str | None) -> None:
    """Validate one GPU completion manifest against the local run context.

    Version 2 is the cross-machine format (no source-tree pin, hence
    `pre-code-hash` provenance on import). Version 3 additionally requires
    the recorded tree to match THIS machine, i.e. same-machine CUDA runs;
    a foreign v3 tree is rejected rather than silently downgraded, because
    cross-machine v3 provenance cannot be verified from this bundle format.
    """
    version = completion.get("manifest_version")
    if version not in (2, 3):
        raise ValueError(f"unsupported GPU manifest version: {version!r}")
    required = {
        "name": cfg.get("name"), "config_name": cfg.get("name"), "seed": cfg.get("seed"),
        "config_hash": config_hash(cfg), "task_file_hash": task_hash,
        "source_commit": source_commit,
        "runner": "single-node", "device": "cuda",
        "summary_sha256": completion.get("summary_sha256"),
        "r_sha256": completion.get("r_sha256"),
    }
    # Self-consistency of the payload hashes is checked by the caller against
    # the actual bundle bytes; here we check identity fields.
    for key, value in required.items():
        if key in ("summary_sha256", "r_sha256"):
            continue
        if completion.get(key) != value:
            raise ValueError(f"invalid GPU completion manifest field: {key}")
    if version == 3 and completion.get("source_tree_hash") != source_tree_hash():
        raise ValueError("v3 GPU manifest is not from this machine's source tree")


def _validate_bundle(zf: zipfile.ZipFile) -> tuple[dict, dict[str, bytes], dict[str, dict]]:
    run_manifest_bytes = zf.read("run_manifest.json")
    run_manifest = json.loads(run_manifest_bytes)
    config_paths = sorted((ROOT / "configs" / "arch").glob("ar_*.yaml"))
    if len(config_paths) != 12:
        raise ValueError("expected 12 architecture configs")
    names = [p.stem for p in config_paths]
    if run_manifest.get("seeds") != SEEDS or sorted(run_manifest.get("configs", [])) != names:
        raise ValueError("GPU bundle has the wrong seeds or config set")
    task_hash = digest((ROOT / "data/processed/tasks_chrono.npz").read_bytes())
    if task_hash != run_manifest.get("task_file_sha256"):
        raise ValueError("GPU task artifact differs from the local task artifact")
    cfgs: dict[str, dict] = {}
    for path in config_paths:
        if digest(path.read_bytes()) != run_manifest["config_sha256"].get(path.stem):
            raise ValueError(f"GPU config differs from {path.name}")
        cfgs[path.stem] = yaml.safe_load(path.read_text(encoding="utf-8"))
    payloads: dict[str, bytes] = {}
    expected: set[str] = set()
    for name in names:
        for seed in SEEDS:
            cfg = dict(cfgs[name], seed=seed, device="cuda")
            paths = {kind: f"results/{name}_{kind}_seed{seed}.{ext}" for kind, ext in
                     (("R", "csv"), ("summary", "json"), ("manifest", "json"))}
            for member in paths.values():
                expected.add(member)
                payloads[member] = zf.read(member)
            summary = json.loads(payloads[paths["summary"]])
            completion = json.loads(payloads[paths["manifest"]])
            validate_summary(summary, cfg)
            if summary.get("runtime_device") != "cuda" or summary["seed"] != seed:
                raise ValueError(f"non-GPU or wrong-seed summary: {name}/{seed}")
            matrix = np.array(list(csv.reader(io.StringIO(payloads[paths["R"]].decode()))), dtype=float)
            validate_R(matrix)
            check_completion_manifest(
                completion, cfg=cfg, task_hash=task_hash,
                source_commit=run_manifest.get("source_commit"))
            if (completion.get("summary_sha256") != digest(payloads[paths["summary"]])
                    or completion.get("r_sha256") != digest(payloads[paths["R"]])):
                raise ValueError(f"GPU payload hash mismatch: {name}/{seed}")
    actual = {p for p in zf.namelist() if p.startswith("results/") and not p.endswith("/")}
    if actual != expected:
        raise ValueError(f"unexpected or missing result members: {sorted(actual ^ expected)[:5]}")
    return run_manifest, payloads, cfgs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    args = ap.parse_args()
    target_dir = (ROOT / "results" / "runs").resolve()
    archive_root = (ROOT / "results" / "_archive").resolve()
    if not target_dir.is_relative_to(ROOT.resolve()) or not archive_root.is_relative_to(ROOT.resolve()):
        raise ValueError("result paths escaped the repository")
    with zipfile.ZipFile(args.archive) as zf:
        _, payloads, cfgs = _validate_bundle(zf)
        run_manifest_bytes = zf.read("run_manifest.json")
    bundle_id = digest(run_manifest_bytes)[:12]
    cpu_archive = archive_root / f"architecture_cpu_pre_gpu_{bundle_id}"
    gpu_record = target_dir.parent / f"gpu_import_{bundle_id}.json"
    if gpu_record.exists() and gpu_record.read_bytes() != run_manifest_bytes:
        raise FileExistsError(f"conflicting GPU provenance record: {gpu_record}")

    # Preflight every existing seed before moving any file.
    to_archive: list[Path] = []
    for name, base in cfgs.items():
        for seed in SEEDS:
            cfg = dict(base, seed=seed, device="cuda")
            if check_artifact(target_dir, name, seed, cfg)["complete"]:
                continue
            files = [target_dir / f"{name}_{kind}_seed{seed}.{ext}" for kind, ext in
                     (("R", "csv"), ("summary", "json"), ("manifest", "json"))]
            present = [p for p in files if p.exists()]
            if present:
                summary_path = files[1]
                if not summary_path.exists():
                    raise ValueError(f"unidentified partial result in {files[0]}; archive manually")
                old = json.loads(summary_path.read_text(encoding="utf-8"))
                if old.get("runtime_device", "cpu") != "cpu":
                    raise ValueError(f"existing non-CPU result differs from bundle: {name}/{seed}")
                to_archive.extend(present)
    if to_archive and cpu_archive.exists():
        raise FileExistsError(f"CPU archive already exists: {cpu_archive}")
    target_dir.mkdir(parents=True, exist_ok=True)
    if to_archive:
        cpu_archive.mkdir(parents=True)
        moved = []
        for source in to_archive:
            old_hash = digest(source.read_bytes())
            target = cpu_archive / source.name
            shutil.move(str(source), str(target))
            if digest(target.read_bytes()) != old_hash:
                raise OSError(f"CPU archive checksum mismatch: {target}")
            moved.append({"source": str(source.relative_to(ROOT)).replace("\\", "/"),
                          "file": source.name, "sha256": old_hash})
        (cpu_archive / "manifest.json").write_text(json.dumps({
            "superseded_by": f"GPU architecture bundle {bundle_id}; CPU and GPU results are separate protocols",
            "n_files": len(moved), "files": moved,
        }, indent=2), encoding="utf-8")
        (cpu_archive / "gpu_run_manifest.json").write_bytes(run_manifest_bytes)
    _atomic_write_bytes(gpu_record, run_manifest_bytes)

    imported = 0
    for name, base in cfgs.items():
        for seed in SEEDS:
            cfg = dict(base, seed=seed, device="cuda")
            if check_artifact(target_dir, name, seed, cfg)["complete"]:
                continue
            for kind, ext in (("R", "csv"), ("summary", "json"), ("manifest", "json")):
                filename = f"{name}_{kind}_seed{seed}.{ext}"
                _atomic_write_bytes(target_dir / filename, payloads[f"results/{filename}"])
            if not check_artifact(target_dir, name, seed, cfg)["complete"]:
                raise OSError(f"imported seed failed completion validation: {name}/{seed}")
            imported += 1
    print(f"Imported {imported} GPU seeds; archived {len(to_archive)} CPU files.")
    print(f"GPU provenance: {gpu_record}")


if __name__ == "__main__":
    main()
