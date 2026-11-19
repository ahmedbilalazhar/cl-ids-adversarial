"""Train-only pilot of the variable-input external method extension.

Loads external training features/labels only. Never loads external test members
or CICIDS final-test records. No test metrics are computed by this runner.
"""
from __future__ import annotations

import copy
import faulthandler
import hashlib
import json
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from src.phase3.common import array_identity, torch_seed
from src.phase3.reference import model_identity, snapshot
from src.phase3_external.model import ExternalMLP
from src.phase3_v2.learning import (admit, aggregate, client_state, commit_importance,
                                    expand_importance, train_client)
from src.phase3_v2.protocol import Settings

DATA = ROOT / "data/processed"
INPUTS = ROOT / "results/phase3-followup/external-method-inputs-v2"
PROTOCOL_PATH = ROOT / "configs/phase3/external-method-extension-v1.json"
OUT = ROOT / "results/phase3-followup/external-method-training-pilot-v1"
METHODS = (("FT", "NONE"), ("EI", "NONE"), ("DR", "NONE"), ("DR", "DC"))
DATASETS = ({"name": "UNSW-NB15", "stem": "unsw", "features": 194},
            {"name": "CICIoT2023", "stem": "iot", "features": 39})


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class ExternalStageInput:
    stage: int
    x: np.ndarray
    y: np.ndarray
    ids: np.ndarray
    owner: np.ndarray
    poison_mask: np.ndarray

    def targets(self, slots: list[int]) -> np.ndarray:
        mapping = {int(code): slot for slot, code in enumerate(slots)}
        try:
            return np.asarray([mapping[int(code)] for code in self.y], dtype=np.int64)
        except KeyError as exc:
            raise ValueError(f"Observed training label {exc.args[0]} has no active classifier slot") from exc


class ExternalTrainBank:
    def __init__(self, dataset: dict, seed: int, condition: str):
        self.dataset, self.seed, self.condition = dataset, seed, condition
        stem = dataset["stem"]
        self.meta_path = DATA / f"tasks_{stem}.json"
        self.archive_path = DATA / f"tasks_{stem}.npz"
        self.input_dir = INPUTS / stem / f"seed-{seed}"
        self.input_manifest_path = self.input_dir / "manifest.json"
        self.input_artifact = self.input_dir / "train-ownership-poison-mask.npz"
        self.metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))
        self.input_manifest = json.loads(self.input_manifest_path.read_text(encoding="utf-8"))
        if sha256(self.archive_path) != self.metadata["npz_sha256"]:
            raise ValueError(f"{dataset['name']}: external task archive changed")
        if self.input_manifest["artifact_sha256"] != sha256(self.input_artifact):
            raise ValueError(f"{dataset['name']}: ownership/poison artifact hash mismatch")
        self.label_map = {str(k): int(v) for k, v in self.metadata["label_map"].items()}
        self.benign_id = int(self.metadata["benign_id"])
        self.stages: list[ExternalStageInput] = []
        with np.load(self.input_artifact, allow_pickle=False) as prepared:
            prepared_task = np.asarray(prepared["task"], dtype=np.uint8)
            prepared_ids = np.asarray(prepared["row_id"], dtype=np.int64)
            prepared_y = np.asarray(prepared["y_train"], dtype=np.int16)
            prepared_owner = np.asarray(prepared["owner"], dtype=np.uint8)
            prepared_poison = np.asarray(prepared["poison_mask"], dtype=np.bool_)
        expected_n = sum(int(row["train"]) for row in self.metadata["task_sizes"])
        if not all(len(a) == expected_n for a in (prepared_task, prepared_ids, prepared_y, prepared_owner, prepared_poison)):
            raise ValueError(f"{dataset['name']}: prepared train ownership arrays have inconsistent lengths")
        if np.any(prepared_owner >= 5):
            raise ValueError(f"{dataset['name']}: invalid simulated owner ID")
        with np.load(self.archive_path, allow_pickle=False) as package:
            for task in range(int(self.metadata["n_tasks"])):
                # Deliberately request only training members; no t*_X_test/y_test/id_test keys.
                x_native = np.asarray(package[f"t{task}_X_train"])
                y_native = np.asarray(package[f"t{task}_y_train"], dtype=np.int16)
                ids_native = np.asarray(package[f"t{task}_id_train"], dtype=np.int64)
                if x_native.shape != (len(y_native), dataset["features"]):
                    raise ValueError(f"{dataset['name']}: task-{task} feature dimensions mismatch")
                if len(ids_native) != len(y_native) or not np.isfinite(x_native).all():
                    raise ValueError(f"{dataset['name']}: malformed or nonfinite training rows")
                positions = np.flatnonzero(prepared_task == task)
                if not (np.array_equal(prepared_ids[positions], ids_native)
                        and np.array_equal(prepared_y[positions], y_native)):
                    raise ValueError(f"{dataset['name']}: prepared ownership alignment differs at task {task}")
                order = np.argsort(ids_native, kind="stable")
                x = np.asarray(x_native[order], dtype=np.float32).copy()
                clean_y = y_native[order].astype(np.int64, copy=True)
                ids = ids_native[order].astype(np.uint64, copy=True)
                owner = prepared_owner[positions][order].astype(np.int8, copy=True)
                poison = prepared_poison[positions][order].copy()
                applied_mask = poison if condition == "poisoned" else np.zeros_like(poison)
                y = clean_y.copy()
                y[applied_mask] = self.benign_id
                if condition not in {"clean", "poisoned"}:
                    raise ValueError(f"Unsupported condition: {condition}")
                for arr in (x, y, ids, owner, poison):
                    arr.setflags(write=False)
                self.stages.append(ExternalStageInput(task + 1, x, y, ids, owner, poison))
        if len(self.stages) != 4 or not all(np.any(s.y == self.benign_id) for s in self.stages):
            raise ValueError(f"{dataset['name']}: expected four tasks with benign rows")
        if condition == "clean" and any(np.any(s.y != self._clean_labels_for(s.stage)) for s in self.stages):
            raise AssertionError("Clean condition labels changed")

    def _clean_labels_for(self, stage: int) -> np.ndarray:
        with np.load(self.archive_path, allow_pickle=False) as package:
            ids = np.asarray(package[f"t{stage-1}_id_train"], dtype=np.int64)
            labels = np.asarray(package[f"t{stage-1}_y_train"], dtype=np.int64)
        order = np.argsort(ids, kind="stable")
        return labels[order]


