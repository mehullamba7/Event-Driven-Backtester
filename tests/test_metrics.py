import pandas as pd
import numpy as np
from backtester.metrics import sharpe, drawdown

def test_metrics_basic():
    r = pd.Series(np.random.normal(0.001, 0.01, size=1000))
    s = sharpe(r)
    assert isinstance(s, float)
    eq = (1 + r).cumprod()
    dd = drawdown(eq)
    assert dd.min() <= 0
