"""Independent count-to-report checks beyond the historical endpoint audit."""
import math
from fractions import Fraction

from scripts.audit_phase3_endpoints import require


def integer(value, name):
    require(type(value) is int and value >= 0, 'Expected nonnegative integer '+name)
    return value


def rate(actual, numerator, denominator, name):
    if denominator == 0:
        require(actual is None, 'Undefined '+name+' must remain unavailable')
    else:
        exact = Fraction(numerator, denominator)
        require(type(actual) in (int, float) and math.isfinite(actual) and
                abs(actual-float(exact)) <= 2e-15, 'Reported '+name+' disagrees with integer counts')


def validate_reported_metrics(metric, classes):
    labels = {c['source_code']: c['label'] for c in classes}
    require(type(metric['stages']) is list and len(metric['stages']) == 4, 'Four complete metric stages required')
    for stage in metric['stages']:
        for key in ('stage', 'head_width', 'full_seen_bank_rows', 'eligible_seen_bank_rows'):
            integer(stage[key], key)
        for key in ('source_codes_in_slot_order', 'eligible_codes'):
            require(type(stage[key]) is list, 'Source-code sequence must be a list')
            for code in stage[key]:
                integer(code, key)
                require(code in labels, 'Unknown source code')
        for key in ('full_seen_classes', 'eligible_classes'):
            for row in stage[key]:
                for count in ('code', 'tp', 'fp', 'fn', 'support'):
                    integer(row[count], count)
                require(row['code'] in labels and row['family'] == labels[row['code']], 'Reported class label differs from taxonomy')
                expected_status = 'supported' if row['support'] else 'no_positive_development_records'
                require(row['status'] == expected_status, 'Reported class support status differs')
                rate(row['precision'], row['tp'], row['tp']+row['fp'], 'class precision')
                rate(row['recall'], row['tp'], row['support'], 'class recall')
                rate(row['f1'], 2*row['tp'], 2*row['tp']+row['fp']+row['fn'] if row['support'] else 0, 'class F1')
        for key, value in stage['hulk_partition'].items():
            integer(value, 'Hulk '+key)
        for row in stage['cohort_counts']:
            for key in ('cohort', 'correct', 'total'):
                integer(row[key], 'cohort '+key)
        binary = stage['binary_full_seen']
        tp, fp, fn, tn = [integer(binary[k], k) for k in ('tp', 'fp', 'fn', 'tn')]
        for key, numerator, denominator in (
                ('attack_precision', tp, tp+fp), ('attack_recall', tp, tp+fn),
                ('f1', 2*tp, 2*tp+fp+fn), ('benign_far', fp, fp+tn), ('attack_miss_rate', fn, tp+fn)):
            rate(binary[key], numerator, denominator, key)
        provenance = stage['benign_provenance_descriptive']
        require([r['group'] for r in provenance] == ['original_background', 'remapped_attempted'],
                'Benign provenance groups must be distinct, fixed and ordered')
        for row in provenance:
            n, alerts = integer(row['benign_rows'], 'benign_rows'), integer(row['alerts'], 'alerts')
            require(alerts <= n, 'Benign subgroup alerts exceed its support')
            rate(row['error_rate'], alerts, n, 'benign subgroup error rate')
