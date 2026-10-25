"""Independently reconstruct development endpoints from integer count artifacts."""
from __future__ import annotations

import argparse
import copy
import math
from fractions import Fraction
from pathlib import Path

from src.phase3.common import ROOT, digest, identity, read_json, write_json
from src.phase3_analysis.statistics import acquisition, benign_far, exact_record, hulk_endpoints
from src.phase3_v3.protocol import code_identity


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix_counts(matrix):
    require(len(matrix) == 16 and all(len(r) == 16 for r in matrix), 'Expected16x16 source-code confusion')
    require(all(type(v) is int and v >= 0 for r in matrix for v in r), 'Confusion counts must be nonnegative integers')
    result = []
    for code, row in enumerate(matrix):
        tp, support = row[code], sum(row)
        fp = sum(r[code] for r in matrix)-tp
        result.append({'code': code, 'tp': tp, 'fp': fp, 'fn': support-tp, 'support': support})
    return result


def same_float(actual, exact):
    require(type(actual) in (int, float) and math.isfinite(actual) and abs(actual-float(exact)) <= 2e-15,
            'Displayed metric disagrees with independently reconstructed counts')


def reconstruct(metric, classes):
    require(metric['schema'] == 'phase3-development-metrics-v3' and metric['status'] == 'valid_development_only'
            and metric['final_test_accessed'] is False, 'Only valid development count artifacts accepted')
    require([s['stage'] for s in metric['stages']] == [1, 2, 3, 4], 'Complete ordered trajectory required')
    cohort_history, groups, hulk, banks, macro = {}, [], [], [], []
    for stage in metric['stages']:
        t = stage['stage']
        slots = [c['source_code'] for c in sorted(classes, key=lambda c: (c['arrival_stage'], c['source_code'])) if c['arrival_stage'] <= t]
        eligible = sorted(c['source_code'] for c in classes if c['arrival_stage'] <= t and c['scoring_eligible'])
        require(stage['source_codes_in_slot_order'] == slots and stage['head_width'] == len(slots), 'Active head/slot order differs')
        require(stage['eligible_codes'] == eligible, 'Frozen eligible source codes differ')
        full, scored = stage['full_seen_confusion_source_code_order'], stage['eligible_confusion_source_code_order']
        full_counts, scored_counts = matrix_counts(full), matrix_counts(scored)
        require(all(full[i][j] == 0 for i in range(16) for j in range(16) if i not in slots or j not in slots), 'Unregistered true/predicted source code')
        require(scored == [r if i in eligible else [0]*16 for i, r in enumerate(full)], 'Eligible bank drops a registered prediction column or includes an ineligible true row')
        require(sum(map(sum, full)) == stage['full_seen_bank_rows'] and sum(map(sum, scored)) == stage['eligible_seen_bank_rows'], 'Confusion bank size mismatch')
        for names, expected_codes, counts in (('full_seen_classes', slots, full_counts), ('eligible_classes', eligible, scored_counts)):
            require([r['code'] for r in stage[names]] == expected_codes, 'Class count order differs')
            for row in stage[names]:
                expected = counts[row['code']]
                require(all(type(row[k]) is int and row[k] == expected[k] for k in ('tp', 'fp', 'fn', 'support')), 'Class counts differ from confusion')
                denominator = 2*row['tp']+row['fp']+row['fn']
                if row['support']:
                    same_float(row['f1'], Fraction(2*row['tp'], denominator))
                    same_float(row['recall'], Fraction(row['tp'], row['support']))
                else:
                    require(row['f1'] is None and row['recall'] is None, 'Unsupported class reported as a computed score')
        require(all(scored_counts[c]['support'] > 0 for c in eligible), 'Fixed eligible class lacks support')
        mean = sum((Fraction(2*scored_counts[c]['tp'], 2*scored_counts[c]['tp']+scored_counts[c]['fp']+scored_counts[c]['fn']) for c in eligible), Fraction())/len(eligible)
        require(stage['eligible_macro_f1_exact'] == [str(mean.numerator), str(mean.denominator)], 'Exact macro-F1 mismatch')
        same_float(stage['eligible_macro_f1'], mean)
        same_float(stage['eligible_pooled_accuracy'], Fraction(sum(scored[i][i] for i in range(16)), sum(map(sum, scored))))
        macro.append(mean)
        expected_binary = {'tn': full[0][0], 'fp': sum(full[0][1:]), 'fn': sum(r[0] for r in full[1:]),
                           'tp': sum(sum(r[1:]) for r in full[1:])}
        binary = stage['binary_full_seen']
        require(all(type(binary[k]) is int and binary[k] == v for k, v in expected_binary.items()), 'Binary/full-seen bank differs')
        far = benign_far(binary['fp'], binary['fp']+binary['tn'])
        same_float(binary['benign_far'], far)
        source = {'support': sum(full[4]), 'predicted_benign': full[4][0], 'predicted_hulk': full[4][4],
                  'predicted_other_attack': sum(full[4][j] for j in range(1, 16) if j != 4)}
        require(stage['hulk_partition'] == source, 'Hulk partition differs from full-head confusion')
        provenance = stage['benign_provenance_descriptive']
        require(sum(r['benign_rows'] for r in provenance) == binary['fp']+binary['tn'] and sum(r['alerts'] for r in provenance) == binary['fp'], 'Benign provenance partition differs')
        cohorts = stage['cohort_counts']
        require([r['cohort'] for r in cohorts] == list(range(1, t+1)), 'Cohort order differs')
        # The cumulative bank includes all fixed benign cohorts from E1, while
        # R[t,j] exists only for j<=t. Unarrived benign cohorts are omitted from
        # early cohort accuracy, not from the full-seen false-alarm bank.
        omitted = stage['eligible_seen_bank_rows']-sum(r['total'] for r in cohorts)
        omitted_correct = sum(scored[i][i] for i in range(16))-sum(r['correct'] for r in cohorts)
        require(0 <= omitted <= binary['fp']+binary['tn'] and 0 <= omitted_correct <= min(omitted, binary['tn'])
                and 0 <= omitted-omitted_correct <= binary['fp'], 'Arrived cohorts omit non-benign records or inconsistent correct counts')
        require(t < 4 or (omitted == 0 and omitted_correct == 0), 'E4 cohorts do not partition the eligible bank')
        for row in cohorts:
            n, correct = row['total'], row['correct']
            require(type(n) is int and type(correct) is int and 0 <= correct <= n and n > 0, 'Invalid cohort integer counts')
            j = row['cohort']
            require(j not in cohort_history or cohort_history[j][0][1] == n, 'Fixed cohort denominator changed across stages')
            cohort_history.setdefault(j, []).append((Fraction(correct, n), n))
        if t > 1:
            group = [r for r in stage['eligible_classes'] if r['code'] not in (0, 4) and next(c['arrival_stage'] for c in classes if c['source_code'] == r['code']) == t]
            groups.append(group)
            a = sum((Fraction(2*r['tp'], 2*r['tp']+r['fp']+r['fn']) for r in group), Fraction())/len(group)
            same_float(stage['untargeted_new_annotated_class_f1'], a)
            hulk.append(source)
        banks.append({'stage': t, 'bank_ids_sha256': stage['bank_ids_sha256'], 'head': slots,
                      'full_support': [r['support'] for r in full_counts], 'eligible_codes': eligible,
                      'benign_support': binary['fp']+binary['tn']})
    acc = sum((cohort_history[j][-1][0] for j in range(1, 5)), Fraction())/4
    bwt = sum((cohort_history[j][-1][0]-cohort_history[j][0][0] for j in range(1, 4)), Fraction())/3
    forgetting = sum((max(v[0] for v in cohort_history[j])-cohort_history[j][-1][0] for j in range(1, 4)), Fraction())/3
    endpoints = {'acquisition_A': acquisition(groups), 'benign_FAR_E4': far, 'equal_stage_ACC4': acc,
                 'BWT4': bwt, 'forgetting4': forgetting, 'mean_four_stage_macro_f1': sum(macro, Fraction())/4}
    for reported, name in (('A', 'acquisition_A'), ('equal_stage_ACC4', 'equal_stage_ACC4'), ('BWT4', 'BWT4'), ('forgetting4', 'forgetting4')):
        same_float(metric[reported], endpoints[name])
    return {'endpoints': endpoints, 'banks': banks, 'hulk': hulk}


