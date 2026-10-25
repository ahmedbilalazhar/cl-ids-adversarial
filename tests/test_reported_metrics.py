"""Independent rejection tests for previously unchecked displayed metrics."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from phase3_delivery.import_counts import import_counts
from src.phase3.common import ROOT, digest, read_json
from tests.test_delivery_catalog import fixture_row


class ReportedMetrics(unittest.TestCase):
    def test_reported_metric_or_label_corruption_rejected(self):
        changes = {
            'precision': lambda m: m['stages'][0]['eligible_classes'][0].update(precision=.123),
            'binary_recall': lambda m: m['stages'][0]['binary_full_seen'].update(attack_recall=.123),
            'binary_precision': lambda m: m['stages'][0]['binary_full_seen'].update(attack_precision=.123),
            'binary_f1': lambda m: m['stages'][0]['binary_full_seen'].update(f1=.123),
            'miss_rate': lambda m: m['stages'][0]['binary_full_seen'].update(attack_miss_rate=.123),
            'subgroup_rate': lambda m: m['stages'][0]['benign_provenance_descriptive'][0].update(error_rate=.123),
            'subgroup_name': lambda m: m['stages'][0]['benign_provenance_descriptive'][1].update(group='original_background'),
            'family_label': lambda m: m['stages'][0]['eligible_classes'][0].update(family='wrong family'),
            'support_status': lambda m: m['stages'][0]['eligible_classes'][0].update(status='unsupported'),
            'cohort_bool': lambda m: m['stages'][0]['cohort_counts'][0].update(cohort=True),
            'hulk_bool': lambda m: m['stages'][1]['hulk_partition'].update(predicted_benign=False),
            'auxiliary_infinity': lambda m: m.update(evaluation_seconds=float('inf')),
        }
        with tempfile.TemporaryDirectory() as directory:
            row, path = fixture_row(Path(directory), 'reported')
            original = read_json(path)
            for name, mutate in changes.items():
                with self.subTest(field=name):
                    metric = copy.deepcopy(original)
                    mutate(metric)
                    path.write_text(json.dumps(metric))
                    with self.assertRaises(ValueError):
                        import_counts(path, digest(path), row['settings'], row['execution'],
                                      read_json(ROOT/'configs/phase3/taxonomy-v1.json')['classes'],
                                      kind='synthetic', run_id=name, seen_ids=set(), seen_conditions=set())


if __name__ == '__main__':
    unittest.main()
