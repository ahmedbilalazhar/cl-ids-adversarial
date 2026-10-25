"""Data-only endpoint/capture concentration; no predictive model or host claim."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
WORK=ROOT/"data/raw/phase3-feasibility-corrected"
started=time.monotonic()
state=np.load(WORK/"domain-checked/conditional-components-120.npz",allow_pickle=False)
split=np.load(WORK/"domain-checked/conditional-candidate-split.npz",allow_pickle=False)
positions=split["source_positions"]
meta=pd.read_csv(WORK/"component-metadata.csv",usecols=["src_ip","dst_ip","protocol"],dtype={"src_ip":"string","dst_ip":"string","protocol":"int16"}).iloc[positions].reset_index(drop=True)
src=meta.src_ip.to_numpy(dtype=str);dst=meta.dst_ip.to_numpy(dtype=str)
lo=np.where(src<=dst,src,dst);hi=np.where(src<=dst,dst,src)
pairs=pd.Series(lo)+"|"+pd.Series(hi)+"|"+meta.protocol.astype(str)
roles=split["roles"];role_names=["train","development","test"]
report=json.loads((DOCS/"corrected-domain-checked-candidate-split-feasibility.json").read_text())
labels=state["labels"][positions]
rows=[]
for code,family in enumerate(report["families"]):
    mask=labels==code
    counts=pairs[mask].value_counts()
    rows.append({"family":family["family"],"surviving_rows":int(mask.sum()),"distinct_endpoint_pair_protocols":len(counts),"largest_pair_rows":int(counts.iloc[0]) if len(counts) else 0,"largest_pair_fraction":float(counts.iloc[0]/mask.sum()) if mask.any() else None,"role_pair_counts":{name:int(pairs[mask&(roles==role)].nunique()) for role,name in enumerate(role_names)}})
pair_sets=[set(pairs[roles==i]) for i in range(3)]
host_sets=[set(src[roles==i])|set(dst[roles==i]) for i in range(3)]
result={"status":"conditional_capture_context_census_not_host_disjoint_evaluation","completed_utc":datetime.now(timezone.utc).isoformat(),"parent_split":"corrected-domain-checked-candidate-split-feasibility.json","rows":len(positions),"models_fitted":0,"endpoint_pair_key":"lexically unordered source/destination IP pair plus protocol; no port; not a victim or campaign ID","role_pair_counts":{name:len(pair_sets[i]) for i,name in enumerate(role_names)},"role_host_counts":{name:len(host_sets[i]) for i,name in enumerate(role_names)},"cross_role_pair_intersections":{f"{role_names[a]}_{role_names[b]}":len(pair_sets[a]&pair_sets[b]) for a,b in [(0,1),(0,2),(1,2)]},"cross_role_host_intersections":{f"{role_names[a]}_{role_names[b]}":len(host_sets[a]&host_sets[b]) for a,b in [(0,1),(0,2),(1,2)]},"families":rows,"elapsed_seconds":round(time.monotonic()-started,3),"limits":["Endpoint concentration does not identify independent campaigns or causal spurious features","Lexical ordering is only a deterministic undirected key, not numeric IP topology","No model outcomes or final profile selection"]}
(DOCS/"capture-context-census.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"pairs":result["role_pair_counts"],"pair_overlap":result["cross_role_pair_intersections"],"host_overlap":result["cross_role_host_intersections"],"elapsed_seconds":result["elapsed_seconds"]}))
