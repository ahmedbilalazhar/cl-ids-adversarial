"""Prove exact split-input identity before reusing a prior conditional split."""
import hashlib
import json
import shutil
import time
from pathlib import Path
from datetime import datetime,timezone
import numpy as np

ROOT=Path(__file__).resolve().parents[3];DOCS=ROOT/"docs/phase3-plan"
BASE=ROOT/"data/raw/phase3-feasibility-corrected";WORK=BASE/"no-headers-74"
started=time.monotonic()
old=np.load(BASE/"conditional-components-120.npz",allow_pickle=False)
new=np.load(WORK/"conditional-components-120.npz",allow_pickle=False)
checks={name:bool(np.array_equal(old[name],new[name])) for name in ["row_ids","labels","kept","t0_fit","t0_closure","survivor"]}

def canonical(state):
    roots=state["roots"];ids=state["row_ids"]
    c=np.full(len(ids),np.iinfo(np.uint64).max,dtype=np.uint64)
    np.minimum.at(c,roots,ids)
    return c[roots]

old_groups=canonical(old);new_groups=canonical(new)
checks["all_provenance_canonical_components_identical"]=bool(np.array_equal(old_groups,new_groups))
old_report=json.loads((DOCS/"corrected-component-feasibility.json").read_text())
new_report=json.loads((DOCS/"corrected-no-headers-74-component-feasibility.json").read_text())
old_stats={r["feature"]:(r["minimum_T0"],r["maximum_T0"],r["denominator"]) for r in old_report["scaler_features"]}
checks["retained_74_scaler_statistics_identical"]=all(old_stats[r["feature"]]==(r["minimum_T0"],r["maximum_T0"],r["denominator"]) for r in new_report["scaler_features"])
old_names=[r["feature"] for r in old_report["scaler_features"]]
indices=[old_names.index(r["feature"]) for r in new_report["scaler_features"]]
rows=len(new["row_ids"])
full=np.memmap(BASE/"candidate-transformed-fp32.raw",dtype="<f4",mode="r",shape=(rows,len(old_names)))
reduced=np.memmap(WORK/"candidate-transformed-fp32.raw",dtype="<f4",mode="r",shape=(rows,len(indices)))
projection_equal=True
for first in range(0,rows,50000):
    last=min(rows,first+50000)
    expected=np.ascontiguousarray(np.asarray(full[first:last])[:,indices]).view(np.uint8)
    actual=np.asarray(reduced[first:last]).view(np.uint8)
    if not np.array_equal(expected,actual):projection_equal=False;break
checks["all_final_input_bytes_are_exact_declared_projection"]=projection_equal
if not all(checks.values()):raise RuntimeError("Split reuse identity failed; run the fixed allocator separately")
parent=DOCS/"corrected-candidate-split-feasibility.json"
report=json.loads(parent.read_text())
if report.get("audit_version")!=2:raise RuntimeError("Canonical-ID split v2 required")
shutil.copyfile(BASE/"conditional-candidate-split.npz",WORK/"conditional-candidate-split.npz")
report.update(release_candidate="corrected-no-headers-74",parent_evidence="corrected-no-headers-74-component-feasibility.json",completed_utc=datetime.now(timezone.utc).isoformat(),split_reuse={"parent":"corrected-candidate-split-feasibility.json","parent_report_sha256":hashlib.sha256(parent.read_bytes()).hexdigest(),"reason":"The allocator reads only ordered row labels and canonical component IDs; both and the selected source positions are exactly identical.","checks":checks,"new_allocator_execution":False,"parent_allocator_elapsed_seconds":report["elapsed_seconds"]},elapsed_seconds=round(time.monotonic()-started,3))
(DOCS/"corrected-no-headers-74-candidate-split-feasibility.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"all_checks_passed":all(checks.values()),"reused_rows":report["rows"],"new_allocator_execution":False,"elapsed_seconds":report["elapsed_seconds"]}))
