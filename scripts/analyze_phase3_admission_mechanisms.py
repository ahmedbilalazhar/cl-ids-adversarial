"""Audit saved DM/DC selection, replay occupancy, and family outcomes.

This is a read-only development-bank diagnostic. It verifies each selected
result against the completion manifest and never loads feature or test arrays.
Counts describe supplied-label classes; replay poison counts describe stored
known-poison IDs, not replay draw exposure or causal contribution.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / 'results/phase3-followup-ablation'
AUDIT_ROOT = ROOT / 'results/phase3-rigorous-audit-v1'
OUT = AUDIT_ROOT / 'admission-mechanism-v1'
SEEDS = [1,2,3,4,5,6,7,8,9,10,11,42]
DOSES = [(0,1),(1,10),(3,10),(1,2)]
METHODS = ('DM','DC')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def bootstrap_mean_ci(values, rng, draws=20000):
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 1 or len(x) != len(SEEDS) or not np.isfinite(x).all():
        raise ValueError('Expected one finite paired value per ownership seed')
    samples = x[rng.integers(0, len(x), size=(draws, len(x)))].mean(axis=1)
    return [float(x.mean()), float(np.quantile(samples,.025)), float(np.quantile(samples,.975))]


def client_class_counts(admission):
    result = {}
    for client in admission['clients']:
        for item in client['quotas']:
            key = (int(client['client']), int(item['source_code']))
            if key in result:
                raise ValueError(f'Duplicate client/class quota: {key}')
            result[key] = {'raw': int(item['raw']), 'admitted': int(item['admitted']),
                           'protected': bool(item['protected'])}
    return result


def class_metrics(matrix, code):
    a = np.asarray(matrix, dtype=np.int64)
    tp = int(a[code,code]); support = int(a[code,:].sum()); predicted = int(a[:,code].sum())
    precision = tp / predicted if predicted else None
    recall = tp / support if support else None
    f1 = 2*tp/(2*tp + predicted-tp + support-tp) if support or predicted else None
    return {'support':support,'precision':precision,'recall':recall,'f1':f1}


def main():
    completion = json.loads((RUN_ROOT/'completion-followup.json').read_text(encoding='utf-8'))
    audit = json.loads((AUDIT_ROOT/'followup-independent-audit.json').read_text(encoding='utf-8'))
    if audit.get('status') != 'passed' or audit.get('completion_inventory_hashes_valid') is not True:
        raise RuntimeError('Independent follow-up audit must pass before analysis')
    manifest = json.loads((ROOT/'data/processed/phase3-reference74-v1/development/manifest.json').read_text(encoding='utf-8'))
    families, eligible = manifest['families'], set(map(int,manifest['eligible_codes']))
    expected = {k.replace('\\','/'):v for k,v in completion['files'].items()
                if k.replace('\\','/').endswith('/result.json')}
    runs = {}
    for rel, digest in expected.items():
        if not rel.startswith('runs/core-DR-'):
            continue
        path = RUN_ROOT/rel
        if sha256(path) != digest:
            raise RuntimeError(f'Completion-manifest digest mismatch: {rel}')
        run = json.loads(path.read_text(encoding='utf-8'))
        s = run['settings']
        if s['admission'] in METHODS:
            key=(s['admission'],int(s['seed']),tuple(s['dose']))
            if key in runs:
                raise RuntimeError(f'Duplicate unique DM/DC core cell: {key}')
            runs[key]=run
    if len(runs) != 96:
        raise RuntimeError(f'Expected 96 unique DM/DC core results, found {len(runs)}')

    rng=np.random.default_rng(240517)
    admission_rows=[]; memory_seed={}; f1_seed={}; paired_id_hash_differences={}
    quota_parity_comparisons=0
    for dose in DOSES:
        paired_id_hash_differences[dose[0]/dose[1]]=0
        for seed in SEEDS:
            dm=runs[('DM',seed,dose)]; dc=runs[('DC',seed,dose)]
            if dm['input_identity'] != dc['input_identity']:
                raise RuntimeError(f'DM/DC input identity differs at seed={seed}, dose={dose}')
            if dm['settings']['q'] != dc['settings']['q'] or dm['settings']['q'] != .75:
                raise RuntimeError('Primary DM/DC comparison is not the matched q=.75 design')
            dmem={int(x['stage']):x for x in dm['memory']}
            cmem={int(x['stage']):x for x in dc['memory']}
            dled={int(x['stage']):x for x in dm['ledger'] if x['kind']=='admission'}
            cled={int(x['stage']):x for x in dc['ledger'] if x['kind']=='admission'}
            if sorted(dled) != [1,2,3,4] or sorted(cled) != [1,2,3,4]:
                raise RuntimeError('Expected four admission stages for each paired run')
            for stage in range(1,5):
                a,b=dled[stage],cled[stage]
                ac,bc=client_class_counts(a),client_class_counts(b)
                if ac.keys()!=bc.keys():
                    raise RuntimeError(f'Class quota inventory differs at seed={seed}, dose={dose}, stage={stage}')
                quota_parity_comparisons += 1
                for client_code in ac:
                    left,right=ac[client_code],bc[client_code]
                    if left['raw'] != right['raw'] or left['admitted'] != right['admitted']:
                        raise RuntimeError(f'Per-client/class counts differ at {(seed,dose,stage,client_code)}')
                    admission_rows.append({
                      'seed':seed,'dose':dose[0]/dose[1],'stage':stage,'client':client_code[0],
                      'source_code':client_code[1],'family':families[client_code[1]],
                      'eligible_metric_class':client_code[1] in eligible,'raw':left['raw'],
                      'admitted':left['admitted'],'retention':left['admitted']/left['raw'] if left['raw'] else None,
                      'protected_by_dc':right['protected']})
                paired_id_hash_differences[dose[0]/dose[1]] += sum(
                    ca['admitted_ids_sha256'] != cb['admitted_ids_sha256']
                    for ca,cb in zip(a['clients'],b['clients']))
            for stage in (2,3,4):
                memory_seed[(dose,seed,stage)]={
                  method:sum(int(c['poison_ids']) for c in run['memory'][stage-1]['clients'])
                  for method,run in (('DM',dm),('DC',dc))}
            for code in range(16):
                if code not in eligible: continue
                fm={method:class_metrics(run['stages'][3]['confusion'],code)
                    for method,run in (('DM',dm),('DC',dc))}
                if fm['DM']['f1'] is None or fm['DC']['f1'] is None:
                    continue
                f1_seed[(dose,seed,code)]={method:fm[method]['f1'] for method in METHODS}

    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'admission-class-counts.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(admission_rows[0]));writer.writeheader();writer.writerows(admission_rows)
    with (OUT/'poison-memory-occupancy.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['dose','stage','seed','DM_poison_ids','DC_poison_ids','DC_minus_DM','capacity_per_method']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for dose in DOSES:
            for seed in SEEDS:
                for stage in (2,3,4):
                    x=memory_seed[(dose,seed,stage)]
                    writer.writerow({'dose':dose[0]/dose[1],'stage':stage,'seed':seed,
                        'DM_poison_ids':x['DM'],'DC_poison_ids':x['DC'],
                        'DC_minus_DM':x['DC']-x['DM'],'capacity_per_method':2500})
    family_rows=[]
    for dose in DOSES:
        for code in sorted(eligible):
            vals=[f1_seed[(dose,s,code)]['DC']-f1_seed[(dose,s,code)]['DM']
                  for s in SEEDS if (dose,s,code) in f1_seed]
            if not vals: continue
            mean,lo,hi=bootstrap_mean_ci(vals,rng)
            family_rows.append({'dose':dose[0]/dose[1],'source_code':code,'family':families[code],
                'n_seed_pairs':len(vals),'mean_F1_DC_minus_DM':mean,'bootstrap95_low':lo,
                'bootstrap95_high':hi,'seed_differences':vals})
    with (OUT/'family-f1-effects.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=[k for k in family_rows[0] if k!='seed_differences']);writer.writeheader()
        for r in family_rows: writer.writerow({k:v for k,v in r.items() if k!='seed_differences'})

    memory_summary=[]
    for dose in DOSES:
        for stage in (2,3,4):
            d=[memory_seed[(dose,s,stage)]['DM'] for s in SEEDS]
            c=[memory_seed[(dose,s,stage)]['DC'] for s in SEEDS]
            delta=[b-a for a,b in zip(d,c)]
            dmean,dlo,dhi=bootstrap_mean_ci(d,rng);cmean,clo,chi=bootstrap_mean_ci(c,rng)
            diff,lo,hi=bootstrap_mean_ci(delta,rng)
            memory_summary.append({'dose':dose[0]/dose[1],'stage':stage,'n_seed_pairs':12,
                'DM_mean_poison_ids':dmean,'DM_bootstrap95':[dlo,dhi],
                'DC_mean_poison_ids':cmean,'DC_bootstrap95':[clo,chi],
                'DC_minus_DM_mean':diff,'paired_bootstrap95':[lo,hi],
                'DM_mean_share_of_2500':dmean/2500,'DC_mean_share_of_2500':cmean/2500})

    # Exact per-client/class quota equality means aggregate class counts cannot
    # explain outcome differences. The hash-only admission artifacts expose
    # changed selected sets but not which examples or their score distributions.
    admission_rate={}
    for dose in DOSES:
        for stage in range(1,5):
            rows=[x for x in admission_rows if x['dose']==dose[0]/dose[1] and x['stage']==stage]
            raw=sum(x['raw'] for x in rows);admitted=sum(x['admitted'] for x in rows)
            admission_rate.setdefault(str(dose[0]/dose[1]),{})[str(stage)]={'raw':raw,'admitted':admitted,'rate':admitted/raw if raw else None}

    # Three panels show retained poisoned memory, per-family downstream F1
    # effects, and parity of supplied-label class admission quotas.
    f,axes=plt.subplots(1,2,figsize=(9.5,4.2))
    focus_dose=.5
    means=[];lower=[];upper=[]
    for stage in (2,3,4):
        vals=[memory_seed[((1,2),s,stage)]['DC']-memory_seed[((1,2),s,stage)]['DM'] for s in SEEDS]
        m,lo,hi=bootstrap_mean_ci(vals,rng);means.append(m);lower.append(m-lo);upper.append(hi-m)
    axes[0].errorbar([2,3,4],means,yerr=[lower,upper],marker='o',capsize=3,color='#C64A4A')
    axes[0].axhline(0,color='black',lw=.7)
    axes[0].set(title='Stored known-poison IDs: DC minus DM',xlabel='End of stage',ylabel='Paired count difference (five clients)',xticks=[2,3,4]);axes[0].grid(alpha=.2)
    class_focus=[r for r in family_rows if r['dose']==focus_dose]
    class_focus.sort(key=lambda r:r['source_code'])
    y=np.arange(len(class_focus));means=[r['mean_F1_DC_minus_DM'] for r in class_focus]
    xerr=[[m-r['bootstrap95_low'] for m,r in zip(means,class_focus)],
          [r['bootstrap95_high']-m for m,r in zip(means,class_focus)]]
    axes[1].errorbar(means,y,xerr=xerr,fmt='o',capsize=2,color='#514A9D')
    axes[1].axvline(0,color='black',lw=.7);axes[1].set(yticks=y,yticklabels=[r['family'] for r in class_focus],xlabel='Stage-4 class F1: DC minus DM',title='Per-family outcome at dose .5');axes[1].grid(axis='x',alpha=.2)
    f.suptitle('Matched DM/DC mechanism diagnostics (12 paired ownership seeds)',y=1.02)
    f.tight_layout();f.savefig(OUT/'admission-mechanism-diagnostic.pdf',bbox_inches='tight');plt.close(f)

    result={'schema':'phase3-admission-mechanism-v1','status':'passed',
      'study':'adopted 74-feature reused development bank; primary DR q=.75; no training performed',
      'source_manifest':'results/phase3-followup-ablation/completion-followup.json',
      'analysis_script_sha256':sha256(Path(__file__)),
      'completion_manifest_sha256':sha256(RUN_ROOT/'completion-followup.json'),
      'development_manifest_sha256':sha256(ROOT/'data/processed/phase3-reference74-v1/development/manifest.json'),
      'unique_DM_DC_core_results':len(runs),'paired_seeds':SEEDS,'doses':[d[0]/d[1] for d in DOSES],
      'result_hashes_verified':True,'paired_input_identities_equal':True,
      'per_client_source_class_raw_and_admitted_counts_equal_DM_DC':True,
      'admission_ledger_stages_compared':quota_parity_comparisons,
      'client_stage_admitted_set_hash_differences_by_dose':{str(k):v for k,v in paired_id_hash_differences.items()},
      'client_stage_admitted_set_hash_difference_fraction_by_dose':{str(k):v/240 for k,v in paired_id_hash_differences.items()},
      'overall_admission_rates':admission_rate,'poison_memory_summary':memory_summary,
      'family_f1_effects':family_rows,
      'interpretation_limits':['Admission score vectors and per-example scores were not retained; hashes reveal identity changes but not which examples/ranks changed.',
       'Poison memory counts are stored corrupted IDs, not actual replay draws or gradient exposure.',
       'Client-specific aggregation weights were not retained in the result ledger.',
       'All outcomes reuse one development bank; intervals resample ownership seeds and do not quantify capture/site uncertainty.',
       'The descriptive diagnostics do not identify a causal mechanism for the DC benign-FAR difference.'],
      'outputs':['admission-class-counts.csv','poison-memory-occupancy.csv','family-f1-effects.csv','admission-mechanism-diagnostic.pdf']}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('family_f1_effects','interpretation_limits','poison_memory_summary')},indent=2))


if __name__=='__main__':main()
