"""Descriptive summaries alongside the unchanged single all_29 Holm family."""
import math
from fractions import Fraction
from src.phase3_analysis.statistics import exact_record, rational, specification


def seed_summary(values):
    """Require explicit fixed seed positions; never silently drop missing pairs."""
    _, spec = specification()
    if set(values) != set(spec['seeds']) or any(type(k) is not int for k in values):
        raise ValueError('Exactly the twelve prescribed seed positions are required')
    missing = [seed for seed in spec['seeds'] if values[seed] is None]
    result = {'seed_order': spec['seeds'], 'missing_seeds': missing,
              'mean': None, 'sample_standard_deviation': None, 'n': 12-len(missing)}
    if missing:
        return result
    ordered = [rational(values[seed]) for seed in spec['seeds']]
    mean = sum(ordered, Fraction())/12
    variance = sum(((x-mean)**2 for x in ordered), Fraction())/11
    return {**result, 'mean': exact_record(mean), 'sample_standard_deviation': math.sqrt(float(variance))}
