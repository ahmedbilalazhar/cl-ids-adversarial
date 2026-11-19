"""Independent verification and paired analysis of the 48-cell eviction block."""
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

OUT = Path(os.environ.get('PHASE3_EVICTION_AUDIT_OUT', ROOT / 'results/phase3-eviction-baseline-v1'))
CONTROL = ROOT / 'results/phase3-overnight/runs'
SEEDS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 42)
DOSES = ((0, 1), (1, 2))
POLICIES = ('fifo', 'class_balanced')
ADMISSION = os.environ.get('PHASE3_EVICTION_ADMISSION', 'NONE')
if ADMISSION not in ('NONE', 'DC'):
    raise ValueError('PHASE3_EVICTION_ADMISSION must be NONE or DC')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dose_key(dose):
    return f'p{dose[0]}of{dose[1]}'


def result_path(policy, seed, dose):
    return OUT / 'runs' / (
        f'eviction-DR-{ADMISSION}-s{seed}-{dose_key(dose)}-y1-z0.1-q0.75-evict-{policy}'
    ) / 'result.json'


def control_path(seed, dose):
    return CONTROL / f'core-DR-{ADMISSION}-s{seed}-{dose_key(dose)}-y1-z0.1-q0.75' / 'result.json'


def admission_at(run, stage):
    rows = [r for r in run['ledger'] if r.get('kind') == 'admission' and int(r.get('stage', -1)) == stage]
    if len(rows) != 1:
        raise ValueError(f'Expected one admission record for E{stage}')
    return rows[0]


def endpoints(run, eligible, arrival, clean):
    by_stage = {int(r['stage']): confusion_metrics(r['confusion'], eligible) for r in run['stages']}
    acquired = []
    for stage in (2, 3, 4):
        codes = [c for c in eligible if c != 4 and int(arrival[c]) == stage]
        if not codes:
            raise ValueError(f'No eligible non-Hulk classes arrive in E{stage}')
        acquired.append(float(np.mean([by_stage[stage]['classes'][c]['f1'] for c in codes])))
    h = float(np.mean([by_stage[s]['hulk_asr'] - clean[s]['hulk_asr'] for s in (3, 4)]))
    return {
        'A': float(np.mean(acquired)), 'A_E2': acquired[0], 'A_E3': acquired[1], 'A_E4': acquired[2],
        'H': h, 'delta_rec': float(by_stage[2]['hulk_recall'] - clean[2]['hulk_recall']),
        'eligible_macro_f1_E4': float(by_stage[4]['macro_f1']),
        'eligible_accuracy_E4': float(by_stage[4]['accuracy']),
        'benign_far_E4': float(by_stage[4]['benign_far']),
        'hulk_recall_E4': float(by_stage[4].get('hulk_recall')),
        'hulk_asr_E4': float(by_stage[4].get('hulk_asr')),
        'elapsed_seconds': float(run['elapsed_seconds']),
    }


def bootstrap(differences, rng, draws=20000):
    x = np.asarray(differences, dtype=np.float64)
    if x.shape != (len(SEEDS),) or not np.isfinite(x).all():
        raise ValueError('Expected 12 finite paired whole-seed differences')
    samples = x[rng.integers(0, len(x), size=(draws, len(x)))].mean(axis=1)
    return float(x.mean()), float(np.median(x)), float(np.quantile(samples, .025)), float(np.quantile(samples, .975))


