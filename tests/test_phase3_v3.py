"""V3 budget/state equivalence and interruption-safe orchestration fixtures."""
from __future__ import annotations

import math
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from src.phase3.common import ROOT, identity, read_json, write_json
from src.phase3_v2.protocol import Settings as OldSettings
from src.phase3_v2.protocol import code_identity as old_identity
from src.phase3_v2.train import Simulator
from src.phase3_v3.development import (
    execute_development,
    pilot_settings,
    select_budget,
    tuning_settings,
    verify_complete_run,
    workflow_lock,
)
from src.phase3_v3.evaluate import evaluate
from src.phase3_v3.protocol import BUDGETS, Settings, code_identity, configure_runtime
from tests.test_phase3_v2 import four_stages

METHODS = [('FT', 'NONE'), ('EI', 'NONE'), ('DR', 'NONE'), ('DR', 'DM'), ('DR', 'DC'), ('DR', 'DQ')]


class Phase3V3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_runtime()

    def test_version_budget_scope_and_parent_unchanged(self):
        self.assertEqual(old_identity(), '4b7561d38300b9f42dd6e9091ecc3509b5e1b2cabdddedb2b9cdd345baffa6a6')
        self.assertNotEqual(code_identity(), old_identity())
        for budget in BUDGETS+((1, 3), (3, 1)):
            Settings(rounds=budget[0], epochs=budget[1]).validate()
        for settings in (Settings(rounds=24), Settings(rounds=12, epochs=4), Settings(rounds=3., epochs=4),
                         Settings(seed=1), Settings(learner='FT', admission='DC'), Settings(dose=(3, 5)), Settings(learning_rate=float('nan'))):
            with self.assertRaises(ValueError):
                settings.validate()
        with self.assertRaises(ValueError):
            OldSettings(rounds=12).validate()

    def test_frozen_grid_numeric_ties_and_no_old_budget_selection(self):
        pilots = pilot_settings()
        self.assertEqual(len(pilots), 18)
        self.assertEqual((pilots[0].rounds, pilots[0].epochs), (3, 4))
        self.assertEqual((pilots[-1].rounds, pilots[-1].epochs), (12, 1))
        for budget in BUDGETS:
            grid = tuning_settings(budget)
            self.assertEqual(len(grid), 60)
            self.assertEqual(len({identity(s.scientific()) for s in grid}), 60)
            for settings in grid:
                settings.validate()
        with self.assertRaises(ValueError):
            tuning_settings((3, 1))
        rows = [{'settings': asdict(s), 'status': 'valid', 'score_exact': ['1', '2']} for s in pilots]
        self.assertEqual(select_budget(rows)[0], (3, 4))
        rows[0]['status'] = 'invalid'
        self.assertEqual(select_budget(rows)[0], (12, 1))

    def test_exact_old_budget_parity_all_six_pipelines(self):
        stages = four_stages()
        with tempfile.TemporaryDirectory() as td:
            for learner, admission in METHODS:
                values = {'learner': learner, 'admission': admission, 'rounds': 3, 'epochs': 1}
                first, second = Path(td)/(learner+admission+'old'), Path(td)/(learner+admission+'new')
                a = Simulator(OldSettings(**values), stages.__getitem__, {'fixture': 'compatibility'}).execute(first)
                b = Simulator(Settings(**values), stages.__getitem__, {'fixture': 'compatibility'}).execute(second)
                self.assertEqual(a['ledger'], b['ledger'])
                self.assertEqual([c['state_identity'] for c in a['checkpoints']], [c['state_identity'] for c in b['checkpoints']])

    def test_extended_updates_proposals_importance_and_exact_recovery_all_methods(self):
        stages = four_stages()
        with tempfile.TemporaryDirectory() as td:
            for rounds, epochs in BUDGETS:
                for learner, admission in METHODS:
                    label = f'r{rounds}e{epochs}{learner}{admission}'
                    settings = Settings(learner=learner, admission=admission, rounds=rounds, epochs=epochs)
                    engine = Simulator(settings, stages.__getitem__, {'fixture': label})
                    full, suffix = Path(td)/label, Path(td)/(label+'resumed')
                    first = engine.execute(full)
                    second = engine.execute(suffix, full/'E1-R2.npz')
                    self.assertEqual(len(first['checkpoints']), 4*rounds)
                    self.assertEqual(len(second['checkpoints']), 4*rounds-2)
                    self.assertEqual(first['ledger'], second['ledger'])
                    original = {r['file']: r for r in first['checkpoints']}
                    for row in second['checkpoints']:
                        self.assertEqual(original[row['file']]['state_identity'], row['state_identity'])
                    self.assertEqual(sum(r['kind'] == 'admission' for r in first['ledger']), 4)
                    self.assertEqual(sum(r['kind'] == 'importance' for r in first['ledger']), 4 if learner == 'EI' else 0)
                    for stage in range(1, 5):
                        admission_row = next(r for r in first['ledger'] if r['kind'] == 'admission' and r['stage'] == stage)
                        transitions = [r for r in first['ledger'] if r['kind'] == 'round' and r['stage'] == stage]
                        for client in range(5):
                            n = admission_row['clients'][client]['admitted']
                            self.assertEqual(sum(r['clients'][client].get('optimizer_updates', 0) for r in transitions), rounds*epochs*math.ceil(n/128))
                            self.assertEqual(sum(r['clients'][client].get('current_exposures', 0) for r in transitions), rounds*epochs*n)
                            self.assertEqual(sum(r['clients'][client].get('proposals', 0) for r in transitions), n if learner == 'DR' else 0)
                    if learner == 'EI':
                        boundary = Path(td)/(label+'boundary')
                        third = engine.execute(boundary, full/f'E1-R{rounds}.npz')
                        self.assertEqual(first['ledger'], third['ledger'])
                        self.assertEqual(first['final_model_sha256'], third['final_model_sha256'])

    def test_cross_revision_resume_and_v2_evaluation_rejected(self):
        stages = four_stages()
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)/'old'
            Simulator(OldSettings(learner='FT'), stages.__getitem__, {'revision': 'v2'}).execute(folder, stop_after_commits=2)
            with self.assertRaises(ValueError):
                Simulator(Settings(learner='FT'), stages.__getitem__, {'revision': 'v3'}).execute(Path(td)/'new', folder/'E1-R2.npz')
            self.assertFalse((Path(td)/'new').exists())
            with self.assertRaises(ValueError):
                evaluate(ROOT/'data/processed/phase3-reference74-v1/development', ROOT/'results/phase3-cpu-v2/integration/DC', Path(td)/'evaluation')
            self.assertFalse((Path(td)/'evaluation').exists())

    def test_single_live_orchestrator_lock(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)/'run'
            with workflow_lock(output), self.assertRaises(RuntimeError), workflow_lock(output):
                pass
            with workflow_lock(output):
                pass

    def workflow_fixture(self, root, interrupt=False):
        packages = root/'packages'
        for seed in (101, 102, 103):
            write_json(packages/f's{seed}-p000/preparation.json', {'train_manifest_sha256': 'fixture'})
        accepted = root/'acceptance.json'
        write_json(accepted, {'status': 'passed', 'code_identity': code_identity()})
        invocations = []
        interrupted = False

        def train(package, output, settings, expected):
            nonlocal interrupted
            invocations.append(settings.scientific())
            write_json(output/'fixture.json', asdict(settings))
            if interrupt and not interrupted:
                interrupted = True
                raise KeyboardInterrupt('transparent infrastructure interruption fixture')
            return {'elapsed_seconds': 7.}

        def metric(development, run, output):
            settings = read_json(run/'fixture.json')
            # Three valid seeds but failing SSH gates; no poison diagnostics.
            result = {'settings': settings, 'stages': [
                {'eligible_macro_f1_exact': ['1', '2'], 'eligible_classes': [{'code': 7, 'tp': 1, 'fn': 0, 'support': 1}, {'code': 12, 'tp': 0, 'fn': 1, 'support': 1}]},
                {'eligible_macro_f1_exact': ['1', '2'], 'eligible_classes': [{'code': 4, 'tp': 1, 'fn': 0, 'support': 1}]},
                {'eligible_macro_f1_exact': ['1', '2']}, {'eligible_macro_f1_exact': ['1', '2']}]}
            write_json(output/'metrics.json', result)
            return result
        return packages, accepted, invocations, train, metric

    def test_unreceipted_import_requires_physical_measured_cost(self):
        settings = Settings(learner='FT')
        markers = [{'stage': s, 'round': r, 'file': f'E{s}-R{r}.npz'} for s in range(1, 5) for r in range(1, 4)]
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            write_json(folder/'settings.json', asdict(settings))
            result = {'schema': 'phase3-run-v2', 'status': 'complete', 'resumed_from': None,
                      'execution': {'fixture': 'import'}, 'settings': {**asdict(settings), 'dose': [0, 1]},
                      'checkpoints': markers, 'next_cursor': [5, 1], 'total_commits': 12,
                      'independent_replicate': True, 'elapsed_seconds': 7.}
            write_json(folder/'run.json', result)
            with patch('src.phase3_v3.development.read_transaction', side_effect=lambda path, execution: (None, None, next(r for r in markers if r['file'] == path.name))):
                self.assertEqual(verify_complete_run(folder, settings, {'fixture': 'import'})['elapsed_seconds'], 7.)
            for bad in ({'elapsed_seconds': None}, {'elapsed_seconds': -1}, {'elapsed_seconds': False},
                        {'independent_replicate': False}, {'artifact_kind': 'verified_recovered_trajectory_collection_v1'}):
                write_json(folder/'run.json', {**result, **bad})
                with self.assertRaises(ValueError):
                    verify_complete_run(folder, settings, {'fixture': 'import'})

    def test_completed_receipts_resume_exact_alias_cost_and_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            packages, accepted, calls, train, metric = self.workflow_fixture(root)
            output = root/'procedure'
            with patch('src.phase3_v3.development.run', side_effect=train), patch('src.phase3_v3.development.evaluate', side_effect=metric), patch('src.phase3_v3.development.verify_train'):
                first = execute_development(output, packages, accepted)
                self.assertEqual(len(calls), 69)
                self.assertEqual(first['exact_clean_aliases'], 9)
                self.assertTrue(all(r['logical_training_seconds'] == 7 for r in first['rows']))
                second = execute_development(output, packages, accepted, True)
                self.assertEqual(first, second)
                self.assertEqual(len(calls), 69)
                physical = next(r for r in first['rows'] if r['physical_execution'])
                write_json(Path(physical['run'])/'fixture.json', {'corrupted': True})
                with self.assertRaises(ValueError):
                    execute_development(output, packages, accepted, True)
                self.assertEqual(len(calls), 69)

    def test_interrupted_condition_retained_and_same_identity_retried(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            packages, accepted, calls, train, metric = self.workflow_fixture(root, True)
            output = root/'procedure'
            with patch('src.phase3_v3.development.run', side_effect=train), patch('src.phase3_v3.development.evaluate', side_effect=metric), patch('src.phase3_v3.development.verify_train'):
                with self.assertRaises(KeyboardInterrupt):
                    execute_development(output, packages, accepted)
                result = execute_development(output, packages, accepted, True)
            self.assertEqual(result['physical_clean_executions'], 70)
            self.assertEqual(result['physical_clean_conditions'], 69)
            self.assertEqual(calls[0], calls[1])
            self.assertEqual(result['invalid_rows'], [])
            first = result['rows'][0]
            self.assertEqual(first['physical_attempts'], 2)
            self.assertTrue(Path(first['run']).parent.parent.joinpath('attempt-001/train/fixture.json').exists())


if __name__ == '__main__':
    unittest.main()
