"""Nonzero fabricated-count oracle for pairing, signs, acquisition and Holm wiring."""
import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import numpy as np

from phase3_delivery.assemble import assemble
from phase3_delivery.import_counts import import_counts
from src.phase3.common import ROOT, digest, read_json
from src.phase3_v2.evaluate import stage_counts
from tests.test_delivery_catalog import fixture_row

SEEDS = list(range(1, 12))+[42]
ARMS = ('FT', 'EI', 'DR', 'DM', 'DC')
DOSES = ((0, 1), (1, 10), (3, 10), (1, 2))


def oracle(arm, dose, seed):
    factor = int(Fraction(*dose)*10)
    jitter = seed % 3
    k = 0 if factor == 0 else {'FT': 3, 'EI': 2, 'DR': 1, 'DM': 3, 'DC': 1}[arm]*factor+jitter
    acquisition_misses = 1+jitter+factor if arm == 'DM' else 0
    far_alerts = 2 if arm == 'DC' else 1
    return {'H': Fraction(k, 20), 'source_recall_change_E2': -Fraction(k//2, 20),
            'acquisition_A': Fraction(2*(20-acquisition_misses), 40-acquisition_misses),
            'benign_FAR_E4': Fraction(far_alerts, 40)}


def nonzero_metric(arm, dose, seed, settings, execution):
    """Fabricate predictions from a declared formula; there are no feature inputs."""
    classes = read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes']
    arrival = [next(c['arrival_stage'] for c in classes if c['source_code'] == i) for i in range(16)]
    eligible = [c['source_code'] for c in classes if c['scoring_eligible']]
    expected = oracle(arm, dose, seed)
    k = int(expected['H']*20)
    m = 1+seed % 3+int(Fraction(*dose)*10) if arm == 'DM' else 0
    stages, matrix = [], [[None]*4 for _ in range(4)]
    for t in range(1, 5):
        slots = [c['source_code'] for c in sorted(classes, key=lambda c: (c['arrival_stage'], c['source_code']))
                 if c['arrival_stage'] <= t]
        y = np.array([0]*40+[code for code in slots if code != 0 for _ in range(20)], dtype=np.int64)
        cohorts = np.array([j for j in range(1, 5) for _ in range(10)]+
                           [arrival[code] for code in slots if code != 0 for _ in range(20)])
        predicted = y.copy()
        if t >= 2:
            misses = k//2 if t == 2 else k+(1 if t == 3 else 2)
            predicted[np.flatnonzero(y == 4)[:misses]] = 0
            for code in eligible:
                if code not in (0, 4) and arrival[code] == t:
                    predicted[np.flatnonzero(y == code)[:m]] = 0
        if t == 4:
            predicted[np.flatnonzero(y == 0)[:int(expected['benign_FAR_E4']*40)]] = 4
        names = [next(c['label'] for c in classes if c['source_code'] == i) for i in range(16)]
        counts = stage_counts(t, slots, y, predicted, eligible, names,
                              arrival, cohorts, np.zeros(len(y), dtype=bool))
        counts['bank_ids_sha256'] = str(t)*64
        stages.append(counts)
        for cell in counts['cohort_counts']:
            matrix[t-1][cell['cohort']-1] = cell['correct']/cell['total']
    final = matrix[3]
    return {'schema': 'kaggle-qualification-development-metrics-v1', 'status': 'valid_development_only',
            'settings': settings, 'execution': execution, 'stages': stages,
            'R_accuracy_by_stage_and_arrival_cohort': matrix,
            'A': float(expected['acquisition_A']), 'equal_stage_ACC4': sum(final)/4,
            'BWT4': sum(final[j]-matrix[j][j] for j in range(3))/3,
            'forgetting4': sum(max(matrix[t][j] for t in range(j, 4))-final[j] for j in range(3))/3,
            'final_test_accessed': False}


def fabricated_catalog(folder):
    classes = read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes']
    records, ids, conditions = [], set(), set()
    for arm in ARMS:
        for dose in DOSES:
            for seed in SEEDS:
                run_id = f'{arm}-{dose[0]}-{dose[1]}-{seed}'
                row, path = fixture_row(folder, run_id, arm, seed, dose)
                metric = nonzero_metric(arm, dose, seed, row['settings'], row['execution'])
                path.write_text(json.dumps(metric), encoding='utf-8')
                row['metric_sha256'] = digest(path)
                result = import_counts(path, row['metric_sha256'], row['settings'], row['execution'], classes,
                                       kind='synthetic', run_id=run_id, seen_ids=ids, seen_conditions=conditions)
                records.append({'row': row, 'counts': result})
    return {'status': 'passed', 'kind': 'synthetic', 'manifest_sha256': 'f'*64,
            'records': records, 'aliases': {}, 'missing_run_ids': [],
            'final_test_accessed': False, 'final_dispatchable': False}


class ResearchEndpoints(unittest.TestCase):
    def test_nonzero_formula_matches_all_29_exact_paired_contrasts(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog = fabricated_catalog(Path(directory))
            result = assemble(catalog)
            self.assertEqual(len(result['analysis']['rows']), 29)
            for contrast in result['analysis']['rows']:
                dose = Fraction(str(contrast['dose']))
                rational_dose = (dose.numerator, dose.denominator)
                for seed, actual in zip(SEEDS, contrast['paired_differences']):
                    expected = (oracle(contrast['left_arm'], rational_dose, seed)[contrast['metric']]-
                                oracle(contrast['right_arm'], rational_dose, seed)[contrast['metric']])
                    self.assertEqual(actual['exact'], [str(expected.numerator), str(expected.denominator)])
                self.assertEqual(contrast['available_pairs'], 12)
                self.assertLessEqual(contrast['raw_p']['value'], 1)
                self.assertGreaterEqual(contrast['holm_adjusted_p']['value'], contrast['raw_p']['value'])
                if contrast['metric'] == 'H':
                    self.assertEqual(contrast['raw_p']['exact'], ['1', '2048'])
                    expected_sign = 1 if contrast['left_arm'] != 'DC' else -1
                    self.assertEqual(contrast['rank_biserial']['value'], expected_sign)
            # Same-dose rows using a different clean profile must never be pooled.
            malformed = copy.deepcopy(catalog)
            malformed['records'][0]['row']['settings']['learning_rate'] = .002
            with self.assertRaises(ValueError):
                assemble(malformed)


if __name__ == '__main__':
    unittest.main()
