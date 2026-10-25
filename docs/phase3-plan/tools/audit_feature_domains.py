"""Descriptive feature-domain census; does not change or clip any inputs."""
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
    n=census["total_rows"]
    names=census["numeric_feature_order"]
    x=np.memmap(work/"candidate-features-fp64.raw",dtype="<f8",mode="r",shape=(n,76))
    counts={key:np.zeros(76,dtype=np.int64) for key in ["finite","negative","minus_one","zero","noninteger"]}
    minimum=np.full(76,np.inf)
    maximum=np.full(76,-np.inf)
    for first in range(0,n,50000):
        part=np.asarray(x[first:first+50000])
        finite=np.isfinite(part)
        counts["finite"]+=finite.sum(axis=0)
        counts["negative"]+=(finite&(part<0)).sum(axis=0)
        counts["minus_one"]+=(finite&(part==-1)).sum(axis=0)
        counts["zero"]+=(finite&(part==0)).sum(axis=0)
        with np.errstate(invalid="ignore"):
            counts["noninteger"]+=(finite&(part!=np.trunc(part))).sum(axis=0)
        minimum=np.minimum(minimum,np.where(finite,part,np.inf).min(axis=0))
        maximum=np.maximum(maximum,np.where(finite,part,-np.inf).max(axis=0))
    rows=[]
    for i,name in enumerate(names):
        rows.append({"feature":name,"finite_values":int(counts["finite"][i]),"nonfinite_or_empty_values":int(n-counts["finite"][i]),
            "minimum":float(minimum[i]),"maximum":float(maximum[i]),"negative_values":int(counts["negative"][i]),
            "minus_one_values":int(counts["minus_one"][i]),"zero_values":int(counts["zero"][i]),"noninteger_values":int(counts["noninteger"][i]),
            "constant_over_finite_source_values":bool(minimum[i]==maximum[i]),
            "interpretation":"Init-window -1 can be a sentinel; domain/unit rules need source-specific validation" if name.startswith("Init_Win") else "Observed negative values need semantic review; this census does not classify every negative as invalid" if counts["negative"][i] else "Descriptive source values; no cleaning decision implied"})
    reports.append({"release_candidate":release,"source_csv_records_including_blank":n,"source_manifest":census_name,"features":rows})
result={"status":"descriptive_source_feature_domain_census_no_cleaning_change","completed_utc":datetime.now(timezone.utc).isoformat(),
    "candidates":reports,"elapsed_seconds":round(time.monotonic()-started,3),"models_fitted":0,
    "limits":["Names/aliases do not establish identical feature semantics across extractors","Nonfinite counts include original empty CSV records","No clipping, imputation, feature removal or eligibility change performed","A finite value is not proof of physical validity; a negative sentinel is not automatically an error"]}
(DOCS/"feature-domain-census.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
negative_summary={}
for candidate in reports:
    negative_summary[candidate["release_candidate"]]=[(f["feature"],f["minimum"],f["negative_values"]) for f in candidate["features"] if f["negative_values"]]
print(json.dumps({"elapsed_seconds":result["elapsed_seconds"],"negative_features":negative_summary},indent=2),flush=True)
