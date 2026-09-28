"""Transactional per-seed results and deterministic aggregate tables.

The completion manifest is the commit record for a seed. Historical files
without one remain on disk as executed evidence, but cannot be resumed or
included in a validated aggregate.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import platform
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import yaml

from src.paths import REPO_ROOT, find_config, resolve_repo_path

SUMMARY_REQUIRED_KEYS = ("acc", "bwt", "fwt", "forgetting", "seed", "cl_method", "scenario")
TASKS_PROTOCOL_MAP = {
    "data/processed/tasks.npz": "random/per-task",
    "data/processed/tasks_frozen.npz": "random/offline-init-T0T1",
    "data/processed/tasks_chrono.npz": "chrono/offline-init-T0T1",
    "data/processed/tasks_chrono_t0.npz": "chrono/t0-only",
    "data/processed/tasks_chrono_alt.npz": "chrono-alt/offline-init-T0T1",
    "data/processed/tasks_chrono_rev.npz": "chrono-rev/offline-init-T0T1",
    "data/processed/tasks_chrono_ci.npz": "chrono-ci/offline-init-T0T1",
    "data/processed/tasks_ci.npz": "random-ci/per-task",
    "data/processed/tasks_order_alt.npz": "order-alt/per-task",
    "data/processed/tasks_unsw.npz": "unsw/standard",
    "data/processed/tasks_iot.npz": "iot/capped",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        bundle = REPO_ROOT / "bundle_manifest.json"
        if bundle.is_file():
            return str(json.loads(bundle.read_text(encoding="utf-8")).get("source_commit", "unknown"))
        return "unknown"


def source_tree_hash() -> str:
    """Hash runtime Python sources, including uncommitted and untracked files."""
    digest = hashlib.sha256()
    for path in sorted((REPO_ROOT / "src").rglob("*.py")):
        digest.update(path.relative_to(REPO_ROOT).as_posix().encode())
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def library_versions() -> dict:
    info: dict = {"python": platform.python_version()}
    for mod, attr in (("numpy", "__version__"), ("torch", "__version__"),
                      ("sklearn", "__version__"), ("scipy", "__version__")):
        try:
            m = __import__(mod)
            info[mod] = str(getattr(m, attr, "?"))
        except Exception:
            info[mod] = "missing"
    return info


def config_hash(cfg: dict) -> str:
    probe = {k: v for k, v in cfg.items() if k != "seed"}
    try:
        blob = json.dumps(probe, sort_keys=True, default=str).encode()
    except Exception:
        blob = str(sorted(probe)).encode()
    return sha256_bytes(blob)


def task_file_for(cfg: dict) -> Path | None:
    rel = (cfg.get("data") or {}).get("tasks")
    if not rel:
        return None
    return resolve_repo_path(Path(rel))


def protocol_for(cfg: dict) -> str:
    rel = (cfg.get("data") or {}).get("tasks", "")
    key = rel.replace("\\", "/")
    task_p = task_file_for(cfg)
    if task_p is not None and task_p.with_suffix(".json").is_file():
        try:
            meta = json.loads(task_p.with_suffix(".json").read_text(encoding="utf-8"))
            if meta.get("schema_version") == 2:
                return str(meta["protocol_id"])
        except (OSError, ValueError, KeyError):
            pass
    return TASKS_PROTOCOL_MAP.get(key, key or "synthetic/none")


def dataset_for(cfg: dict) -> str:
    rel = ((cfg.get("data") or {}).get("tasks") or "").lower()
    if "unsw" in rel:
        return "unsw-nb15"
    if "iot" in rel:
        return "ciciot2023"
    return "cicids2017"


def model_for(cfg: dict) -> str:
    parts = [str(cfg.get("cl_method", "?"))]
    if cfg.get("arch"):
        parts.append(str(cfg.get("arch")))
    elif cfg.get("hidden"):
        parts.append("wide-%s" % (cfg.get("hidden"),))
    if cfg.get("grow_head"):
        parts.append("grow_head")
    return "+".join(parts)


def manifest_path(out_dir: Path, name: str, seed: int) -> Path:
    return out_dir / f"{name}_manifest_seed{seed}.json"


def validate_summary(summary: dict, cfg: dict | None = None) -> None:
    if not isinstance(summary, dict):
        raise ValueError("summary must be a JSON object")
    for key in SUMMARY_REQUIRED_KEYS:
        if key not in summary:
            raise ValueError(f"summary missing required key: {key}")
    for key in ("acc", "bwt", "forgetting"):
        v = summary.get(key)
        if v is None or isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(float(v)):
            raise ValueError(f"summary[{key!r}] must be finite number, got {v!r}")
    if isinstance(summary["seed"], bool) or not isinstance(summary["seed"], int):
        raise ValueError("summary seed must be an integer")
    if summary["fwt"] is not None and (
        isinstance(summary["fwt"], bool)
        or not isinstance(summary["fwt"], (int, float))
        or not np.isfinite(float(summary["fwt"]))
    ):
        raise ValueError("summary FWT must be a finite measured number or null")
    if not isinstance(summary["cl_method"], str) or not isinstance(summary["scenario"], str):
        raise ValueError("summary method and scenario must be strings")
    if cfg is not None:
        wants_fed = bool(cfg.get("fed"))
        has_fed = isinstance(summary.get("fed"), dict)
        if wants_fed and not has_fed:
            raise ValueError(
                "federated config result missing 'fed' field (wrong runner? "
                "single-node output must never count for a federated config)"
            )
        if not wants_fed and has_fed:
            raise ValueError("single-node config result carries unexpected 'fed' field")


def validate_R(R, n_tasks: int | None = None) -> np.ndarray:
    arr = np.asarray(R, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1] or arr.shape[0] == 0:
        raise ValueError(f"R must be a non-empty square matrix, got shape {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("R must be all finite")
    if arr.min() < -1e-9 or arr.max() > 1 + 1e-9:
        raise ValueError("R entries must be in [0,1]")
    if n_tasks is not None and arr.shape[0] != n_tasks:
        raise ValueError("R task count mismatch")
    return arr


def build_manifest(cfg: dict, summary_sha: str, r_sha: str, summary: dict) -> dict:
    name = cfg.get("name", "experiment")
    seed = int(cfg.get("seed", 42))
    task_p = task_file_for(cfg)
    if task_p is None or not task_p.is_file():
        raise FileNotFoundError(f"task artifact missing for manifest: {task_p}")
    task_hash = sha256_file(task_p)
    task_meta = task_p.with_suffix(".json")
    task_meta_hash = sha256_file(task_meta) if task_meta.is_file() else None
    attack = cfg.get("attack") or {}
    up = (attack.get("update_attack") or {}).get("method") if isinstance(attack.get("update_attack"), dict) else None
    split = "unknown"
    scaler = "unknown"
    meta_path = task_p.with_suffix(".json")
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("schema_version") == 2:
            split = str((meta.get("split") or {}).get("name", "unknown"))
            scaler = str((meta.get("scaler") or {}).get("kind", "unknown"))
    if scaler == "unknown":
        legacy = TASKS_PROTOCOL_MAP.get(str((cfg.get("data") or {}).get("tasks", "")).replace("\\", "/"), "")
        if "/" in legacy:
            split, scaler = legacy.split("/", 1)
    return {
        "name": name,
        "seed": seed,
        "config_name": name,
        "config_hash": config_hash(cfg),
        "task_file": str((cfg.get("data") or {}).get("tasks", "")),
        "task_file_hash": task_hash,
        "task_metadata_hash": task_meta_hash,
        "source_commit": source_commit(),
        "source_tree_hash": source_tree_hash(),
        "protocol": protocol_for(cfg),
        "split_protocol": split,
        "scaler_protocol": scaler,
        "runner": "federated" if cfg.get("fed") else "single-node",
        "dataset": dataset_for(cfg),
        "scenario": (cfg.get("data") or {}).get("scenario", ""),
        "model": model_for(cfg),
        "attack": attack.get("type"),
        "attack_mode": attack.get("mode"),
        "attack_budget": attack.get("budget"),
        "update_attack": up,
        "defense": (cfg.get("defense") or {}).get("type"),
        "device": str(summary.get("runtime_device", cfg.get("device", "cpu"))),
        "requested_device": str(cfg.get("device", "cpu")),
        "versions": library_versions(),
        "cl_threads": os.environ.get("CL_THREADS", ""),
        "summary_sha256": summary_sha,
        "r_sha256": r_sha,
        "created_utc": datetime.now(UTC).isoformat(),
        "manifest_version": 3,
    }


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp." + path.name + ".")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def _stage_bytes(directory: Path, name: str, data: bytes) -> Path:
    fd, temp = tempfile.mkstemp(dir=str(directory), prefix=f".tmp.{name}.")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise
    return Path(temp)


def save_results(result: dict, cfg: dict, out_dir: Path, *, expected_code_hash: str | None = None) -> dict:
    """Commit one seed; never replace a completed or unauthenticated legacy run."""
    out_dir.mkdir(parents=True, exist_ok=True)
    name = cfg.get("name", "experiment")
    seed = int(cfg.get("seed", 42))
    R = validate_R(result["R"])
    validate_summary(result["summary"], cfg)
    if result["summary"]["seed"] != seed:
        raise ValueError("result summary seed does not match run config seed")
    if expected_code_hash is not None and source_tree_hash() != expected_code_hash:
        raise RuntimeError("runtime source changed during the seed; result was not committed")

    r_path = out_dir / f"{name}_R_seed{seed}.csv"
    s_path = out_dir / f"{name}_summary_seed{seed}.json"
    m_path = manifest_path(out_dir, name, seed)
    pending = out_dir / f"{name}_pending_seed{seed}.json"
    lock_path = out_dir / f".{name}_seed{seed}.lock"

    buf = io.StringIO(newline="")
    w = csv.writer(buf)
    for row in R.tolist():
        w.writerow([f"{v:.6f}" for v in row])
    r_bytes = buf.getvalue().encode()
    s_bytes = json.dumps(result["summary"], indent=2, sort_keys=True, allow_nan=False).encode()
    manifest = build_manifest(cfg, sha256_bytes(s_bytes), sha256_bytes(r_bytes), result["summary"])
    if expected_code_hash is not None and manifest["source_tree_hash"] != expected_code_hash:
        raise RuntimeError("runtime source changed while building the manifest")
    identity = {key: manifest[key] for key in (
        "name", "seed", "config_hash", "task_file_hash", "task_metadata_hash", "source_tree_hash")}
    with open(lock_path, "a+b") as lock:
        _lock_file(lock)
        try:
            if m_path.exists():
                previous = json.loads(m_path.read_text(encoding="utf-8"))
                if any(previous.get(k) != v for k, v in identity.items()):
                    raise FileExistsError(
                        f"{m_path} belongs to a different config/task; archive the old seed first"
                    )
                state = check_artifact(out_dir, name, seed, cfg)
                if state["complete"]:
                    if previous["summary_sha256"] == manifest["summary_sha256"] and previous["r_sha256"] == manifest["r_sha256"]:
                        return previous
                    raise FileExistsError(f"completed seed already exists: {m_path}")
                raise FileExistsError(f"{m_path} is corrupt ({state['reason']}); archive it before rerunning")
            if pending.exists():
                previous = json.loads(pending.read_text(encoding="utf-8"))
                if any(previous.get(k) != v for k, v in identity.items()):
                    raise FileExistsError(f"pending seed has different config/task: {pending}")
            else:
                if r_path.exists() or s_path.exists():
                    raise FileExistsError(
                        f"unmanifested seed files exist for {name} seed {seed}; archive legacy files first"
                    )
                _atomic_write_bytes(pending, json.dumps(identity, sort_keys=True).encode())
            staged: list[Path] = []
            try:
                staged = [
                    _stage_bytes(out_dir, r_path.name, r_bytes),
                    _stage_bytes(out_dir, s_path.name, s_bytes),
                ]
                os.replace(staged[0], r_path)
                os.replace(staged[1], s_path)
                _atomic_write_bytes(m_path, json.dumps(manifest, indent=2, sort_keys=True).encode())
                pending.unlink(missing_ok=True)
            finally:
                for p in staged:
                    p.unlink(missing_ok=True)
        finally:
            _unlock_file(lock)

    print(json.dumps(result["summary"], indent=2))
    print("R matrix:\n", np.array2string(R, precision=3))
    return manifest


def check_artifact(out_dir: Path, name: str, seed: int, cfg: dict | None = None) -> dict:
    """Only a valid manifest and matching R/summary/provenance complete a seed."""
    r_path = out_dir / f"{name}_R_seed{seed}.csv"
    s_path = out_dir / f"{name}_summary_seed{seed}.json"
    m_path = manifest_path(out_dir, name, seed)
    if not m_path.is_file():
        reason = "unmanifested legacy or interrupted seed" if r_path.exists() or s_path.exists() else "missing seed"
        return {"complete": False, "has_manifest": False, "reason": reason}
    if not r_path.is_file() or not s_path.is_file():
        return {"complete": False, "has_manifest": True, "reason": "missing R or summary"}
    try:
        manifest = json.loads(m_path.read_text(encoding="utf-8"))
        required = ("config_name", "config_hash", "task_file_hash", "source_commit", "protocol",
                    "split_protocol", "scaler_protocol", "runner", "dataset", "model", "device",
                    "versions", "cl_threads", "summary_sha256", "r_sha256", "task_metadata_hash")
        version = manifest.get("manifest_version")
        if version not in (2, 3) or any(k not in manifest for k in required):
            raise ValueError("manifest schema invalid")
        if version == 3 and manifest.get("source_tree_hash") != source_tree_hash():
            raise ValueError("runtime source tree hash mismatch")
        if manifest.get("name") != name or manifest.get("config_name") != name or manifest.get("seed") != seed:
            raise ValueError("manifest identity mismatch")
        if manifest["summary_sha256"] != sha256_file(s_path) or manifest["r_sha256"] != sha256_file(r_path):
            raise ValueError("output hash mismatch")
        summary = json.loads(s_path.read_text(encoding="utf-8"))
        runner_cfg = cfg if cfg is not None else {"fed": manifest["runner"] == "federated"}
        validate_summary(summary, runner_cfg)
        if summary["seed"] != seed:
            raise ValueError("summary seed mismatch")
        if summary.get("runtime_device", manifest["device"]) != manifest["device"]:
            raise ValueError("runtime device mismatch")
        if manifest["runner"] not in ("federated", "single-node"):
            raise ValueError("unknown runner")
        rows = list(csv.reader(r_path.read_text(encoding="utf-8").splitlines()))
        validate_R(np.array(rows, dtype=float))
        task_p = task_file_for(cfg) if cfg is not None else resolve_repo_path(Path(manifest["task_file"]))
        if task_p is None or not task_p.is_file() or manifest["task_file_hash"] != sha256_file(task_p):
            raise ValueError("task file hash mismatch")
        task_meta = task_p.with_suffix(".json")
        actual_meta_hash = sha256_file(task_meta) if task_meta.is_file() else None
        if manifest["task_metadata_hash"] != actual_meta_hash:
            raise ValueError("task metadata hash mismatch")
        if cfg is not None:
            if manifest["config_hash"] != config_hash(cfg):
                raise ValueError("config hash mismatch")
            if manifest["runner"] != ("federated" if cfg.get("fed") else "single-node"):
                raise ValueError("runner mismatch")
    except Exception as e:
        return {"complete": False, "has_manifest": True, "reason": str(e)}
    return {"complete": True, "has_manifest": True,
            "provenance_level": "code-hashed" if version == 3 else "pre-code-hash",
            "reason": "manifest, provenance, and outputs match"}


def is_complete(out_dir: Path, name: str, seed: int, cfg: dict | None = None) -> bool:
    return bool(check_artifact(out_dir, name, seed, cfg).get("complete"))


def assert_seed_writable(out_dir: Path, name: str, seed: int, cfg: dict) -> None:
    """Fail before training when a legacy or incompatible seed occupies the slot."""
    manifest = manifest_path(out_dir, name, seed)
    pending = out_dir / f"{name}_pending_seed{seed}.json"
    r_path = out_dir / f"{name}_R_seed{seed}.csv"
    s_path = out_dir / f"{name}_summary_seed{seed}.json"
    if manifest.exists():
        state = check_artifact(out_dir, name, seed, cfg)
        if state["complete"]:
            return
        raise FileExistsError(f"{manifest}: {state['reason']}; archive before rerunning")
    if (r_path.exists() or s_path.exists()) and not pending.exists():
        raise FileExistsError(f"unmanifested seed {name}/{seed} must be archived before rerun")
    if pending.exists():
        marker = json.loads(pending.read_text(encoding="utf-8"))
        task_p = task_file_for(cfg)
        task_meta = task_p.with_suffix(".json") if task_p else None
        expected = {"name": name, "seed": seed, "config_hash": config_hash(cfg),
                    "task_file_hash": sha256_file(task_p) if task_p and task_p.is_file() else "",
                    "task_metadata_hash": sha256_file(task_meta) if task_meta and task_meta.is_file() else None,
                    "source_tree_hash": source_tree_hash()}
        if marker != expected:
            raise FileExistsError(f"pending seed {name}/{seed} has different provenance")


def _lock_file(f) -> None:
    if os.name == "nt":
        import msvcrt
        f.seek(0)
        if not f.read(1):
            f.write(b"\0")
            f.flush()
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)


def _unlock_file(f) -> None:
    if os.name == "nt":
        import msvcrt
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def append_table(result: dict, cfg: dict, out_dir: Path) -> None:
    """Compatibility entry point: regenerate the aggregate from committed seeds."""
    validate_summary(result["summary"], cfg)
    rebuild_table(out_dir)


def write_csv_atomic(path: Path, fields: list[str], rows: list[dict]) -> None:
    """Replace a complete CSV in one step, including the header-only case."""
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    _atomic_write_bytes(path, buf.getvalue().encode())


def rebuild_table(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    runs = out_dir / "runs"
    lock_path = out_dir / ".baseline_table.lock"
    with open(lock_path, "a+b") as lock:
        _lock_file(lock)
        try:
            rows = []
            skipped: list[str] = []
            seen: set[str] = set()
            candidates = sorted(runs.glob("*_manifest_seed*.json")) + sorted(out_dir.glob("*_manifest_seed*.json"))
            for p in candidates:
                if p.name in seen:
                    continue
                seen.add(p.name)
                stem = p.name.removesuffix(".json")
                base, separator, raw_seed = stem.rpartition("_manifest_seed")
                if not separator or not raw_seed.isdigit():
                    skipped.append(f"{p.name}: invalid filename")
                    continue
                seed = int(raw_seed)
                try:
                    cfg = yaml.safe_load(find_config(base).read_text(encoding="utf-8"))
                except FileNotFoundError:
                    cfg = None  # external synthetic runs still have self-contained manifests
                try:
                    manifest = json.loads(p.read_text(encoding="utf-8"))
                except (OSError, ValueError) as exc:
                    skipped.append(f"{p.name}: malformed manifest ({exc})")
                    continue
                if cfg is not None and manifest.get("requested_device") == "cuda":
                    cfg = dict(cfg, device="cuda")
                state = check_artifact(p.parent, base, seed, cfg)
                if not state["complete"]:
                    skipped.append(f"{p.name}: {state['reason']}")
                    continue
                s = json.loads((p.parent / f"{base}_summary_seed{seed}.json").read_text(encoding="utf-8"))
                atk = s.get("attack")
                if cfg and cfg.get("defense"):
                    atk = f"{atk}+defense" if atk else "defense"
                rows.append({
                    "name": base, "method": s["cl_method"], "attack": atk or "",
                    "scenario": s["scenario"], "acc": f"{s['acc']:.6f}",
                    "bwt": f"{s['bwt']:.6f}", "fwt": f"{s['fwt']:.6f}" if s["fwt"] is not None else "",
                    "forgetting": f"{s['forgetting']:.6f}", "asr_mean": s.get("asr_mean"),
                    "seed": seed, "device": manifest["device"],
                })
            rows.sort(key=lambda r: (r["name"], r["seed"]))
            fields = ["name", "method", "attack", "scenario", "acc", "bwt", "fwt", "forgetting", "asr_mean", "seed", "device"]
            write_csv_atomic(out_dir / "baseline_table.csv", fields, rows)
        finally:
            _unlock_file(lock)
    print(f"Rebuilt baseline_table.csv with {len(rows)} validated rows; skipped {len(skipped)} invalid manifests")
    for entry in skipped:
        print(f"  SKIP {entry}")
