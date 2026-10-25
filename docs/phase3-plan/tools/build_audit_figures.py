"""Plot observed data-feasibility counts, never simulated model performance."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
OUT=ROOT/"output/figures/phase3-audit"
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.titlesize":14,"axes.labelsize":11,"axes.spines.top":False,"axes.spines.right":False,"svg.fonttype":"none","savefig.facecolor":"white"})
TEAL="#176B70";NAVY="#19364B";ORANGE="#B75B28"

def save(fig,name):
    fig.savefig(OUT/(name+".png"),dpi=180)
    fig.savefig(OUT/(name+".svg"))
    plt.close(fig)

split=json.loads((DOCS/"corrected-domain-checked-candidate-split-feasibility.json").read_text())
lookup={f["family"]:f for f in split["families"]}
names=["FTP-Patator","SSH-Patator","DoS Hulk","Heartbleed","Infiltration","Infiltration - Portscan","Web Attack Brute Force","Web Attack XSS","Web Attack Sql Injection"]
short=["FTP anchor","SSH anchor","Hulk source","Heartbleed","Infiltration","Infiltration-Portscan","Web brute force","Web XSS","Web SQL injection"]
fig,ax=plt.subplots(figsize=(10,6));fig.subplots_adjust(left=.23,right=.96,top=.82,bottom=.16)
y=np.arange(len(names));height=.23
for offset,(role,color,label) in enumerate(zip(["train","development","test"],[NAVY,TEAL,ORANGE],["Train","Development","Test"])):
    values=np.array([lookup[n][role]["rows"] for n in names])
    bars=ax.barh(y+(offset-1)*height,np.maximum(values,.6),height,color=color,label=label)
    for bar,value in zip(bars,values):
        if value==0:bar.set_fill(False);bar.set_edgecolor(color)
        ax.text(max(value,.6)*1.12,bar.get_y()+bar.get_height()/2,f"{value:,}",va="center",fontsize=8.5,color=color)
ax.set_yticks(y,short);ax.invert_yaxis();ax.set_xscale("log");ax.set_xlim(.5,220000)
ax.axvline(50,color="#6A7077",ls="--",lw=1);ax.text(54,-.65,"50-row floor",fontsize=9,color="#555555")
ax.set_xlabel("Retained unique records per role (log scale; zero shown as an outline)")
ax.legend(loc="lower right",frameon=False,fontsize=10)
fig.suptitle("76-feature corrected candidate: split support",x=.23,ha="left",y=.96,color=NAVY)
fig.text(.23,.89,"Fixed component split; support also requires 5 components in every role.\nHeartbleed is test-only; only Infiltration-Portscan qualifies in E3.",fontsize=10)
fig.text(.02,.025,"DATA FEASIBILITY AUDIT - not trained-model performance. Candidate profile remains prospective.",fontsize=9,color="#555555")
save(fig,"candidate-support")

strict=json.loads((DOCS/"candidate-ownership-dose-audit.json").read_text())
bundle=json.loads((DOCS/"candidate-ownership-dose-audit-benign-subset.json").read_text())
fig,ax=plt.subplots(figsize=(10,6));fig.subplots_adjust(left=.11,right=.97,top=.79,bottom=.17)
x=np.arange(4);width=.34
for offset,(data,color,label) in enumerate([(strict,ORANGE,"Strict mixed-component retention"),(bundle,TEAL,"Proposed benign bundles")]):
    values=data["selected_benign_stage_counts"]
    bars=ax.bar(x+(offset-.5)*width,values,width,color=color,label=label)
    ax.bar_label(bars,labels=[f"{v:,}" for v in values],padding=4,fontsize=10)
ax.axhline(3500,color="#6A7077",ls="--",lw=1);ax.set_ylim(0,20500)
ax.set_xticks(x,["E1","E2","E3","E4"]);ax.set_ylabel("Selected benign training records")
ax.legend(loc="upper left",frameon=False,fontsize=10)
fig.suptitle("Original conditional candidate: benign workload",x=.11,ha="left",y=.96,color=NAVY)
fig.text(.11,.88,"The bundle amendment preserves one role/owner per retained component.\nDashed line: 3,500-record target. No model outcomes selected either rule.",fontsize=10)
fig.text(.02,.025,"DATA FEASIBILITY AUDIT - same original as-published candidate and fixed split in both bars.",fontsize=9,color="#555555")
save(fig,"benign-volume")

corrected=DOCS/"corrected-domain-checked-candidate-ownership-dose-audit-benign-subset.json"
if corrected.exists():
    c=json.loads(corrected.read_text());seeds=[s["seed"] for s in bundle["seeds"]]
    fig,ax=plt.subplots(figsize=(10,6));fig.subplots_adjust(left=.12,right=.97,top=.80,bottom=.18)
    x=np.arange(len(seeds));width=.35
    for offset,(data,color,label) in enumerate([(bundle,ORANGE,"Original 76-feature profile"),(c,TEAL,"Corrected 76-feature profile")]):
        vals=[100*s["doses"][-1]["global_raw_poison_fraction"] for s in data["seeds"]]
        ax.bar(x+(offset-.5)*width,vals,width,color=color,label=label)
    ax.set_xticks(x,[str(s) for s in seeds]);ax.set_xlabel("Prescribed ownership / training seed")
    ax.set_ylabel("Flipped records / all raw E2 records (%)");ax.legend(frameon=False,fontsize=10)
    fig.suptitle("A 50% local source dose is not 50% global contamination",x=.12,ha="left",y=.96,color=NAVY)
    fig.text(.12,.88,"Each candidate uses its own audited split, source inventory and synthetic ownership.\nSource-specific differences are not an isolated causal comparison.",fontsize=10)
    fig.text(.02,.025,"DATA FEASIBILITY AUDIT - before admission scoring; not observed defense or attack success.",fontsize=9,color="#555555")
    save(fig,"realized-dose")
print(json.dumps({"figures":[p.name for p in OUT.glob("*.png")],"models_fitted":0}))
