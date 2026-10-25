"""Independent transparent arithmetic for the frozen statistical contract."""
from __future__ import annotations

import unittest
from fractions import Fraction

from src.phase3_analysis.statistics import (
    acquisition,
    analyze_family,
    benign_far,
    bootstrap_mean,
    contrast_differences,
    exact_sign_test,
    exact_signed_rank,
    holm,
    hulk_endpoints,
    specification,
)


def partition(benign, hulk, other):
    return {'support': benign+hulk+other, 'predicted_benign': benign, 'predicted_hulk': hulk, 'predicted_other_attack': other}


class Phase3Analysis(unittest.TestCase):
    def test_hulk_integer_endpoints_signs_and_denominator_rejection(self):
        clean = [partition(10, 60, 30), partition(20, 50, 30), partition(30, 40, 30)]
        poison = [partition(30, 40, 30), partition(45, 30, 25), partition(50, 20, 30)]
        values = hulk_endpoints(clean, poison)
        self.assertEqual(values['H'], Fraction(9, 40))
        self.assertEqual(values['source_recall_change_E2'], Fraction(-1, 5))
        reverse = hulk_endpoints(poison, clean)
        self.assertEqual(reverse['H'], -values['H'])
        with self.assertRaises(ValueError):
            hulk_endpoints(clean, poison[:2]+[partition(50, 20, 31)])
        with self.assertRaises(ValueError):
            hulk_endpoints([partition(0, 0, 0)]*3, [partition(0, 0, 0)]*3)
        broken = [*poison[:2], {**poison[-1], 'predicted_hulk': -1}]
        with self.assertRaises(ValueError):
            hulk_endpoints(clean, broken)

    def test_acquisition_equal_family_then_equal_stage_not_pooled(self):
        groups = [[{'tp': 1, 'fp': 0, 'fn': 1}],
                  [{'tp': 0, 'fp': 0, 'fn': 100}, {'tp': 1, 'fp': 0, 'fn': 0}],
                  [{'tp': 1, 'fp': 1, 'fn': 0}]]
        self.assertEqual(acquisition(groups), Fraction(11, 18))
        with self.assertRaises(ValueError):
            acquisition([[], *groups[1:]])
        with self.assertRaises(ValueError):
            acquisition([[{'tp': 0, 'fp': 0, 'fn': 0}], *groups[1:]])

    def test_exact_signed_rank_independent_small_sign_counts(self):
        result = exact_signed_rank([1, 2, 3])
        self.assertEqual(result['extreme_sign_assignments'], 2)
        self.assertEqual(result['sign_assignments'], 8)
        self.assertEqual(result['p'], Fraction(1, 4))
        self.assertEqual(result['rank_biserial'], 1)
        # Ranks1,2,3; observed signed sum1+2-3=0, so all8 signs qualify.
        result = exact_signed_rank([1, 2, -3])
        self.assertEqual(result['p'], 1)
        self.assertEqual(result['rank_biserial'], 0)
        self.assertEqual(exact_signed_rank([-1, -2, -3])['rank_biserial'], -1)

    def test_exact_zeros_tied_ranks_and_rational_near_ties(self):
        result = exact_signed_rank([0, 1, 1, -1])
        self.assertEqual(result['zero_pairs'], 1)
        self.assertEqual(result['nonzero_pairs'], 3)
        self.assertEqual(result['rank_twice_by_nonzero_input_order'], [4, 4, 4])
        self.assertEqual(result['p'], 1)
        self.assertEqual(result['rank_biserial'], Fraction(1, 3))
        zero = exact_signed_rank([0]*12)
        self.assertEqual(zero['p'], 1)
        self.assertEqual(zero['rank_biserial'], 0)
        near = exact_signed_rank([Fraction(1), Fraction(10**25+1, 10**25)])
        self.assertEqual(near['ties'], [])
        self.assertEqual(near['rank_twice_by_nonzero_input_order'], [2, 4])
        with self.assertRaises(ValueError):
            exact_signed_rank([.1])

    def test_resolution_with_twelve_nonzero_pairs(self):
        result = exact_signed_rank([1]*12)
        self.assertEqual(result['p'], Fraction(1, 2048))
        self.assertEqual(result['sign_assignments'], 4096)
        self.assertEqual(exact_sign_test([1]*12), Fraction(1, 2048))
        self.assertEqual(exact_sign_test([1, -1, 0]), 1)
        self.assertEqual(exact_sign_test([0]*12), 1)

    def test_benign_far_raw_integer_denominator(self):
        self.assertEqual(benign_far(3, 20), Fraction(3, 20))
        self.assertEqual(benign_far(0, 20), 0)
        for a, n in ((1, 0), (21, 20), (-1, 20), (True, 20)):
            with self.assertRaises(ValueError):
                benign_far(a, n)

    def test_holm_exact_full_family_and_monotonicity(self):
        self.assertEqual(holm([Fraction(1, 100), Fraction(4, 100), Fraction(3, 100)]),
                         [Fraction(3, 100), Fraction(6, 100), Fraction(6, 100)])
        self.assertEqual(holm([Fraction(1, 2048)]+[Fraction(1)]*28)[0], Fraction(29, 2048))
        with self.assertRaises(ValueError):
            holm([Fraction(2)])

    def test_whole_seed_bootstrap_constant_interval_and_fixed_rng(self):
        interval = bootstrap_mean([Fraction(1, 4)]*12, 0)
        self.assertEqual((interval['lower'], interval['upper']), (.25, .25))
        self.assertEqual(interval['resamples'], 10000)
        self.assertEqual(interval['sample_size'], 12)
        self.assertEqual(interval['quantile_method'], 'linear')
        self.assertNotEqual(interval['initial_rng'], interval['final_rng'])
        with self.assertRaises(ValueError):
            bootstrap_mean([Fraction(1)]*11, 0)

    def test_bootstrap_keeps_zero_pairs_in_resampling(self):
        interval = bootstrap_mean([Fraction(1)]*6+[Fraction()]*6, 1)
        # The mean resample is Binomial(12,1/2)/12. Its population 2.5/97.5
        # percentiles are3/12 and9/12; this locked10000-draw fixture attains them.
        # Dropping zero pairs would incorrectly produce the constant interval1.
        self.assertEqual((interval['lower'], interval['upper']), (.25, .75))

    def test_contrast_wiring_no_double_clean_subtraction(self):
        _, spec = specification()
        endpoints = {}
        for seed in spec['seeds']:
            endpoints['FT', Fraction(1, 10), seed] = {'H': Fraction(9, 40), 'source_recall_change_E2': Fraction(-1, 5)}
            endpoints['EI', Fraction(1, 10), seed] = {'H': Fraction(1, 20), 'source_recall_change_E2': Fraction(-1, 10)}
            endpoints['DC', Fraction(), seed] = {'acquisition_A': Fraction(3, 5), 'benign_FAR_E4': Fraction(1, 20)}
            endpoints['DM', Fraction(), seed] = {'acquisition_A': Fraction(1, 2), 'benign_FAR_E4': Fraction(1, 10)}
        differences = contrast_differences(endpoints)
        self.assertEqual(differences['C1_01'], [Fraction(7, 40)]*12)
        self.assertEqual(differences['C1_10'], [Fraction(-1, 10)]*12)
        self.assertEqual(differences['C2_A_p000'], [Fraction(1, 10)]*12)
        self.assertEqual(differences['C2_FAR_clean'], [Fraction(-1, 20)]*12)
        self.assertEqual(differences['C1_02'], [None]*12)
        self.assertEqual(len(differences), 29)

    def test_unavailable_contrast_is_not_zero_imputation(self):
        _, spec = specification()
        values = {c['id']: [Fraction()]*12 for c in spec['contrasts']}
        values['C1_01'] = [Fraction(1)]*12
        values['C2_FAR_clean'][-1] = None
        output = analyze_family(values)
        first = output['rows'][0]
        self.assertEqual(first['raw_p']['exact'], ['1', '2048'])
        self.assertEqual(first['holm_adjusted_p']['exact'], ['29', '2048'])
        missing = output['rows'][-1]
        self.assertEqual(missing['missing_seeds'], [42])
        for field in ('raw_p', 'holm_adjusted_p', 'reject', 'mean_difference', 'median_difference', 'rank_biserial', 'bootstrap'):
            self.assertIsNone(missing[field])
        self.assertEqual(missing['holm_bookkeeping_p']['value'], 1)
        self.assertEqual(missing['status'], 'unavailable_with_protocol_deviation')
        self.assertEqual(output['family_size'], 29)
        self.assertFalse(output['final_release_enabled'])


if __name__ == '__main__':
    unittest.main()
