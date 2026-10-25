"""Explain conditional data exclusions with additive, reason-coded totals."""
from __future__ import annotations
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
WORK=ROOT/"data/raw/phase3-feasibility-original"
started=time.monotonic()
state=np.load(WORK/"conditional-components-120.npz",allow_pickle=False)
parent=json.loads((DOCS/"original-component-feasibility.json").read_text(encoding="utf-8"))
if parent.get("audit_version")!=2:
    raise RuntimeError("Requires v2 conditional audit")
census=json.loads((DOCS/"original-full-census.json").read_text(encoding="utf-8"))
csv_audit=json.loads((DOCS/"original-csv-record-audit.json").read_text(encoding="utf-8"))
labels=state["labels"]
names=[row["family"] for row in next(g for g in parent["gap_sensitivities"] if g["gap_seconds"]==120)["families"]]
finite=np.fromfile(WORK/"candidate-finite.raw",dtype=np.uint8).astype(bool)
n=len(labels)
row_ids=state["row_ids"]
file_index=state["file_index"]
local_rows=(row_ids & np.uint64((1<<32)-1)).astype(np.uint32)
file_map={row["name"]:row["file_index"] for row in census["files"]}
blank=np.zeros(n,dtype=bool)
for row in csv_audit["members"]:
    if row["all_empty_records"]:
        if not row["all_empty_records_form_one_trailing_tail"]:
            raise RuntimeError("Need explicit row mask for non-tail empty records")
        blank |= (file_index==file_map[row["member"]]) & (local_rows>=row["first_empty_zero_based_data_row"])
reason_names=["empty_csv_record","nonfinite_numeric","invalid_metadata_or_annotation","ambiguous_input_annotation",
              "T0_component_closure","same_label_duplicate_copy","retained_candidate"]
conditions=[blank,~finite,~state["valid_metadata"],state["raw_conflict"]|state["final_conflict"],
            state["t0_closure"],~state["survivor"],state["kept"]]
reason=np.full(n,-1,dtype=np.int8)
for code,condition in enumerate(conditions):
    reason[(reason<0)&condition]=code
if (reason<0).any() or not np.array_equal(reason==6,state["kept"]):
    raise RuntimeError("Reasoned record inventory fails conservation")
families=[]
for code,name in [(-1,"<missing_annotation>")]+list(enumerate(names)):
    family=labels==code
    counts={r:int((family&(reason==j)).sum()) for j,r in enumerate(reason_names)}
    families.append({"family":name,"source_csv_records":int(family.sum()),"primary_reasons":counts,
                     "sum_matches_source":sum(counts.values())==int(family.sum())})

meta=pd.read_csv(WORK/"feasibility-metadata.csv",usecols=["duration_us_raw","src_port","dst_port","protocol","timestamp_raw"],low_memory=False)
duration=pd.to_numeric(meta["duration_us_raw"],errors="coerce")
src=pd.to_numeric(meta["src_port"],errors="coerce")
dst=pd.to_numeric(meta["dst_port"],errors="coerce")
protocol=pd.to_numeric(meta["protocol"],errors="coerce")
nonblank=~blank
metadata_diagnostics={
    "nonempty_negative_duration_rows":int((nonblank&duration.lt(0)).sum()),
    "nonempty_out_of_range_source_ports":int((nonblank&~src.between(0,65535)).sum()),
    "nonempty_out_of_range_destination_ports":int((nonblank&~dst.between(0,65535)).sum()),
    "nonempty_out_of_range_protocol":int((nonblank&~protocol.between(0,255)).sum()),
    "nonempty_missing_timestamp":int((nonblank&meta["timestamp_raw"].isna()).sum()),
}
fit_ids=row_ids[state["t0_fit"]].astype("<u8")
result={"status":"conditional_additive_source_accounting_not_final_data_lock","completed_utc":datetime.now(timezone.utc).isoformat(),
    "parent_evidence":"original-component-feasibility.json","audit_version":2,"source_csv_records":n,
    "precedence":reason_names,"primary_reason_counts":{r:int((reason==j).sum()) for j,r in enumerate(reason_names)},
    "families":families,"metadata_diagnostics_overlapping":metadata_diagnostics,
    "T0_fitting_count":len(fit_ids),"T0_fitting_ordered_uint64_sha256":hashlib.sha256(fit_ids.tobytes()).hexdigest(),
    "role_note":"Calibration fitting is a separate role; this mutually exclusive inventory describes model-record selection after the fixed calibration fit.",
    "elapsed_seconds":round(time.monotonic()-started,3),"models_trained":False,
    "limits":["Counts use the proposed original source/clock/conservative graph policy","Exclusion is not proof a physical event or reference label is wrong","No experiment performance or deployed traffic rate is measured"]}
(DOCS/"candidate-exclusion-accounting.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"source_csv_records":n,"reasons":result["primary_reason_counts"],"metadata":metadata_diagnostics,"elapsed_seconds":result["elapsed_seconds"]}),flush=True)
