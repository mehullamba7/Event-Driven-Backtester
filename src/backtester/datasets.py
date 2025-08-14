from __future__ import annotations
import pandas as pd
import numpy as np

def make_synthetic_ticks(rows: int = 500_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ts = pd.date_range('2024-01-01', periods=rows, freq='ms')
    price = 100 + np.cumsum(rng.normal(0, 0.001, size=rows))
    size = rng.integers(1, 5, size=rows)
    side = rng.choice(['bid','ask'], size=rows)
    return pd.DataFrame({'ts': ts, 'price': price, 'size': size, 'side': side, 'symbol': 'SYN'})
