"""Independently audit and analyze the prospective DG admission block.

Uses saved development-bank confusion matrices only. It checks result and
checkpoint hashes, Phase 2 E1 parity, matched attack/input identities, and
the recorded 75% DG quotas before producing exploratory paired summaries.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.phase3_evidence import confusion_metrics
from src.phase3.common import array_identity, identity as model_identity, read_json

OUT = Path(os.environ.get('PHASE3_DG_AUDIT_OUT', ROOT / 'results/phase3-dg-baseline-v5'))
CONTROL = ROOT / 'results/phase3-overnight/runs'
SEEDS = (1,2,3,4,5,6,7,8,9,10,11,42)
DOSES = ((0,1),(1,10),(3,10),(1,2))
METHODS = ('DG','DM','DC')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dose_key(dose):
    return f'p{dose[0]}of{dose[1]}'


def run_path(method, seed, dose):
    if method == 'DG':
        folder = OUT / 'runs' / f'dg-baseline-DR-DG-s{seed}-{dose_key(dose)}-y1-z0.1-q0.75'
    else:
        folder = CONTROL / f'core-DR-{method}-s{seed}-{dose_key(dose)}-y1-z0.1-q0.75'
    return folder / 'result.json'


def admission_at(run, stage):
    rows = [r for r in run['ledger'] if r.get('kind') == 'admission' and r.get('stage') == stage]
    if len(rows) != 1:
        raise ValueError(f"Expected one admission ledger for stage {stage}")
    return rows[0]


def metrics(run, eligible, arrival, clean):
    by_stage = {}
    for row in run['stages']:
        stage = int(row['stage'])
        by_stage[stage] = confusion_metrics(row['confusion'], eligible)
    acquisition = []
    for stage in (2,3,4):
        new = [c for c in eligible if c != 4 and int(arrival[c]) == stage]
        if not new:
            raise ValueError(f'No eligible non-Hulk arrivals in E{stage}')
        acquisition.append(float(np.mean([by_stage[stage]['classes'][c]['f1'] for c in new])))
    h = float(np.mean([
        by_stage[s]['hulk_asr'] - clean[s]['hulk_asr'] for s in (3,4)
    ]))
    delta_rec = float(by_stage[2]['hulk_recall'] - clean[2]['hulk_recall'])
    final = by_stage[4]
    return {
        'A': float(np.mean(acquisition)), 'A_E2': acquisition[0],
        'A_E3': acquisition[1], 'A_E4': acquisition[2], 'H': h,
        'delta_rec': delta_rec, 'eligible_macro_f1_E4': final['macro_f1'],
        'eligible_accuracy_E4': final['accuracy'], 'benign_far_E4': final['benign_far'],
        'hulk_recall_E4': final.get('hulk_recall'), 'hulk_asr_E4': final.get('hulk_asr'),
        'elapsed_seconds': float(run['elapsed_seconds']),
    }


def bootstrap(values, rng, draws=20000):
    a = np.asarray(values, dtype=np.float64)
    if a.shape != (len(SEEDS),) or not np.isfinite(a).all():
        raise ValueError('Expected 12 finite whole-seed paired differences')
    samples = a[rng.integers(0, len(a), size=(draws, len(a)))].mean(axis=1)
    return float(a.mean()), float(np.median(a)), float(np.quantile(samples, .025)), float(np.quantile(samples, .975))


def main():
    completion = read_json(OUT / 'completion.json')
    study_identity = read_json(OUT / 'identity.json')
    executed_source = OUT / 'executed-source/scripts/run_phase3_overnight.py'
    expected_runner_sha = study_identity.get('source', {}).get('scripts/run_phase3_overnight.py')
    if not expected_runner_sha or not executed_source.is_file() or sha256(executed_source) != expected_runner_sha:
        raise RuntimeError('Archived DG runner source is missing or differs from the source frozen at launch')
    old_identity = read_json(ROOT / 'results/phase3-overnight/identity.json')
    dev = read_json(ROOT / 'data/processed/phase3-reference74-v1/development/manifest.json')
    old_completion = read_json(ROOT / 'results/phase3-overnight/completion.json')
    if completion.get('status') != 'complete' or completion.get('block') != 'dg-baseline' or completion.get('count') != 48:
        raise RuntimeError('A complete 48-cell DG block is required')
    if completion.get('final_test_accessed') is not False or study_identity.get('final_test_accessed') is not False:
        raise RuntimeError('Final-test access must remain false')
    env_fields=('python','torch','numpy')
    if any(study_identity.get(k) != old_identity.get(k) for k in env_fields):
        raise RuntimeError('DG and DM/DC controls were executed in different numerical environments')
    for rel, expected in study_identity['inputs'].items():
        if rel.endswith('/ownership-source.npz'):
            continue
        if old_identity['inputs'].get(rel) != expected:
            raise RuntimeError(f'Input identity differs from frozen controls: {rel}')
    result_hashes = completion.get('result_files_sha256', {})
    checkpoint_hashes = completion.get('checkpoint_files_sha256', {})
    if len(result_hashes) != 48 or len(checkpoint_hashes) != 192:
        raise RuntimeError('Incomplete DG result/checkpoint hash inventory')
    eligible = sorted(map(int, dev['eligible_codes']))
    arrival = list(map(int, dev['arrival']))
    raw = {}
    old_hashes = old_completion.get('files', {})

    # Verify every result payload and exact settings before making comparisons.
    for seed in SEEDS:
        for dose in DOSES:
            for method in METHODS:
                path = run_path(method, seed, dose)
                if not path.is_file():
                    raise RuntimeError(f'Missing {method}/{seed}/{dose}: {path}')
                rel = path.relative_to(OUT).as_posix() if method == 'DG' else path.relative_to(ROOT / 'results/phase3-overnight').as_posix()
                expected = result_hashes.get(rel) if method == 'DG' else old_hashes.get(rel)
                if not expected or sha256(path) != expected:
                    raise RuntimeError(f'Result hash missing/mismatched: {rel}')
                run = read_json(path)
                settings = run['settings']
                if (settings['admission'] != method or int(settings['seed']) != seed
                        or tuple(settings['dose']) != dose or run.get('final_test_accessed') is not False):
                    raise RuntimeError(f'Settings/final-test mismatch in {rel}')
                if method == 'DG' and run.get('study_identity') != study_identity.get('sha256'):
                    raise RuntimeError(f'Study identity mismatch: {rel}')
                raw[(method,seed,dose)] = run

                if method == 'DG':
                    for stage in range(1,5):
                        cp = path.parent / f'E{stage}-weights.npz'
                        cp_rel = cp.relative_to(OUT).as_posix()
                        if checkpoint_hashes.get(cp_rel) != sha256(cp):
                            raise RuntimeError(f'Checkpoint hash mismatch: {cp_rel}')
                        with np.load(cp, allow_pickle=False) as arrays:
                            slots = arrays['source_codes'].astype(int).tolist()
                            model_hash = model_identity({'slots': slots,
                                'weights': {k: array_identity(arrays[k])
                                            for k in arrays.files if k != 'source_codes'}})
                        if model_hash != run['stages'][stage-1]['model_sha256']:
                            raise RuntimeError(f'Checkpoint/model identity mismatch: {cp_rel}')

    # Validate parity of supplied data/attack IDs and the common, unfiltered E1.
    e1_cells = 0
    for seed in SEEDS:
        for dose in DOSES:
            dg = raw[('DG',seed,dose)]
            dc = raw[('DC',seed,dose)]
            dm = raw[('DM',seed,dose)]
            for method, ref in (('DC',dc),('DM',dm)):
                if dg['input_identity'] != ref['input_identity'] or dg['attack'] != ref['attack']:
                    raise RuntimeError(f'DG/{method} input or attack mismatch at {seed}/{dose}')
                if dg['stages'][0]['model_sha256'] != ref['stages'][0]['model_sha256']:
                    raise RuntimeError(f'DG/{method} E1 model mismatch at {seed}/{dose}')
                a, b = admission_at(dg,1), admission_at(ref,1)
                identity_fields = ('scorer_model_sha256','score_ids_sha256','scores_sha256')
                if any(a.get(k) != b.get(k) for k in identity_fields):
                    raise RuntimeError(f'DG/{method} E1 scorer mismatch at {seed}/{dose}')
                ca, cb = a['clients'], b['clients']
                summary_a = [(x['client'],x['raw'],x['admitted'],x['admitted_ids_sha256']) for x in ca]
                summary_b = [(x['client'],x['raw'],x['admitted'],x['admitted_ids_sha256']) for x in cb]
                if summary_a != summary_b:
                    raise RuntimeError(f'DG/{method} E1 admitted-ID mismatch at {seed}/{dose}')
            e1_cells += 1

            for stage in (2,3,4):
                adm = admission_at(dg,stage)
                if len(adm['clients']) != 5:
                    raise RuntimeError('DG must record all five clients')
                for client in adm['clients']:
                    if client.get('filter_policy') != 'global_low_loss' or client.get('keep_fraction') != [3,4]:
                        raise RuntimeError(f'Incorrect DG policy metadata at {seed}/{dose}/E{stage}')
                    expected_count = (3*int(client['raw']) + 2)//4
                    if int(client['admitted']) != expected_count:
                        raise RuntimeError(f'DG count does not equal floor(0.75*n + 0.5) at {seed}/{dose}/E{stage}')
                    if sum(int(c['raw']) for c in client['class_counts']) != int(client['raw']):
                        raise RuntimeError('DG class raw counts do not sum to client total')
                    if sum(int(c['admitted']) for c in client['class_counts']) != int(client['admitted']):
                        raise RuntimeError('DG class admitted counts do not sum to client total')

    # Derive metrics from stored confusion matrices and paired clean twins.
    clean = {}
    for method in METHODS:
        for seed in SEEDS:
            run = raw[(method,seed,(0,1))]
            clean[(method,seed)] = {int(row['stage']): confusion_metrics(row['confusion'],eligible)
                                    for row in run['stages']}
    rows = []
    for method in METHODS:
        for seed in SEEDS:
            for dose in DOSES:
                run = raw[(method,seed,dose)]
                m = metrics(run,eligible,arrival,clean[(method,seed)])
                rows.append({'method':method,'seed':seed,'dose':dose[0]/dose[1],**m})

    audit_dir = OUT / 'audit'
    audit_dir.mkdir(parents=True,exist_ok=True)
    fields = list(rows[0])
    with (audit_dir/'paired-metrics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    count_rows=[]
    for seed in SEEDS:
        for dose in DOSES:
            run=raw[('DG',seed,dose)]
            for stage in range(1,5):
                for c in admission_at(run,stage)['clients']:
                    count_rows.append({'seed':seed,'dose':dose[0]/dose[1],'stage':stage,
                        'client':c['client'],'raw':c['raw'],'admitted':c['admitted'],
                        'filter_policy':c.get('filter_policy','class_aware_or_bypass'),
                        'keep_fraction':c.get('keep_fraction'),
                        'admitted_ids_sha256':c['admitted_ids_sha256'],
                        'class_counts':json.dumps(c.get('class_counts',c.get('quotas',[])),sort_keys=True)})
    with (audit_dir/'dg-admission-counts.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(count_rows[0]));w.writeheader();w.writerows(count_rows)

    rng=np.random.default_rng(20261118)
    comparisons=[]
    metrics_to_compare=('A','H','delta_rec','eligible_macro_f1_E4','eligible_accuracy_E4','benign_far_E4','hulk_recall_E4','hulk_asr_E4')
    for dose in DOSES:
        dvalue=dose[0]/dose[1]
        for other in ('DC','DM'):
            for metric in metrics_to_compare:
                if metric in ('H','delta_rec') and dose==(0,1):
                    continue
                diffs=[]
                for seed in SEEDS:
                    left=next(x for x in rows if x['method']=='DG' and x['seed']==seed and x['dose']==dvalue)
                    right=next(x for x in rows if x['method']==other and x['seed']==seed and x['dose']==dvalue)
                    diffs.append(float(left[metric]-right[metric]))
                mean,median,lo,hi=bootstrap(diffs,rng)
                comparisons.append({'dose':dvalue,'contrast':f'DG-{other}','metric':metric,
                    'n_paired_seeds':12,'mean_difference':mean,'median_difference':median,
                    'whole_seed_bootstrap95_low':lo,'whole_seed_bootstrap95_high':hi,
                    'seed_differences':json.dumps(diffs)})
    with (audit_dir/'paired-comparisons.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(comparisons[0]));w.writeheader();w.writerows(comparisons)

    # Four-panel view emphasizes the primary adaptation/security endpoints.
    fig,axes=plt.subplots(2,2,figsize=(10,7))
    palette={'DG':'#3568A8','DM':'#E28E2C','DC':'#3A8E69'}
    for ax,metric,title in zip(axes.flat,('A','H','delta_rec','benign_far_E4'),
        ('Acquisition A','Persistent error H','E2 Hulk recall change','E4 benign FAR (clean dose)')):
        doses_plot=[d[0]/d[1] for d in DOSES]
        for method in METHODS:
            means=[];los=[];his=[]
            for dv in doses_plot:
                vals=[x[metric] for x in rows if x['method']==method and x['dose']==dv]
                if metric=='benign_far_E4' and dv!=0:
                    vals=[x[metric] for x in rows if x['method']==method and x['dose']==0]
                arr=np.asarray(vals,float)
                means.append(float(arr.mean()))
                if len(arr)==12:
                    samples=arr[rng.integers(0,len(arr),size=(10000,len(arr)))].mean(axis=1)
                    los.append(means[-1]-float(np.quantile(samples,.025)))
                    his.append(float(np.quantile(samples,.975))-means[-1])
                else:
                    los.append(0);his.append(0)
            ax.errorbar(doses_plot,means,yerr=np.vstack([los,his]),marker='o',capsize=3,label=method,color=palette[method])
        ax.axhline(0,color='black',lw=.7) if metric in ('H','delta_rec') else None
        ax.set_title(title);ax.set_xlabel('Poison dose');ax.grid(alpha=.22)
    axes[0,0].legend(title='Admission')
    fig.suptitle('Environment-pinned admission comparison (development outcomes; exploratory)')
    fig.tight_layout()
    fig.savefig(audit_dir/'dg-dm-dc-comparison.png',dpi=180,bbox_inches='tight')
    fig.savefig(audit_dir/'dg-dm-dc-comparison.pdf',bbox_inches='tight')
    plt.close(fig)

    summary={
        'schema':'phase3-dg-baseline-audit-v1','status':'passed',
        'study_identity_sha256':study_identity['sha256'],'completion_manifest_sha256':sha256(OUT/'completion.json'),
        'verified_DG_trajectories':48,'verified_checkpoints':192,'paired_control_trajectories':96,
        'seed_pairs':list(SEEDS),'doses':[d[0]/d[1] for d in DOSES],
        'environment':{'python':study_identity['python'],'torch':study_identity['torch'],'numpy':study_identity['numpy']},
        'environment_matches_frozen_controls':True,'nonownership_input_hashes_match_frozen_controls':True,
        'E1_cells_checked':e1_cells,'E1_admission_and_model_hash_parity_DG_DM_DC':True,
        'input_and_attack_parity_checked':True,'DG_75_percent_per_client_count_rule_checked':True,
        'all_metrics_recomputed_from_saved_confusion_matrices':True,
        'final_test_accessed':False,'analysis_role':'development-only exploratory; not in the original 29-test family',
        'comparison_rows':len(comparisons),
        'limits':['No per-example admission score vectors or accepted ID lists were stored; the audit verifies source-score hashes, policy metadata and counts, but cannot independently rerank every row.',
          'The 12 seeds vary synthetic ownership and training randomness on one fixed CICIDS2017-derived capture; they are not independent sites or captures.',
          'No sealed final-test or qualified external-method outcomes were accessed.',
          'Confidence intervals are descriptive whole-seed bootstrap intervals; no confirmatory significance claim is made.'],
        'outputs':['paired-metrics.csv','paired-comparisons.csv','dg-admission-counts.csv','dg-dm-dc-comparison.png','dg-dm-dc-comparison.pdf']}
    (audit_dir/'audit.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    report=['# DG baseline: audited exploratory comparison','',
      'This analysis uses the pinned CPU runtime and the development bank. It does not replace the frozen study or belong to the original confirmatory test family.','',
      f"- Verified DG trajectories: {summary['verified_DG_trajectories']} (all 12 seeds × 4 doses).",
      f"- Verified DG stage checkpoints: {summary['verified_checkpoints']}; DM/DC matched controls: {summary['paired_control_trajectories']}.",
      '- E1 admission IDs, scorer hashes and checkpoint model hashes match DM and DC; input/attack identities match for each paired cell.',
      '- DG keeps `floor(0.75 × client rows + 0.5)` from E2 onward without class protection; E1 is passed through unchanged.','',
      '## Paired outcomes','',
      'See `paired-comparisons.csv` for all dose-specific seed pairs and descriptive whole-seed bootstrap intervals. Positive H means more Hulk-to-benign error than the same admission method’s clean trajectory; negative Δrec means lower E2 Hulk recall than its clean twin. A is the equal-stage/equal-new-family F1 average for E2–E4, excluding Hulk.','',
      '## Limits','',
      *[f'- {x}' for x in summary['limits']],
      '']
    (audit_dir/'report.md').write_text('\n'.join(report),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('limits','outputs')},indent=2))


if __name__ == '__main__':
    main()
