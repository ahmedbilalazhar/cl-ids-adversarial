"""Execute generated upload bootstrap against an emulated read-only mount."""
import contextlib
import base64
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.prepare_kaggle_upload import BUNDLE_LINE, CLOCK_LINE, adapt_notebook, prepare, sha


def notebook_fixture(bundle_sha):
    return {'nbformat': 4, 'nbformat_minor': 5,
            'metadata': {'phase3': {'bundle_sha256': bundle_sha, 'final_dispatchable': False}},
            'cells': [{'cell_type': 'markdown', 'metadata': {}, 'source': ['Original instructions\n']},
                      {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [],
                       'source': ['from pathlib import Path\n', 'import time\n', BUNDLE_LINE+'\n',
                                  CLOCK_LINE+'\n', "DEVICE = 'cpu'\n", 'RUN_FULL_DATA = False\n']},
                      {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [],
                       'source': ['# Original versioned scientific entry point remains unchanged.\n',
                                  'sentinel = 8123\n']}]}


class KaggleUpload(unittest.TestCase):
    def fixture(self, root, size=10000001):
        archive = root/'reviewed.zip'
        # Exercise full Base64 block boundaries, remainder and binary zeros.
        archive.write_bytes((bytes(range(256))*((size+255)//256))[:size])
        source = root/'reviewed.ipynb'
        source.write_text(json.dumps(notebook_fixture(sha(archive))), encoding='utf-8')
        output = root/'upload'
        result = prepare(archive, sha(archive), source, sha(source), output)
        notebook = json.loads((output/'phase3-kaggle-start.ipynb').read_text(encoding='utf-8'))
        return archive, source, output, result, notebook

    def bootstrap(self, notebook, encoded, target):
        original = ''.join(notebook['cells'][1]['source'])
        # Change operator configuration only; execute the real generated logic.
        code = original.replace("Path('/kaggle/input/CHANGE-TO-YOUR-PRIVATE-DATASET/qualification.zip.b64')",
                                'Path('+repr(str(encoded))+')').replace(
                                    "Path('/kaggle/working/phase3-qualification.zip')", 'Path('+repr(str(target))+')')
        namespace = {}
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            exec(compile(code, 'generated-upload-bootstrap', 'exec'), namespace)
        return namespace, stream.getvalue()

    def test_exact_multiblock_roundtrip_reuse_and_original_workflow_cells_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, source, output, receipt, notebook = self.fixture(root)
            original = json.loads(source.read_text(encoding='utf-8'))
            expected = copy.deepcopy(original['cells'])
            code = ''.join(expected[1]['source']).replace(BUNDLE_LINE, 'BUNDLE = DECODED_BUNDLE').replace(
                CLOCK_LINE, 'SESSION_STARTED = UPLOAD_SESSION_STARTED')
            expected[1]['source'] = code.splitlines(keepends=True)
            self.assertEqual(notebook['cells'][2:], expected)
            self.assertEqual(notebook['metadata']['phase3']['bundle_sha256'], sha(archive))
            target = root/'working/qualification.zip'
            namespace, message = self.bootstrap(notebook, output/'qualification.zip.b64', target)
            self.assertIn('exact_original_bundle_restored', message)
            self.assertEqual(target.read_bytes(), archive.read_bytes())
            self.assertEqual(receipt['archive_sha256'], sha(target))
            self.assertEqual(receipt['encoded_upload_bytes'], 4*((archive.stat().st_size+2)//3))
            self.assertFalse(receipt['provider_upload_qualified'] or receipt['uploaded'] or receipt['worker_source_changed'])
            namespace2, message = self.bootstrap(notebook, output/'qualification.zip.b64', target)
            self.assertIn('existing_exact_bundle_verified', message)
            self.assertGreaterEqual(namespace2['UPLOAD_SESSION_STARTED'], namespace['UPLOAD_SESSION_STARTED'])

    def test_changed_truncated_or_appended_upload_rejected_before_archive_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, output, _, notebook = self.fixture(root, 5001)
            encoded = output/'qualification.zip.b64'
            raw = encoded.read_bytes()
            for index, changed in enumerate((raw[:-4], raw+b'AAAA', b'!'+raw[1:])):
                encoded.write_bytes(changed)
                target = root/f'never-published-{index}.zip'
                with self.subTest(case=index), self.assertRaises(ValueError):
                    self.bootstrap(notebook, encoded, target)
                self.assertFalse(target.exists())

    def test_existing_wrong_archive_and_original_inputs_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, source, output, _, notebook = self.fixture(root, 5001)
            target = root/'preserved.zip'
            target.write_bytes(b'previous failed attempt')
            with self.assertRaises(ValueError):
                self.bootstrap(notebook, output/'qualification.zip.b64', target)
            self.assertEqual(target.read_bytes(), b'previous failed attempt')
            before = {path: sha(path) for path in (archive, source, output/'receipt.json')}
            with self.assertRaises(FileExistsError):
                prepare(archive, sha(archive), source, sha(source), output)
            self.assertEqual({path: sha(path) for path in before}, before)

    def test_decoder_flush_failure_retains_staging_without_completed_zip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, output, _, notebook = self.fixture(root, 5001)
            target = root/'working/qualification.zip'
            with patch('os.fsync', side_effect=OSError('injected decode flush failure')), self.assertRaises(OSError):
                self.bootstrap(notebook, output/'qualification.zip.b64', target)
            self.assertFalse(target.exists())
            self.assertEqual(len(list(target.parent.glob('uncommitted-qualification-*'))), 1)

    def test_upload_changed_after_preflight_hash_is_rejected_by_used_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, output, _, notebook = self.fixture(root)
            encoded = output/'qualification.zip.b64'
            decode, changed = base64.b64decode, []
            def mutate_then_decode(block, **kwargs):
                if not changed:
                    changed.append(True)
                    payload = bytearray(encoded.read_bytes())
                    payload[-100] = ord('A') if payload[-100] != ord('A') else ord('B')
                    encoded.write_bytes(payload)
                return decode(block, **kwargs)
            target = root/'working/never-published.zip'
            with patch('base64.b64decode', side_effect=mutate_then_decode), self.assertRaises(ValueError):
                self.bootstrap(notebook, encoded, target)
            self.assertFalse(target.exists())
            self.assertEqual(len(list(target.parent.glob('uncommitted-qualification-*'))), 1)

    def test_input_pins_and_notebook_layout_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, source, _, _, notebook = self.fixture(root, 5001)
            with self.assertRaises(ValueError):
                prepare(archive, '0'*64, source, sha(source), root/'wrong-archive')
            self.assertFalse((root/'wrong-archive').exists())
            with self.assertRaises(ValueError):
                prepare(archive, sha(archive), source, '0'*64, root/'wrong-notebook')
            self.assertFalse((root/'wrong-notebook').exists())
            value = notebook_fixture(sha(archive))
            value['cells'][1]['source'].append(BUNDLE_LINE+'\n')
            with self.assertRaises(ValueError):
                adapt_notebook(value, 'pass\n')
            value = notebook_fixture(sha(archive))
            value['metadata']['phase3']['final_dispatchable'] = True
            with self.assertRaises(ValueError):
                adapt_notebook(value, 'pass\n')
            self.assertEqual(notebook['metadata']['phase3']['upload_transport'], 'base64-exact-zip-v1')


if __name__ == '__main__':
    unittest.main()