def configure_runtime() -> dict:
    torch.set_num_threads(1)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_float32_matmul_precision("highest")
    torch.set_default_dtype(torch.float32)
    return {"python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__,
            "device": "cpu", "threads": 1, "interop_threads": 1,
            "deterministic_algorithms": True, "amp": False, "dtype": "float32"}


def make_clients(settings: Settings, input_dim: int, max_width: int):
    clients = [client_state(settings, i) for i in range(5)]
    for client in clients:
        if client.replay is not None:
            client.replay["x"] = np.zeros((500, input_dim), dtype=np.float32)
            client.replay["z"] = np.zeros((500, max_width), dtype=np.float32)
    return clients


def validate_external_settings(settings: Settings, allowed_seeds: list[int]) -> None:
    """Validate the extension locally without widening the CIC development allowlist."""
    if settings.seed not in allowed_seeds:
        raise ValueError("Seed is absent from the external extension protocol")
    if settings.learner not in {"FT", "EI", "DR"} or settings.admission not in {"NONE", "DC"}:
        raise ValueError("Unsupported external pilot learner/admission pair")
    if (settings.learner == "DR") != (settings.admission == "DC") and settings.admission != "NONE":
        raise ValueError("External admission control requires DR")
    if (settings.rounds, settings.epochs) != (3, 1) or settings.dose not in {(0, 1), (1, 2)}:
        raise ValueError("External training budget or intervention dose differs from the frozen protocol")
    if settings.learning_rate <= 0 or any(not np.isfinite(v) or v < 0 for v in
                                          (settings.learning_rate, settings.lambda_E,
                                           settings.lambda_y, settings.lambda_z)):
        raise ValueError("Invalid external training coefficient")


