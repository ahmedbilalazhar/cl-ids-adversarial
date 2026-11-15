"""Rebuild amended exploratory endpoints from immutable archived GPU runs."""
import hashlib,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from phase3_evidence import confusion_metrics, signed_rank_enumeration, holm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"phase3-implementation/results/final-run"
OUT=ROOT/"submissions/phase3-report"
OUT.mkdir(parents=True,exist_ok=True)
ledger=json.loads((SRC/"analysis/run-file-hashes.json").read_text())
rows=[]; audit=[]; family_rows=[]
with zipfile.ZipFile(SRC/"part-b-experiment-runs.zip") as z:
 for name in z.namelist():
  if "/runs_cuda/" not in name or not name.endswith(".json"):continue
  raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==ledger[Path(name).name]
  r=json.loads(raw);c=r["cfg"];s=r["stages"]
  row=dict(tag=r["tag"],learner=c["learner"],adm=c["admission"],seed=c["seed"],rep=c["rep"],dose=c["dose"],k=c["n_att"],variant=r["tag"].split(f"-s{c['seed']}")[1] or "default",A=r["summary"]["A"])
  admission=r['admission'][1]
  row['poisoned_admission_fraction']=admission['admitted_poisoned']/admission['poisoned_rows'] if admission['poisoned_rows'] else np.nan
  row['new_label_retention']=admission['new_class_rows_admitted']/admission['new_class_rows']
  row['admitted_fraction']=admission['admitted']/admission['rows']
  row['poisoned_memory_end']=r['cost']['buffer_poisoned_records_end']
  row['realized_hulk_corruption']=r['poison']['flipped']/r['poison']['hulk_rows_stage'] if c['dose']>0 else 0.
  acquisition=[]
  tax=json.loads((ROOT/'configs/phase3/taxonomy-v1.json').read_text())
  arrival={c['source_code']:c['arrival_stage'] for c in tax['classes']}
  for t,st in enumerate(s,1):
   conf=np.asarray(st['confusion'],dtype=np.int64)
   diag=np.diag(conf);denom=conf.sum(1)+conf.sum(0)
   full_f1=np.divide(2*diag,denom,out=np.zeros(16,float),where=denom>0)
   assert abs(float(full_f1[st['eligible']].mean())-st['macro_f1']) < 1e-12
   for code,reported in st['classes'].items():
    code=int(code);support=int(conf[code].sum());predicted=int(conf[:,code].sum())
    assert reported['support']==support and reported['tp']==int(conf[code,code])
    assert abs(reported['recall']-conf[code,code]/support) < 1e-12
    assert abs(reported['precision']-(conf[code,code]/predicted if predicted else 0)) < 1e-12
    assert abs(reported['f1']-full_f1[code]) < 1e-12
   assert abs(float(np.trace(conf)/conf.sum())-st['accuracy']) < 1e-12
   assert abs(float(1-conf[0,0]/conf[0].sum())-st['benign_far']) < 1e-12
   if t>=2:
    assert abs(float(conf[4,4]/conf[4].sum())-st['hulk_recall']) < 1e-12
    assert abs(float(conf[4,0]/conf[4].sum())-st['hulk_asr']) < 1e-12
   m=confusion_metrics(conf,st['eligible'])
   audit.append(dict(tag=r['tag'],stage=t,original_macro_f1=st['macro_f1'],eligible_bank_macro_f1=m['macro_f1'],
       difference=m['macro_f1']-st['macro_f1'],unsupported_true_rows=int(conf.sum()-conf[st['eligible']].sum())))
   for code,metrics in m['classes'].items():family_rows.append(dict(tag=r['tag'],stage=t,code=code,**metrics))
   new=[code for code in m['classes'] if arrival[code]==t and code not in (0,4) and t>=2]
   if new:acquisition.append(np.mean([m['classes'][code]['f1'] for code in new]))
   for key in ["accuracy","macro_f1","benign_far","hulk_recall","hulk_asr"]:row[f"{key}_{t}"]=st.get(key,np.nan)
   for key in ('accuracy','macro_f1'):row[f'{key}_{t}']=m[key]
   for key in ('macro_precision','macro_recall'):row[f'{key}_{t}']=m[key]
   for key in ('accuracy','precision','recall','f1','fpr'):row[f'binary_{key}_{t}']=m['binary'][key]
  row['original_A']=row['A'];row['A']=float(np.mean(acquisition))
  row['BWT']=r['summary']['BWT'];row['forgetting']=r['summary']['forgetting']
  rows.append(row)
