"""Reject allocation bombs and altered NPZ encodings before loading arrays."""
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np

from phase3_delivery.archive_policy import check_archive_npz, check_npz
from phase3_delivery.io import MAX_JSON_BYTES


class ArchivePolicy(unittest.TestCase):
    def test_normal_numeric_npz_passes(self):
        payload = io.BytesIO()
        np.savez(payload, metadata=np.array('{}'), values=np.zeros((3, 74), dtype='<f4'))
        self.assertEqual(check_npz(io.BytesIO(payload.getvalue()), len(payload.getvalue()))['array_members'], 2)

    def test_shape_claiming_missing_bytes_rejected_without_allocation(self):
        array = io.BytesIO()
        np.lib.format.write_array_header_1_0(array, {'descr': '<f4', 'fortran_order': False, 'shape': (2**45,)})
        container = io.BytesIO()
        with zipfile.ZipFile(container, 'w') as archive:
            archive.writestr('huge.npy', array.getvalue())
        with self.assertRaises(ValueError):
            check_npz(io.BytesIO(container.getvalue()), len(container.getvalue()))

    def test_nested_compression_and_object_arrays_rejected(self):
        for writer, value in ((np.savez_compressed, np.zeros(5)), (np.savez, np.array([{}], dtype=object)),
                              (np.savez, np.zeros(2, dtype=[('nested', '<f4')]))):
            payload = io.BytesIO()
            writer(payload, values=value)
            with self.assertRaises(ValueError):
                check_npz(io.BytesIO(payload.getvalue()), len(payload.getvalue()))

    def test_oversized_json_rejected_before_handoff_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'oversized-json.zip'
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('synthetic-acceptance.json', b' '*(MAX_JSON_BYTES+1))
            with self.assertRaises(ValueError):
                check_archive_npz(path)


if __name__ == '__main__':
    unittest.main()
