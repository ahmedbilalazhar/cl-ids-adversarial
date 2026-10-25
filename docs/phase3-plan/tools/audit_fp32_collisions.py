"""Measure distinct raw inputs collapsed by the declared T0/FP32 projection.

Descriptive numerical data audit, not model testing or performance evaluation.
No feature/scaler policy is changed. Local ULP arithmetic is not a causal estimate
of any observed classification effect.
"""
import hashlib
import json
import time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
started=time.monotonic()
reports=[]
for release,census_name in [("original","original-full-census.json"),("corrected","corrected-component-input-manifest.json")]:
    work=ROOT/f"data/raw/phase3-feasibility-{release}"
    census=json.loads((DOCS/census_name).read_text())
    parent=json.loads((DOCS/f"{release}-component-feasibility.json").read_text())
    n=census["total_rows"]
    names=census["numeric_feature_order"]
    state=np.load(work/"conditional-components-120.npz",allow_pickle=False)
    positions=np.flatnonzero(state["final_finite"])
    raw=np.memmap(work/"candidate-features-fp64.raw",dtype="<f8",mode="r",shape=(n,76))
    final=np.memmap(work/"candidate-transformed-fp32.raw",dtype="<f4",mode="r",shape=(n,76))
    hashes=np.empty(len(positions),dtype="V32")
    for first in range(0,len(positions),100000):
        part=positions[first:first+100000]
        hashes[first:first+len(part)]=[hashlib.sha256(final[int(i)]).digest() for i in part]
    _,inverse,counts=np.unique(hashes,return_inverse=True,return_counts=True)
    order=np.argsort(inverse,kind="stable")
    sorted_positions=positions[order]
    offsets=np.concatenate(([0],np.cumsum(counts)))
    merged_groups=0
    merged_rows=0
    raw_distinctions_lost=0
    varying_feature_groups=np.zeros(76,dtype=np.int64)
    examples=[]
    for group in np.flatnonzero(counts>1):
        ids=sorted_positions[offsets[group]:offsets[group+1]]
        values=np.asarray(raw[ids])
        varying=np.any(values!=values[0],axis=0)
        if not varying.any():
            continue
        # All bytes in a final group are confirmed, not only fingerprint matches.
        if not np.all(np.asarray(final[ids])==final[int(ids[0])]):
            raise RuntimeError("Unexpected SHA-256 collision; audit not promoted")
        raw_unique=len(np.unique(np.ascontiguousarray(values).view("V608").reshape(-1)))
        merged_groups+=1
        merged_rows+=len(ids)
        raw_distinctions_lost+=raw_unique-1
        varying_feature_groups+=varying
        if len(examples)<4:
            different=np.flatnonzero(np.any(values!=values[0],axis=1))[0]
            changed=np.flatnonzero(values[different]!=values[0])
            row_ids=state["row_ids"]
            examples.append({"row_ids":[str(int(row_ids[ids[0]])),str(int(row_ids[ids[different]]))],
                "reference_label_codes":[int(state["labels"][ids[0]]),int(state["labels"][ids[different]])],
                "differences":[{"feature":names[c],"raw_values":[float(values[0,c]),float(values[different,c])],
                    "same_final_fp32_value":float(final[int(ids[0]),c])} for c in changed]})
    ulps=[]
    for feature in parent["scaler_features"]:
        if feature["minimum_T0"]<0 and feature["feature"] not in ["Init_Win_bytes_forward","Init_Win_bytes_backward"]:
            denominator=feature["denominator"]
            z=np.float32(-feature["minimum_T0"]/denominator)
            next_z=np.nextafter(z,np.float32(np.inf))
            ulps.append({"feature":feature["feature"],"T0_minimum":feature["minimum_T0"],"T0_maximum":feature["maximum_T0"],
                "transformed_zero_fp32":float(z),"local_one_ULP_in_raw_units_near_zero":(float(next_z)-float(z))*denominator})
    report={"release_candidate":release,"finite_raw_and_final_rows":len(positions),"distinct_final_fp32_inputs":len(counts),
        "final_groups_merging_distinct_raw_inputs":merged_groups,"rows_in_these_merged_groups":merged_rows,
        "distinct_raw_inputs_lost_to_projection":raw_distinctions_lost,
        "feature_group_variations":[{"feature":name,"merged_groups_with_raw_difference":int(varying_feature_groups[i])} for i,name in enumerate(names) if varying_feature_groups[i]],
        "observed_pair_examples":examples,"negative_minimum_resolution_diagnostics":ulps}
    reports.append(report)
    print(json.dumps({"release":release,"merged_groups":merged_groups,"raw_distinctions_lost":raw_distinctions_lost,"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)
result={"status":"source_projection_collision_audit_no_model_results","completed_utc":datetime.now(timezone.utc).isoformat(),
    "candidates":reports,"elapsed_seconds":round(time.monotonic()-started,3),"models_fitted":0,
    "limits":["Collision is feature-representation equality, not proof of source-event identity","Local ULP describes numerical resolution near raw zero, not all values or learned accuracy","No alternate scaler, clipping, curation or model variant was selected"]}
(DOCS/"fp32-projection-collision-audit.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"elapsed_seconds":result["elapsed_seconds"],"complete":True}),flush=True)
