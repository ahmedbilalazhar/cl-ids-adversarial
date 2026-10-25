"""Prepare same-row FP64 inputs for a conditional corrected-release graph audit.

This projection is a candidate alias map, not a claim of unchanged extractor
semantics or an adopted learner dataset. Attempted labels never become features.
"""
from __future__ import annotations
import json
import time
import zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
from census_corrected_feasibility import ALIASES

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
WORK=ROOT/"data/raw/phase3-feasibility-corrected"
started=time.monotonic()
original=json.loads((ROOT/"docs/phase3-plan/candidate-feature-schema.json").read_text(encoding="utf-8"))["features"]
mapped=[ALIASES.get(c,c) for c in original]
files=[]
total=0
first_metadata=True
with zipfile.ZipFile(WORK/"CICIDS2017_improved.zip") as archive, (WORK/"candidate-features-fp64.raw").open("wb") as output, (WORK/"candidate-finite.raw").open("wb") as valid_output, (WORK/"component-metadata.csv").open("w",encoding="utf-8",newline="") as metadata_output:
    for file_index,name in enumerate(sorted(n for n in archive.namelist() if n.endswith(".csv"))):
        local_start=0
        with archive.open(name) as source:
            for frame in pd.read_csv(source,chunksize=50000,low_memory=False):
                numeric=frame[mapped].apply(pd.to_numeric,errors="coerce").to_numpy(dtype="<f8",copy=True)
                numeric[numeric==0]=0
                finite=np.isfinite(numeric).all(axis=1)
                count=len(frame)
                ids=(np.uint64(file_index)<<np.uint64(32))|np.arange(local_start,local_start+count,dtype=np.uint64)
                attempted=pd.to_numeric(frame["Attempted Category"],errors="coerce")
                labels=frame["Label"].astype(str).str.strip().where(attempted.eq(-1),"BENIGN")
                # Invalid/missing attempted annotations are excluded explicitly,
                # rather than treated as successful benign remaps.
                labels=labels.where(np.isfinite(attempted)&attempted.mod(1).eq(0),None)
                meta=pd.DataFrame({"row_id":ids,"file_index":np.full(count,file_index,dtype=np.uint8),
                    "archive_row":np.arange(local_start,local_start+count,dtype=np.uint32),
                    "src_ip":frame["Src IP"],"src_port":frame["Src Port"],"dst_ip":frame["Dst IP"],"dst_port":frame["Dst Port"],
                    "protocol":frame["Protocol"],"timestamp_raw":frame["Timestamp"],"duration_us_raw":frame["Flow Duration"],
                    "reference_label_raw":labels,"source_label_before_attempted_policy":frame["Label"],
                    "attempted_category":attempted,"valid_numeric":finite})
                meta.to_csv(metadata_output,index=False,header=first_metadata)
                first_metadata=False
                output.write(numeric.tobytes(order="C"))
                valid_output.write(finite.astype(np.uint8).tobytes())
                local_start+=count
                total+=count
        files.append({"name":name,"file_index":file_index,"rows":local_start})
        print(json.dumps({"file":name,"rows":local_start,"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)
result={"status":"conditional_corrected_component_audit_inputs_not_model_dataset","completed_utc":datetime.now(timezone.utc).isoformat(),
    "total_rows":total,"files":files,"numeric_feature_order":original,"source_feature_order":mapped,
    "numeric_dtype":"little-endian float64 before T0 transform","source_census":"corrected-full-census.json",
    "label_policy":"Attempted Category != -1 maps to benign; confirmed Infiltration - Portscan retained as a distinct label; no attempted/annotation fields become predictors.",
    "semantic_equivalence_to_original_verified":False,"elapsed_seconds":round(time.monotonic()-started,3),"models_trained":False}
(DOCS/"corrected-component-input-manifest.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"rows":total,"elapsed_seconds":result["elapsed_seconds"]}),flush=True)
