"""Additive exclusion ledger for a domain-screened data candidate; no models."""
import argparse
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3];DOCS=ROOT/"docs/phase3-plan"
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--release",choices=["original","corrected"],required=True)
parser.add_argument("--profile",choices=["domain-checked","no-headers-74"],default="domain-checked")
args=parser.parse_args();release=args.release
if args.profile=="no-headers-74" and release!="corrected":raise ValueError("74-feature candidate is corrected-source only")
work=ROOT/f"data/raw/phase3-feasibility-{release}"
state=np.load(work/args.profile/"conditional-components-120.npz",allow_pickle=False)
parent_name=f"{release}-{args.profile}-component-feasibility.json"
parent=json.loads((DOCS/parent_name).read_text())
n=len(state["labels"]);blank=np.zeros(n,dtype=bool)
if release=="original":
    census=json.loads((DOCS/"original-full-census.json").read_text())
    audit=json.loads((DOCS/"original-csv-record-audit.json").read_text())
    file_map={r["name"]:r["file_index"] for r in census["files"]}
    local_rows=state["row_ids"] & np.uint64((1<<32)-1)
    for r in audit["members"]:
        if r["all_empty_records"]:
            if not r["all_empty_records_form_one_trailing_tail"]:raise RuntimeError("Explicit non-tail blank mask required")
            blank |= (state["file_index"]==file_map[r["member"]])&(local_rows>=r["first_empty_zero_based_data_row"])
finite=np.fromfile((work/args.profile if args.profile=="no-headers-74" else work)/"candidate-finite.raw",dtype=np.uint8).astype(bool)
names=["empty_csv_record","nonfinite_numeric_raw_or_final","invalid_metadata_or_annotation","invalid_feature_domain","ambiguous_input_annotation","T0_component_closure","same_label_duplicate_copy","retained_candidate"]
conditions=[blank,~finite|~state["final_finite"],~state["valid_metadata"]|(state["labels"]<0),~state["valid_domain"],state["raw_conflict"]|state["final_conflict"],state["t0_closure"],~state["survivor"],state["kept"]]
reason=np.full(n,-1,dtype=np.int8)
for i,condition in enumerate(conditions):reason[(reason<0)&condition]=i
if (reason<0).any() or not np.array_equal(reason==len(names)-1,state["kept"]):raise RuntimeError("Exclusion ledger does not conserve candidate records")
families=[]
label_names=parent["label_code_order"]
for code,label in [(-1,"<missing_annotation>")]+list(enumerate(label_names)):
    mask=state["labels"]==code
    families.append({"family":label,"source_records":int(mask.sum()),"primary_reasons":{name:int((mask&(reason==i)).sum()) for i,name in enumerate(names)}})
fit=state["row_ids"][state["t0_fit"]].astype("<u8")
result={"status":"conditional_additive_domain_screened_candidate_accounting","completed_utc":datetime.now(timezone.utc).isoformat(),"parent_evidence":parent_name,"source_csv_records":n,"precedence":names,"primary_reason_counts":{name:int((reason==i).sum()) for i,name in enumerate(names)},"families":families,"T0_fitting_count":len(fit),"T0_fitting_ordered_uint64_sha256":hashlib.sha256(fit.tobytes()).hexdigest(),"role_note":"Calibration role is separate from this mutually exclusive model-record selection ledger","models_fitted":0,"limits":["Precedence counts are disjoint, diagnostic flags can overlap","Counts do not prove physical-event identity or source-label error","Profile adoption and canonical production builder remain pending"]}
(DOCS/f"{release}-{args.profile}-exclusion-accounting.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"release":release,"records":n,"counts":result["primary_reason_counts"]}))