def rejection_checks(metric, classes):
    checks = []
    for name, mutate in (
        ('negative_confusion', lambda m: m['stages'][0]['full_seen_confusion_source_code_order'][0].__setitem__(0, -1)),
        ('boolean_confusion', lambda m: m['stages'][0]['full_seen_confusion_source_code_order'][0].__setitem__(0, True)),
        ('dropped_rare_prediction_column', lambda m: m['stages'][1]['eligible_confusion_source_code_order'][0].__setitem__(8, 1)),
        ('binary_bank_mismatch', lambda m: m['stages'][0]['binary_full_seen'].__setitem__('fp', 0 if m['stages'][0]['binary_full_seen']['fp'] else 1)),
        ('wrong_Hulk_partition', lambda m: m['stages'][1]['hulk_partition'].__setitem__('predicted_hulk', -1)),
        ('changed_cohort_denominator', lambda m: m['stages'][3]['cohort_counts'][0].__setitem__('total', 1)),
        ('reordered_registered_slots', lambda m: m['stages'][1]['source_codes_in_slot_order'].reverse()),
        ('incorrect_acquisition_endpoint', lambda m: m.__setitem__('A', -1)),
    ):
        changed = copy.deepcopy(metric)
        mutate(changed)
        try:
            reconstruct(changed, classes)
        except ValueError:
            checks.append({'check': name, 'rejected': True})
        else:
            raise AssertionError('Invalid count artifact accepted: '+name)
    return checks


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--development', type=Path, default=ROOT/'results/phase3-cpu-v3/development')
    p.add_argument('--output', type=Path, default=ROOT/'results/phase3-endpoint-audit-v1/audit.json')
    p.add_argument('--receipt-preflight', action='store_true')
    args = p.parse_args()
    require(not args.output.exists(), 'Preserve existing count audit; use a fresh output')
    classes = read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes']
    if args.receipt_preflight:
        rows = [read_json(f)['row'] for f in sorted((args.development/'receipts').glob('*.json'))]
    else:
        rows = read_json(args.development/'completion.json')['rows']
    valid = [r for r in rows if r['status'] == 'valid']
    require(bool(valid), 'No valid committed row available')
    records, reference, checks = {}, None, []
    for row in valid:
        metric_path, run_path = Path(row['metrics']), Path(row['run'])/'run.json'
        metric, run = read_json(metric_path), read_json(run_path)
        require(run['execution']['code_identity'] == code_identity() and metric['run_manifest_sha256'] == digest(run_path), 'Metric/run source identity differs')
        require(metric['settings'] == run['settings'] == row['settings'], 'Consumed settings differ')
        result = reconstruct(metric, classes)
        if reference is None:
            reference = result['banks']
            checks = rejection_checks(metric, classes)
        require(result['banks'] == reference, 'Fixed banks/supports differ across conditions')
        records[row['row_id']] = {'metric_sha256': digest(metric_path), 'endpoints': {k: exact_record(v) for k, v in result['endpoints'].items()},
                                  'Hulk_partitions_E2_E3_E4': result['hulk'], 'alias_of': row['alias_of']}
    control_records = {}
    control_root = ROOT/'results/phase3-cpu-v3/controls'
    if not args.receipt_preflight and (control_root/'acceptance.json').exists():
        for arm in ('DM', 'DC', 'DQ'):
            path = control_root/f'{arm}-evaluation/metrics.json'
            metric, run_path = read_json(path), control_root/arm/'run.json'
            require(metric['run_manifest_sha256'] == digest(run_path) and read_json(run_path)['execution']['code_identity'] == code_identity(), 'Control count lineage differs')
            result = reconstruct(metric, classes)
            require(result['banks'] == reference, 'Control fixed banks differ')
            control_records[arm] = {'metric_sha256': digest(path), 'seed': 101,
                                   'endpoints': {k: exact_record(v) for k, v in result['endpoints'].items()},
                                   'scope': 'One paired engineering seed; no extra independent replicate'}
    paired = []
    diagnostic_index = ROOT/'results/phase3-cpu-v3/matched-diagnostic/index.json'
    if not args.receipt_preflight and diagnostic_index.exists():
        index = read_json(diagnostic_index)
        selection = read_json(ROOT/'results/phase3-cpu-v3/cost-correction/selection.json')
        selected = selection['learners']['FT']['selected']
        for row in index['rows']:
            if row.get('status', 'valid') != 'valid':
                continue
            seed = row['settings']['seed']
            cleanrow = next(r for r in valid if r['row_id'] in selected['rows'] and r['settings']['seed'] == seed)
            clean = reconstruct(read_json(Path(cleanrow['metrics'])), classes)
            metric_path, run_path = Path(row['metrics']), Path(row['run'])/'run.json'
            poison_metric = read_json(metric_path)
            require(poison_metric['run_manifest_sha256'] == digest(run_path) and read_json(run_path)['execution']['code_identity'] == code_identity(), 'Diagnostic count lineage differs')
            poison = reconstruct(poison_metric, classes)
            require(clean['banks'] == poison['banks'], 'Paired diagnostic banks differ')
            endpoints = hulk_endpoints(clean['hulk'], poison['hulk'])
            paired.append({'seed': seed, 'clean_row_id': cleanrow['row_id'], 'poison_row_id': row['row_id'],
                           'poison_metric_sha256': digest(metric_path), 'clean_metric_sha256': digest(Path(cleanrow['metrics'])),
                           'H': exact_record(endpoints['H']), 'source_recall_change_E2': exact_record(endpoints['source_recall_change_E2']),
                           'scope': 'Descriptive development point, not final-seed inference'})
    write_json(args.output, {'schema': 'phase3-independent-development-count-audit-v1', 'status': 'passed',
               'code_identity': code_identity(), 'auditor_sha256': digest(Path(__file__)),
               'analysis_source_sha256': digest(ROOT/'src/phase3_analysis/statistics.py'),
               'taxonomy_sha256': digest(ROOT/'configs/phase3/taxonomy-v1.json'), 'fixed_banks': reference,
               'valid_logical_rows_audited': len(valid), 'physical_conditions': len({r['logical_identity'] for r in valid}),
               'counts_and_endpoints': records, 'engineering_controls': control_records,
               'rejection_checks': checks, 'paired_FT_diagnostics': paired,
               'snapshot_identity': identity({r['row_id']: records[r['row_id']]['metric_sha256'] for r in valid}),
               'scope': 'Committed receipt snapshot during grid; no selection/inference' if args.receipt_preflight else 'Full declared development count artifacts; no confirmatory statistics',
               'limitations': 'Reconstructs count arithmetic and fixed-bank identities; does not independently recompute predictions from features/models',
               'final_test_accessed': False, 'gpu_dispatchable': False})
    print({'status': 'passed', 'valid_rows': len(valid), 'rejection_checks': len(checks), 'paired_diagnostics': len(paired)})


if __name__ == '__main__':
    main()
