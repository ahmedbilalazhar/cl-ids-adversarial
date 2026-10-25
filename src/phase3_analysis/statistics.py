"""Count-derived endpoints and the unchanged fixed 29-contrast paired analysis."""
from __future__ import annotations

import itertools
import math
from fractions import Fraction

import numpy as np

from src.phase3.common import ROOT, array_identity, digest, encode_rng, identity, read_json, rng

CONFIG = ROOT/'configs/phase3/analysis-cpu-v1.json'
SPEC = ROOT/'docs/phase3-plan/analysis-contrasts.json'
DECISIONS = ROOT/'docs/phase3-analysis-v1/decisions-2026-10-24.md'


def analysis_identity():
    files = list((ROOT/'src/phase3_analysis').glob('*.py')) + [CONFIG, SPEC, DECISIONS, ROOT/'src/phase3/common.py', ROOT/'tests/test_phase3_analysis.py']
    return identity({p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(files)})


def specification():
    config, spec = read_json(CONFIG), read_json(SPEC)
    if digest(SPEC) != config['contrast_spec_sha256'] or spec['seeds'] != config['final_seeds'] or len(spec['contrasts']) != 29 or len({c['id'] for c in spec['contrasts']}) != 29:
        raise ValueError('Frozen contrast family or seed list differs')
    return config, spec


def rational(value):
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    raise ValueError('Use exact integer or Fraction values; floating inference inputs are ambiguous')


def exact_record(value):
    value = rational(value)
    return {'exact': [str(value.numerator), str(value.denominator)], 'value': float(value)}


def nonnegative_integer(value):
    if type(value) is not int or value < 0:
        raise ValueError('Expected a nonnegative integer count')
    return value


def hulk_endpoints(clean, poisoned):
    """Three E2/E3/E4 Hulk partitions; caller supplies already validated banks."""
    if len(clean) != 3 or len(poisoned) != 3:
        raise ValueError('Three complete Hulk stage partitions required')
    for row in clean+poisoned:
        if set(row) != {'support', 'predicted_benign', 'predicted_hulk', 'predicted_other_attack'}:
            raise ValueError('Invalid Hulk count schema')
        if not row['support'] or sum(nonnegative_integer(row[k]) for k in ('predicted_benign', 'predicted_hulk', 'predicted_other_attack')) != nonnegative_integer(row['support']):
            raise ValueError('Hulk count partition is incomplete')
    n = clean[0]['support']
    if any(r['support'] != n for r in clean+poisoned):
        raise ValueError('The same positive Hulk denominator is required')
    persistent = Fraction(sum(poisoned[i]['predicted_benign']-clean[i]['predicted_benign'] for i in (1, 2)), 2*n)
    immediate = Fraction(poisoned[0]['predicted_hulk']-clean[0]['predicted_hulk'], n)
    return {'H': persistent, 'source_recall_change_E2': immediate,
            'clean_ASR_E2_E3_E4': [Fraction(r['predicted_benign'], n) for r in clean],
            'poisoned_ASR_E2_E3_E4': [Fraction(r['predicted_benign'], n) for r in poisoned]}


def acquisition(groups):
    """U2/U3/U4 count lists already fixed by eligibility, excluding Hulk."""
    if len(groups) != 3 or any(not group for group in groups):
        raise ValueError('All three fixed untargeted acquisition groups required')
    means = []
    for group in groups:
        values = []
        for row in group:
            tp, fp, fn = [nonnegative_integer(row[k]) for k in ('tp', 'fp', 'fn')]
            if tp+fn == 0:
                raise ValueError('An eligible new family must have fixed positive support')
            values.append(Fraction(2*tp, 2*tp+fp+fn))
        means.append(sum(values, Fraction())/len(values))
    return sum(means, Fraction())/3


def benign_far(alerts, benign_support):
    alerts, benign_support = nonnegative_integer(alerts), nonnegative_integer(benign_support)
    if benign_support == 0 or alerts > benign_support:
        raise ValueError('A positive fixed benign denominator containing all alerts is required')
    return Fraction(alerts, benign_support)


def exact_signed_rank(differences):
    values = [rational(v) for v in differences]
    if len(values) > 12:
        raise ValueError('This exact enumerator is bounded to the twelve-seed protocol')
    active = [(i, v) for i, v in enumerate(values) if v]
    ordered = sorted(active, key=lambda item: (abs(item[1]), item[0]))
    ranks, ties, start = {}, [], 0
    while start < len(ordered):
        end = start+1
        while end < len(ordered) and abs(ordered[end][1]) == abs(ordered[start][1]):
            end += 1
        # Mean one-based ranks start+1..end, stored doubled as an integer.
        rank_twice = start+1+end
        for index, _ in ordered[start:end]:
            ranks[index] = rank_twice
        if end-start > 1:
            ties.append({'absolute_difference': exact_record(abs(ordered[start][1])), 'count': end-start, 'rank_twice': rank_twice})
        start = end
    signed = sum(ranks[i] if v > 0 else -ranks[i] for i, v in active)
    rank_values = [ranks[i] for i, _ in active]
    extreme = sum(abs(sum(sign*rank for sign, rank in zip(signs, rank_values))) >= abs(signed)
                  for signs in itertools.product((-1, 1), repeat=len(active)))
    p = Fraction(extreme, 2**len(active))
    total = sum(rank_values)
    return {'p': p, 'nonzero_pairs': len(active), 'zero_pairs': len(values)-len(active), 'ties': ties,
            'rank_twice_by_nonzero_input_order': rank_values, 'nonzero_input_indexes': [i for i, _ in active],
            'signed_rank_sum_twice': signed, 'rank_biserial': Fraction(signed, total) if total else Fraction(),
            'sign_assignments': 2**len(active), 'extreme_sign_assignments': extreme}


