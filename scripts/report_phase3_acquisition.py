"""Derive an acquisition report and proposed amendment from locked E1 evidence."""
from __future__ import annotations

import argparse
import shutil
import statistics
from pathlib import Path

from src.phase3.common import ROOT, digest, read_json, write_json


def mean_recall(rows, code):
    return statistics.mean(next(c['recall'] for c in row['classes'] if c['source_code'] == code) for row in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=ROOT/'results/phase3-acquisition-diagnostic-v1')
    parser.add_argument('--docs', type=Path, default=ROOT/'docs/phase3-acquisition-diagnostic-v1')
    args = parser.parse_args()
    base, docs = args.results, args.docs
    summary = read_json(base/'summary.json')
    acceptance = read_json(base/'acceptance.json')
    inputs = read_json(base/'inputs.json')
    index = read_json(base/'artifact-index.json')
    if summary['status'] != 'completed_exploratory_E1_diagnostic' or acceptance['status'] != 'passed':
        raise ValueError('Completed, accepted diagnostic evidence required')
    if len(summary['baseline_exact_checks']) != 9 or not all(c['state_dropout_counters_exact'] for c in summary['baseline_exact_checks']):
        raise ValueError('Exact parent equivalence is required')
    if any(digest(base/name) != sha for name, sha in index['files'].items()):
        raise ValueError('A diagnostic input artifact changed')
    parent = ROOT/'docs/phase3-cpu-v2/evidence'
    parent_index = read_json(parent/'artifact-index.json')
    parent_preserved = all(digest(parent/name) == sha for name, sha in parent_index['files'].items())
    source = read_json(parent/'source-code-manifest.json')
    files = {**source['files'], **source['delivery_scripts']}
    source_preserved = all(digest(ROOT/name) == sha for name, sha in files.items())
    if not parent_preserved or not source_preserved:
        raise ValueError('Parent scientific source/delivery evidence changed')
    trajectories = [read_json(p) for p in sorted(base.glob('*-s*/trajectory.json'))]
    if len(trajectories) != 6:
        raise ValueError('Six complete E1 trajectories required')
    cell_rows, local_rows = [], []
    for cell in summary['cells']:
        if sorted(r['seed'] for r in cell['per_seed']) != [101, 102, 103]:
            raise ValueError('Incomplete or duplicated seed cell')
        dev = [r['development'] for r in cell['per_seed']]
        cell_rows.append({'objective': cell['objective'], 'rounds': cell['rounds'],
                          'mean_dev_FTP_recall': mean_recall(dev, 7), 'mean_dev_SSH_recall': mean_recall(dev, 12),
                          'mean_dev_macro_f1': statistics.mean(r['macro_f1'] for r in dev),
                          'mean_dev_benign_far': statistics.mean(r['benign_far'] for r in dev),
                          'E1_context_passed': cell['E1_development_anchor_context_passed']})
    for trajectory in trajectories:
        for round_id in (3, 12):
            curve = trajectory['curves'][round_id]
            for code in (7, 12):
                global_cell = next(c for c in curve['development']['classes'] if c['source_code'] == code)
                local_cells = [{'client': r['client'], 'development_recall': next(c['recall'] for c in r['development']['classes'] if c['source_code'] == code),
                                'own_train_recall': next(c['recall'] for c in r['own_train']['classes'] if c['source_code'] == code),
                                'own_train_support': next(c['support'] for c in r['own_train']['classes'] if c['source_code'] == code)}
                               for r in curve['locals_before_aggregation']]
                local_rows.append({'objective': trajectory['objective'], 'seed': trajectory['seed'], 'round': round_id, 'source_code': code,
                                   'aggregate_development_recall': global_cell['recall'], 'local_endpoints': local_cells,
                                   'local_pass_aggregate_fail': global_cell['recall'] < .5 and any(c['development_recall'] >= .5 for c in local_cells)})
    natural12 = next(c for c in cell_rows if c['objective'] == 'natural' and c['rounds'] == 12)
    if natural12['E1_context_passed']:
        recommendation = 'Prospective v3 synchronization pilots with twelve local passes and unchanged objectives'
    else:
        weighted12 = next(c for c in cell_rows if c['objective'] == 'equal_class' and c['rounds'] == 12)
        recommendation = ('Prospective supplied-label objective amendment, with common current-loss semantics specified before full-grid runs'
                          if weighted12['E1_context_passed'] else 'Separate representation/optimizer diagnostic; neither intervention restored the E1 context gates')
    interpretation = {'schema': 'phase3-acquisition-interpretation-v1', 'diagnostic_identity': summary['diagnostic_identity'],
                      'summary_sha256': digest(base/'summary.json'), 'report_script_sha256': digest(Path(__file__)),
                      'parent_source_and_delivery_preserved': source_preserved, 'parent_indexed_evidence_preserved': parent_preserved,
                      'feature_audit': inputs['features'],
                      'cells': cell_rows, 'local_aggregation_comparisons': local_rows, 'recommendation': recommendation,
                      'status': 'exploratory_diagnosis_complete_amendment_proposed_not_adopted',
                      'full_clean_feasibility': 'unestablished; E2 Hulk and EI/DR not exercised',
                      'extra_complete_study_candidates': 0, 'final_test_accessed': False, 'gpu_dispatchable': False,
                      'failures': ['Initial bank preflight used arrival==1, corrected to the frozen arrival<=1 before training; attempt1 preserved'],
                      'missing': ['EI/DR E1 under longer budget', 'All E2-E4 behavior under the longer budget',
                                  'Poison diagnostics and filtered controls under a revised schedule', 'GPU/runtime/cost/final analysis release gates']}
    docs.mkdir(parents=True, exist_ok=True)
    source_docs = ROOT/'docs/phase3-acquisition-diagnostic-v1'
    for name in ('plan-2026-10-24.md', 'proposed-amendment.md', 'log.md', 'README.md'):
        source_path, target_path = source_docs/name, docs/name
        if source_path.resolve() != target_path.resolve():
            if target_path.exists():
                raise FileExistsError('Refusing to replace reproduction documentation: '+str(target_path))
            shutil.copyfile(source_path, target_path)
    review = docs/'evidence'
    review.mkdir(exist_ok=False)
    write_json(review/'interpretation.json', interpretation)
    for name in ('summary.json', 'acceptance.json', 'execution.json', 'inputs.json', 'artifact-index.json'):
        shutil.copyfile(base/name, review/('diagnostic-artifact-index.json' if name == 'artifact-index.json' else name))
    for path in sorted(base.glob('*-s*/trajectory.json')):
        shutil.copyfile(path, review/(path.parent.name+'-trajectory.json'))
    write_json(review/'review-index.json', {'files': {p.name: digest(p) for p in sorted(review.glob('*.json'))}})
    lines = ['# E1 acquisition diagnosis — 24 October 2026', '',
             ('Extending the original-loss FT schedule from three to twelve rounds restored the existing mean E1 acquisition thresholds in this fixed diagnostic. '
             'The same three development seeds were used. This supports testing a longer common training budget before changing the loss. '
             'It does not qualify any four-stage learner or unlock final evaluation.'), '',
             (f"All {acceptance['tests_run']} independent arithmetic/scope fixtures passed. The probe reproduced all nine frozen FT round states, "
             'all client dropout states and update/exposure counters exactly. Parent source, delivery scripts and indexed evidence remain unchanged.'), '',
             '## Fixed paired comparison', '',
             '| Current CE objective | Rounds x epochs | Mean dev FTP recall | Mean dev SSH recall | Mean E1 macro-F1 | Mean benign FAR | E1 mean thresholds |',
             '|---|---|---:|---:|---:|---:|---|']
    for row in cell_rows:
        lines.append(f"| {row['objective']} | {row['rounds']} x 1 | {row['mean_dev_FTP_recall']:.4f} | {row['mean_dev_SSH_recall']:.4f} | "
                     f"{row['mean_dev_macro_f1']:.4f} | {100*row['mean_dev_benign_far']:.2f}% | {'Pass (E1 only)' if row['E1_context_passed'] else 'Fail'} |")
    lines.extend(['', 'The natural twelve-round FTP recalls are 1.0, 1.0 and 0.0 for seeds101–103. Its SSH recalls are '+
                  ', '.join(f"{r['development']['classes'][2]['recall']:.4f}" for r in next(c for c in summary['cells'] if c['objective'] == 'natural' and c['rounds'] == 12)['per_seed'])+'. '
                  'Seed103 remains unable to acquire FTP. A mean gate pass must not conceal that failure.', '',
                  ('Equal-class weighting at three rounds did not meet either mean anchor threshold and had lower mean macro-F1 than the natural objective. '
                  'At twelve rounds it slightly raised SSH recall but still left seed103 FTP recall at zero, with lower mean macro-F1 and higher benign FAR than natural. '
                  'These cells do not support promoting weighting as the next revision.'), '',
                  ('The longer schedule jointly changes current-record exposure, synchronization count and Adam reset count. '
                  'The paired intervention establishes sensitivity to that bundle; it does not identify which part causes the change.'), '',
                  '## Location of the failure', '',
                  ('The E1 inventory contains 3,500 benign, 2,382 FTP and 1,776 SSH records. This does not show extreme global label imbalance. '
                  'Seeds101 and102 each have three clients without benign E1 rows; seed103 has two. Class ownership and per-client update counts are uneven. '
                  'There are 7,658 distinct FP32 E1 feature vectors and zero cross-label exact feature collisions. '
                  'This rules out an exact-feature collision bound as the explanation for these particular training errors; it does not prove separability or rule out source-label problems.'), '',
                  '| Natural objective, round3 | FTP aggregate recall | Local models with FTP recall >=0.5 | SSH aggregate recall | Local models with SSH recall >=0.5 |',
                  '|---|---:|---:|---:|---:|'])
    for seed in (101, 102, 103):
        a, b = [next(r for r in local_rows if r['objective'] == 'natural' and r['round'] == 3 and r['seed'] == seed and r['source_code'] == code) for code in (7, 12)]
        lines.append(f"| Seed {seed} | {a['aggregate_development_recall']:.4f} | {sum(c['development_recall'] >= .5 for c in a['local_endpoints'])}/5 | "
                     f"{b['aggregate_development_recall']:.4f} | {sum(c['development_recall'] >= .5 for c in b['local_endpoints'])}/5 |")
    suppressed = [r for r in local_rows if r['objective'] == 'natural' and r['round'] == 3 and r['local_pass_aggregate_fail']]
    lines.extend(['', (f"At {len(suppressed)} natural round3 seed/family comparisons, at least one local endpoint attained recall >=0.50 on the common development bank while the averaged model did not. "
                  'The shared bank makes these directly comparable outputs. They show loss of that local decision behavior during weight averaging at those transitions, '
                  'but do not show that aggregation is the sole cause. Local models may have poor precision, benign behavior or other-class recall; full local confusion tables are retained.'), '',
                  '## Compute and evidence', '',
                  (f"Six new physical E1 trajectories produced twelve logical objective/budget cells across three paired development seeds. "
                  f"They used {summary['E1_total_optimizer_updates']:,} local optimizer updates and {summary['E1_total_current_exposures']:,} current-record exposures, "
                  f"taking {summary['elapsed_seconds_including_readouts']:.2f} measured CPU seconds including readouts. "
                  'This is additional diagnostic work, separate from the original 69 complete physical clean executions. Prefix replay is verification work and adds no independent replicate.'), '',
                  ('Per-round training/development CE, probability, logit margins, recalls and confusion matrices; local endpoints; source identities and model hashes are in '
                  '[the indexed evidence](evidence/review-index.json). The original result folder retains the E1 model arrays. '
                  'No final-test row was loaded. A preflight bank-slicing defect and its preserved failed attempt are documented in [the log](log.md).'), '',
                  '## Next gated experiment', '',
                  ('Prepare a distinct v3 development revision with synchronization candidates (3 rounds,4 epochs) and (12 rounds,1 epoch), '
                  'both twelve local passes. This compares the present three-broadcast schedule with a more frequent-broadcast schedule at equal nominal exposure. '
                  'Preserve the natural objectives first, repeat method/recovery acceptance for the added budget, then rerun all 18 pilots and the selected-budget 60-row grid. '
                  'No E1-only result substitutes for EI/DR, E2 Hulk or later acquisition/retention.'), '',
                  ('The [proposed amendment](proposed-amendment.md) records exact changes, visible evidence, reruns and release gates. '
                  'It is a proposal for the next implementation milestone. V2 remains the valid record of its failed clean procedure.')])
    (docs/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print({'status': interpretation['status'], 'recommendation': recommendation, 'local_round3_suppression_cells': len(suppressed)})


if __name__ == '__main__':
    main()
