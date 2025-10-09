import numpy as np
import pandas as pd

def equity_to_metrics(equity_curve):
    df = pd.DataFrame(equity_curve, columns=["dt", "equity"]).set_index("dt")
    rets = df["equity"].pct_change().dropna()
    sharpe = (rets.mean() / (rets.std()+ 1e-12)) * np.sqrt(252)
    roll_max = df["equity"].cummax()
    drawdown = df["equity"] / roll_max - 1
    max_dd = drawdown.min()
    days = (df.index[-1] - df.index[0]).days or 1
    cagr = (df["equity"].iloc[-1] / df["equity"].iloc[0]) ** (252 / days) - 1
    return {
        "sharpe": float(sharpe),
        "max_drawdown": float(max_dd),
        "cagr": float(cagr)
    }