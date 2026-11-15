"""Validate and summarise only completed, identity-matched CPU trajectories."""
import json
from pathlib import Path
import sys
import argparse

import numpy as np
import pandas as pd

from phase3_evidence import confusion_metrics, signed_rank_enumeration, holm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from run_phase3_cpu_study import digest, canonical, assert_parity, validate_result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--required-snapshot',action='store_true',help='Build a truthful 21-run submission while optional expansion continues')
    parser.add_argument('--mechanism-snapshot',action='store_true',help='Use only the complete 12-run first-replicate mechanism study')
    args=parser.parse_args()
    study = ROOT / 'results/phase3-cpu-supplement'
    out = ROOT / 'submissions/phase3-report'; out.mkdir(exist_ok=True)
    if args.required_snapshot or args.mechanism_snapshot:
        names=[]
        for seed in (101,102,103):
            for dose in ('000','050'):
                names.append(f'DR-NONE-d{dose}-k5-r0-s{seed}.json')
                if not args.mechanism_snapshot:names.append(f'DR-DQ-d{dose}-k5-r0-s{seed}.json')
            names.extend(f'DR-NONE-d050-k5-r0-s{seed}-{mode}.json' for mode in ('oracle_purge','random_delete'))
            if not args.mechanism_snapshot:names.append(f'POOLED-s{seed}.json')
        expected=12 if args.mechanism_snapshot else 21
        assert len(names)==expected and all((study/'runs'/name).exists() for name in names)
        completion=dict(required_complete=not args.mechanism_snapshot,expanded_complete=False,count=expected,
            run_hashes={name:digest(study/'runs'/name) for name in names})
    else:
        completion_path=study/'completion.json'
        completion = json.loads(completion_path.read_text()) if completion_path.exists() else json.loads((out/'cpu-selected-results.json').read_text())
    assert completion['required_complete'] or args.mechanism_snapshot
    identity = json.loads((study / 'identity.json').read_text())
    for rel, sha in identity['sources'].items(): assert digest(ROOT / rel) == sha
    missing_inputs=[]
    for rel, sha in identity['inputs'].items():
        if (ROOT/rel).exists():assert digest(ROOT / rel) == sha
        else:missing_inputs.append(rel)
    raw = []
    for name, sha in completion['run_hashes'].items():
        path = study / 'runs' / name
        assert digest(path) == sha
        r = json.loads(path.read_text()); validate_result(r)
        assert r['study_identity'] == identity['sha256']
        assert r['run_identity'] == canonical(dict(study=identity['sha256'],cfg=r['cfg'],kind=r['study_kind']))
        assert r['cfg']['rounds']==12 and r['cfg']['batch']==256
        raw.append(r)
    assert len(raw) == completion['count'] == (12 if args.mechanism_snapshot else 57 if completion['expanded_complete'] else 21)
    lookup = {(r['cfg']['seed'], r['cfg']['rep'], r['cfg']['dose'], r['cfg']['admission'],
               r['cfg']['intervention'], r['study_kind']): r for r in raw}
    assert len(lookup) == len(raw)
    for r in raw:
        c = r['cfg']
        if c['intervention'] != 'none':
            ref = lookup[(c['seed'], c['rep'], c['dose'], 'NONE', 'none', 'federated')]
            assert_parity(ref, r)
    arrivals = {x['source_code']: x['arrival_stage'] for x in json.loads((ROOT / 'configs/phase3/taxonomy-v1.json').read_text())['classes']}
    rows = []; perclass = []; memories = []
    for r in raw:
        c = r['cfg']
        condition = 'pooled' if r['study_kind'] == 'pooled' else ('clean' if c['dose'] == 0 else c['intervention'])
        row = dict(tag=r['tag'], seed=c['seed'], rep=c['rep'], condition=condition,
                   adm=c['admission'], dose=c['dose'], study_kind=r['study_kind'],
                   seconds=r['cost']['seconds'], device='cpu')
        new_scores = []
        for st in r['stages']:
            t = st['stage']; m = confusion_metrics(st['confusion'], st['eligible'])
            for k in ('accuracy', 'macro_f1', 'benign_far', 'hulk_recall', 'hulk_asr'):
                row[f'{k}_{t}'] = m.get(k, np.nan)
            for k in ('macro_precision','macro_recall'):row[f'{k}_{t}']=m[k]
            for k in ('accuracy','precision','recall','f1','fpr'):row[f'binary_{k}_{t}']=m['binary'][k]
            for code, metrics in m['classes'].items():
                perclass.append(dict(tag=r['tag'], seed=c['seed'], rep=c['rep'], stage=t, code=code, **metrics))
            cs = [code for code in m['classes'] if arrivals[code] == t and code not in (0, 4) and t >= 2]
            if cs: new_scores.append(np.mean([m['classes'][code]['f1'] for code in cs]))
        row['A'] = float(np.mean(new_scores)) if r['study_kind'] == 'federated' else np.nan
        if r['study_kind'] == 'federated':
            row.update(BWT=r['summary']['BWT'], forgetting=r['summary']['forgetting'])
        for entry in r.get('memory_trajectory', []):
            memories.append(dict(tag=r['tag'], seed=c['seed'], rep=c['rep'], condition=condition,
                stage=entry['stage'], position='pre_deletion' if entry['stage']==2 else 'stage_end',
                records=sum(v['size'] for v in entry['clients']), poisoned=sum(v['poisoned'] for v in entry['clients'])))
        if r.get('interventions'):
            memories.append(dict(tag=r['tag'], seed=c['seed'], rep=c['rep'], condition=condition,
                stage=2, position='post_deletion', records=sum(v['after'] for v in r['interventions']),
                poisoned=sum(v['poison_remaining'] for v in r['interventions'])))
        rows.append(row)
    d = pd.DataFrame(rows)
    clean = d[(d.condition == 'clean') & (d.study_kind == 'federated')].set_index(['seed','rep','adm'])
    for i, r in d.iterrows():
        if r.study_kind == 'pooled': continue
        twin = clean.loc[(r.seed, r.rep, r.adm)]
        d.loc[i,'H_targeted'] = np.mean([r[f'hulk_asr_{t}']-twin[f'hulk_asr_{t}'] for t in (3,4)])
        d.loc[i,'delta_recall_E2'] = r.hulk_recall_2-twin.hulk_recall_2
        d.loc[i,'final_recall_damage'] = twin.hulk_recall_4-r.hulk_recall_4
    d.to_csv(out/'cpu-runs.csv', index=False)
    pd.DataFrame(perclass).to_csv(out/'cpu-family-metrics.csv', index=False)
    pd.DataFrame(memories).to_csv(out/'cpu-memory-trajectory.csv', index=False)
    metrics = ['H_targeted','hulk_asr_4','hulk_recall_4','macro_f1_4','accuracy_4','benign_far_4','A','seconds']
    d.groupby(['study_kind','adm','condition'])[metrics].agg(['mean','std','count']).to_csv(out/'cpu-summary.csv')
    comparisons = []; effects = []
    for left,right in [('oracle_purge','none'),('random_delete','none'),('oracle_purge','random_delete')]:
        for endpoint in ['H_targeted','hulk_asr_4','macro_f1_4','benign_far_4','A']:
            def vec(condition):
                return d[(d.condition==condition)&(d.adm=='NONE')].set_index(['seed','rep'])[endpoint]
            delta = vec(left)-vec(right)
            assert not delta.isna().any()
            g = delta.groupby(level='seed').mean(); assert len(g)==3
            test = signed_rank_enumeration(g.values)
            comparisons.append(dict(comparison=left+' minus '+right, endpoint=endpoint,
                mean_difference=g.mean(), min_partition=g.min(), max_partition=g.max(),
                n_partitions=3, replicates_per_partition=len(delta)//3, **test))
            for seed,v in g.items(): effects.append(dict(comparison=left+' minus '+right,endpoint=endpoint,seed=seed,difference=v))
    tests = pd.DataFrame(comparisons); tests['p_holm_all15']=holm(tests.p)
    tests.to_csv(out/'cpu-exploratory-comparisons.csv', index=False)
    pd.DataFrame(effects).to_csv(out/'cpu-partition-effects.csv', index=False)
    (out/'cpu-validation.json').write_text(json.dumps(dict(count=len(raw),
        required_complete=completion['required_complete'], mechanism_complete=True, expanded_complete=completion['expanded_complete'],
        e2_state_parity=True, all_hashes_valid=True, oracle_purity_valid=True,
        cpu_only_clean_references=True, missing_inputs_for_recheck=missing_inputs,
        study_identity=identity['sha256']), indent=2))
    (out/'cpu-selected-results.json').write_text(json.dumps(dict(required_complete=completion['required_complete'],
        expanded_complete=completion['expanded_complete'],count=len(raw),run_hashes=completion['run_hashes'],
        study_identity=identity['sha256']),indent=2))
    print('Validated CPU supplement:', len(raw), 'trajectories')


if __name__ == '__main__': main()
