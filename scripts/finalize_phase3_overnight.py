"""Validate, independently score, plot and package the prospective CPU extension."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from phase3_evidence import confusion_metrics, signed_rank_enumeration, holm
OUT=ROOT/'results/phase3-overnight'
REPORT=ROOT/'submissions/phase3-overnight'
SEEDS=list(range(1,12))+[42]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2),encoding='utf-8')

def score(result,eligible,arrival):
    s=result['settings'];stages=[]
    for row in result['stages']:
        cm=np.asarray(row['confusion']);assert cm.shape==(16,16) and (cm>=0).all()
        codes=[c for c in eligible if arrival[c]<=row['stage']]
        metric=confusion_metrics(cm,codes);stages.append(metric)
    new=[]
    for stage in (2,3,4):
        codes=[c for c in eligible if arrival[c]==stage and c!=4]
        assert codes
        new.append(np.mean([stages[stage-1]['classes'][c]['f1'] for c in codes]))
    final=stages[-1]
    full_final=confusion_metrics(result['stages'][-1]['confusion'],list(range(16)))
    method=s['learner'] if s['admission']=='NONE' else s['admission']
    return dict(block=s['block'],method=method,seed=s['seed'],dose=s['dose'][0]/s['dose'][1],q=s['q'],lambda_y=s['lambda_y'],lambda_z=s['lambda_z'],
        macro_f1=final['macro_f1'],macro_precision=final['macro_precision'],macro_recall=final['macro_recall'],accuracy=final['accuracy'],benign_far=final['benign_far'],binary_precision=final['binary']['precision'],binary_recall=final['binary']['recall'],binary_f1=final['binary']['f1'],
        full_inventory_binary_precision=full_final['binary']['precision'],full_inventory_binary_recall=full_final['binary']['recall'],full_inventory_binary_f1=full_final['binary']['f1'],full_inventory_accuracy=full_final['accuracy'],
        A=float(np.mean(new)),e2_recall=stages[1]['hulk_recall'],e3_asr=stages[2]['hulk_asr'],e4_asr=stages[3]['hulk_asr'],elapsed_seconds=result['elapsed_seconds'])

def interval(values):
    v=np.asarray(values,float);g=np.random.default_rng(20261116)
    b=v[g.integers(0,len(v),size=(10000,len(v)))].mean(axis=1)
    return float(np.quantile(b,.025)),float(np.quantile(b,.975))

def markdown_table(frame,columns=None):
    frame=frame if columns is None else frame[columns]
    def fmt(x):return f'{x:.4f}' if isinstance(x,(float,np.floating)) else str(x)
    return '| '+' | '.join(map(str,frame.columns))+' |\n| '+' | '.join('---' for _ in frame.columns)+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None))

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--render-only',action='store_true');parser.add_argument('--package-to',type=Path);args=parser.parse_args()
    REPORT.mkdir(parents=True,exist_ok=True)
    if (OUT/'completion.json').exists():
        done=json.loads((OUT/'completion.json').read_text())
        if done.get('status')=='complete':raise RuntimeError('This completion is immutable; use a new output directory for additional experiments.')
    frozen=json.loads((OUT/'identity.json').read_text());fail=[]
    for rel,expected in frozen['source'].items():
        if sha(ROOT/rel)!=expected:fail.append(rel)
    assert not fail,('Study source drift',fail)
    missing_provenance=[]
    for rel,expected in frozen['inputs'].items():
        path=ROOT/rel
        if path.exists():assert sha(path)==expected,('Input drift',rel)
        else:
            assert rel.startswith(('data/raw/','data/processed/phase3-reference74-v1/builder/')),rel
            missing_provenance.append(rel)
    initial=json.loads((ROOT/'results/phase3-cpu-supplement/identity.json').read_text())
    tax_expected=next(v for k,v in initial['inputs'].items() if k.replace('\\','/')=='configs/phase3/taxonomy-v1.json')
    assert sha(ROOT/'configs/phase3/taxonomy-v1.json')==tax_expected
    tax=json.loads((ROOT/'configs/phase3/taxonomy-v1.json').read_text())
    eligible=[c['source_code'] for c in tax['classes'] if c['scoring_eligible']]
    arrival={c['source_code']:c['arrival_stage'] for c in tax['classes']}
    raw=[];rows=[];hashes={};repair=[]
    for path in sorted((OUT/'runs').glob('*/result.json')):
        r=json.loads(path.read_text());assert r['status']=='complete' and not r['final_test_accessed'] and r['study_identity']==frozen['sha256']
        if r['settings']['block']=='smoke':continue
        raw.append(r);row=score(r,eligible,arrival);rows.append(row);hashes[path.relative_to(ROOT).as_posix()]=sha(path)
        oracle=r['oracle_label_repair']
        if oracle:
            assert oracle['nonlabel_state_unchanged'] and not oracle['independent_replicate']
            metrics=[confusion_metrics(s['confusion'],[c for c in eligible if arrival[c]<=s['stage']]) for s in oracle['stages']]
            repair.append(dict(method=row['method'],seed=row['seed'],changed_labels=oracle['changed_labels'],
                asr_effect=float(np.mean([metrics[i]['hulk_asr']-row[f'e{i+3}_asr'] for i in range(2)])),macro_f1_effect=metrics[-1]['macro_f1']-row['macro_f1']))
    frame=pd.DataFrame(rows);assert len(frame)
    for idx,row in frame.iterrows():
        clean=frame[(frame.block==row.block)&(frame.method==row.method)&(frame.seed==row.seed)&(frame.dose==0)&(frame.q==row.q)&(frame.lambda_y==row.lambda_y)&(frame.lambda_z==row.lambda_z)]
        if len(clean)==1:
            c=clean.iloc[0];frame.loc[idx,'H']=.5*((row.e3_asr-c.e3_asr)+(row.e4_asr-c.e4_asr));frame.loc[idx,'delta_recall']=row.e2_recall-c.e2_recall
    frame.to_csv(REPORT/'trajectory-metrics.csv',index=False)
    repair_frame=pd.DataFrame(repair);repair_frame.to_csv(REPORT/'oracle-repair.csv',index=False)
    core=frame[frame.block=='core'];complete=len(core)==240
    if complete:
        assert not core.duplicated(['method','seed','dose']).any()
        for method in ('FT','EI','DR','DM','DC'):
            for dose in (0.,.1,.3,.5):assert sorted(core[(core.method==method)&(core.dose==dose)].seed)==SEEDS
        core_raw=[r for r in raw if r['settings']['block']=='core']
        for seed in SEEDS:
            paired=[r for r in core_raw if r['settings']['seed']==seed]
            replay=[r for r in paired if r['settings']['learner']=='DR']
            assert len({r['stages'][0]['model_sha256'] for r in replay})==1,'Replay E1 prefix mismatch'
            for dose in ((0,1),(1,10),(3,10),(1,2)):
                group=[r for r in paired if tuple(r['settings']['dose'])==dose]
                assert len({tuple(r['attack']['poison_ids']) for r in group})==1,'Attack IDs differ between methods'
            for method in ('FT','EI','DR','DM','DC'):
                group=[r for r in paired if (r['settings']['learner'] if r['settings']['admission']=='NONE' else r['settings']['admission'])==method]
                assert len({r['stages'][0]['model_sha256'] for r in group})==1,'Dose E1 prefix mismatch'
    checks=dict(source_hashes_valid=True,present_input_hashes_valid=True,unbundled_raw_provenance=missing_provenance,result_hashes=hashes,complete_core=complete,complete_ownership_seeds=SEEDS if complete else [],trajectory_count=len(frame),oracle_suffixes=len(repair),final_test_accessed=False)
    write(REPORT/'validation.json',checks)
    summary=core.groupby(['method','dose'])[['macro_f1','H','A','benign_far','delta_recall']].agg(['mean','std','count'])
    summary.to_csv(REPORT/'core-summary.csv')
    comparisons=[]
    if complete:
        spec=json.loads((ROOT/'configs/phase3/overnight-analysis.json').read_text())
        for group in spec['family']:
            for endpoint in group['endpoints']:
                for left,right in group['pairs']:
                    for dose in group['doses']:
                        a=core[(core.method==left)&(core.dose==dose)].set_index('seed').loc[SEEDS,endpoint]
                        b=core[(core.method==right)&(core.dose==dose)].set_index('seed').loc[SEEDS,endpoint]
                        diff=(a-b).to_numpy();test=signed_rank_enumeration(diff);lo,hi=interval(diff)
                        comparisons.append(dict(group=group['group'],endpoint=endpoint,contrast=f'{left} - {right}',dose=dose,n=12,mean=float(diff.mean()),median=float(np.median(diff)),ci_low=lo,ci_high=hi,**test))
        assert len(comparisons)==29
        for row,p in zip(comparisons,holm([r['p'] for r in comparisons])):row['holm_p']=float(p)
    comparisons=pd.DataFrame(comparisons);comparisons.to_csv(REPORT/'paired-comparisons.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#17324D','text.color':'#17324D','axes.titleweight':'bold','savefig.bbox':'tight'})
    colors=dict(FT='#8996A5',EI='#B98428',DR='#7656A0',DM='#CE6061',DC='#147D83')
    fig,axes=plt.subplots(2,2,figsize=(10,7.2),layout='constrained')
    for ax,(metric,title) in zip(axes.flat,[('H','(a) Targeted error after withdrawal'),('A','(b) Untargeted new-family acquisition'),('macro_f1','(c) Final eligible macro F1'),('benign_far','(d) Final benign false-alarm rate')]):
        for method,color in colors.items():
            g=core[core.method==method].groupby('dose')[metric].agg(['mean','std','count'])
            if len(g):ax.errorbar(g.index,g['mean'],yerr=g['std']/np.sqrt(g['count']),label=method,color=color,marker='o',capsize=3,linewidth=1.7)
        ax.set_title(title,loc='left',fontsize=11);ax.set_xlabel('Fraction of attacker\'s Hulk labels flipped');ax.set_ylabel(metric);ax.set_xticks([0,.1,.3,.5]);ax.grid(axis='y',alpha=.15)
    if len(core):axes[0,0].legend(ncol=3,frameon=False,fontsize=9)
    fig.savefig(REPORT/'core-results.pdf');fig.savefig(REPORT/'core-results.png',dpi=180);plt.close(fig)
    gates=json.loads((OUT/'clean-gates.json').read_text()) if (OUT/'clean-gates.json').exists() else dict(passed=False,checks=[])
    parity_path=REPORT/'reference-parity.json'
    parity=json.loads(parity_path.read_text()) if parity_path.exists() else {}
    parity_note=('All nine clean final model hashes also reproduce the corresponding historical selected reference-engine runs exactly.' if parity.get('all_final_weights_match') else 'Historical final-weight parity is not asserted.')
    gateframe=pd.DataFrame(gates['checks'])
    main_pdf_info=json.loads((ROOT/'submissions/phase3-report/pdf-validation.json').read_text())
    original_pdf=ROOT/'submissions/phase3-report'/main_pdf_info['pdf'];assert sha(original_pdf)==main_pdf_info['sha256']
    mean_table=core.groupby(['method','dose'])[['macro_f1','H','A','benign_far']].mean().reset_index()
    discussion='The primary matrix is incomplete; no comparative conclusion is drawn.'
    if complete:
        means=core.groupby(['method','dose'])[['macro_f1','H','A','benign_far']].mean()
        dc=means.loc[('DC',.5)];dm=means.loc[('DM',.5)]
        direction='higher' if dc.A>=dm.A else 'lower'
        security='lower' if dc.H<=dm.H else 'higher'
        discussion=(f"At dose .5, DC has {direction} mean untargeted acquisition than DM "
            f"(A difference {dc.A-dm.A:+.4f}) and {security} mean poisoning-associated persistence "
            f"(H difference {dc.H-dm.H:+.4f}). These are distinct endpoints: protecting new-labelled "
            "admission does not by itself establish resistance to mislabeled Hulk records. "
            f"Clean final macro F1 is {means.loc[('FT',0),'macro_f1']:.4f} for FT, "
            f"{means.loc[('EI',0),'macro_f1']:.4f} for EI and {means.loc[('DR',0),'macro_f1']:.4f} for DR. "
            "Interpret these differences with the paired intervals and the single corrected family below. "
            "Neither a favorable mean nor non-significance establishes universal superiority or equivalence. "
            "The reference engine changes several historical numerical choices together; this study "
            "does not identify the individual causal benefit of batch size, head initialization or importance handling.")
    optional=frame[~frame.block.isin(['core','clean-confirmation'])]
    optional_table=optional.groupby(['block','method','q','lambda_y','lambda_z','dose'])[['macro_f1','H','A']].mean().reset_index()
    attacks=[];seen=set()
    e2_rows=len(np.load(ROOT/'data/processed/phase3-reference74-v1/train/E2/y.npy',mmap_mode='r',allow_pickle=False))
    for r in raw:
        s=r['settings'];key=(s['seed'],tuple(s['dose']))
        if s['block']!='core' or key in seen:continue
        seen.add(key);a=r['attack'];attacks.append(dict(seed=s['seed'],dose=s['dose'][0]/s['dose'][1],attacker=a['attacked_client'],eligible_hulk=a['eligible_hulk'],poison_rows=a['realized_poison_count'],global_E2_poison_share=a['realized_poison_count']/e2_rows))
    pd.DataFrame(attacks).to_csv(REPORT/'realized-attack-doses.csv',index=False)
    runtime=frame.elapsed_seconds
    text=f'''# Phase 3: Prospective CPU Extension

Saneedullah (23I-2568) and Ahmed Bilal (23I-2581) | 16 November 2026

## Status and scope

This appendix supplements the preceding report. It contains {len(frame)} completed
full trajectories and {len(repair)} paired oracle suffixes from a separately frozen
CPU protocol. Core status: **{'complete (240 trajectories, twelve ownership seeds)' if complete else 'incomplete; no complete-core claim'}**.
The original 696 GPU and 57 CPU results remain distinct historical experiments.
These counts must not be pooled as independent replicates.

The new experiment restores the Phase 2 single-attacker design, twelve independent
ownership/randomization seeds, client-local importance and the exact label-repair
intervention. It uses the previously selected reference-engine clean parameters,
with a fresh clean feasibility check before primary runs. **All outcomes in this
appendix use the frozen development bank, not an independent final-test bank.**
Historical use of that bank for model selection limits generalization claims;
prospective randomization does not turn it into a new final test.

## Reproducible implementation and clean feasibility

Python {frozen['python']}, PyTorch {frozen['torch']}, NumPy {frozen['numpy']}; CPU
FP32, deterministic operations, two worker processes and one numerical thread per
worker. Four stages, five persistent clients, 12 rounds per stage, one local epoch,
batch 128, Adam learning rate .001. EI uses client-local per-example empirical
importance (coefficient 100); replay uses 500 records per client, supervised replay
coefficient 1 and dark-logit coefficient .1. Newly introduced head rows use Xavier
initialization. DC and DM admit equal totals per client, using q=.75 and rare floor20.
Attack ownership is whole-component Dirichlet(.5); one eligible client receives
E2-only Hulk-to-benign corruption at nested doses 0, .1, .3 and .5. No escalation
is selected from observed effects. The fixed benign bank is present at every stage.

Clean-gate outcome: **{'passed' if gates['passed'] else 'not passed / unavailable'}**.
{parity_note}
Each learner must average at least .5 E1 recall on both FTP and SSH and .7 E2
Hulk recall across development ownership seeds 101--103. New ownership seeds are
1--11 and 42. They quantify variation within this historical capture, not across
independent organizations, campaigns or days.
The gate is an average over three partitions; passing it does not establish that
every partition learned each family. Per-seed gate recalls are retained in clean-gates.json.

{markdown_table(gateframe,['learner','stage','code','mean_recall','threshold','passed']) if len(gateframe) else 'No completed feasibility table.'}

## Primary outcomes

H is the E3/E4 mean change in Hulk-to-benign error relative to the same method's
clean trajectory. Negative values favor the poisoned run on this endpoint and are
reported without clipping. A equally weights stages E2--E4, then eligible newly
introduced untargeted families within each stage. Macro F1 restricts the true-label
population to eligible seen classes while retaining all prediction columns. Binary
metrics and per-stage matrices are supplied in machine-readable files.

{markdown_table(mean_table) if len(mean_table) else 'No completed primary trajectories.'}

{discussion}

![Primary results. Points are ownership-seed means; error bars are standard errors across completed seeds, not uncertainty across independent captures.](core-results.pdf)

The complete trajectory table also reports accuracy, binary precision/recall/F1,
Hulk recall and false-alarm rate. Rare-family errors remain in each full-inventory
16 by 16 confusion matrix; unsupported true rows are retained as zero support.
Binary metrics are supplied for both the eligible population and, in separately
named full_inventory columns, every supported seen family.

## Paired inference and uncertainty

The analysis specification was frozen before the new primary runs. One family of
29 comparisons follows Phase 2: 18 learner-pair contrasts for H and immediate Hulk
recall change, four DC-minus-DM acquisition contrasts, six corresponding security
contrasts and one clean false-alarm contrast. Tests use two-sided conditional
signed-rank sign enumeration, averaged tied ranks, zero removal and one Holm
correction across all 29 tests. Bootstrap intervals resample whole paired seeds
10,000 times and are descriptive, not simultaneous. The development-bank status
makes these comparisons exploratory evidence despite their prospective specification.
Non-significance is not equivalence; seed-level intervals are not capture-level intervals.

{markdown_table(comparisons,['endpoint','contrast','dose','mean','ci_low','ci_high','holm_p']) if len(comparisons) else 'The complete 29-comparison family is withheld because the core is incomplete.'}

## Exact replay label-repair diagnostic

At the maximum-dose E2 boundary, DR and DC clone their complete model, memory and
random states. The intervention changes only the replay labels of poisoned IDs
back to Hulk. Features, IDs, cached logits, widths, occupancy, RNG and weights are
unchanged, verified by hashes. The original branch continues unchanged. This is an
explanatory oracle, not a deployable defense, and does not undo E2 weight damage
or poisoned cached logits. A zero-survivor pair remains in the results.

{markdown_table(repair_frame.groupby('method')[['changed_labels','asr_effect','macro_f1_effect']].agg(['mean','std']).reset_index().set_axis(['method','labels mean','labels SD','ASR effect mean','ASR effect SD','F1 effect mean','F1 effect SD'],axis=1)) if len(repair_frame) else 'No completed oracle pairs.'}

Effects are repair minus unchanged continuation; negative ASR effects indicate
less targeted benign prediction after label repair. This estimates the total
downstream intervention effect, including later admission and weight changes.
It does not isolate a direct gradient pathway or prove labels are the only cause.

## Ablations, cost and remaining limitations

Optional complete twelve-seed blocks are reported in trajectory-metrics.csv with
their own block and coefficient/quota columns. Their scheduling uses runtime only,
never favorable outcomes. See completion.json for completed and omitted blocks.

{markdown_table(optional_table) if len(optional_table) else 'No optional ablation block was completed; the core and exact-repair controls take priority.'}

Per-seed attacker identity, eligible source count, realized poison count and global
E2 poison share are supplied in realized-attack-doses.csv. The nominal dose is a
fraction of one client's Hulk rows, not of all clients or all E2 records.
Median trajectory wall time was {runtime.median():.1f} s (90th percentile
{runtime.quantile(.9):.1f} s), including evaluation and checkpointing, measured
under two-process contention. Three clean-reference results include batch-1 and
batch-256 inference median/p95 after ten warm-ups and 100 timed calls. Stage weight
file sizes are serialized checkpoint costs, not measured network traffic.

The stronger CPU design addresses early-learning feasibility, client-local
importance, the prescribed single attacker, partition replication and exact memory
repair. DG, FIFO/class-balanced eviction, independent-capture evaluation, a validated
IoT schema and actual distributed networking remain outside this extension unless
separately evidenced. No generated result is substituted for missing classroom
feedback. The final-test bank remains sealed. Attack strength may legitimately
be weak under a single-client threat model; null and adverse results remain valid.

## Evidence and reproduction

The package includes source/input/runtime identities, the frozen analysis, the
whole-component ownership source, raw stage confusion matrices, selected stage
weights and per-seed CSVs. SHA-256 validation covers every packaged file. The
reference definitions and literature context are those in the preceding report;
this appendix introduces no new external performance claims.

Run `python scripts/finalize_phase3_overnight.py` to regenerate this appendix.
Use the pinned CPU environment to reproduce training; original result identities
must never be silently pooled with a different runtime. See
docs/phase3-overnight-plan.md and configs/phase3/overnight-analysis.json.
'''
    (REPORT/'appendix.md').write_text(text,encoding='utf-8')
    subprocess.run(['pandoc','appendix.md','-s','-V','papersize:a4','-V','geometry:margin=0.8in','-V','fontsize=10pt','-o','appendix.tex'],cwd=REPORT,check=True)
    tex=(REPORT/'appendix.tex').read_text(encoding='utf-8')
    theme=r'''\usepackage{titlesec}
\usepackage{fancyhdr}
\definecolor{reportnavy}{HTML}{17324D}
\definecolor{reportteal}{HTML}{147D83}
\titleformat{\section}{\Large\bfseries\color{reportnavy}}{}{0pt}{}
\titleformat{\subsection}{\large\bfseries\color{reportteal}}{}{0pt}{}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small Computer Networks | Phase 3 CPU Extension}
\fancyfoot[L]{\small 23I-2568 | 23I-2581}
\fancyfoot[R]{\small\thepage}
\setlength{\headheight}{15pt}
\setlength{\emergencystretch}{3em}
'''
    tex=tex.replace(r'\begin{document}',theme+'\n'+r'\begin{document}')
    (REPORT/'appendix.tex').write_text(tex,encoding='utf-8')
    subprocess.run(['tectonic','appendix.tex'],cwd=REPORT,check=True)
    main_tex=(ROOT/'submissions/phase3-report/phase3-report.tex').read_text(encoding='utf-8')
    appendix_tex=(REPORT/'appendix.tex').read_text(encoding='utf-8')
    appendix_body=appendix_tex.split(r'\begin{document}',1)[1].rsplit(r'\end{document}',1)[0]
    appendix_body=appendix_body.replace('{core-results.pdf}','{submissions/phase3-overnight/core-results.pdf}')
    complete_tex=main_tex.replace('{figures/','{submissions/phase3-report/figures/')
    complete_tex=complete_tex.replace('15 November 2026','16 November 2026')
    complete_tex=complete_tex.rsplit(r'\end{document}',1)[0]+'\n'+r'\clearpage'+'\n'+appendix_body+'\n'+r'\end{document}'+'\n'
    (REPORT/'Phase3_Report.tex').write_text(complete_tex,encoding='utf-8')
    local=ROOT/'tmp/phase3-overnight-tex/Phase3_Report.tex';local.parent.mkdir(parents=True,exist_ok=True)
    local.write_text(complete_tex.replace('{submissions/','{'+ROOT.as_posix()+'/submissions/'),encoding='utf-8')
    subprocess.run(['tectonic',str(local),'--outdir',str(REPORT)],cwd=ROOT,check=True)
    final=REPORT/'Phase3_Report.pdf'
    doc=pymupdf.open(final);page_checks=[]
    preview=ROOT/'tmp/pdfs/phase3-overnight';preview.mkdir(parents=True,exist_ok=True)
    for i,page in enumerate(doc):
        content=page.get_text();assert len(content.strip())>60
        page.get_pixmap(matrix=pymupdf.Matrix(1,1)).save(preview/f'page-{i+1:02}.png')
        page_checks.append(dict(page=i+1,characters=len(content)))
    write(REPORT/'pdf-validation.json',dict(pages=len(doc),sha256=sha(final),checks=page_checks));doc.close()
    if args.render_only:
        print('Render-only preflight complete; upload unchanged.');return
    # Preserve the previous upload and atomically replace the roll-number ZIP.
    rolls='23I-2568_23I-2581';target=ROOT/'submissions/phase3-final'/f'{rolls}.zip'
    original_target=target
    if args.package_to:target=args.package_to.resolve()
    target.parent.mkdir(parents=True,exist_ok=True)
    safe=(target.parent/'phase3-before-overnight.zip') if args.package_to else (ROOT/'submissions/phase3-overnight-baseline.zip')
    if not safe.exists():shutil.copy2(original_target,safe)
    temp=target.with_suffix('.building.zip');inventory={}
    def put(z,rel,data):
        if rel in inventory:
            assert inventory[rel]==hashlib.sha256(data).hexdigest(),('Conflicting archive input',rel)
            return
        z.writestr(f'{rolls}/{rel}',data);inventory[rel]=hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        with zipfile.ZipFile(safe) as old:
            for info in old.infolist():
                rel=info.filename.split('/',1)[1]
                if rel in ('Phase3_Report.pdf','Phase3_Report.tex','UPLOAD_INVENTORY.json','START_HERE.md'):continue
                put(z,rel,old.read(info.filename))
        put(z,'Phase3_Report.pdf',final.read_bytes())
        put(z,'Phase3_Report.tex',(REPORT/'Phase3_Report.tex').read_bytes())
        put(z,'START_HERE.md',f'''# Computer Networks Phase 3\n\nSaneedullah 23I-2568; Ahmed Bilal 23I-2581.\n\nOpen Phase3_Report.pdf. It contains the reviewed main report plus the prospective CPU appendix.\n\nHistorical evidence: 696 GPU and 57 CPU trajectories. New extension: {len(frame)} full trajectories, {len(repair)} paired suffixes; core complete: {complete}. All new inference is explicitly development-only. Do not pool experiment counts as independent seeds.\n\nComplete TeX: Phase3_Report.tex. Compile from the extracted ZIP root with XeLaTeX or Tectonic; it includes the main report and CPU extension with continuous pagination. All referenced vector figures are included. Separate appendix source is retained under submissions/phase3-overnight/.\n\nPrepared training/development data are deduplicated in data/shared/. Run scripts/materialize_submission_data.py first. Overnight ownership-source.npz permits ownership reconstruction without raw capture files. The recorded original raw-source hash remains provenance.\n\nSee docs/phase3-overnight-plan.md, configs/phase3/overnight-analysis.json and submissions/phase3-overnight/validation.json. The final-test bank is not included or evaluated. Every supplied file is hashed in UPLOAD_INVENTORY.json.\n'''.encode())
        for folder in (REPORT,):
            for p in sorted(folder.glob('*')):
                if p.is_file() and p.name!='upload-validation.json':put(z,p.relative_to(ROOT).as_posix(),p.read_bytes())
        for p in sorted((OUT/'runs').glob('*/result.json')):
            if p.parent.name.startswith('smoke-'):continue
            put(z,p.relative_to(ROOT).as_posix(),p.read_bytes())
            if p.parent.name.startswith('clean-confirmation-') and '-s101-' in p.parent.name:
                weights=p.parent/'E4-weights.npz';put(z,weights.relative_to(ROOT).as_posix(),weights.read_bytes())
        for rel in ('results/phase3-overnight/identity.json','results/phase3-overnight/ownership-source.npz','results/phase3-overnight/clean-gates.json','results/phase3-overnight/completion.json','scripts/run_phase3_overnight.py','scripts/reproduce_phase3_overnight.py','scripts/finalize_phase3_overnight.py','scripts/start_phase3_overnight.ps1','tests/test_phase3_overnight.py','docs/phase3-overnight-plan.md','configs/phase3/overnight-analysis.json','results/phase3-cpu-v3/development/tuning-selection.json'):
            p=ROOT/rel
            if p.exists():put(z,rel,p.read_bytes())
        z.writestr(f'{rolls}/UPLOAD_INVENTORY.json',json.dumps(dict(files=inventory,overnight=checks,final_test_features_included=False),indent=2))
    with zipfile.ZipFile(temp) as z:
        assert z.testzip() is None
        for rel,expected in inventory.items():assert hashlib.sha256(z.read(f'{rolls}/{rel}')).hexdigest()==expected
    try:os.replace(temp,target)
    except PermissionError:
        target=ROOT/'submissions/phase3-completed'/f'{rolls}.zip';target.parent.mkdir(parents=True,exist_ok=True)
        os.replace(temp,target)
    write(REPORT/'upload-validation.json',dict(path=str(target),sha256=sha(target),bytes=target.stat().st_size,files=len(inventory),all_hashes_valid=True))
    (ROOT/'submissions/phase3-final/STATUS.md').write_text(f'# Phase 3 CPU extension finished\n\nCore complete: {complete}. Full trajectories: {len(frame)}; paired oracle suffixes: {len(repair)}.\n\nValidated upload: {target}\n\nSHA-256: {sha(target)}\n\nFinal-test data were not accessed.\n',encoding='utf-8')
    print('OVERNIGHT REPORT AND UPLOAD VERIFIED',target,flush=True)

if __name__=='__main__':main()
