"""Regenerate readable, consistently labelled research figures."""
from pathlib import Path
import json
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'submissions/phase3-report'
FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':10,
 'axes.titlesize':11,'axes.titleweight':'semibold','axes.spines.top':False,'axes.spines.right':False,
 'axes.edgecolor':'#8a989f','axes.linewidth':.7,'axes.labelcolor':'#263b48','text.color':'#263b48',
 'xtick.color':'#52616b','ytick.color':'#52616b','xtick.labelsize':9,'ytick.labelsize':9,
 'legend.fontsize':9,'legend.framealpha':.96,'legend.edgecolor':'#dce4e8',
 'lines.linewidth':1.8,'lines.markersize':5,'axes.axisbelow':True,
 'savefig.facecolor':'white','figure.facecolor':'white'})
C={'FT':'#b94735','EI':'#bc8415','DR':'#177e89','NONE':'#177e89','DC':'#b94735','DM':'#7153a0','DQ':'#38864d',
   'none':'#177e89','oracle_purge':'#38864d','random_delete':'#bc8415'}
def save(f,name):
 regular=[ax for ax in f.axes if not ax.images and ax.get_label()!='<colorbar>']
 for i,ax in enumerate(regular):
  ax.grid(axis='y',color='#dce4e8',linewidth=.6,alpha=.7)
  ax.tick_params(length=3,width=.6)
  if len(regular)>1:ax.text(0,1.04,f'({chr(97+i)})',transform=ax.transAxes,fontsize=10,fontweight='bold',va='bottom')
 f.tight_layout(pad=1.2)
 for ext in ('png','pdf'):f.savefig(FIG/f'{name}.{ext}',dpi=220,bbox_inches='tight')
 plt.close(f)
