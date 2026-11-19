"""Deterministic fixed-capacity replay eviction primitives for amended studies."""
from __future__ import annotations

import numpy as np


def insert_with_eviction(memory: dict, x, labels, ids, teachers, width: int,
                         policy: str, next_order: int, capacity: int = 500) -> int:
    """Insert every proposal, applying FIFO or largest-class oldest eviction.

    `memory` uses the phase3.reference buffer arrays and adds `order` (uint64)
    and `next_order` (monotone insertion counter). Reservoir Algorithm R stays
    in the historical function and is not altered by this amended primitive.
    """
    if policy not in {'fifo', 'class_balanced'}:
        raise ValueError('policy must be fifo or class_balanced')
    if memory['size'] > capacity or memory['seen'] < memory['size']:
        raise ValueError('invalid buffer occupancy')
    if 'order' not in memory or memory['order'].shape != memory['ids'].shape or memory['order'].dtype != np.dtype('<u8'):
        raise ValueError('missing insertion-order state')
    for row, label, identifier, teacher in zip(x, labels, ids, teachers):
        size = memory['size']
        if size < capacity:
            slot = size
            memory['size'] += 1
        elif policy == 'fifo':
            slot = int(np.argmin(memory['order'][:size]))
        else:
            occupied, counts = np.unique(memory['y'][:size], return_counts=True)
            largest = int(occupied[np.flatnonzero(counts == counts.max())[0]])
            candidates = np.flatnonzero(memory['y'][:size] == largest)
            slot = int(candidates[np.argmin(memory['order'][candidates])])
        memory['x'][slot] = row
        memory['y'][slot] = label
        memory['ids'][slot] = identifier
        memory['z'][slot].fill(0)
        memory['z'][slot, :width] = teacher
        memory['width'][slot] = width
        memory['order'][slot] = next_order
        next_order += 1
        memory['seen'] += 1
    return next_order
