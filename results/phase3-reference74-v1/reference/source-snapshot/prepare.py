"""Promote audited 74-input assets into isolated reference worker packages.

This checks and exports the frozen audit graph/split. It does not claim a fresh
CSV/session reconstruction; the upstream reconstruction evidence is hash-linked.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from .common import ROOT, array_identity, canonical, digest, identity, read_json, reference_protocol, rng, write_json


def allocate(component_ids, labels, seed, classes=16):
    components, inverse = np.unique(component_ids, return_inverse=True)
    vectors = np.zeros((len(components), classes), dtype=np.int64)
    np.add.at(vectors, (inverse, labels), 1)
    totals = vectors.sum(axis=0)
    present = totals > 0
    denominators = np.where(present, totals, 1).astype(np.float64)
    generator = rng(1, seed)
    shares = np.zeros((5, classes), dtype=np.float64)
    for family in range(classes):
        if present[family]:
            shares[:, family] = generator.dirichlet(np.full(5, .5))
    targets = shares * totals
    assigned = np.zeros_like(targets)
    owners = np.full(len(components), -1, dtype=np.int8)
    order = np.lexsort((components, -vectors.sum(axis=1)))
    for group in order:
        vector = vectors[group]
        delta = ((assigned + vector - targets) / denominators)**2 - ((assigned - targets) / denominators)**2
        client = int(np.argmin(delta[:, present].sum(axis=1)))
        owners[group] = client
        assigned[client] += vector
    return owners[inverse], {
        "components": components, "component_owner": owners, "component_order": components[order],
        "shares": shares, "targets": targets, "realized": assigned,
        "objective": float((((assigned-targets)/denominators)[:, present]**2).sum()),
    }


def select_training(positions, labels, stages, components):
    groups, inverse = np.unique(components, return_inverse=True)
    benign_counts = np.zeros((len(groups), 4), dtype=np.int64)
    benign = labels == 0
    np.add.at(benign_counts, (inverse[benign], stages[benign]-1), 1)
    selected = np.zeros(len(groups), dtype=bool)
    counts = np.zeros(4, dtype=np.int64)
    generator = np.random.Generator(np.random.PCG64(np.random.SeedSequence(2027)))
    for group in generator.permutation(np.flatnonzero(benign_counts.sum(axis=1) > 0)):
        increment = benign_counts[group]
        if int(2*np.dot(increment, counts-3500)+np.dot(increment, increment)) < 0:
            selected[group] = True
            counts += increment
    keep = ~benign | selected[inverse]
    if not np.all(counts == 3500):
        raise RuntimeError(f"Adopted benign inventory changed: {counts}")
    return positions[keep]


def benign_cohorts(components, labels):
    """Fixed development analogue of the whole-component accounting cohorts."""
    output = np.zeros(len(labels), dtype=np.int8)
    groups, inverse, sizes = np.unique(components[labels == 0], return_inverse=True, return_counts=True)
    generator = np.random.Generator(np.random.PCG64(np.random.SeedSequence(2028)))
    # Canonical component IDs precede seeded tie priorities. This is not time order.
    priority = generator.permutation(len(groups))
    order = np.lexsort((priority, -sizes))
    loads = np.zeros(4, dtype=np.int64)
    owner = np.empty(len(groups), dtype=np.int8)
    for group in order:
        cohort = int(generator.choice(np.flatnonzero(loads == loads.min())))
        owner[group] = cohort + 1
        loads[cohort] += sizes[group]
    output[labels == 0] = owner[inverse]
    if np.any(loads == 0):
        raise RuntimeError("Empty benign development cohort")
    return output, loads.tolist()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT/"configs/phase3/reference74-v1.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = reference_protocol(args.protocol)
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite a prepared package")
    docs = ROOT/"docs/phase3-plan"
    base = ROOT/"data/raw/phase3-feasibility-corrected"
    work = base/"no-headers-74"
    evidence = protocol["data_evidence"]
    for relative, expected in evidence.items():
        if digest(ROOT/relative) != expected:
            raise RuntimeError(f"Pinned data evidence changed: {relative}")
    identities = read_json(docs/"audit-local-data-identities.json")
    pinned = {v["path"]: v["sha256"] for v in identities["files"]}
    required = [work/"candidate-features-fp64.raw", work/"candidate-transformed-fp32.raw",
                work/"conditional-components-120.npz", work/"conditional-candidate-split.npz",
                base/"component-metadata.csv"]
    sources = {}
    for path in required:
        relative = path.relative_to(ROOT).as_posix()
        actual = digest(path)
        if actual != pinned[relative]:
            raise RuntimeError(f"Audited local asset changed: {relative}")
        sources[relative] = actual
    archive = base/"CICIDS2017_improved.zip"
    if digest(archive) != protocol["data"]["archive_sha256"]:
        raise RuntimeError("Source archive hash changed")
    source = read_json(docs/"corrected-no-headers-74-input-manifest.json")
    report = read_json(docs/"corrected-no-headers-74-component-feasibility.json")
    split_report = read_json(docs/"corrected-no-headers-74-candidate-split-feasibility.json")
    families = report["label_code_order"]
    if families != protocol["taxonomy"]["source_code_order"] or len(source["numeric_feature_order"]) != 74:
        raise RuntimeError("Taxonomy/schema changed")
    with np.load(work/"conditional-components-120.npz", allow_pickle=False) as f:
        state = {k: f[k] for k in f.files}
    with np.load(work/"conditional-candidate-split.npz", allow_pickle=False) as split:
        positions, roles = split["source_positions"], split["roles"]
    n = len(state["row_ids"])
    canonical_ids = np.full(n, np.iinfo(np.uint64).max, dtype=np.uint64)
    np.minimum.at(canonical_ids, state["roots"], state["row_ids"])
    groups = canonical_ids[state["roots"]]
    role_groups = [np.unique(groups[positions[roles == role]]) for role in range(3)]
    for a, b in [(0, 1), (0, 2), (1, 2)]:
        if np.intersect1d(role_groups[a], role_groups[b]).size:
            raise RuntimeError("Component crosses a split")
    if not np.all(state["kept"][positions]) or np.any(state["t0_closure"][positions]):
        raise RuntimeError("Excluded/T0 record in assigned inventory")
    file_stage = np.array([4, 0, 3, 1, 2], dtype=np.int8)
    stages = file_stage[state["file_index"]]
    train_pool = positions[roles == 0]
    selected = select_training(train_pool, state["labels"][train_pool], stages[train_pool], groups[train_pool])
    if len(selected) != 183045:
        raise RuntimeError("Selected training row count changed")
    # Independent rebuild against the audit's fixed-pool identity, not its seed-1 allocation.
    with np.load(work/"conditional-ownership-benign-subset-seed-1.npz", allow_pickle=False) as old:
        if not np.array_equal(selected, old["source_positions"]):
            raise RuntimeError("Rebuilt selected training IDs differ from audited pool")
    owners, ownership = allocate(groups[selected], state["labels"][selected], protocol["seed"])
    features = np.memmap(work/"candidate-transformed-fp32.raw", dtype="<f4", mode="r", shape=(n, 74))
    raw = np.memmap(work/"candidate-features-fp64.raw", dtype="<f8", mode="r", shape=(n, 74))
    t0 = np.flatnonzero(state["t0_fit"])
    if len(t0) != 371621 or not np.all(state["file_index"][t0] == 1) or np.any(state["labels"][t0] != 0):
        raise RuntimeError("Monday-only T0 fit identity changed")
    minimum = raw[t0].min(axis=0)
    maximum = raw[t0].max(axis=0)
    denominator = maximum-minimum
    denominator[denominator == 0] = 1
    for i, row in enumerate(report["scaler_features"]):
        if minimum[i] != row["minimum_T0"] or denominator[i] != row["denominator"]:
            raise RuntimeError("Audited T0 statistics differ")
    # Recompute every exported input from frozen T0; no clipping or refitting.
    dev = positions[roles == 1]
    for pool in [selected, dev]:
        for start in range(0, len(pool), 8192):
            indexes = pool[start:start+8192]
            transformed = ((raw[indexes]-minimum)/denominator).astype("<f4")
            transformed[transformed == 0] = 0
            if not np.isfinite(transformed).all() or not np.array_equal(transformed, features[indexes]):
                raise RuntimeError("Exported FP32 inputs differ from frozen transform")
    # Provenance is exported only to the development evaluator, never the learner.
    attempted = np.empty(n, dtype=bool)
    with (base/"component-metadata.csv").open(newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if int(row["row_id"]) != int(state["row_ids"][i]):
                raise RuntimeError("Source metadata alignment changed")
            attempted[i] = int(row["attempted_category"]) != -1
    if i+1 != n:
        raise RuntimeError("Metadata row count changed")
    output = args.output
    output.mkdir(parents=True)
    worker = output/"train"
    worker.mkdir()
    stage_counts = {}
    for stage in range(1, 5):
        local = stages[selected] == stage
        indexes = selected[local]
        # Opaque IDs determine base order. No reference/poison/provenance columns.
        order = np.argsort(state["row_ids"][indexes], kind="stable")
        indexes = indexes[order]
        target = worker/f"E{stage}"
        target.mkdir()
        arrays = {"x": np.array(features[indexes]), "y": state["labels"][indexes].astype("<i8"),
                  "ids": state["row_ids"][indexes], "owner": owners[local][order]}
        for key, value in arrays.items():
            np.save(target/f"{key}.npy", value, allow_pickle=False)
        stage_counts[str(stage)] = {"rows": len(indexes), "by_client": np.bincount(arrays["owner"], minlength=5).tolist(),
                                    "by_family": np.bincount(arrays["y"], minlength=16).tolist()}
    worker_files = {p.relative_to(worker).as_posix(): digest(p) for p in sorted(worker.rglob("*.npy"))}
    scientific = {"protocol_sha256": digest(args.protocol), "seed": protocol["seed"], "files": worker_files,
                  "feature_order": source["numeric_feature_order"], "source_code_order": families,
                  "stage_counts": stage_counts, "reference_labels_or_poison_flags_exported": False,
                  "final_test_feature_rows_exported": 0, "development_feature_rows_exported": 0}
    write_json(worker/"manifest.json", scientific)
    arrival = np.zeros(16, dtype=np.int8)
    for family in range(1, 16):
        observed = np.unique(stages[selected[state["labels"][selected] == family]])
        if len(observed) != 1:
            raise RuntimeError("Unexpected attack annotation arrival")
        arrival[family] = observed[0]
    dev_order = np.argsort(state["row_ids"][dev], kind="stable")
    dev = dev[dev_order]
    cohort, benign_loads = benign_cohorts(groups[dev], state["labels"][dev])
    attack = state["labels"][dev] != 0
    cohort[attack] = arrival[state["labels"][dev][attack]]
    evaluator = output/"development"
    evaluator.mkdir()
    for key, value in {"x": np.array(features[dev]), "y": state["labels"][dev].astype("<i8"),
                       "ids": state["row_ids"][dev], "attempted": attempted[dev], "cohort": cohort}.items():
        np.save(evaluator/f"{key}.npy", value, allow_pickle=False)
    eligible = [families.index(row["family"]) for row in split_report["families"] if row["eligible_50_rows_5_components_each"]]
    write_json(evaluator/"manifest.json", {"role": "development_only", "train_manifest_sha256": digest(worker/"manifest.json"),
               "protocol_sha256": digest(args.protocol), "files": {p.name: digest(p) for p in sorted(evaluator.glob("*.npy"))},
               "families": families, "eligible_codes": eligible, "arrival": arrival.tolist(),
               "benign_cohort_counts": benign_loads, "final_test_rows_exported": 0})
    builder = output/"builder"
    builder.mkdir()
    np.savez(builder/"ownership.npz", source_positions=selected, canonical_components=groups[selected],
             row_owner=owners, **{k: v for k, v in ownership.items() if isinstance(v, np.ndarray)})
    write_json(builder/"scaler.json", {"feature_order": source["numeric_feature_order"], "minimum": minimum.tolist(),
               "denominator": denominator.tolist(), "clip": False, "fit_ids_sha256": array_identity(state["row_ids"][t0]),
               "fit_rows": len(t0), "ambiguous_calibration_only_rows": 3})
    summary = {"status": "adopted_reference_package", "scientific_identity": identity(scientific),
               "protocol_sha256": digest(args.protocol), "source_assets": sources, "stage_counts": stage_counts,
               "training_rows": len(selected), "development_rows": len(dev), "test_rows_exported": 0,
               "cross_role_component_overlap": 0, "ownership_objective": ownership["objective"],
               "ownership_sha256": digest(builder/"ownership.npz"), "scaler_sha256": digest(builder/"scaler.json"),
               "train_manifest_sha256": digest(worker/"manifest.json"), "development_manifest_sha256": digest(evaluator/"manifest.json"),
               "reconstruction_scope": "Hash-checked audited graph/split; independently rebuilt benign pool/seed-101 ownership/T0 transform on all exported records."}
    write_json(output/"preparation-report.json", summary)
    print(canonical(summary), flush=True)


if __name__ == "__main__":
    main()
