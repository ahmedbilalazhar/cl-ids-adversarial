"""Clean DR+DC development reference; intentionally cannot dispatch a GPU grid.

Checkpoints commit an entire federated round. An interrupted round rolls back
all five clients to the previous transaction and is replayed in full. Adam is
fresh at every broadcast, so no live optimizer exists at a committed boundary.
"""
from __future__ import annotations

import argparse
import copy
import platform
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from .common import (ROOT, array_identity, canonical, decode_rng, digest, encode_rng, identity,
                     load_state, read_json, reference_protocol, rng, save_state, state_identity, torch_seed, write_json)
from .model import ReferenceMLP


def code_identity():
    return identity({p.name: digest(p) for p in sorted((ROOT/"src/phase3").glob("*.py"))})


def runtime(config):
    if torch.__version__ != config["runtime"]["torch"] or np.__version__ != config["runtime"]["numpy"]:
        raise RuntimeError("Reference runtime differs from the pinned CPU protocol")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_float32_matmul_precision("highest")
    torch.set_default_dtype(torch.float32)
    return {"python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__,
            "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor(),
            "device": "cpu", "threads": torch.get_num_threads(), "interop_threads": torch.get_num_interop_threads(),
            "deterministic_algorithms": True, "amp": False, "default_dtype": str(torch.get_default_dtype()),
            "torch_build": torch.__config__.show()}


def new_client(seed, client):
    generator = torch.Generator(device="cpu").manual_seed(torch_seed(10, seed, client))
    return {"x": np.zeros((500, 74), dtype="<f4"), "y": np.zeros(500, dtype="<i8"),
            "ids": np.zeros(500, dtype="<u8"), "z": np.zeros((500, 16), dtype="<f4"),
            "width": np.zeros(500, dtype="u1"), "size": 0, "seen": 0,
            "draw": rng(7, seed, client), "insert": rng(8, seed, client),
            "dropout": generator.get_state().numpy().copy(), "updates": 0,
            "current_exposures": 0, "replay_exposures": 0,
            "accepted": np.empty(0, dtype="<i8")}


def snapshot(model):
    return {k: v.detach().clone() for k, v in model.state_dict().items()}


def model_identity(model, slots):
    return identity({"slots": slots, "weights": {k: array_identity(v.detach().numpy()) for k, v in model.state_dict().items()}})


def load_stage(worker, stage, slots=None):
    path = worker/f"E{stage}"
    arrays = {k: np.load(path/f"{k}.npy", allow_pickle=False) for k in ("x", "y", "ids", "owner")}
    n = len(arrays["y"])
    if arrays["x"].shape != (n, 74) or arrays["x"].dtype != np.float32 or not np.isfinite(arrays["x"]).all():
        raise RuntimeError("Bad worker features")
    if any(len(v) != n for v in arrays.values()) or np.unique(arrays["ids"]).size != n:
        raise RuntimeError("Unaligned/non-unique worker rows")
    if not np.all((arrays["owner"] >= 0) & (arrays["owner"] < 5)):
        raise RuntimeError("Bad logical client owner")
    if slots is not None:
        mapping = {code: slot for slot, code in enumerate(slots)}
        arrays["target"] = np.array([mapping[int(y)] for y in arrays["y"]], dtype=np.int64)
    return arrays


def admit(model, data, slots, new_codes, clients, stage, ledger):
    model.eval()
    scorer_hash = model_identity(model, slots)
    y = data["target"]
    scores = np.empty(len(y), dtype=np.float32)
    with torch.no_grad():
        for start in range(0, len(y), 2048):
            end = start+2048
            values = F.cross_entropy(model(torch.from_numpy(data["x"][start:end])),
                                     torch.from_numpy(y[start:end]), reduction="none")
            scores[start:end] = values.numpy()
    if not np.isfinite(scores).all():
        raise FloatingPointError("Non-finite frozen admission score")
    rows = []
    for client in range(5):
        indexes = np.flatnonzero(data["owner"] == client)
        accepted = []
        quotas = []
        for code in np.unique(data["y"][indexes]):
            group = indexes[data["y"][indexes] == code]
            protected = int(code) in new_codes or len(group) < 20
            count = len(group) if protected else (3*len(group)+3)//4
            rank = np.lexsort((data["ids"][group], scores[group]))
            accepted.extend(group[rank[:count]].tolist())
            quotas.append({"source_code": int(code), "raw": len(group), "admitted": count, "protected": protected})
        accepted = np.asarray(accepted, dtype=np.int64)
        accepted = accepted[np.argsort(data["ids"][accepted], kind="stable")]
        clients[client]["accepted"] = accepted
        rows.append({"client": client, "raw": len(indexes), "admitted": len(accepted), "quotas": quotas,
                     "admitted_ids_sha256": array_identity(data["ids"][accepted])})
    if not any(len(c["accepted"]) for c in clients):
        raise RuntimeError("All clients inactive: invalid stage")
    ledger.append({"kind": "admission", "stage": stage, "expanded_head_width": len(slots),
                   "scorer_model_sha256": scorer_hash, "score_ids_sha256": array_identity(data["ids"]),
                   "scores_sha256": array_identity(scores), "clients": rows})
    return scores


