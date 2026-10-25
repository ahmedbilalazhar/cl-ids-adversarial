"""Label-independent source-field consistency audit, not a model evaluation."""
import json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np

ROOT=Path(__file__).resolve().parents[3];DOCS=ROOT/"docs/phase3-plan"
reports=[]
for release,census_name in [("original","original-full-census.json"),("corrected","corrected-component-input-manifest.json")]:
    c=json.loads((DOCS/census_name).read_text());n=c["total_rows"];names=c["numeric_feature_order"]
    work=ROOT/f"data/raw/phase3-feasibility-{release}"
    x=np.memmap(work/"candidate-features-fp64.raw",dtype="<f8",mode="r",shape=(n,len(names)))
    state=np.load(work/"domain-checked/conditional-components-120.npz",allow_pickle=False)
    f=x[:,names.index("Total Fwd Packets")];h=x[:,names.index("Fwd Header Length")];m=x[:,names.index("min_seg_size_forward")]
    okay=np.isfinite(f)&np.isfinite(h)&np.isfinite(m)&(f>=0)&(h>=0)&(m>=0)
    violation=okay&(h<f*m)
    finite=np.fromfile(work/"candidate-finite.raw",dtype=np.uint8).astype(bool)
    valid=finite&state["valid_metadata"]&state["valid_domain"]
    row={"candidate":release,"constraint":"Fwd Header Length >= Total Fwd Packets * min_seg_size_forward","applicability":"Nonnegative finite total/count/minimum header fields with the documented source semantics","nonnegative_finite_triplets":int(okay.sum()),"violating_triplets":int(violation.sum()),"violations_after_current_domain_and_metadata":int((violation&valid).sum()),"violations_in_domain_screened_T0_fit":int((violation&state["t0_fit"]).sum()),"violations_among_screened_unique_survivors":int((violation&state["kept"]).sum()),"violations_with_lower_bound_above_int16_max":int((violation&(f*m>32767)).sum()),"examples":[]}
    for i in np.flatnonzero(violation&valid)[:6]:
        row["examples"].append({"row_id":str(int(state["row_ids"][i])),"forward_packets":int(f[i]),"stored_header_total":int(h[i]),"minimum_segment_header":int(m[i]),"implied_minimum_total":int(f[i]*m[i])})
    reports.append(row)
result={"status":"source_feature_consistency_audit_not_model_evaluation","completed_utc":datetime.now(timezone.utc).isoformat(),"reports":reports,"models_fitted":0,"scope":"Own-row label-independent field relation; no prediction or threshold tuning","limits":["Source semantics and archive/extractor provenance remain relevant","No values repaired, unsigned-cast or silently reclassified","Consistency flags do not uniquely recover pre-cast totals"]}
(DOCS/"header-consistency-feasibility.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({r["candidate"]:r["violations_after_current_domain_and_metadata"] for r in reports}))
