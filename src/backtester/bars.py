from __future__ import annotations
import pandas as pd

def time_bars(df: pd.DataFrame, freq: str = "1min") -> pd.DataFrame:
    g = df.set_index('ts').sort_index()
    ohlcv = g['price'].resample(freq).ohlc()
    vol = g['size'].resample(freq).sum().rename('volume')
    return pd.concat([ohlcv, vol], axis=1).dropna(how='all')

def volume_bars(df: pd.DataFrame, vol_per_bar: float = 1_000.0) -> pd.DataFrame:
    df = df.sort_values('ts').copy()
    cum = df['size'].cumsum()
    bar_id = (cum // vol_per_bar).astype(int)
    o = df.groupby(bar_id).agg(
        ts=('ts','first'),
        open=('price','first'),
        high=('price','max'),
        low=('price','min'),
        close=('price','last'),
        volume=('size','sum'),
    )
    return o.reset_index(drop=True)

def tick_bars(df: pd.DataFrame, ticks_per_bar: int = 100) -> pd.DataFrame:
    df = df.sort_values('ts').copy()
    bar_id = (pd.RangeIndex(len(df)) // ticks_per_bar).astype(int)
    o = df.groupby(bar_id).agg(
        ts=('ts','first'),
        open=('price','first'),
        high=('price','max'),
        low=('price','min'),
        close=('price','last'),
        volume=('size','sum'),
    )
    return o.reset_index(drop=True)
