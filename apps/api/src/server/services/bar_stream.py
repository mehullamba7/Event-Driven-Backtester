from __future__ import annotations
from typing import Iterator, Dict, NamedTuple
import pandas as pd
from ..repositories.bars_repo import BarsRepo

class Bar(NamedTuple):
    ts: pd.Timestamp
    open: float; high: float; low: float; close: float; volume: float

class BarStream:
    """
    Yields (ts, {symbol: Bar}) with INTERSECTION alignment across symbols.
    For Phase-1 we read all bars in-memory for the window (dev-scale).
    """
    def __init__(self, bars_repo: BarsRepo, symbols: list[str], timeframe: str, start_ts: str, end_ts: str):
        self.bars_repo = bars_repo
        self.symbols = symbols
        self.timeframe = timeframe
        self.start_ts = start_ts
        self.end_ts = end_ts

    def __iter__(self) -> Iterator[tuple[pd.Timestamp, Dict[str, Bar]]]:
        frames = {}
        for s in self.symbols:
            df, _ = self.bars_repo.get_page(s, self.timeframe, self.start_ts, self.end_ts, page_size=10_000_000, page_after_ts=None)
            df = df[["ts","open","high","low","close","volume"]].dropna().copy()
            df["ts"] = pd.to_datetime(df["ts"], utc=True)
            df.set_index("ts", inplace=True)
            frames[s] = df
        # intersection of timestamps
        common_index = None
        for s, df in frames.items():
            common_index = df.index if common_index is None else common_index.intersection(df.index)
        if common_index is None:
            return
        for ts in common_index:
            out = {}
            for s, df in frames.items():
                row = df.loc[ts]
                out[s] = Bar(ts=ts, open=float(row.open), high=float(row.high), low=float(row.low),
                             close=float(row.close), volume=float(row.volume))
            yield ts, out