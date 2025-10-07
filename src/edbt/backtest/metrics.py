import numpy as np
import pandas as pd


def sharpe(returns: pd.Series, risk_free: float = 0.0) -> float:
    r = returns - risk_free
    if r.std(ddof=1) == 0:
        return 0.0
    return np.sqrt(252) * r.mean() / r.std(ddof=1)


def drawdown(equity: pd.Series) -> pd.Series:
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return dd


def turnover(trades: pd.Series, equity: pd.Series) -> float:
    return trades.abs().sum() / equity.iloc[0]
