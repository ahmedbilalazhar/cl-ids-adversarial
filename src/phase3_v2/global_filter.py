"""Deterministic Phase 2 global 75% low-loss admission baseline."""
from __future__ import annotations

import numpy as np

from src.phase3.common import array_identity


def choose_global_low_loss(data, scores):
    """Apply Phase 2 DG admission, with the shared unfiltered E1 prefix.

    Ranking is global across the client's labels (no class protection), with
    immutable record ID as the deterministic tie-break. The per-client scope
    avoids pooling private client records at the simulated server. Phase 2
    disables every admission filter in E1; the fixed 75% rule therefore starts
    at E2. This implements the unmatched DG arm, not volume-matched DM.
    """
    scores = np.asarray(scores)
    if scores.shape != (len(data.y),) or not np.issubdtype(scores.dtype, np.number) or not np.isfinite(scores).all():
        raise ValueError('Global-filter scores must be a finite vector aligned with current rows')
    if len(data.ids) != len(data.y) or len(data.owner) != len(data.y):
        raise ValueError('Global-filter input arrays are misaligned')

    accepted = []
    rows = []
    for client in range(5):
        indexes = np.flatnonzero(data.owner == client)
        count = len(indexes)
        if data.stage == 1:
            chosen = indexes
            filter_policy = 'bypass_e1'
        else:
            # Phase 2 specifies floor(0.75*n + 0.5), i.e. nearest integer
            # with exact half cases rounded upward.
            keep = (3 * count + 2) // 4
            ranked = indexes[np.lexsort((data.ids[indexes], scores[indexes]))]
            chosen = ranked[:keep]
            filter_policy = 'global_low_loss'
        chosen = np.sort(chosen).astype('<i8')
        accepted.append(chosen)

        classes = []
        for code in sorted(set(map(int, data.y[indexes]))):
            raw = int(np.count_nonzero(data.y[indexes] == code))
            admitted = int(np.count_nonzero(data.y[chosen] == code))
            classes.append({'source_code': code, 'raw': raw, 'admitted': admitted})
        rows.append({
            'client': client,
            'raw': count,
            'admitted': len(chosen),
            'filter_policy': filter_policy,
            'keep_fraction': [1, 1] if data.stage == 1 else [3, 4],
            'class_counts': classes,
            'admitted_ids_sha256': array_identity(data.ids[chosen]),
        })

    if not any(len(chosen) for chosen in accepted):
        raise ValueError('All-inactive stage')
    return accepted, rows
