"""Prepare synthetic persistent owners and train-only poison masks for the external extension.

Never requests any feature or test array. The artifacts contain task-local row IDs,
training labels, synthetic client owners, and the task-1 poison mask only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
RESULTS = ROOT / "results/phase3-followup"
CONFIG_PATH = ROOT / "configs/phase3/external-method-extension-v1.json"
SUPPORT_PATH = RESULTS / "external-training-support-audit-v1.json"
ID_AUDIT_PATH = RESULTS / "external-id-isolation-audit-v1.json"
OUT = RESULTS / "external-method-inputs-v2"
SEEDS = (101, 202, 303)
N_CLIENTS = 5
DIRICHLET_ALPHA = 0.5
MIN_SOURCE_ROWS_PER_CLIENT = 50
DATASETS = (
    {"name": "UNSW-NB15", "stem": "unsw", "code": 1},
    {"name": "CICIoT2023", "stem": "iot", "code": 2},
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def generator(*parts: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([1, *parts])))


def prepare_dataset(dataset: dict, config: dict, support: dict, id_audit: dict) -> list[dict]:
    name, stem, code = dataset["name"], dataset["stem"], dataset["code"]
    entry = config["datasets"][name]
    meta_path, archive_path = DATA / f"tasks_{stem}.json", DATA / f"tasks_{stem}.npz"
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    if metadata["protocol_id"] != entry["protocol_id"]:
        raise ValueError(f"{name}: protocol ID changed")
    if sha256(archive_path) != metadata["npz_sha256"]:
        raise ValueError(f"{name}: task archive hash differs from metadata")
    support_entry = next(x for x in support["datasets"] if x["dataset"] == name)
    ids_entry = next(x for x in id_audit["datasets"] if x["dataset"] == name)
    if not support_entry["feasible_for_source_to_benign_pilot"]:
        raise ValueError(f"{name}: no train-label source class meets the frozen support rule")
    if not (ids_entry["train_task_ids_disjoint"] and ids_entry["test_task_ids_disjoint"]):
        raise ValueError(f"{name}: task ID audit has a collision")
    source_name = entry["task_1_source"]
    source_id = int(metadata["label_map"][source_name])
    benign_id = int(metadata["benign_id"])
    if source_id == benign_id:
        raise ValueError(f"{name}: source and benign labels must differ")

    task_ids: list[np.ndarray] = []
    task_labels: list[np.ndarray] = []
    # Request only train labels and train IDs; do not index feature/test members.
    with np.load(archive_path, allow_pickle=False) as package:
        for task in range(int(metadata["n_tasks"])):
            ids = np.asarray(package[f"t{task}_id_train"], dtype=np.int64)
            labels = np.asarray(package[f"t{task}_y_train"], dtype=np.int16)
            if ids.ndim != 1 or labels.ndim != 1 or ids.size != labels.size:
                raise ValueError(f"{name}: malformed task-{task} train IDs/labels")
            if np.unique(ids).size != ids.size:
                raise ValueError(f"{name}: duplicate train IDs in task {task}")
            task_ids.append(ids)
            task_labels.append(labels)

    task_index = np.concatenate([np.full(len(ids), t, dtype=np.uint8) for t, ids in enumerate(task_ids)])
    row_ids = np.concatenate(task_ids)
    labels_all = np.concatenate(task_labels)
    if int(np.sum((task_index == 1) & (labels_all == source_id))) != support_entry["selected_source_t1_train_rows"]:
        raise ValueError(f"{name}: selected task-1 support differs from frozen audit")

    outputs = []
    for seed in SEEDS:
        owner_rng = generator(1, code, seed)
        owners = np.full(labels_all.size, 255, dtype=np.uint8)
        for label_id in sorted(int(v) for v in np.unique(labels_all)):
            group = np.flatnonzero(labels_all == label_id)
            order = np.lexsort((row_ids[group], task_index[group]))
            group = group[order]
            shares = owner_rng.dirichlet(np.full(N_CLIENTS, DIRICHLET_ALPHA))
            counts = owner_rng.multinomial(group.size, shares)
            permuted = owner_rng.permutation(group)
            cursor = 0
            for client, count in enumerate(counts):
                owners[permuted[cursor:cursor + count]] = client
                cursor += int(count)
        if np.any(owners == 255):
            raise AssertionError(f"{name}: an external training row lacks a synthetic owner")

        attacker_rng = generator(2, code, seed)
        eligible = [
            client for client in range(N_CLIENTS)
            if int(np.sum((task_index == 1) & (labels_all == source_id) & (owners == client))) >= MIN_SOURCE_ROWS_PER_CLIENT
        ]
        if not eligible:
            raise ValueError(f"{name}, seed {seed}: no eligible simulated attacker client")
        attacker = int(attacker_rng.choice(np.asarray(eligible, dtype=np.int64)))
        source_rows = np.flatnonzero((task_index == 1) & (labels_all == source_id) & (owners == attacker))
        source_rows = source_rows[np.argsort(row_ids[source_rows], kind="stable")]
        poison_count = source_rows.size // 2
        poison_rng = generator(3, code, seed)
        chosen = poison_rng.permutation(source_rows)[:poison_count]
        poison_mask = np.zeros(labels_all.size, dtype=np.bool_)
        poison_mask[chosen] = True
        if np.any(poison_mask & (labels_all != source_id)) or np.any(poison_mask & (task_index != 1)):
            raise AssertionError(f"{name}: poison mask escaped the selected task-1 source rows")
        if np.any(poison_mask & (owners != attacker)):
            raise AssertionError(f"{name}: poison mask escaped the selected attacker")

        out_dir = OUT / stem / f"seed-{seed}"
        out_dir.mkdir(parents=True, exist_ok=True)
        artifact = out_dir / "train-ownership-poison-mask.npz"
        manifest_path = out_dir / "manifest.json"
        if artifact.exists() or manifest_path.exists():
            raise FileExistsError(out_dir)
        np.savez_compressed(artifact, task=task_index, row_id=row_ids, y_train=labels_all,
                            owner=owners, poison_mask=poison_mask)
        manifest = {
            "schema": "phase3-external-method-input-v1",
            "dataset": name,
            "protocol_id": metadata["protocol_id"],
            "seed": seed,
            "task_archive_sha256": sha256(archive_path),
            "metadata_sha256": sha256(meta_path),
            "support_audit_sha256": sha256(SUPPORT_PATH),
            "id_audit_sha256": sha256(ID_AUDIT_PATH),
            "input_kind": "training labels and task-local training row IDs only",
            "artifact_sha256": sha256(artifact),
            "n_clients": N_CLIENTS,
            "dirichlet_alpha": DIRICHLET_ALPHA,
            "source_label": source_name,
            "source_label_id": source_id,
            "benign_label_id": benign_id,
            "attacker_client": attacker,
            "eligible_attacker_clients": eligible,
            "task1_source_rows_on_attacker": int(source_rows.size),
            "poisoned_rows": int(poison_count),
            "realized_dose": [int(poison_count), int(source_rows.size)],
            "train_rows": int(labels_all.size),
            "feature_arrays_accessed": False,
            "test_arrays_accessed": False,
            "cicids_final_test_accessed": False,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        outputs.append({"dataset": name, "seed": seed,
                        "artifact": artifact.relative_to(ROOT).as_posix(),
                        "manifest": manifest_path.relative_to(ROOT).as_posix(),
                        "attacker_client": attacker, "poisoned_rows": int(poison_count),
                        "source_rows": int(source_rows.size), "artifact_sha256": manifest["artifact_sha256"]})
    return outputs


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if config["status"] != "train_only_pilot_authorized_test_scoring_gated":
        raise ValueError("Protocol status differs from the train-only pilot contract")
    support = json.loads(SUPPORT_PATH.read_text(encoding="utf-8"))
    id_audit = json.loads(ID_AUDIT_PATH.read_text(encoding="utf-8"))
    if support.get("test_arrays_accessed") is not False or id_audit.get("feature_arrays_accessed") is not False:
        raise ValueError("Input-audit boundaries differ from the expected train-only/ID-only contract")
    all_rows = []
    for dataset in DATASETS:
        all_rows.extend(prepare_dataset(dataset, config, support, id_audit))
    result = {
        "schema": "phase3-external-method-inputs-v1",
        "status": "synthetic_client_training_inputs_prepared_no_models_run",
        "protocol_sha256": sha256(CONFIG_PATH),
        "rows": all_rows,
        "feature_arrays_accessed": False,
        "test_arrays_accessed": False,
        "cicids_final_test_accessed": False,
        "model_training_performed": False,
    }
    summary_path = RESULTS / "external-method-inputs-summary-v2.json"
    if summary_path.exists():
        raise FileExistsError(summary_path)
    summary_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(summary_path), "status": result["status"],
                      "prepared_runs": len(all_rows), "models_run": False,
                      "features_accessed": False, "test_arrays_accessed": False,
                      "cicids_final_test_accessed": False}, indent=2))


if __name__ == "__main__":
    main()
