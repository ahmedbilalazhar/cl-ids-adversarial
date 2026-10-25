"""Apply the proposed fixed SGKF allocator to conditional data audit records.

Data-only feasibility evidence. No model is fitted, no outcome is evaluated, and
this does not approve the candidate clock/release/group policy for final use.
"""
from __future__ import annotations
import argparse
import hashlib
import inspect
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import sklearn
from sklearn.model_selection import StratifiedGroupKFold

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--release",choices=["original","corrected"],default="original")
parser.add_argument("--domain-checked",action="store_true")
parser.add_argument("--profile",choices=["default","no-headers-74"],default="default")
args=parser.parse_args()
release=args.release
candidate_prefix=release+("-domain-checked" if args.domain_checked else "")
WORK=ROOT/f"data/raw/phase3-feasibility-{release}"
if args.profile!="default":
    if release!="corrected" or args.domain_checked:raise ValueError("74-feature profile is a separate corrected candidate")
    candidate_prefix="corrected-no-headers-74"
    WORK=WORK/"no-headers-74"
if args.domain_checked:
    WORK=WORK/"domain-checked"
report_name="candidate-split-feasibility.json" if candidate_prefix=="original" else f"{candidate_prefix}-candidate-split-feasibility.json"
started=time.monotonic()
evidence=json.loads((DOCS/f"{candidate_prefix}-component-feasibility.json").read_text(encoding="utf-8"))
if evidence.get("audit_version")!=2 or not evidence["calibration_policy_gate_passes"]:
    raise RuntimeError("Requires the explicit v2 conditional calibration audit")
if tuple(int(x) for x in sklearn.__version__.split(".")[:2])<(1,8):
    raise RuntimeError("Require an SGKF implementation containing the 1.8 shuffle fix")
state=np.load(WORK/"conditional-components-120.npz",allow_pickle=False)
ids=np.flatnonzero(state["kept"])
y=state["labels"][ids]
all_roots=state["roots"]
canonical_id=np.full(len(all_roots),np.iinfo(np.uint64).max,dtype=np.uint64)
np.minimum.at(canonical_id,all_roots,state["row_ids"])
groups=canonical_id[all_roots[ids]]
names=[r["family"] for r in next(r for r in evidence["gap_sensitivities"] if r["gap_seconds"]==120)["families"]]
allocator=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=2026)
folds=np.full(len(ids),-1,dtype=np.int8)
print(json.dumps({"step":"starting_full_group_allocator","rows":len(ids),"components":len(np.unique(groups)),"sklearn":sklearn.__version__}),flush=True)
for fold,(_,held_out) in enumerate(allocator.split(np.zeros((len(ids),1),dtype=np.uint8),y,groups)):
    folds[held_out]=fold
    print(json.dumps({"fold":fold,"rows":len(held_out),"elapsed_seconds":round(time.monotonic()-started,3)}),flush=True)
if (folds<0).any():
    raise RuntimeError("Unassigned candidate records")
roles=np.where(folds==0,2,np.where(folds==1,1,0)).astype(np.int8)
role_names=["train","development","test"]
family_rows=[]
for code,name in enumerate(names):
    counts={}
    for role,role_name in enumerate(role_names):
        selected=(y==code)&(roles==role)
        counts[role_name]={"rows":int(selected.sum()),"components":len(np.unique(groups[selected]))}
    counts["family"]=name
    counts["eligible_50_rows_5_components_each"]=all(counts[r]["rows"]>=50 and counts[r]["components"]>=5 for r in role_names)
    family_rows.append(counts)
owner_sets=[set(groups[roles==role].tolist()) for role in range(3)]
intersections={f"{role_names[left]}_{role_names[right]}":len(owner_sets[left]&owner_sets[right]) for left,right in [(0,1),(0,2),(1,2)]}
np.savez(WORK/"conditional-candidate-split.npz",source_positions=ids,folds=folds,roles=roles)
result={"status":"conditional_candidate_split_census_not_final_protocol_lock","audit_version":2,"completed_utc":datetime.now(timezone.utc).isoformat(),
    "parent_evidence":f"{candidate_prefix}-component-feasibility.json","release_candidate":candidate_prefix,"allocator":"StratifiedGroupKFold","n_splits":5,"shuffle":True,"random_state":2026,
    "role_fold_mapping":{"train":[2,3,4],"development":[1],"test":[0]},"scikit_learn_version":sklearn.__version__,
    "allocator_source_sha256":hashlib.sha256(inspect.getsource(StratifiedGroupKFold).encode()).hexdigest(),
    "component_id_rule":"Minimum immutable provenance row ID of the entire connected component, including excluded members; not the union-find implementation root.",
    "rows":len(ids),"components":len(np.unique(groups)),"cross_role_component_intersections":intersections,
    "role_counts":{r:int((roles==i).sum()) for i,r in enumerate(role_names)},"families":family_rows,
    "elapsed_seconds":round(time.monotonic()-started,3),"models_fitted":0,
    "limits":["Release, clock and conservative graph choices remain conditional","Support audit is on this exact candidate, not the legacy tasksets","No model outcome or final performance has been inspected","Benign training selection and ownership are subsequent data gates"]}
(DOCS/report_name).write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"status":result["status"],"elapsed_seconds":result["elapsed_seconds"],"component_overlap":intersections}),flush=True)
