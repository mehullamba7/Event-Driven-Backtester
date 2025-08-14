from __future__ import annotations
import numpy as np

def purged_walk_forward_split(n: int, n_splits: int, embargo: int = 0):
    fold = n // n_splits
    for i in range(n_splits):
        start = i * fold
        end = (i + 1) * fold if i < n_splits - 1 else n
        test_idx = np.arange(start, end)
        train_idx = np.setdiff1d(np.arange(n), np.arange(max(0, start - embargo), min(n, end + embargo)))
        yield train_idx, test_idx