def insert_batch(client, x, labels, ids, teachers, width):
    for i in range(len(labels)):
        client["seen"] += 1
        seen = client["seen"]
        slot = seen-1 if seen <= 500 else int(client["insert"].integers(0, seen))
        if slot < 500:
            client["x"][slot] = x[i]
            client["y"][slot] = labels[i]
            client["ids"][slot] = ids[i]
            client["z"][slot].fill(0)
            client["z"][slot, :width] = teachers[i]
            client["width"][slot] = width
        client["size"] = min(500, seen)


def train_client(broadcast, template, client, data, slots, config, stage, round_id, client_id):
    indexes = client["accepted"]
    if not len(indexes):
        return None, {"client": client_id, "admitted": 0, "optimizer_updates": 0, "inactive": True}
    local = copy.deepcopy(template)
    local.load_state_dict(broadcast)
    optimizer = torch.optim.Adam(local.parameters(), lr=config["learning_rate"], betas=(.9, .999), eps=1e-8,
                                 weight_decay=0, amsgrad=False, foreach=False, fused=False)
    if optimizer.state:
        raise RuntimeError("Adam must start empty at every broadcast")
    seed = config["seed"]
    mapping = {code: slot for slot, code in enumerate(slots)}
    updates = 0
    current_exposures = 0
    replay_exposures = 0
    replay_batches = 0
    full_replay_with_short_current = 0
    proposals_before = client["seen"]
    summed_current = 0.0
    summed_replay = 0.0
    summed_dark = 0.0
    raw_indexes = np.flatnonzero(data["owner"] == client_id)
    accepted_mask = np.zeros(len(data["y"]), dtype=bool)
    accepted_mask[indexes] = True
    with torch.random.fork_rng(devices=[]):
        torch.set_rng_state(torch.from_numpy(client["dropout"].copy()))
        for epoch in range(1, config["epochs"]+1):
            raw_order = rng(6, seed, client_id, stage, round_id, epoch).permutation(raw_indexes)
            order = raw_order[accepted_mask[raw_order]]
            if len(order) != len(indexes):
                raise RuntimeError("Admitted subsequence does not cover the local pool")
            for start in range(0, len(order), 128):
                current = order[start:start+128]
                x = torch.from_numpy(data["x"][current])
                y = torch.from_numpy(data["target"][current])
                proposal_pass = round_id == 1 and epoch == 1
                local.eval()
                teachers = None
                if proposal_pass:
                    with torch.no_grad():
                        teachers = local(x).numpy().copy()
                    if not np.isfinite(teachers).all():
                        raise FloatingPointError("Non-finite pre-update teacher")
                # Draw from the old buffer before the optimizer step and insertion.
                replay = None
                if client["size"]:
                    draw = client["draw"].choice(client["size"], min(128, client["size"]), replace=False)
                    replay = {k: client[k][draw].copy() for k in ("x", "y", "z", "width")}
                    if np.any(replay["width"] == 0) or np.any(replay["width"] > len(slots)):
                        raise RuntimeError("Invalid stored dark-logit width")
                local.train()
                optimizer.zero_grad(set_to_none=True)
                current_loss = F.cross_entropy(local(x), y)
                total = current_loss
                replay_loss = torch.zeros((), dtype=torch.float32)
                dark_loss = torch.zeros((), dtype=torch.float32)
                if replay is not None:
                    rx = torch.from_numpy(replay["x"])
                    ry = torch.tensor([mapping[int(label)] for label in replay["y"]], dtype=torch.int64)
                    replay_loss = F.cross_entropy(local(rx), ry)
                    local.eval()
                    predicted = local(rx)  # eval mode with gradients; dropout is disabled
                    widths = torch.from_numpy(replay["width"].astype(np.int64))
                    valid = torch.arange(len(slots))[None, :] < widths[:, None]
                    difference = torch.where(valid, predicted-torch.from_numpy(replay["z"][:, :len(slots)]), 0)
                    dark_loss = (difference.square().sum(dim=1)/widths).mean()
                    total = total+config["lambda_y"]*replay_loss+config["lambda_z"]*dark_loss
                    local.train()
                if not bool(torch.isfinite(total)):
                    raise FloatingPointError("Non-finite reference objective")
                total.backward()
                if any(p.grad is not None and not bool(torch.isfinite(p.grad).all()) for p in local.parameters()):
                    raise FloatingPointError("Non-finite reference gradient")
                optimizer.step()
                if any(not bool(torch.isfinite(p).all()) for p in local.parameters()):
                    raise FloatingPointError("Non-finite reference weight")
                if any(not bool(torch.isfinite(value).all()) for state in optimizer.state.values()
                       for value in state.values() if isinstance(value, torch.Tensor)):
                    raise FloatingPointError("Non-finite Adam state")
                if proposal_pass:
                    insert_batch(client, data["x"][current], data["y"][current], data["ids"][current], teachers, len(slots))
                updates += 1
                current_exposures += len(current)
                replay_exposures += 0 if replay is None else len(replay["y"])
                replay_batches += int(replay is not None)
                full_replay_with_short_current += int(replay is not None and len(current) < 128 and len(replay["y"]) == 128)
                summed_current += float(current_loss.detach())
                summed_replay += float(replay_loss.detach())
                summed_dark += float(dark_loss.detach())
        client["dropout"] = torch.get_rng_state().numpy().copy()
    client["updates"] += updates
    client["current_exposures"] += current_exposures
    client["replay_exposures"] += replay_exposures
    expected_proposals = len(indexes) if round_id == 1 else 0
    if client["seen"]-proposals_before != expected_proposals:
        raise RuntimeError("Reservoir stream repeated a current record")
    return snapshot(local), {"client": client_id, "admitted": len(indexes), "inactive": False,
             "optimizer_updates": updates, "adam_reset": True, "current_exposures": current_exposures,
             "replay_exposures": replay_exposures, "proposals": expected_proposals,
             "replay_batches": replay_batches, "full_replay_with_short_current_batches": full_replay_with_short_current,
             "buffer_occupancy": client["size"], "reservoir_seen": client["seen"],
             "mean_current_batch_ce": summed_current/updates,
             "mean_replay_batch_ce": summed_replay/updates, "mean_dark_batch_loss": summed_dark/updates}


