"""Validate and import a completed Colab architecture sweep.

Usage: python scripts/import_architecture_gpu.py PATH/architecture_gpu_results.zip
CPU architecture seeds are archived before replacement; no other results move.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 42]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    args = ap.parse_args()
    config_paths = sorted((ROOT / "configs" / "arch").glob("ar_*.yaml"))
    names = [p.stem for p in config_paths]
    assert len(names) == 12
    target_dir = (ROOT / "results").resolve()
    archive_dir = (ROOT / "results" / "_archive" / "architecture_cpu_pre_gpu").resolve()
    assert target_dir.is_relative_to(ROOT.resolve())
    assert archive_dir.is_relative_to(ROOT.resolve())

    with zipfile.ZipFile(args.archive) as zf:
        manifest = json.loads(zf.read("run_manifest.json"))
        if manifest["seeds"] != SEEDS or sorted(manifest["configs"]) != names:
            raise ValueError("GPU manifest has the wrong seeds or configuration set")
        task_path = ROOT / "data/processed/tasks_chrono.npz"
        if digest(task_path.read_bytes()) != manifest["task_file_sha256"]:
            raise ValueError("GPU task file differs from local tasks_chrono.npz")
        for path in config_paths:
            if digest(path.read_bytes()) != manifest["config_sha256"][path.stem]:
                raise ValueError(f"GPU config differs from local {path.name}")

        expected = set()
        payloads = {}
        for name in names:
            for seed in SEEDS:
                for suffix in (f"_R_seed{seed}.csv", f"_summary_seed{seed}.json"):
                    member = f"results/{name}{suffix}"
                    expected.add(member)
                    payloads[member] = zf.read(member)
                summary = json.loads(payloads[f"results/{name}_summary_seed{seed}.json"])
                if summary.get("runtime_device") != "cuda" or summary.get("seed") != seed:
                    raise ValueError(f"Non-GPU or wrong-seed result: {name} seed {seed}")
        actual = {p for p in zf.namelist() if p.startswith("results/") and not p.endswith("/")}
        if actual != expected:
            raise ValueError(f"Unexpected or missing results: {len(actual ^ expected)} paths")

    # All validation finishes before any move or write.
    if (archive_dir / "manifest.json").exists():
        changed = [
            member for member, payload in payloads.items()
            if (target_dir / Path(member).name).exists()
            and digest((target_dir / Path(member).name).read_bytes()) != digest(payload)
        ]
        if changed:
            raise FileExistsError("A previous CPU archive exists; refusing to replace more results")
    archive_dir.mkdir(parents=True, exist_ok=True)
    moved = []
    for member, payload in sorted(payloads.items()):
        name = Path(member).name
        current = target_dir / name
        if current.exists():
            if digest(current.read_bytes()) == digest(payload):
                continue  # safe repeat import
            archived = archive_dir / name
            if archived.exists():
                raise FileExistsError(f"Existing archive collision: {archived}")
            shutil.move(str(current), str(archived))
            moved.append({"file": name, "sha256": digest(archived.read_bytes())})
        current.write_bytes(payload)
    if moved:
        manifest_path = archive_dir / "manifest.json"
        if manifest_path.exists():
            raise FileExistsError(manifest_path)
        manifest_path.write_text(json.dumps(moved, indent=2), encoding="utf-8")
    print(f"Imported 144 GPU architecture runs; archived {len(moved) // 2} earlier runs.")
    print("Next: CL_THREADS=2 python -m src.run_experiment --rebuild-table")
    print("Then: python scripts/stats_summary.py; python scripts/make_figures.py")


if __name__ == "__main__":
    main()
