"""Census original-background versus remapped-attempted benign annotations."""
import json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3];DOCS=ROOT/"docs/phase3-plan"
BASE=ROOT/"data/raw/phase3-feasibility-corrected";WORK=BASE/"no-headers-74"
meta=pd.read_csv(BASE/"component-metadata.csv",usecols=["file_index","source_label_before_attempted_policy","attempted_category"],dtype={"file_index":"uint8","source_label_before_attempted_policy":"string","attempted_category":"int16"})
state=np.load(WORK/"conditional-components-120.npz",allow_pickle=False)
split=np.load(WORK/"conditional-candidate-split.npz",allow_pickle=False)
ownership=np.load(WORK/"conditional-ownership-benign-subset-seed-1.npz",allow_pickle=False)
selected=np.zeros(len(meta),dtype=bool);selected[ownership["source_positions"]]=True
role=np.full(len(meta),-1,dtype=np.int8);role[split["source_positions"]]=split["roles"]
parent=json.loads((DOCS/"corrected-no-headers-74-input-manifest.json").read_text())
file_names={f["file_index"]:f["name"] for f in parent["files"]}
labels=json.loads((DOCS/"corrected-no-headers-74-component-feasibility.json").read_text())["label_code_order"]
benign=state["labels"]==labels.index("Benign")
attempted=meta.attempted_category.to_numpy()!=-1
marked=meta.source_label_before_attempted_policy.str.contains("Attempted",case=False,na=False).to_numpy(dtype=bool)
rows=[]
for role_id,role_name in [(0,"training_inventory_before_benign_selection"),(1,"development_inventory"),(2,"test_inventory")]:
    mask=benign&(role==role_id)
    rows.append({"role":role_name,"benign_total":int(mask.sum()),"original_background":int((mask&~attempted).sum()),"remapped_attempted":int((mask&attempted).sum())})
training=[]
for fi,name in file_names.items():
    mask=selected&benign&(meta.file_index.to_numpy()==fi)
    if mask.any():training.append({"source_file":name,"selected_benign":int(mask.sum()),"original_background":int((mask&~attempted).sum()),"remapped_attempted":int((mask&attempted).sum())})
result={"status":"conditional_annotation_provenance_census_no_predictions","completed_utc":datetime.now(timezone.utc).isoformat(),"profile":"corrected-no-headers-74","role_census":rows,"selected_training_benign":training,"raw_category_values":sorted(int(v) for v in meta.attempted_category.unique()),"raw_attempted_marker_category_disagreements":int((attempted!=marked).sum()),"models_fitted":0,"limits":["Original background remains a reference annotation, not certified benign ground truth","Remapped attempted traffic need not match an operational false-alert definition","No outcome-driven subgroup or threshold selection"]}
(DOCS/"annotation-provenance-census.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"roles":rows,"training":training,"marker_disagreements":result["raw_attempted_marker_category_disagreements"]}))
