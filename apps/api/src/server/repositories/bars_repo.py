from __future__ import annotations
from pathlib import Path
from typing import Iterator, Optional, Tuple, Dict
import pandas as pd
from ..server.config import BARS_ROOT

def bars_parquet_path(symbol: str, timeframe: str) -> Path:
    return BARS_ROOT / f"{symbol}_{timeframe}.parquet"

class BarsRepo:
    def get_page(self, symbol: str, timeframe: str, start_ts: Optional[str], end_ts: Optional[str],
                 page_size: int, page_after_ts: Optional[str]) -> Tuple[pd.DataFrame, Optional[str]]:
        p = bars_parquet_path(symbol, timeframe)
        if not p.exists():
            return pd.DataFrame(columns=["ts","open","high","low","close","volume"]), None

        df = pd.read_parquet(p)  # columns: ts (datetime64[ns, UTC]), OHLCV
        if start_ts: df = df[df["ts"] >= pd.Timestamp(start_ts, tz="UTC")]
        if end_ts:   df = df[df["ts"] <= pd.Timestamp(end_ts, tz="UTC")]
        if page_after_ts:
            df = df[df["ts"] > pd.Timestamp(page_after_ts, tz="UTC")]

        df = df.sort_values("ts").head(page_size + 1)
        next_token = None
        if len(df) > page_size:
            next_token = df.iloc[page_size]["ts"].isoformat()
            df = df.iloc[:page_size]
        return df, next_token