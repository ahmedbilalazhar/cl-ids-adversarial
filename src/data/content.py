"""Label-independent identities in the float32 feature space seen by models."""
from __future__ import annotations

import numpy as np


def feature_row_keys(features: np.ndarray) -> np.ndarray:
    rows = np.array(features, dtype=np.float32, order="C", copy=True)
    if rows.ndim != 2 or rows.shape[1] == 0:
        raise ValueError("feature rows must be a matrix with at least one column")
    if not np.isfinite(rows).all():
        raise ValueError("feature rows must be finite at model precision")
    rows[rows == 0] = 0.0
    width = rows.dtype.itemsize * rows.shape[1]
    return rows.view(f"V{width}").reshape(-1)
