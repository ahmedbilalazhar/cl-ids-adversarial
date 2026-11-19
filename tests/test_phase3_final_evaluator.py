import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from src.phase3.common import array_identity, digest, identity, save_state, state_identity, write_json
from src.phase3.model import ReferenceMLP
from src.phase3_v2.final_evaluate import (
    FINAL_FILES, REQUIRED_MANIFEST, validate_final_package,
    evaluate_final, validate_checkpoint_matrix, final_stage_counts,
)


def make_package(root, role='final_test', duplicate=False, bad_component=False,
                 bad_cohort_count=False, nonfinite=False, wrong_feature_shape=False,
                 excluded_taxonomy_class=False, low_support=False):
    root.mkdir(parents=True)
    n = 16
    x = np.zeros((n, 74), dtype='<f4')
    if nonfinite:
        x[0, 0] = np.nan
    if wrong_feature_shape:
        x = np.zeros((n, 73), dtype='<f4')
    y = np.arange(16, dtype='<i8')
    ids = np.arange(n, dtype='<u8')
    if duplicate:
        ids[-1] = ids[0]
    cohort = np.resize(np.arange(1, 5, dtype='u1'), n)
    attempted = np.zeros(n, dtype=np.bool_)
    components = np.arange(100, 100+n, dtype='<u8')
    files = {'x.npy':x,'y.npy':y,'ids.npy':ids,'cohort.npy':cohort,
             'attempted.npy':attempted,'component_ids.npy':components}
    for name, value in files.items(): np.save(root/name, value, allow_pickle=False)
    eligible_codes = list(range(15)) if excluded_taxonomy_class else list(range(16))
    manifest = {
        'schema':'phase3-final-test-v1','role':role,'release_id':'synthetic',
        'files':{name:digest(root/name) for name in FINAL_FILES},
        'eligible_codes':eligible_codes,'families':[str(i) for i in range(16)],
        'arrival':[0,1,1,2,2,2,2,2,3,3,3,3,3,4,4,4],
        'component_ids_sha256':array_identity(components),
        'development_manifest_sha256':'dev','protocol_sha256':'protocol',
        'frozen_checkpoint_inventory_sha256':'inventory','analysis_sha256':'analysis',
        'support_min_rows':2 if low_support else 1,'support_min_components':1,
        'benign_cohort_count':2 if bad_cohort_count else 1,
        'train_component_ids_sha256':'train','development_component_ids_sha256':'dev-components',
    }
    if bad_component: manifest['component_ids_sha256']='wrong'
    (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    frozen={'development_manifest_sha256':'dev','protocol_sha256':'protocol',
            'frozen_checkpoint_inventory_sha256':'inventory','analysis_sha256':'analysis',
            'final_manifest_sha256':digest(root/'manifest.json')}
    return frozen


class FinalEvaluatorContractTests(unittest.TestCase):
    def test_accepts_valid_synthetic_final_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p)
            self.assertEqual(validate_final_package(p,frozen)['role'],'final_test')

    def test_rejects_development_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p,role='development_only')
            with self.assertRaisesRegex(ValueError,'final_test'):
                validate_final_package(p,frozen)

    def test_retains_taxonomy_rows_excluded_from_eligible_macro_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p,excluded_taxonomy_class=True)
            manifest=validate_final_package(p,frozen)
            y=np.load(p/'y.npy',allow_pickle=False)
            self.assertNotIn(15,manifest['eligible_codes'])
            self.assertEqual(int((y==15).sum()),1)
            prediction=np.arange(16,dtype=np.int64)
            counts=final_stage_counts(
                4,list(range(16)),y,prediction,manifest['eligible_codes'],manifest['families'],
                manifest['arrival'],np.load(p/'cohort.npy',allow_pickle=False),
                np.load(p/'attempted.npy',allow_pickle=False))
            self.assertEqual(counts['full_seen_confusion_source_code_order'][15][15],1)
            self.assertNotIn(15,[row['code'] for row in counts['eligible_classes']])

    def test_enforces_frozen_minimum_row_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p,low_support=True)
            with self.assertRaisesRegex(ValueError,'below frozen row support'):
                validate_final_package(p,frozen)

    def test_rejects_duplicate_row_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p,duplicate=True)
            with self.assertRaisesRegex(ValueError,'duplicated'):
                validate_final_package(p,frozen)

    def test_rejects_component_identity_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p,bad_component=True)
            frozen['final_manifest_sha256']=digest(p/'manifest.json')
            with self.assertRaisesRegex(ValueError,'component identity'):
                validate_final_package(p,frozen)

    def test_rejects_incomplete_checkpoint_matrix(self):
        run={'schema':'phase3-run-v2','status':'complete','resumed_from':None,
             'final_test_accessed':False,'gpu_grid_launched':False,
             'settings':{'rounds':2},'checkpoints':[], 'total_commits':0,'next_cursor':[5,1]}
        with self.assertRaisesRegex(ValueError,'incomplete'):
            validate_checkpoint_matrix(run,'unused','unused')

    def test_rejects_nonfinite_features(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p,nonfinite=True)
            with self.assertRaisesRegex(ValueError,'feature matrix'):
                validate_final_package(p,frozen)

    def test_rejects_feature_width_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p,wrong_feature_shape=True)
            with self.assertRaisesRegex(ValueError,'feature matrix'):
                validate_final_package(p,frozen)

    def test_rejects_benign_cohort_inventory_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'package'; frozen=make_package(p,bad_cohort_count=True)
            with self.assertRaisesRegex(ValueError,'cohort count'):
                validate_final_package(p,frozen)

    def test_one_shot_synthetic_run_writes_auditable_predictions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); package=root/'package'; make_package(package)
            run_dir=root/'run'; run_dir.mkdir()
            execution={'synthetic':'contract-only','protocol_sha256':'protocol'}
            rows=[]
            for stage in range(1,5):
                slots=list(range((3,8,13,16)[stage-1]))
                model=ReferenceMLP(len(slots),101)
                arrays={'model.'+k:v.detach().numpy().copy() for k,v in model.state_dict().items()}
                meta={'execution':execution,'slots':slots}
                checkpoint=f'E{stage}-R1.npz'; path=run_dir/checkpoint
                save_state(path,meta,arrays)
                row={'schema':'phase3-commit-v2','stage':stage,'round':1,'stage_end':True,
                     'file':checkpoint,'file_sha256':digest(path),
                     'state_identity':state_identity(meta,arrays),'head_width':len(slots),
                     'source_codes_in_slot_order':slots}
                write_json(path.with_suffix('.commit.json'),row); rows.append(row)
            inventory=identity([{'file':r['file'],'sha256':r['file_sha256'],'stage':r['stage'],
                                 'round':r['round'],'stage_end':r['stage_end']} for r in rows])
            run={'schema':'phase3-run-v2','status':'complete','resumed_from':None,
                 'final_test_accessed':False,'gpu_grid_launched':False,'execution':execution,
                 'settings':{'rounds':1,'seed':101},'checkpoints':rows,'total_commits':4,
                 'next_cursor':[5,1]}
            run_path=run_dir/'run.json'; write_json(run_path,run)
            run_hash=digest(run_path)
            manifest=json.loads((package/'manifest.json').read_text())
            manifest['frozen_checkpoint_inventory_sha256']='frozen-inventory'
            write_json(package/'manifest.json',manifest)
            freeze={'schema':'phase3-final-freeze-v1','status':'authorized_one_shot',
                    'development_manifest_sha256':'dev','protocol_sha256':'protocol',
                    'frozen_checkpoint_inventory_sha256':'frozen-inventory',
                    'analysis_sha256':'analysis','final_manifest_sha256':digest(package/'manifest.json'),
                    'run_manifest_sha256':[run_hash],'checkpoint_inventory_sha256':[inventory],
                    'settings':[run['settings']]}
            freeze_path=root/'freeze.json'; write_json(freeze_path,freeze)
            output=root/'metrics'
            evaluate_final(package,[run_dir],freeze_path,output)
            metrics=json.loads((output/'metrics.json').read_text())
            self.assertEqual(metrics['status'],'one_shot_final_test_complete')
            self.assertEqual(len(metrics['runs'][0]['stages']),4)
            first=metrics['runs'][0]['stages'][0]
            self.assertEqual(first['source_codes_in_slot_order'],[0,1,2])
            self.assertEqual(first['eligible_seen_bank_rows'],3)
            self.assertEqual(sum(map(sum,first['full_seen_confusion_source_code_order'])),16)
            prediction=output/metrics['runs'][0]['stages'][0]['predictions_file']
            self.assertTrue(prediction.is_file())
            self.assertEqual(digest(prediction),metrics['runs'][0]['stages'][0]['predictions_sha256'])
            self.assertTrue((root/'metrics.one-shot-claimed.json').is_file())
            with self.assertRaises(FileExistsError):
                evaluate_final(package,[run_dir],freeze_path,output)

    def test_nonfinite_logits_leave_durable_one_shot_claim_and_no_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); package=root/'package'; make_package(package)
            run_dir=root/'run'; run_dir.mkdir()
            execution={'synthetic':'contract-only','protocol_sha256':'protocol'}
            rows=[]
            for stage in range(1,5):
                slots=list(range((3,8,13,16)[stage-1]))
                model=ReferenceMLP(len(slots),101)
                arrays={'model.'+k:v.detach().numpy().copy() for k,v in model.state_dict().items()}
                meta={'execution':execution,'slots':slots}
                checkpoint=f'E{stage}-R1.npz'; path=run_dir/checkpoint
                save_state(path,meta,arrays)
                row={'schema':'phase3-commit-v2','stage':stage,'round':1,'stage_end':True,
                     'file':checkpoint,'file_sha256':digest(path),
                     'state_identity':state_identity(meta,arrays),'head_width':len(slots),
                     'source_codes_in_slot_order':slots}
                write_json(path.with_suffix('.commit.json'),row); rows.append(row)
            inventory=identity([{'file':r['file'],'sha256':r['file_sha256'],'stage':r['stage'],
                                 'round':r['round'],'stage_end':r['stage_end']} for r in rows])
            run={'schema':'phase3-run-v2','status':'complete','resumed_from':None,
                 'final_test_accessed':False,'gpu_grid_launched':False,'execution':execution,
                 'settings':{'rounds':1,'seed':101},'checkpoints':rows,'total_commits':4,
                 'next_cursor':[5,1]}
            write_json(run_dir/'run.json',run)
            manifest=json.loads((package/'manifest.json').read_text())
            manifest['frozen_checkpoint_inventory_sha256']='frozen-inventory'
            write_json(package/'manifest.json',manifest)
            freeze={'schema':'phase3-final-freeze-v1','status':'authorized_one_shot',
                    'development_manifest_sha256':'dev','protocol_sha256':'protocol',
                    'frozen_checkpoint_inventory_sha256':'frozen-inventory',
                    'analysis_sha256':'analysis','final_manifest_sha256':digest(package/'manifest.json'),
                    'run_manifest_sha256':[digest(run_dir/'run.json')],
                    'checkpoint_inventory_sha256':[inventory],'settings':[run['settings']]}
            freeze_path=root/'freeze.json'; write_json(freeze_path,freeze)
            output=root/'metrics'
            def nonfinite_logits(self, features):
                return torch.full((len(features),self.classifier.out_features),float('nan'))
            with patch('src.phase3_v2.final_evaluate.ReferenceMLP.forward',nonfinite_logits):
                with self.assertRaisesRegex(FloatingPointError,'Nonfinite final logits'):
                    evaluate_final(package,[run_dir],freeze_path,output)
            receipt=root/'metrics.one-shot-claimed.json'
            self.assertTrue(receipt.is_file())
            self.assertEqual(json.loads(receipt.read_text())['status'],'claimed')
            self.assertFalse((output/'metrics.json').exists())


if __name__=='__main__': unittest.main()