def main():
    completion = read_json(OUT / 'completion.json')
    study = read_json(OUT / 'identity.json')
    control_identity = read_json(ROOT / 'results/phase3-overnight/identity.json')
    control_completion = read_json(ROOT / 'results/phase3-overnight/completion.json')
    control_hashes = control_completion.get('files', {})
    dev = read_json(ROOT / 'data/processed/phase3-reference74-v1/development/manifest.json')
    if completion.get('status') != 'complete' or completion.get('block') != 'eviction' or completion.get('count') != 48:
        raise RuntimeError('A complete 48-cell eviction block is required')
    if completion.get('final_test_accessed') is not False or study.get('final_test_accessed') is not False:
        raise RuntimeError('Final-test access must remain false')
    for key in ('python', 'torch', 'numpy'):
        if study.get(key) != control_identity.get(key):
            raise RuntimeError(f'Numerical environment differs for {key}')
    for rel, value in study['inputs'].items():
        if rel.endswith('/ownership-source.npz'):
            continue
        if control_identity['inputs'].get(rel) != value:
            raise RuntimeError(f'Frozen input differs from controls: {rel}')

    eligible = sorted(map(int, dev['eligible_codes']))
    arrival = list(map(int, dev['arrival']))
    raw, result_hashes, checkpoint_hashes = {}, {}, {}
    e1_parity = 0
    for policy in POLICIES:
        for seed in SEEDS:
            for dose in DOSES:
                path = result_path(policy, seed, dose)
                if not path.is_file():
                    raise RuntimeError(f'Missing {policy}/{seed}/{dose}: {path}')
                run = read_json(path)
                s = run['settings']
                if (s['block'] != 'eviction' or s['eviction_policy'] != policy or s['admission'] != ADMISSION
                        or s['learner'] != 'DR' or int(s['seed']) != seed or tuple(s['dose']) != dose
                        or int(s['rounds']) != 12 or int(s['epochs']) != 1 or float(s['lambda_z']) != .1
                        or float(s['q']) != .75 or run.get('final_test_accessed') is not False
                        or run.get('study_identity') != study.get('sha256')):
                    raise RuntimeError(f'Unexpected settings or identity in {path}')
                result_hashes[path.relative_to(OUT).as_posix()] = sha256(path)
                ref = read_json(control_path(seed, dose))
                ref_path = control_path(seed, dose)
                ref_rel = ref_path.relative_to(ROOT / 'results/phase3-overnight').as_posix()
                if control_hashes.get(ref_rel) != sha256(ref_path):
                    raise RuntimeError(f'Frozen reservoir control hash mismatch: {ref_rel}')
                if run.get('input_identity') != ref.get('input_identity') or run.get('attack') != ref.get('attack'):
                    raise RuntimeError(f'Input/attack mismatch {policy}/{seed}/{dose}')
                for stage in range(1, 5):
                    current_admission = admission_at(run, stage)['clients']
                    reference_admission = admission_at(ref, stage)['clients']
                    current_ids = [(c['client'], c['raw'], c['admitted'], c['admitted_ids_sha256'])
                                   for c in current_admission]
                    reference_ids = [(c['client'], c['raw'], c['admitted'], c['admitted_ids_sha256'])
                                     for c in reference_admission]
                    if current_ids != reference_ids:
                        raise RuntimeError(f'Admission changed under eviction treatment: {policy}/{seed}/{dose}/E{stage}')
                    if ADMISSION == 'NONE' and any(int(c['raw']) != int(c['admitted']) for c in current_admission):
                        raise RuntimeError(f'Unfiltered admission did not retain every input row: {policy}/{seed}/{dose}/E{stage}')
                if run['stages'][0]['model_sha256'] == ref['stages'][0]['model_sha256']:
                    e1_parity += 1
                for stage in range(1, 5):
                    cp = path.parent / f'E{stage}-weights.npz'
                    checkpoint_hashes[cp.relative_to(OUT).as_posix()] = sha256(cp)
                    with np.load(cp, allow_pickle=False) as arrays:
                        slots = arrays['source_codes'].astype(int).tolist()
                        model_hash = model_identity({'slots': slots, 'weights': {
                            k: array_identity(arrays[k]) for k in arrays.files if k != 'source_codes'}})
                    if model_hash != run['stages'][stage - 1]['model_sha256']:
                        raise RuntimeError(f'Checkpoint/model identity mismatch: {cp}')
                for stage_memory in run['memory']:
                    if int(stage_memory['stage']) < 1 or int(stage_memory['stage']) > 4:
                        raise RuntimeError('Invalid memory stage')
                    for client in stage_memory['clients']:
                        if client is None or client.get('policy') != policy:
                            raise RuntimeError(f'Memory policy telemetry mismatch {policy}/{seed}/{dose}')
                        if int(client['size']) > 500:
                            raise RuntimeError('Replay buffer exceeded the fixed 500-item capacity')
                        if policy != 'reservoir' and int(client.get('insertion_order_bytes', -1)) != 4000:
                            raise RuntimeError('Eviction insertion-order accounting mismatch')
                raw[(policy, seed, dose)] = run
    if len(result_hashes) != 48 or len(checkpoint_hashes) != 192:
        raise RuntimeError('Unexpected result or checkpoint inventory size')

    # Retain whole-file digest inventories alongside the derived tables.
    audit = OUT / 'audit'
    audit.mkdir(parents=True, exist_ok=True)
    integrity = {
        'schema': 'phase3-eviction-independent-audit-v1', 'status': 'integrity_passed',
        'study_identity_sha256': study['sha256'], 'result_files_sha256': result_hashes,
        'checkpoint_files_sha256': checkpoint_hashes, 'result_count': len(result_hashes),
        'checkpoint_count': len(checkpoint_hashes), 'e1_model_parity_cells': e1_parity,
        'e1_model_parity_scope': 'diagnostic only; full-policy eviction is active from E1',
        'final_test_accessed': False,
    }
    (audit / 'integrity.json').write_text(json.dumps(integrity, indent=2) + '\n', encoding='utf-8')

    metrics_rows, exposure_rows = [], []
    clean = {}
    for policy in POLICIES:
        for seed in SEEDS:
            clean[(policy, seed)] = {int(r['stage']): confusion_metrics(r['confusion'], eligible)
                                     for r in raw[(policy, seed, (0, 1))]['stages']}
    for policy in POLICIES:
        for seed in SEEDS:
            for dose in DOSES:
                run = raw[(policy, seed, dose)]
                metrics = endpoints(run, eligible, arrival, clean[(policy, seed)])
                metrics_rows.append({'policy': policy, 'seed': seed, 'dose': dose[0] / dose[1], **metrics})
                for m in run['memory']:
                    for client_id, client in enumerate(m['clients']):
                        exposure_rows.append({
                            'policy': policy, 'seed': seed, 'dose': dose[0] / dose[1], 'stage': int(m['stage']),
                            'client': client_id, 'size': client['size'], 'seen': client['seen'],
                            'poison_ids': client['poison_ids'], 'poison_label_benign': client['poison_label_benign'],
                            'replay_exposures': client['replay_exposures'], 'replayed_ids': client['replayed_ids'],
                            'stored_class_counts': json.dumps(client['stored_class_counts'], sort_keys=True),
                            'insertion_order_bytes': client.get('insertion_order_bytes'),
                        })

    def write_csv(path, rows):
        with path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    write_csv(audit / 'cell-metrics.csv', metrics_rows)
    write_csv(audit / 'replay-exposure-and-occupancy.csv', exposure_rows)

    rng = np.random.default_rng(20261119)
    compare_rows = []
    compared_metrics = ('A', 'H', 'delta_rec', 'eligible_macro_f1_E4', 'eligible_accuracy_E4',
                        'benign_far_E4', 'hulk_recall_E4', 'hulk_asr_E4')
    for dose in DOSES:
        d = dose[0] / dose[1]
        for policy in POLICIES:
            for metric in compared_metrics:
                differences = []
                for seed in SEEDS:
                    left = next(r[metric] for r in metrics_rows
                                if r['policy'] == policy and r['seed'] == seed and r['dose'] == d)
                    right = next(r[metric] for r in metrics_rows
                                 if r['policy'] == 'fifo' and r['seed'] == seed and r['dose'] == d)
                    if policy == 'fifo':
                        continue
                    differences.append(float(left - right))
                if policy == 'fifo':
                    continue
                mean, median, lo, hi = bootstrap(differences, rng)
                compare_rows.append({'dose': d, 'contrast': 'class_balanced-fifo', 'metric': metric,
                    'n_paired_seeds': 12, 'mean_difference': mean, 'median_difference': median,
                    'whole_seed_bootstrap95_low': lo, 'whole_seed_bootstrap95_high': hi,
                    'seed_differences': json.dumps(differences)})
        for policy in POLICIES:
            for metric in compared_metrics:
                differences = []
                for seed in SEEDS:
                    current = next(r[metric] for r in metrics_rows
                                   if r['policy'] == policy and r['seed'] == seed and r['dose'] == d)
                    # The archived reservoir control is recomputed with its own clean twin below.
                    clean_ref = {int(r['stage']): confusion_metrics(r['confusion'], eligible)
                                 for r in raw.get(('reservoir', seed, (0, 1)), {}).get('stages', [])}
                    if not clean_ref:
                        clean_run = read_json(control_path(seed, (0, 1)))
                        clean_ref = {int(r['stage']): confusion_metrics(r['confusion'], eligible)
                                     for r in clean_run['stages']}
                    ref_run = read_json(control_path(seed, dose))
                    ref_metric = endpoints(ref_run, eligible, arrival, clean_ref)[metric]
                    differences.append(float(current - ref_metric))
                mean, median, lo, hi = bootstrap(differences, rng)
                compare_rows.append({'dose': d, 'contrast': f'{policy}-reservoir', 'metric': metric,
                    'n_paired_seeds': 12, 'mean_difference': mean, 'median_difference': median,
                    'whole_seed_bootstrap95_low': lo, 'whole_seed_bootstrap95_high': hi,
                    'seed_differences': json.dumps(differences)})
    write_csv(audit / 'paired-comparisons.csv', compare_rows)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    colors = {'reservoir': '#777777', 'fifo': '#3568A8', 'class_balanced': '#3A8E69'}
    for ax, metric, title in zip(axes.flat, ('A', 'H', 'delta_rec', 'benign_far_E4'),
        ('Acquisition A', 'Persistent error H', 'E2 Hulk recall change', 'E4 benign FAR')):
        for policy in ('reservoir', *POLICIES):
            xs, means, lows, highs = [], [], [], []
            for dose in DOSES:
                vals = []
                for seed in SEEDS:
                    if policy == 'reservoir':
                        run = read_json(control_path(seed, dose))
                        clean_run = read_json(control_path(seed, (0, 1)))
                        clean_metrics = {int(r['stage']): confusion_metrics(r['confusion'], eligible)
                                         for r in clean_run['stages']}
                        vals.append(endpoints(run, eligible, arrival, clean_metrics)[metric])
                    else:
                        vals.append(next(r[metric] for r in metrics_rows if r['policy'] == policy
                                         and r['seed'] == seed and r['dose'] == dose[0] / dose[1]))
                arr = np.asarray(vals, dtype=float); mean = float(arr.mean())
                samples = arr[rng.integers(0, len(arr), size=(10000, len(arr)))].mean(axis=1)
                xs.append(dose[0] / dose[1]); means.append(mean)
                lows.append(mean - float(np.quantile(samples, .025)))
                highs.append(float(np.quantile(samples, .975)) - mean)
            ax.errorbar(xs, means, yerr=np.asarray([lows, highs]), marker='o', capsize=3,
                        color=colors[policy], label=policy)
        if metric in ('H', 'delta_rec'):
            ax.axhline(0, color='black', lw=.7)
        ax.set_title(title); ax.set_xlabel('Poison dose'); ax.grid(alpha=.22)
    axes[0, 0].legend(title='Eviction')
    fig.suptitle('Matched eviction-policy comparison (development outcomes; exploratory)')
    fig.tight_layout()
    fig.savefig(audit / 'eviction-policy-comparison.png', dpi=180, bbox_inches='tight')
    fig.savefig(audit / 'eviction-policy-comparison.pdf', bbox_inches='tight')
    plt.close(fig)

    summary = {
        **integrity, 'status': 'passed', 'schema': 'phase3-eviction-independent-audit-v1',
        'admission': ADMISSION, 'control_policy': 'reservoir', 'policies': list(POLICIES), 'seeds': list(SEEDS),
        'doses': [d[0] / d[1] for d in DOSES], 'paired_comparison_count': len(compare_rows),
        'analysis_scope': 'exploratory development-bank ablation; paired whole-seed bootstrap intervals are descriptive',
        'interpretation_limit': ('All policies use identical unfiltered admission when admission=NONE; E1 may still differ because memory policies are active from the first stage. '
                                 'This estimates the eviction-policy effect under the matched admission setting, not across all admission mechanisms.'),
    }
    (audit / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
