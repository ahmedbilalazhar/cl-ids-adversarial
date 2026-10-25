"""Separate prospective 74-feature source-consistency candidate; no models."""
import json
import time
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from audit_original_components import main,ROOT

DOCS=ROOT/"docs/phase3-plan"
BASE=ROOT/"data/raw/phase3-feasibility-corrected"
WORK=BASE/"no-headers-74"

if __name__=="__main__":
    started=time.monotonic();WORK.mkdir(parents=True,exist_ok=True)
    parent=json.loads((DOCS/"corrected-component-input-manifest.json").read_text())
    old_names=parent["numeric_feature_order"]
    excluded=["Fwd Header Length","Bwd Header Length"]
    indices=[i for i,n in enumerate(old_names) if n not in excluded]
    n=parent["total_rows"]
    source=np.memmap(BASE/"candidate-features-fp64.raw",dtype="<f8",mode="r",shape=(n,len(old_names)))
    target=np.memmap(WORK/"candidate-features-fp64.raw",dtype="<f8",mode="w+",shape=(n,len(indices)))
    mask=np.memmap(WORK/"candidate-finite.raw",dtype="uint8",mode="w+",shape=(n,))
    for first in range(0,n,50000):
        last=min(first+50000,n);part=np.asarray(source[first:last])[:,indices]
        target[first:last]=part;mask[first:last]=np.isfinite(part).all(axis=1)
    target.flush();mask.flush();del target,mask,source
    candidate=dict(parent)
    candidate.update(status="prospective_74_feature_projection_not_adopted",completed_utc=datetime.now(timezone.utc).isoformat(),numeric_feature_order=[old_names[i] for i in indices],source_feature_order=[parent["source_feature_order"][i] for i in indices],excluded_fields=excluded,parent_manifest="corrected-component-input-manifest.json",reason="Published labeling code casts header totals to int16; positive consistency violations survive a negative-value screen. Omission avoids assuming recoverable original totals.",metadata_file="../component-metadata.csv")
    (DOCS/"corrected-no-headers-74-input-manifest.json").write_text(json.dumps(candidate,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"projection_dimensions":len(indices),"rows":n,"projection_seconds":round(time.monotonic()-started,3)}),flush=True)
    main(work=WORK,census_file="corrected-no-headers-74-input-manifest.json",metadata_file="../component-metadata.csv",output_prefix="corrected-no-headers-74",timestamp_kind="corrected",domain_policy="nonnegative_flow_features_with_window_sentinel_v1")