def main():
 d=pd.read_csv(OUT/'corrected-runs.csv');b=d[d.variant=='default']
 # Preserve the original report's useful full-inventory confusion view, rebuilt
 # from the verified run archive rather than extracted as a low-resolution image.
 with zipfile.ZipFile(ROOT/'phase3-implementation/results/final-run/part-b-experiment-runs.zip') as z:
  confs=[]
  for name in z.namelist():
   if '/runs_cuda/DR-NONE-d000-' not in name or not name.endswith('.json'):continue
   r=json.loads(z.read(name));c=r['cfg']
   if c['mem']==500 and c['lam_y']==1 and c['lam_z']==.1 and c['buffer']=='reservoir':confs.append(np.asarray(r['stages'][-1]['confusion']))
 assert len(confs)==12
 conf=np.mean(confs,axis=0);support=conf.sum(1);rows=np.flatnonzero(support>0)
 normalized=conf[rows]/support[rows,None]
 labels=['Benign','Bot','DDoS','GoldenEye','Hulk','SlowHTTP','Slowloris','FTP-Patator','Heartbleed','Infiltration','Infil.-Portscan','PortScan','SSH-Patator','Web brute force','Web SQLi','Web XSS']
 f,ax=plt.subplots(figsize=(8.8,6.4));im=ax.imshow(normalized,vmin=0,vmax=1,cmap='Blues',aspect='auto')
 ax.set_xticks(range(16),labels,rotation=55,ha='right',fontsize=10)
 ax.set_yticks(range(len(rows)),[f'{labels[i]} (n={int(support[i])})' for i in rows],fontsize=10)
 ax.set(xlabel='Predicted annotation',ylabel='True annotation / fixed development support')
 for i in range(len(rows)):
  for j in range(16):
   if normalized[i,j]>=.05:ax.text(j,i,f'{normalized[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if normalized[i,j]>.55 else '#213b50')
 f.colorbar(im,ax=ax,fraction=.035,pad=.025,label='Fraction within true class');save(f,'07-full-inventory-confusion')
 pd.DataFrame(normalized,index=[labels[i] for i in rows],columns=labels).to_csv(OUT/'full-inventory-confusion.csv')
 f,aa=plt.subplots(1,3,figsize=(8.2,2.8))
 for j,l in enumerate(('FT','EI','DR')):
  q=b[(b.learner==l)&(b.adm=='NONE')&(b.arm=='clean')]
  for ax,key in zip(aa,('A','BWT','forgetting')):
   v=q.groupby('seed')[key].mean();ax.scatter([j]*len(v),v,s=22,color=C[l],alpha=.6);ax.scatter(j,v.mean(),marker='_',s=160,color=C[l]);ax.set_xticks([0,1,2],['FT','EI','DR']);ax.axhline(0,color='.7',lw=.6)
 for ax,label in zip(aa,('Acquisition A','Backward transfer','Forgetting')):ax.set_ylabel(label)
 save(f,'08-retention-acquisition')
 costs=pd.read_csv(ROOT/'phase3-implementation/results/final-run/analysis/table-cost.csv').set_index('learner').loc[['FT','EI','DR']]
 f,aa=plt.subplots(1,3,figsize=(8.2,2.8))
 for ax,key,label in zip(aa,('seconds','comm_MB','buffer_KB'),('GPU wall seconds / run','Analytical exchange MB','Replay storage KB')):
  ax.bar(range(3),costs[key],color=[C[l] for l in costs.index],width=.6,zorder=3)
  ax.set_ylim(0,max(costs[key])*1.18)
  for j,value in enumerate(costs[key]):ax.text(j,value+max(costs[key])*.025,f'{value:.1f}' if key=='comm_MB' else f'{value:.0f}',ha='center',fontsize=9)
  ax.set_xticks(range(3),costs.index);ax.set_ylabel(label)
 save(f,'09-resource-cost')
 f,aa=plt.subplots(1,2,figsize=(8.2,3))
 for l in ('FT','EI','DR'):
  q=b[(b.learner==l)&(b.adm=='NONE')&(b.arm=='clean')]
  for ax,key in zip(aa,('macro_f1','benign_far')):
   v=np.array([q[f'{key}_{t}'] for t in range(1,5)])
   ax.plot(range(1,5),v.mean(1),'o-',color=C[l],label=l)
   ax.fill_between(range(1,5),v.mean(1)-v.std(1,ddof=1),v.mean(1)+v.std(1,ddof=1),color=C[l],alpha=.12)
   ax.set(xticks=[1,2,3,4],xlabel='Learning stage',ylim=(-.03,1.03))
 aa[0].set_ylabel('Eligible-bank macro-F1');aa[1].set_ylabel('Benign false-alarm rate');aa[0].legend(ncol=3)
 save(f,'01-clean-learning')
 arms=['k5-d0.25','k1-d1','k5-d0.5','k3-d1','k5-d0.9']
 labels=['5 clients\n25%','1 client\n100%','5 clients\n50%','3 clients\n100%','5 clients\n90%']
 f,aa=plt.subplots(1,2,figsize=(8.2,3.3))
 for j,l in enumerate(('FT','EI','DR')):
  q=b[(b.learner==l)&(b.adm=='NONE')]
  for ax,key in zip(aa,('delta_recall_E2','H_targeted')):
   for i,arm in enumerate(arms):
    v=q[q.arm==arm].groupby('seed')[key].mean();x=i+(j-1)*.19
    ax.scatter([x]*len(v),v,s=17,alpha=.5,color=C[l]);ax.scatter(x,v.mean(),marker='_',s=160,color=C[l],label=l if i==0 else None)
   ax.set_xticks(range(5),labels,fontsize=8);ax.axhline(0,color='.6',lw=.6);ax.set_xlabel('Attacker count / within-client corruption')
 aa[0].set_ylabel('Signed recall change at E2');aa[1].set_ylabel('Targeted persistence H');aa[0].legend(ncol=3)
 save(f,'02-poisoning-effects')
 f,aa=plt.subplots(1,2,figsize=(8.2,3.2))
 for ax,arm in zip(aa,('k5-d0.5','k5-d0.9')):
  for adm in ('NONE','DC','DM','DQ'):
   g=b[(b.learner=='DR')&(b.adm==adm)&(b.arm==arm)].groupby('seed')[['A','H_targeted']].mean()
   marker={'NONE':'D','DC':'s','DM':'^','DQ':'P'}[adm]
   ax.scatter(g.A,g.H_targeted,color=C[adm],s=20,alpha=.4);ax.scatter(g.A.mean(),g.H_targeted.mean(),color=C[adm],s=60,marker=marker,label=adm)
  ax.set(xlabel='Untargeted acquisition A (higher is better)',ylabel='Persistence H (lower is better)',title='50% corruption' if arm.endswith('0.5') else '90% corruption',ylim=(0,1.03),xlim=(0,.4))
 aa[0].legend(ncol=2);save(f,'03-admission-tradeoffs')
 variants=[('default','DR reference'),('-z0','No logit matching'),('-y0','No replay-label term'),('-fifo','FIFO memory'),('-mem100','100 records/client'),('-mem1000','1000 records/client')]
 f,aa=plt.subplots(1,2,figsize=(8.2,3.4),sharey=True);rows=[]
 for i,(v,label) in enumerate(variants):
  q=d[(d.learner=='DR')&(d.adm=='NONE')&(d.variant==v)];clean=q[q.arm=='clean'];po=q[q.arm=='k5-d0.5']
  assert len(clean)==len(po)==12,(v,len(clean),len(po))
  aa[0].barh(i,clean.macro_f1_4.mean(),color=C['DR']);aa[1].barh(i,po.H_targeted.mean(),color=C['FT'])
  rows.append(dict(variant=label,clean_macro_f1=clean.macro_f1_4.mean(),poison_macro_f1=po.macro_f1_4.mean(),H_targeted=po.H_targeted.mean(),A=po.A.mean(),FAR=po.benign_far_4.mean()))
 aa[0].invert_yaxis();aa[0].set_yticks(range(6),[x[1] for x in variants])
 for ax in aa:ax.set_xlim(0,1)
 aa[1].tick_params(labelleft=False)
 aa[0].set_xlabel('Clean final macro-F1');aa[1].set_xlabel('Targeted persistence H (50% corruption)')
 save(f,'04-component-ablations');pd.DataFrame(rows).to_csv(OUT/'ablation-summary-corrected.csv',index=False)
 full=[]
 specs=[('DR','NONE',v,label) for v,label in variants]+[
  ('DR','DC','default','DR+DC reference'),('DR','DC','-q0.5','DC quota 0.5'),('DR','DC','-q0.9','DC quota 0.9'),
  ('DR','DC','-nmin5','DC small-class threshold 5'),('DR','DC','-nmin100','DC small-class threshold 100'),
  ('EI','NONE','default','EI reference'),('EI','NONE','-lam_E10','EI penalty 10'),('EI','NONE','-lam_E1000','EI penalty 1000')]
 for l,a,v,label in specs:
  q=d[(d.learner==l)&(d.adm==a)&(d.variant==v)];clean=q[q.arm=='clean'];po=q[q.arm=='k5-d0.5']
  assert len(clean)==len(po)==12,(l,a,v)
  full.append(dict(variant=label,clean_macro_f1=clean.macro_f1_4.mean(),poison_macro_f1=po.macro_f1_4.mean(),
   H_targeted=po.H_targeted.mean(),A=po.A.mean(),FAR=po.benign_far_4.mean(),final_recall_damage=po.final_recall_damage.mean(),
   poisoned_memory_end=po.poisoned_memory_end.mean(),delta_recall_E2=po.delta_recall_E2.mean()))
 pd.DataFrame(full).to_csv(OUT/'ablation-summary-all.csv',index=False)
 if not (OUT/'cpu-runs.csv').exists():print('Four GPU figure sets complete; CPU results pending');return
 cpu=pd.read_csv(OUT/'cpu-runs.csv');f,aa=plt.subplots(1,3,figsize=(9,3.2))
 for mode in ('none','oracle_purge','random_delete'):
  q=cpu[(cpu.condition==mode)&(cpu.adm=='NONE')];label={'none':'Ordinary','oracle_purge':'Oracle purge','random_delete':'Random deletion'}[mode]
  v=q.groupby('seed')[[f'hulk_asr_{t}' for t in (2,3,4)]].mean()
  aa[0].plot([2,3,4],v.mean().values,'o-',color=C[mode],label=label)
  for ax,key in zip(aa[1:],('H_targeted','macro_f1_4')):
   v=q.groupby('seed')[key].mean();x=('none','oracle_purge','random_delete').index(mode)
   ax.scatter([x]*len(v),v,color=C[mode],s=25);ax.scatter(x,v.mean(),marker='_',s=160,color=C[mode]);ax.set_xticks([0,1,2],['Ordinary','Oracle','Random'],rotation=25)
 aa[0].set(xlabel='Stage (intervene after E2)',ylabel='Hulk predicted benign',xticks=[2,3,4]);aa[0].legend(fontsize=7)
 aa[1].set_ylabel('Targeted persistence H');aa[2].set_ylabel('Final macro-F1')
 for ax in aa:ax.set_ylim(-.03,1.03)
 save(f,'05-cpu-memory-intervention')
 if not (cpu.condition=='pooled').any():print('Five completed figure sets; pooled reference pending');return
 f,aa=plt.subplots(1,2,figsize=(8.2,3.2));mem=pd.read_csv(OUT/'cpu-memory-trajectory.csv')
 for mode in ('none','oracle_purge','random_delete'):
  q=mem[(mem.condition==mode)&(mem.position!='post_deletion')].groupby('stage').poisoned.mean()
  aa[0].plot(q.index,q.values,'o-',label=mode,color=C[mode])
 aa[0].set(xlabel='Stage (pre-deletion at E2)',ylabel='Poisoned memory records',xticks=[1,2,3,4]);aa[0].legend(fontsize=7)
 clean=cpu[(cpu.condition=='clean')&(cpu.adm=='NONE')].groupby('seed').macro_f1_4.mean();pooled=cpu[cpu.condition=='pooled'].macro_f1_4
 aa[1].scatter([0]*len(clean),clean,color=C['DR']);aa[1].scatter([1]*len(pooled),pooled,color=C['DM'])
 aa[1].set(xticks=[0,1],xticklabels=['Continual DR','Offline pooled'],ylabel='Clean final macro-F1',ylim=(0,1));save(f,'06-memory-and-offline-reference')
 print('Six figure sets complete')
if __name__=='__main__':main()
