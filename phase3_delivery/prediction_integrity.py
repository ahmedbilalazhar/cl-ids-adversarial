"""Check saved development prediction structure and count marginals, no inference.

Returned files contain IDs and predictions, not reference labels. These checks
cannot reconstruct class-conditioned confusion cells or prove model inference.
They do establish the advertised bank, slot space and predicted-class totals.
"""
import io

import numpy as np

from scripts.audit_phase3_endpoints import matrix_counts, require
from src.phase3.common import array_identity

from .archive_policy import check_npz


def validate_predictions(payload, stage):
    """Validate one bounded NPZ against the independently registered count row."""
    check_npz(io.BytesIO(payload), len(payload))
    with np.load(io.BytesIO(payload), allow_pickle=False) as arrays:
        required = {'ids', 'predicted_slots', 'source_codes_in_slot_order'}
        require(len(arrays.files) == len(required) and set(arrays.files) == required,
                'Prediction array inventory differs')
        ids = arrays['ids']
        predicted = arrays['predicted_slots']
        slots = arrays['source_codes_in_slot_order']
    count = stage['full_seen_bank_rows']
    require(type(count) is int and count > 0, 'Prediction bank size must be a positive integer')
    require(ids.dtype == np.dtype('<u8') and ids.shape == (count,) and
            (ids[1:] > ids[:-1]).all(), 'Prediction IDs must be distinct canonical increasing uint64')
    require(array_identity(ids) == stage['bank_ids_sha256'], 'Prediction bank IDs differ from the reported bank')
    codes = stage['source_codes_in_slot_order']
    require(type(codes) is list and bool(codes) and all(type(code) is int and 0 <= code < 16 for code in codes) and
            len(set(codes)) == len(codes), 'Invalid reported prediction source codes')
    require(slots.dtype == np.dtype('<i2') and slots.shape == (len(codes),) and
            slots.tolist() == codes, 'Saved prediction source-code slot order differs')
    require(predicted.dtype == np.dtype('u1') and predicted.shape == (count,) and
            (predicted < len(slots)).all(), 'Invalid saved prediction slot indices')
    matrix = stage['full_seen_confusion_source_code_order']
    matrix_counts(matrix)  # Independently enforce shape, integer types and signs.
    columns = [sum(row[code] for row in matrix) for code in range(16)]
    totals = np.bincount(slots[predicted], minlength=16).tolist()
    require(totals == columns, 'Saved predictions disagree with confusion-column counts')
    return {'prediction_rows': count, 'bank_ids_sha256': stage['bank_ids_sha256'],
            'class_marginals_verified': True, 'reference_labels_accessed': False, 'new_inference': False}
