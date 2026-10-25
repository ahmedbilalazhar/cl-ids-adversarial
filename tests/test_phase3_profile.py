"""Concrete serialization and communication arithmetic; no network-performance claim."""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts.profile_phase3_v3 import communication, model_message, peak_working_set
from src.phase3.common import write_json


class CPUProfile(unittest.TestCase):
    def test_model_message_fp32_payload_roundtrip_and_value_independent_size(self):
        shapes = {'backbone.0.weight': (128, 74), 'backbone.0.bias': (128,),
                  'backbone.3.weight': (64, 128), 'backbone.3.bias': (64,),
                  'classifier.weight': (16, 64), 'classifier.bias': (16,)}
        arrays = {k: np.zeros(shape, dtype='<f4') for k, shape in shapes.items()}
        metadata = {'schema': 'fixture', 'slots': list(range(16))}
        raw, payload = model_message(arrays, metadata)
        # Independently count linear weights/biases for74->128->64->16.
        self.assertEqual(raw, (74*128+128+128*64+64+64*16+16)*4)
        self.assertEqual(raw, 75584)
        self.assertGreater(len(payload), raw)
        with np.load(io.BytesIO(payload), allow_pickle=False) as f:
            self.assertEqual(json.loads(str(f['metadata'])), metadata)
            self.assertEqual(set(f.files), set(arrays)|{'metadata'})
            for k, a in arrays.items():
                np.testing.assert_array_equal(f[k], a)
        _, changed = model_message({k: a+np.float32(7) for k, a in arrays.items()}, metadata)
        self.assertEqual(len(payload), len(changed))
        for bad in ({}, {'x': np.zeros(3, dtype='f8')}, {'x': np.array([float('nan')], dtype='f4')}, {'x': np.array(['x'], dtype=object)}):
            with self.assertRaises(ValueError):
                model_message(bad, metadata)

    def test_logical_active_all_client_and_anchor_counts(self):
        widths = [3, 8, 13, 16]
        rows = [{'kind': 'round', 'stage': stage, 'round': round_id,
                 'clients': [{'client': i, 'inactive': i in (2, 4)} for i in range(5)]}
                for stage in range(1, 5) for round_id in range(1, 4)]
        result = {'settings': {'learner': 'EI'}, 'ledger': rows,
                  'checkpoints': [{'stage': s, 'stage_end': True, 'file': f'E{s}-R3.npz'} for s in range(1, 5)]}

        def transaction(path):
            width = widths[int(path.name[1])-1]
            return {'slots': list(range(width))}, {'model.w': np.zeros((width, 2), dtype='f4'), 'model.b': np.zeros(width, dtype='f4')}, None
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            write_json(folder/'run.json', result)
            with patch('src.phase3_v2.checkpoint.read_transaction', side_effect=transaction):
                measured = communication(folder)['totals']
        # Sum widths40 * three scalars per output * four bytes =480 per stage-set.
        self.assertEqual(measured['active_only_downlink_raw'], 3*3*480)
        self.assertEqual(measured['active_uplink_raw'], 4320)
        self.assertEqual(measured['all_five_downlink_raw'], 5*3*480)
        self.assertEqual(measured['potential_EI_final_anchor_downlink_raw'], 5*480)
        self.assertGreater(measured['active_only_downlink_serialized'], measured['active_only_downlink_raw'])

    def test_memory_availability_is_explicit(self):
        observed = peak_working_set()
        self.assertIn(observed['status'], ('measured', 'unavailable'))
        if observed['status'] == 'measured':
            self.assertGreater(observed['peak_working_set_bytes'], 0)
            self.assertGreaterEqual(observed['peak_working_set_bytes'], observed['working_set_bytes_at_readout'])
        else:
            self.assertNotIn('peak_working_set_bytes', observed)


if __name__ == '__main__':
    unittest.main()