def exact_sign_test(differences):
    values = [rational(v) for v in differences if rational(v)]
    m = len(values)
    positive = sum(v > 0 for v in values)
    observed = abs(2*positive-m)
    count = sum(math.comb(m, k) for k in range(m+1) if abs(2*k-m) >= observed)
    return Fraction(count, 2**m)


def holm(p_values):
    values = [rational(p) for p in p_values]
    if any(p < 0 or p > 1 for p in values):
        raise ValueError('Invalid probability')
    result, maximum = [Fraction()]*len(values), Fraction()
    for order, index in enumerate(sorted(range(len(values)), key=lambda i: (values[i], i))):
        maximum = max(maximum, min(Fraction(1), values[index]*(len(values)-order)))
        result[index] = maximum
    return result


def bootstrap_mean(differences, contrast_index):
    config, _ = specification()
    options = config['bootstrap']
    if np.__version__ != options['numpy'] or type(contrast_index) is not int or contrast_index not in range(29):
        raise ValueError('Pinned NumPy and frozen contrast index required')
    if len(differences) != 12:
        raise ValueError('Bootstrap requires all twelve paired seeds')
    values = np.asarray([float(rational(v)) for v in differences], dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite bootstrap inputs')
    generator = rng(options['rng_namespace'], options['seed'], contrast_index)
    initial = encode_rng(generator)
    indexes = generator.integers(0, 12, size=(options['resamples'], 12), dtype=np.int64)
    means = values[indexes].mean(axis=1, dtype=np.float64)
    interval = np.quantile(means, options['probabilities'], method=options['quantile_method']).tolist()
    return {'lower': interval[0], 'upper': interval[1], 'resamples': len(indexes), 'sample_size': 12,
            'quantile_method': options['quantile_method'], 'draws_sha256': array_identity(indexes),
            'initial_rng': initial, 'final_rng': encode_rng(generator), 'simultaneous': False,
            'target': 'descriptive mean paired difference; not a signed-rank inversion'}


def analyze_family(differences):
    config, spec = specification()
    ids = [c['id'] for c in spec['contrasts']]
    if set(differences) != set(ids):
        raise ValueError('Exactly the frozen29 planned contrast IDs are required')
    rows, bookkeeping = [], []
    for index, contrast in enumerate(spec['contrasts']):
        values = differences[contrast['id']]
        if len(values) != 12:
            raise ValueError('Use the twelve fixed seed positions, retaining unavailable values as None')
        missing = [seed for seed, value in zip(spec['seeds'], values) if value is None]
        row = {**contrast, 'seed_order': spec['seeds'], 'paired_differences': [None if v is None else exact_record(v) for v in values],
               'missing_seeds': missing, 'raw_p': None, 'holm_adjusted_p': None, 'reject': None,
               'mean_difference': None, 'median_difference': None, 'rank_biserial': None, 'bootstrap': None,
               'sign_test_sensitivity_p': None, 'available_pairs': 12-len(missing)}
        if missing:
            row['status'] = 'unavailable_with_protocol_deviation'
            row['holm_bookkeeping_p'] = exact_record(1)
            bookkeeping.append(Fraction(1))
        else:
            exact = [rational(v) for v in values]
            ranks = exact_signed_rank(exact)
            ordered = sorted(exact)
            row.update({'status': 'computed_complete_paired_seeds', 'raw_p': exact_record(ranks['p']),
                        'holm_bookkeeping_p': exact_record(ranks['p']), 'mean_difference': exact_record(sum(exact, Fraction())/12),
                        'median_difference': exact_record((ordered[5]+ordered[6])/2), 'rank_biserial': exact_record(ranks['rank_biserial']),
                        'signed_rank_details': {k: v for k, v in ranks.items() if k not in ('p', 'rank_biserial')},
                        'bootstrap': bootstrap_mean(exact, index), 'sign_test_sensitivity_p': exact_record(exact_sign_test(exact))})
            bookkeeping.append(ranks['p'])
        rows.append(row)
    alpha = Fraction(*config['alpha'])
    for row, adjusted in zip(rows, holm(bookkeeping)):
        row['holm_bookkeeping_adjusted_p'] = exact_record(adjusted)
        if row['status'] == 'computed_complete_paired_seeds':
            row['holm_adjusted_p'] = exact_record(adjusted)
            row['reject'] = adjusted <= alpha
    return {'schema': 'phase3-paired-analysis-v1', 'analysis_identity': analysis_identity(), 'family_size': 29,
            'seed_order': spec['seeds'], 'alpha': exact_record(alpha), 'rows': rows,
            'assumptions': ['Independent seed-level differences and sign symmetry for signed rank; enumeration does not remove that assumption.',
                            'Descriptive bootstrap intervals are not simultaneous; small-sample coverage may be unstable.',
                            'Fixed capture/split variability; no deployment generalization or equivalence follows from non-rejection.'],
            'final_release_enabled': False}


def contrast_differences(endpoints):
    """Map (arm,exact dose,seed)->already-derived endpoints to fixed contrasts.

    H/recall change are already clean-subtracted by hulk_endpoints; this layer
    performs only the specified left-minus-right contrast. A/FAR remain raw.
    """
    _, spec = specification()
    result = {}
    for contrast in spec['contrasts']:
        dose = Fraction(str(contrast['dose']))
        rows = []
        for seed in spec['seeds']:
            left = endpoints.get((contrast['left_arm'], dose, seed), {}).get(contrast['metric'])
            right = endpoints.get((contrast['right_arm'], dose, seed), {}).get(contrast['metric'])
            rows.append(None if left is None or right is None else rational(left)-rational(right))
        result[contrast['id']] = rows
    return result