df=pd.DataFrame(rows);assert len(df)==696
keys=["learner","adm","seed","rep","variant"]
clean=df[df.dose==0].set_index(keys)
assert clean.index.is_unique
for i,r in df.iterrows():
 twin=clean.loc[tuple(r[k] for k in keys)]
 df.loc[i,"H_targeted"]=np.mean([r[f"hulk_asr_{t}"]-twin[f"hulk_asr_{t}"] for t in [3,4]])
 df.loc[i,"delta_recall_E2"]=r.hulk_recall_2-twin.hulk_recall_2
 df.loc[i,"final_recall_damage"]=twin.hulk_recall_4-r.hulk_recall_4
 df.loc[i,"arm"]="clean" if r.dose==0 else f"k{r.k}-d{r.dose:g}"
df.to_csv(OUT/"corrected-runs.csv",index=False)
pd.DataFrame(audit).to_csv(OUT/'metric-population-audit.csv',index=False)
family_frame=pd.DataFrame(family_rows)
family_frame.to_csv(OUT/'eligible-family-metrics.csv',index=False)
family_frame[(family_frame.stage==4)&family_frame.code.isin([7,12])].groupby('tag')[['f1','recall']].mean().rename(columns={'f1':'E1_anchor_F1','recall':'E1_anchor_recall'}).to_csv(OUT/'anchor-retention.csv')
def paired(l,a,arm,e):
 return df[(df.learner==l)&(df.adm==a)&(df.arm==arm)&(df.variant=="default")].set_index(["seed","rep"])[e]
tests=[]
for e in ["H_targeted","delta_recall_E2"]:
 for l1,l2 in [("DR","EI"),("DR","FT"),("EI","FT")]:
  for arm in sorted(set(df.arm)-{"clean"}):
   d=paired(l1,"NONE",arm,e)-paired(l2,"NONE",arm,e)
   tests.append(("C1",l1+" minus "+l2,arm,e,d))
for arm in sorted(set(df.arm)):
 for e in (["A","benign_far_4"] if arm=="clean" else ["A","H_targeted","delta_recall_E2"]):
  tests.append(("C2","DC minus DM",arm,e,paired("DR","DC",arm,e)-paired("DR","DM",arm,e)))
res=[];parts=[]
for family,comp,arm,e,d in tests:
 assert len(d)==12 and not d.isna().any()
 g=d.groupby(level="seed").mean();assert len(g)==3
 test=signed_rank_enumeration(g.values)
 res.append(dict(family=family,comparison=comp,arm=arm,endpoint=e,n_partitions=3,replicates_per_partition=4,mean_difference=g.mean(),min_partition=g.min(),max_partition=g.max(),p_partition=test['p'],rank_biserial=test['rank_biserial'],method=test['method']))
 for seed,v in g.items():parts.append(dict(comparison=comp,arm=arm,endpoint=e,seed=seed,difference=v))
r=pd.DataFrame(res);assert len(r)==47
r["p_holm_all47"]=holm(r.p_partition.values)
r.to_csv(OUT/"exploratory-comparisons.csv",index=False)
pd.DataFrame(parts).to_csv(OUT/"partition-effects.csv",index=False)
base=df[df.variant=="default"]
base.groupby(["learner","adm","arm"])[["H_targeted","delta_recall_E2","final_recall_damage","macro_f1_4","benign_far_4","A"]].agg(["mean","std"]).to_csv(OUT/"summary.csv")
fig,ax=plt.subplots(1,2,figsize=(10,4))
for l in ["FT","EI","DR"]:
 b=base[(base.learner==l)&(base.adm=="NONE")&(base.dose==0)]
 ax[0].plot(range(1,5),[b[f"macro_f1_{t}"].mean() for t in range(1,5)],marker="o",label=l)
 b=base[(base.learner==l)&(base.adm=="NONE")&(base.arm=="k5-d0.5")]
 ax[1].plot(range(2,5),[b[f"hulk_asr_{t}"].mean() for t in range(2,5)],marker="o",label=l)
ax[0].set(title="Clean continual learning",xlabel="Stage",ylabel="Eligible macro-F1")
ax[1].set(title="Targeted error: five attackers, 50% corruption",xlabel="Stage (withdrawal after E2)",ylabel="Hulk predicted benign")
for a in ax:a.legend();a.set_ylim(0,1)
fig.tight_layout();fig.savefig(OUT/"corrected-trajectories.png",dpi=180);plt.close(fig)
print(f"Verified {len(df)} runs; wrote {len(r)} exploratory comparisons to {OUT}")
