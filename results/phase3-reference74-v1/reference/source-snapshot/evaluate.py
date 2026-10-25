"""Read-only development evaluation, separated from the training executable."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from .common import ROOT, array_identity, canonical, digest, load_state, read_json, reference_protocol, write_json
from .model import ReferenceMLP
from .reference import code_identity, model_identity, runtime


def ratio(numerator, denominator):
    return None if denominator == 0 else numerator/denominator


def counts_for(y, predicted, codes, names):
    matrix = np.zeros((16, 16), dtype=np.int64)
    np.add.at(matrix, (y, predicted), 1)
    metrics = []
    for code in codes:
        tp = int(matrix[code, code])
        support = int(matrix[code].sum())
        predicted_count = int(matrix[:, code].sum())
        fp, fn = predicted_count-tp, support-tp
        metrics.append({"family": names[code], "code": code, "support": support, "tp": tp, "fp": fp, "fn": fn,
                        "precision": ratio(tp, predicted_count), "recall": ratio(tp, support),
                        "f1": ratio(2*tp, 2*tp+fp+fn) if support else None,
                        "status": "supported" if support else "no_positive_development_records"})
    return matrix.tolist(), metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT/"configs/phase3/reference74-v1.json")
    parser.add_argument("--development-package", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Evaluation outputs are immutable")
    config = reference_protocol(args.protocol)
    runtime(config)
    run = read_json(args.run/"run.json")
    if run["status"] != "complete_reference" or run["execution"]["code_identity"] != code_identity():
        raise RuntimeError("A complete compatible reference run is required")
    manifest = read_json(args.development_package/"manifest.json")
    if manifest["role"] != "development_only" or manifest["protocol_sha256"] != digest(args.protocol):
        raise RuntimeError("Only the locked development bank is accepted")
    if manifest["train_manifest_sha256"] != run["execution"]["train_manifest_sha256"]:
        raise RuntimeError("Development and training package identities differ")
    for name, expected in manifest["files"].items():
        if digest(args.development_package/name) != expected:
            raise RuntimeError(f"Development array changed: {name}")
    data = {k: np.load(args.development_package/f"{k}.npy", allow_pickle=False) for k in ("x", "y", "ids", "attempted", "cohort")}
    args.output.mkdir(parents=True)
    names, eligible = manifest["families"], manifest["eligible_codes"]
    arrival = np.asarray(manifest["arrival"])
    rows = []
    trajectory = [[None]*4 for _ in range(4)]
    for checkpoint in run["checkpoints"]:
        if not checkpoint["stage_end"]:
            continue
        stage = checkpoint["stage"]
        path = args.run/checkpoint["file"]
        if digest(path) != checkpoint["file_sha256"]:
            raise RuntimeError("Stage checkpoint payload changed")
        meta, arrays = load_state(path)
        slots = meta["slots"]
        model = ReferenceMLP(len(slots), config["seed"])
        model.load_state_dict({k[6:]: torch.from_numpy(v) for k, v in arrays.items() if k.startswith("model.")})
        model.eval()
        full_mask = np.isin(data["y"], slots)
        indexes = np.flatnonzero(full_mask)
        predicted_slots = np.empty(len(indexes), dtype=np.uint8)
        with torch.no_grad():
            for start in range(0, len(indexes), 2048):
                logits = model(torch.from_numpy(data["x"][indexes[start:start+2048]]))
                if not bool(torch.isfinite(logits).all()):
                    raise FloatingPointError("Non-finite development logits")
                predicted_slots[start:start+2048] = logits.argmax(dim=1).numpy().astype(np.uint8)
        # Full active head stays available even on eligible-only scoring banks.
        predicted = np.asarray(slots, dtype=np.int64)[predicted_slots]
        y = data["y"][indexes]
        np.savez(args.output/f"E{stage}-predictions.npz", ids=data["ids"][indexes], predicted_slots=predicted_slots,
                 source_codes_in_slot_order=np.asarray(slots, dtype=np.int16))
        full_matrix, full_classes = counts_for(y, predicted, slots, names)
        eligible_seen = [code for code in eligible if code in slots]
        eligible_mask = np.isin(y, eligible_seen)
        eligible_matrix, eligible_classes = counts_for(y[eligible_mask], predicted[eligible_mask], eligible_seen, names)
        macro = float(np.mean([r["f1"] for r in eligible_classes]))
        benign, alerted = y == 0, predicted != 0
        tp = int((~benign & alerted).sum())
        fp = int((benign & alerted).sum())
        fn = int((~benign & ~alerted).sum())
        tn = int((benign & ~alerted).sum())
        cohorts = data["cohort"][indexes]
        for j in range(1, stage+1):
            mask = eligible_mask & (cohorts == j)
            trajectory[stage-1][j-1] = ratio(int((predicted[mask] == y[mask]).sum()), int(mask.sum()))
        provenance = []
        for flag, label in [(False, "original_background"), (True, "remapped_attempted")]:
            mask = benign & (data["attempted"][indexes] == flag)
            provenance.append({"group": label, "benign_rows": int(mask.sum()), "alerts": int((mask & alerted).sum()),
                               "error_rate": ratio(int((mask & alerted).sum()), int(mask.sum()))})
        hulk = names.index("DoS Hulk")
        source_mask = y == hulk
        source = {"support": int(source_mask.sum()), "predicted_benign": int((source_mask & ~alerted).sum()),
                  "predicted_hulk": int((source_mask & (predicted == hulk)).sum()),
                  "predicted_other_attack": int((source_mask & alerted & (predicted != hulk)).sum())}
        if sum(source[k] for k in ("predicted_benign", "predicted_hulk", "predicted_other_attack")) != source["support"]:
            raise RuntimeError("Hulk prediction partition is inconsistent")
        newly_eligible = [c for c in eligible_seen if c != 0 and c != hulk and arrival[c] == stage]
        acquisition = None if stage == 1 else float(np.mean([r["f1"] for r in eligible_classes if r["code"] in newly_eligible]))
        rows.append({"stage": stage, "head_width": len(slots), "slot_names": [names[c] for c in slots],
                     "model_sha256": model_identity(model, slots), "bank_ids_sha256": array_identity(data["ids"][indexes]),
                     "full_seen_bank_rows": len(indexes), "full_seen_confusion_source_code_order": full_matrix,
                     "full_seen_classes": full_classes, "eligible_seen_bank_rows": int(eligible_mask.sum()),
                     "eligible_codes": eligible_seen, "eligible_confusion_source_code_order": eligible_matrix,
                     "eligible_classes": eligible_classes, "eligible_macro_f1": macro,
                     "eligible_pooled_accuracy": float((predicted[eligible_mask] == y[eligible_mask]).mean()),
                     "untargeted_new_annotated_class_f1": acquisition,
                     "binary_full_seen": {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "attack_precision": ratio(tp, tp+fp),
                        "attack_recall": ratio(tp, tp+fn), "f1": ratio(2*tp, 2*tp+fp+fn), "benign_far": ratio(fp, fp+tn)},
                     "benign_provenance_descriptive": provenance, "hulk_partition": source})
    if len(rows) != 4:
        raise RuntimeError("Expected exactly four completed stage evaluations")
    final = trajectory[3]
    bwt = float(np.mean([final[j]-trajectory[j][j] for j in range(3)]))
    forgetting = float(np.mean([max(trajectory[t][j] for t in range(j, 4))-final[j] for j in range(3)]))
    result = {"status": "development_reference_only_not_paper_evidence", "run_manifest_sha256": digest(args.run/"run.json"),
              "development_manifest_sha256": digest(args.development_package/"manifest.json"), "final_test_accessed": False,
              "stages": rows, "R_accuracy_by_stage_and_arrival_cohort": trajectory,
              "equal_stage_ACC4": float(np.mean(final)), "BWT4": bwt, "forgetting4": forgetting,
              "A": float(np.mean([r["untargeted_new_annotated_class_f1"] for r in rows[1:]])),
              "limitations": ["One clean development seed with untuned reference settings; no efficacy, comparative or significance claim.",
                "Benign bank is a fixed mixture across capture periods, including at E1.",
                "Portscan labels are distinct source scenarios, not certified novel attack techniques.",
                "No held-out Heartbleed positives; rare supported outputs remain active."]}
    write_json(args.output/"metrics.json", result)
    print(canonical({"A": result["A"], "ACC4": result["equal_stage_ACC4"],
                     "stage_macro_f1": [r["eligible_macro_f1"] for r in rows],
                     "stage_benign_far": [r["binary_full_seen"]["benign_far"] for r in rows]}))


if __name__ == "__main__":
    main()
