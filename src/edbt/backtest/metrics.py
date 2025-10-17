import numpy as np
import pandas as pd
from ..utils.timeutils import resample_equity_daily

def equity_to_metrics(equity_curve: list[tuple]) -> dict:
    """
    Convert (dt, equity) series to headline metrics.
    We forward-fill to business days to keep frequency consistent for Sharpe/DD.
    """
    if not equity_curve or len(equity_curve) < 2:
        return {"sharpe": 0.0, "max_drawdown": 0.0, "cagr": 0.0}

    daily = resample_equity_daily(equity_curve)
    if daily.size < 2:
        return {"sharpe": 0.0, "max_drawdown": 0.0, "cagr": 0.0}

    rets = daily.pct_change().dropna()
    if rets.empty or rets.std() == 0:
        sharpe = 0.0
    else:
        sharpe = (rets.mean() / (rets.std() + 1e-12)) * np.sqrt(252)

    roll_max = daily.cummax()
    drawdown = daily / roll_max - 1.0
    max_dd = float(drawdown.min())

    # CAGR using first/last daily equity points
    n_days = (daily.index[-1] - daily.index[0]).days or 1
    cagr = float((daily.iloc[-1] / daily.iloc[0]) ** (252 / n_days) - 1.0)

    return {"sharpe": float(sharpe), "max_drawdown": max_dd, "cagr": cagr}