def run_arm(dataset: dict, seed: int, learner: str, admission: str, condition: str,
            runtime: dict, settings_cfg: dict) -> dict:
    name, stem, input_dim = dataset["name"], dataset["stem"], dataset["features"]
    settings = Settings(learner=learner, admission=admission, seed=seed,
                        rounds=int(settings_cfg["rounds_per_task"]),
                        epochs=int(settings_cfg["epochs_per_round"]),
                        learning_rate=float(settings_cfg["learning_rate"]),
                        lambda_E=float(settings_cfg["lambda_E"]),
                        lambda_y=float(settings_cfg["lambda_y"]),
                        lambda_z=float(settings_cfg["lambda_z"]),
                        dose=(1, 2) if condition == "poisoned" else (0, 1))
    validate_external_settings(settings, [101, 202, 303])
    data_bank = ExternalTrainBank(dataset, seed, condition)
    clients = make_clients(settings, input_dim, len(data_bank.label_map))
    model = None
    slots: list[int] = []
    all_seen: set[int] = set()
    trajectory = []
    ledger = []
    stage_checkpoints = []
    started = time.perf_counter()

    for data in data_bank.stages:
        new_codes = [int(v) for v in sorted(set(map(int, data.y))) if int(v) not in all_seen]
        if not new_codes and model is None:
            raise ValueError("First external task has no trainable classes")
        if not slots:
            slots.extend(new_codes)
            if data_bank.benign_id not in slots or slots[0] != data_bank.benign_id:
                raise ValueError("Benign must be the initial external output slot")
            model = ExternalMLP(input_dim, len(slots), seed)
        else:
            slots.extend(new_codes)
            if new_codes:
                model.expand(len(slots), data.stage, seed)
        if learner == "EI":
            for client in clients:
                expand_importance(client, model)
        scores = admit(model, data, slots, set(new_codes), clients, settings, ledger)
        active = [len(c.accepted) for c in clients]
        stage_rows = []
        for round_id in range(1, settings.rounds + 1):
            broadcast = snapshot(model)
            before = model_identity(model, slots)
            updates, rows = [], []
            for client_id, client in enumerate(clients):
                update, row = train_client(broadcast, model, client, data, slots,
                                           settings, round_id, client_id)
                updates.append(update)
                rows.append(row)
            combined, weights = aggregate(broadcast, updates, active)
            model.load_state_dict(combined)
            after = model_identity(model, slots)
            stage_rows.append({"round": round_id, "broadcast_sha256": before,
                               "aggregate_sha256": after, "weights": weights, "clients": rows})
            ledger.append({"kind": "round", "stage": data.stage, **stage_rows[-1]})
        if learner == "EI":
            commit_importance(model, clients, data, slots, settings, ledger)
        poison_rows = int(np.count_nonzero(data.poison_mask)) if condition == "poisoned" else 0
        stage_report = {
            "stage": data.stage,
            "new_label_ids": new_codes,
            "active_slots": slots.copy(),
            "train_rows": len(data.y),
            "clean_source_rows": int(np.count_nonzero(data.poison_mask)),
            "poisoned_rows": poison_rows,
            "class_counts_supplied": {str(k): int(v) for k, v in zip(*np.unique(data.y, return_counts=True))},
            "owner_rows": [int(np.count_nonzero(data.owner == i)) for i in range(5)],
            "admitted_rows": active,
            "admission_score_sha256": array_identity(scores),
            "rounds": stage_rows,
            "model_sha256": model_identity(model, slots),
        }
        trajectory.append(stage_report)
        stage_checkpoints.append({"stage": data.stage, "model_sha256": stage_report["model_sha256"],
                                  "state_dict": {k: v.detach().cpu().numpy().copy()
                                                 for k, v in model.state_dict().items()},
                                  "slots": slots.copy()})
        all_seen.update(new_codes)

    arm_dir = OUT / stem / f"seed-{seed}" / f"{learner}-{admission}-{condition}"
    arm_dir.mkdir(parents=True, exist_ok=True)
    if any(arm_dir.iterdir()):
        raise FileExistsError(arm_dir)
    for record in stage_checkpoints:
        path = arm_dir / f"stage-{record['stage']}-model.npz"
        np.savez_compressed(path, **record["state_dict"])
    (arm_dir / "slots.json").write_text(json.dumps([r["slots"] for r in stage_checkpoints], indent=2) + "\n", encoding="utf-8")
    result = {
        "schema": "phase3-external-method-trainpilot-arm-v1",
        "dataset": name,
        "protocol_id": data_bank.metadata["protocol_id"],
        "dataset_artifact_sha256": sha256(data_bank.archive_path),
        "training_input_manifest_sha256": sha256(data_bank.input_manifest_path),
        "training_input_artifact_sha256": sha256(data_bank.input_artifact),
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "learner": learner,
        "admission": admission,
        "condition": condition,
        "seed": seed,
        "settings": {"rounds": settings.rounds, "epochs": settings.epochs,
                      "learning_rate": settings.learning_rate, "lambda_E": settings.lambda_E,
                      "lambda_y": settings.lambda_y, "lambda_z": settings.lambda_z},
        "input_dim": input_dim,
        "class_count": len(data_bank.label_map),
        "stages": trajectory,
        "ledger": ledger,
        "stage_checkpoints": [
            {"stage": r["stage"], "model_sha256": r["model_sha256"],
             "file_sha256": sha256(arm_dir / f"stage-{r['stage']}-model.npz")}
            for r in stage_checkpoints
        ],
        "runtime": runtime,
        "elapsed_seconds": time.perf_counter() - started,
        "feature_arrays_accessed": True,
        "external_test_arrays_accessed": False,
        "cicids_final_test_accessed": False,
        "test_metrics_computed": False,
        "interpretation": "Train-only exploratory adapter pilot; synthetic owners; not a faithful external replication.",
    }
    run_path = arm_dir / "run.json"
    run_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return {"dataset": name, "seed": seed, "learner": learner, "admission": admission,
            "condition": condition, "elapsed_seconds": result["elapsed_seconds"],
            "stages": len(trajectory), "final_model_sha256": trajectory[-1]["model_sha256"],
            "run": run_path.relative_to(ROOT).as_posix(),
            "external_test_arrays_accessed": False, "cicids_final_test_accessed": False}