def pack(model, clients, metadata):
    arrays = {"model."+k: v.detach().numpy().copy() for k, v in model.state_dict().items()}
    metadata = copy.deepcopy(metadata)
    metadata["clients"] = []
    for i, client in enumerate(clients):
        metadata["clients"].append({k: encode_rng(v) if k in {"draw", "insert"} else v
                                     for k, v in client.items() if not isinstance(v, np.ndarray)})
        for k, v in client.items():
            if isinstance(v, np.ndarray):
                arrays[f"client{i}.{k}"] = v.copy()
    return metadata, arrays


def unpack(metadata, arrays, seed):
    model = ReferenceMLP(len(metadata["slots"]), seed)
    model.load_state_dict({k[6:]: torch.from_numpy(v) for k, v in arrays.items() if k.startswith("model.")})
    clients = []
    for i, info in enumerate(metadata["clients"]):
        client = {k: decode_rng(v) if k in {"draw", "insert"} else v for k, v in info.items()}
        prefix = f"client{i}."
        client.update({k[len(prefix):]: v.copy() for k, v in arrays.items() if k.startswith(prefix)})
        clients.append(client)
    metadata = {k: v for k, v in metadata.items() if k != "clients"}
    return model, clients, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT/"configs/phase3/reference74-v1.json")
    parser.add_argument("--train-package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--stop-after-commits", type=int)
    args = parser.parse_args()
    config = reference_protocol(args.protocol)
    if config["learner"] != "DR" or config["admission"] != "DC" or config["dose"] != [0, 1] or not config["reference_only"]:
        raise ValueError("This executable accepts only the adopted clean DR+DC reference")
    if args.output.exists():
        raise FileExistsError("Use a new output directory, including for resumed suffixes")
    args.output.mkdir(parents=True)
    runtime_info = runtime(config)
    write_json(args.output/"runtime.json", {**runtime_info, "executable": sys.executable})
    manifest = read_json(args.train_package/"manifest.json")
    if manifest["protocol_sha256"] != digest(args.protocol):
        raise RuntimeError("Prepared bundle uses another protocol")
    expected_files = set(manifest["files"])
    actual_files = {p.relative_to(args.train_package).as_posix() for p in args.train_package.rglob("*") if p.is_file()}
    if actual_files != expected_files | {"manifest.json"}:
        raise RuntimeError("Unexpected files in training-only package")
    for path, expected in manifest["files"].items():
        if digest(args.train_package/path) != expected:
            raise RuntimeError(f"Worker array hash mismatch: {path}")
    execution = {"protocol_sha256": digest(args.protocol), "train_manifest_sha256": digest(args.train_package/"manifest.json"),
                 "code_identity": code_identity(), "runtime_identity": identity(runtime_info)}
    seed = config["seed"]
    if args.resume:
        commit = read_json(args.resume.with_suffix(".commit.json"))
        if digest(args.resume) != commit["file_sha256"]:
            raise RuntimeError("Resume transaction payload hash mismatch")
        meta, arrays = load_state(args.resume)
        if state_identity(meta, arrays) != commit["state_identity"]:
            raise RuntimeError("Resume logical state identity mismatch")
        if meta["execution"] != execution:
            raise RuntimeError("Resume code/data/protocol/runtime identity mismatch")
        model, clients, meta = unpack(meta, arrays, seed)
    else:
        model = None
        clients = [new_client(seed, i) for i in range(5)]
        meta = {"schema": "phase3-round-transaction-v1", "execution": execution, "slots": [], "stage": 1,
                "round": 1, "admission_stage": 0, "ledger": [], "commits": 0}
    started = time.perf_counter()
    checkpoints = []
    while meta["stage"] <= 4:
        stage, round_id = meta["stage"], meta["round"]
        data = load_stage(args.train_package, stage)
        if meta["admission_stage"] != stage:
            observed = sorted(set(int(y) for y in data["y"]))
            new_codes = [code for code in observed if code not in meta["slots"]]
            if stage == 1 and (not new_codes or new_codes[0] != 0):
                raise RuntimeError("Benign must be the first active class")
            meta["slots"].extend(new_codes)
            if model is None:
                model = ReferenceMLP(len(meta["slots"]), seed)
            else:
                model.expand(len(meta["slots"]), stage, seed)
            data = load_stage(args.train_package, stage, meta["slots"])
            scores = admit(model, data, meta["slots"], set(new_codes), clients, stage, meta["ledger"])
            np.savez(args.output/f"E{stage}-admission.npz", ids=data["ids"], scores=scores,
                     **{f"client{i}_accepted_ids": data["ids"][c["accepted"]] for i, c in enumerate(clients)})
            meta["admission_stage"] = stage
        else:
            data = load_stage(args.train_package, stage, meta["slots"])
        broadcast = snapshot(model)
        before = model_identity(model, meta["slots"])
        local_states = []
        rows = []
        for i, client in enumerate(clients):
            update, row = train_client(broadcast, model, client, data, meta["slots"], config, stage, round_id, i)
            local_states.append(update)
            rows.append(row)
        if model_identity(model, meta["slots"]) != before:
            raise RuntimeError("Local updates mutated the broadcast")
        counts = [len(c["accepted"]) for c in clients]
        total = sum(counts)
        if not total:
            raise RuntimeError("No active aggregation weight")
        combined = {key: torch.zeros_like(value) for key, value in broadcast.items()}
        weights = []
        for count, update in zip(counts, local_states):
            weight = float(np.float32(count/total))
            weights.append(weight)
            if count:
                for key in combined:
                    combined[key].add_(update[key]*weight)
        if abs(sum(weights)-1) > 5e-7:
            raise RuntimeError("Aggregation weights do not sum to one")
        model.load_state_dict(combined)
        shared_hash = model_identity(model, meta["slots"])
        meta["ledger"].append({"kind": "round", "stage": stage, "round": round_id,
                               "broadcast_sha256": before, "aggregate_sha256": shared_hash,
                               "five_final_client_model_identities": [shared_hash]*5,
                               "weights_fp32": weights, "clients": rows})
        meta["commits"] += 1
        stage_end = round_id == config["rounds"]
        meta["stage"] = stage+1 if stage_end else stage
        meta["round"] = 1 if stage_end else round_id+1
        metadata, arrays = pack(model, clients, meta)
        checkpoint = args.output/f"E{stage}-R{round_id}.npz"
        save_state(checkpoint, metadata, arrays)
        checkpoint_row = {"stage": stage, "round": round_id, "stage_end": stage_end, "file": checkpoint.name,
                          "file_sha256": digest(checkpoint), "state_identity": state_identity(metadata, arrays),
                          "head_width": len(meta["slots"]), "source_codes_in_slot_order": meta["slots"].copy()}
        checkpoints.append(checkpoint_row)
        write_json(checkpoint.with_suffix(".commit.json"), checkpoint_row)
        print(canonical({**checkpoint_row, "elapsed_seconds": round(time.perf_counter()-started, 3)}), flush=True)
        if args.stop_after_commits is not None and len(checkpoints) >= args.stop_after_commits:
            break
    complete = meta["stage"] == 5
    write_json(args.output/"run.json", {"status": "complete_reference" if complete else "stopped_at_committed_boundary",
               "execution": execution, "logical_reference_only": True, "final_test_accessed": False,
               "gpu_grid_launched": False, "resumed_from": None if not args.resume else str(args.resume.resolve()),
               "checkpoints": checkpoints, "ledger": meta["ledger"], "elapsed_seconds": time.perf_counter()-started,
               "total_commits": meta["commits"], "final_model_sha256": model_identity(model, meta["slots"]),
               "next_cursor": [meta["stage"], meta["round"]]})


if __name__ == "__main__":
    main()
