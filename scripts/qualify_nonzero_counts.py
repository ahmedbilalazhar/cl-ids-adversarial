"""Publish fabricated nonzero count/oracle acceptance, never research results."""
import argparse
import copy
import tempfile
from fractions import Fraction
from pathlib import Path

from phase3_delivery.assemble import assemble
from phase3_delivery.catalog import create_output
from src.phase3.common import ROOT, digest
from tests.test_research_endpoints import SEEDS, fabricated_catalog, oracle


def qualify(output):
    with tempfile.TemporaryDirectory(prefix='nonzero-count-oracle-') as directory:
        catalog = fabricated_catalog(Path(directory))
        result = assemble(catalog)
        assertions = 0
        for row in result['analysis']['rows']:
            dose = Fraction(str(row['dose']))
            pair = (dose.numerator, dose.denominator)
            for seed, actual in zip(SEEDS, row['paired_differences']):
                expected = (oracle(row['left_arm'], pair, seed)[row['metric']]-
                            oracle(row['right_arm'], pair, seed)[row['metric']])
                if actual['exact'] != [str(expected.numerator), str(expected.denominator)]:
                    raise ValueError('Independent endpoint formula disagrees')
                assertions += 1
        missing = copy.deepcopy(catalog)
        missing['records'] = [record for record in missing['records']
                              if record['row']['run_id'] != 'FT-0-1-42']
        incomplete = assemble(missing)
        unavailable = [row for row in incomplete['analysis']['rows'] if row['status'] != 'computed_complete_paired_seeds']
        # The existing assembler names availability explicitly; retain exact rows
        # rather than treating missing pairs as zero or filtering the family.
        if len(result['analysis']['rows']) != 29 or len(incomplete['analysis']['rows']) != 29:
            raise ValueError('The single all_29 comparison family changed')
        create_output(output, {'schema': 'phase3-nonzero-count-oracle-v1', 'status': 'passed',
                      'scope': '240 fabricated count trajectories; no training/features/final outcomes',
                      'oracle_pair_assertions': assertions, 'analysis': result,
                      'missing_clean_reference': incomplete, 'unavailable_contrasts': len(unavailable),
                      'fixture_sources': {name: digest(ROOT/name) for name in
                          ('tests/test_research_endpoints.py', 'tests/test_delivery_catalog.py',
                           'tests/test_continuation.py')},
                      'final_test_accessed': False, 'final_dispatchable': False})
        print({'status': 'passed', 'oracle_pair_assertions': assertions, 'contrasts': 29,
               'unavailable_contrasts_after_missing_clean': len(unavailable)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    qualify(parser.parse_args().output)


if __name__ == '__main__':
    main()