def main() -> None:
    faulthandler.enable()
    config = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if config["status"] != "train_only_pilot_authorized_test_scoring_gated":
        raise ValueError("Protocol status does not allow the train-only pilot")
    pilot = config["training"]
    seeds = [int(seed) for seed in config["client_simulation"]["seeds"]]
    if seeds != [101, 202, 303] or int(pilot["pilot_seed"]) != seeds[0]:
        raise ValueError("External method pilot seed set differs from the frozen configuration")
    runtime = configure_runtime()
    manifests = []
    OUT.mkdir(parents=True, exist_ok=True)
    for dataset in DATASETS:
        for seed in seeds:
            for learner, admission in METHODS:
                for condition in ("clean", "poisoned"):
                    arm_dir = OUT / dataset["stem"] / f"seed-{seed}" / f"{learner}-{admission}-{condition}"
                    run_path = arm_dir / "run.json"
                    if run_path.exists():
                        prior = json.loads(run_path.read_text(encoding="utf-8"))
                        if prior.get("external_test_arrays_accessed") is not False or prior.get("test_metrics_computed") is not False:
                            raise ValueError(f"Existing arm violates train-only boundary: {run_path}")
                        manifests.append({"dataset": dataset["name"], "seed": seed,
                                          "learner": learner, "admission": admission,
                                          "condition": condition, "elapsed_seconds": prior["elapsed_seconds"],
                                          "stages": len(prior["stages"]),
                                          "final_model_sha256": prior["stages"][-1]["model_sha256"],
                                          "run": run_path.relative_to(ROOT).as_posix(),
                                          "external_test_arrays_accessed": False,
                                          "cicids_final_test_accessed": False})
                        print(json.dumps({"status": "already_completed", **manifests[-1]}), flush=True)
                        continue
                    if arm_dir.exists() and any(arm_dir.iterdir()):
                        raise RuntimeError(f"Incomplete arm artifacts found; preserved for review: {arm_dir}")
                    print(json.dumps({"status": "starting", "dataset": dataset["name"],
                                      "learner": learner, "admission": admission,
                                      "condition": condition, "seed": seed}), flush=True)
                    manifests.append(run_arm(dataset, seed, learner, admission,
                                             condition, runtime, pilot))
                    print(json.dumps({"status": "completed", **manifests[-1]}), flush=True)
    summary = {
        "schema": "phase3-external-method-training-pilot-v1",
        "status": "completed_train_only_pilot_no_test_metrics",
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "runtime": runtime,
        "runs": manifests,
        "feature_arrays_accessed": True,
        "external_test_arrays_accessed": False,
        "cicids_final_test_accessed": False,
        "test_metrics_computed": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "completed_runs": len(manifests),
                      "external_test_arrays_accessed": False, "cicids_final_test_accessed": False}, indent=2))


if __name__ == "__main__":
    main()
