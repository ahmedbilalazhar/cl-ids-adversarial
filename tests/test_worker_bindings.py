"""Data-independent frozen-source and qualification-header regressions."""
import copy
import unittest
from pathlib import Path
from unittest.mock import patch

from kaggle_worker.bundle import QUALIFICATION_TRAIN, validate_header
from kaggle_worker.contracts import SourceBindings
from kaggle_worker.runtime import FROZEN_FILES, verify_frozen_bindings
from src.phase3.common import digest
from src.phase3_v2.data import BASE_DEV


class WorkerBindings(unittest.TestCase):
    def test_every_frozen_config_or_decision_change_is_rejected(self):
        self.assertEqual(verify_frozen_bindings(), FROZEN_FILES)
        for name in FROZEN_FILES:
            def altered(path, name=name):
                return '0'*64 if Path(path).as_posix().endswith('/'+name) else digest(path)
            with self.subTest(name=name), patch('kaggle_worker.runtime.digest', side_effect=altered):
                with self.assertRaises(ValueError):
                    SourceBindings.local()

    def test_header_pins_and_types_rejected_without_private_dataset(self):
        files = {'project/'+name: sha for name, sha in FROZEN_FILES.items()}
        files.update({'project/inputs/train/manifest.json': QUALIFICATION_TRAIN,
                      'project/inputs/development/manifest.json': BASE_DEV})
        header = {'schema': 'kaggle-qualification-snapshot-v1', 'seed': 101, 'dose': [0, 1],
                  'files': files, 'frozen_sources': {}, 'worker_sources': {},
                  'train_manifest_sha256': QUALIFICATION_TRAIN, 'includes_development': True,
                  'development_manifest_sha256': BASE_DEV, 'private_upload_only': True,
                  'final_test_accessed': False, 'final_dispatchable': False}
        validate_header(header, files)
        for key, value in [('train_manifest_sha256', '0'*64), ('development_manifest_sha256', '0'*64),
                           ('includes_development', 1), ('dose', [False, True]), ('seed', 101.),
                           ('schema', 'unknown'), ('private_upload_only', False), ('final_dispatchable', True)]:
            changed = copy.deepcopy(header)
            changed[key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                validate_header(changed, changed['files'])
        changed = copy.deepcopy(header)
        changed['files']['project/configs/phase3/cpu-v3.json'] = '0'*64
        with self.assertRaises(ValueError):
            validate_header(changed, changed['files'])


if __name__ == '__main__':
    unittest.main()
