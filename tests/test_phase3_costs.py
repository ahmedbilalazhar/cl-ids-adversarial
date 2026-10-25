"""Independent fixtures for the prospectively fixed timing correction."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from scripts.remeasure_phase3_v3 import anomalies, derive_selection
from src.phase3.common import write_json


class TimingDisposition(unittest.TestCase):
    def test_fixed_anomaly_rule(self):
        rows = [{'stage': 2, 'round': i, 'training_seconds': s} for i, s in enumerate((18., 20., 8900.), 1)]
        found = anomalies({'timings': rows})
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['round'], 3)
        self.assertEqual(found[0]['other_rounds_median_seconds'], 19.)
        rows[-1]['training_seconds'] = 600.
        self.assertEqual(anomalies({'timings': rows}), [])
        rows[-1]['training_seconds'] = 601.
        rows[0]['training_seconds'] = rows[1]['training_seconds'] = 70.
        self.assertEqual(anomalies({'timings': rows}), [])

    def test_only_tied_cost_changes_without_mutating_original_rows(self):
        with tempfile.TemporaryDirectory() as td:
            rows = []
            for lr, cost in ((.0001, 99.), (.001, 5.)):
                for seed in (101, 102, 103):
                    path = Path(td)/f'{lr}-{seed}.json'
                    write_json(path, {'settings': {'seed': seed}, 'stages': [
                        {'eligible_macro_f1_exact': ['1', '2'], 'eligible_classes': [{'code': 7, 'tp': 1, 'fn': 0, 'support': 1}, {'code': 12, 'tp': 1, 'fn': 0, 'support': 1}]},
                        {'eligible_macro_f1_exact': ['1', '2'], 'eligible_classes': [{'code': 4, 'tp': 1, 'fn': 0, 'support': 1}]},
                        {'eligible_macro_f1_exact': ['1', '2']}, {'eligible_macro_f1_exact': ['1', '2']}]})
                    rows.append({'group': 'tuning', 'row_id': str(path), 'settings': {'learner': 'FT', 'seed': seed, 'learning_rate': lr},
                                 'logical_identity': f'{lr}-{seed}', 'status': 'valid', 'metrics': str(path), 'logical_training_seconds': cost})
            original = copy.deepcopy(rows)
            first = derive_selection(rows, {})['FT']['selected']
            self.assertEqual(first['settings_without_seed']['learning_rate'], .001)
            corrected = derive_selection(rows, {f'0.0001-{s}': 1. for s in (101, 102, 103)})['FT']['selected']
            self.assertEqual(corrected['settings_without_seed']['learning_rate'], .0001)
            self.assertEqual(first['score_exact'], corrected['score_exact'])
            self.assertEqual(rows, original)


if __name__ == '__main__':
    unittest.main()
