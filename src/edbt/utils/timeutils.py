# src/edbt/utils/timeutils.py
from __future__ import annotations
from datetime import datetime
from typing import Iterable
import numpy as np
import pandas as pd

UTC = "UTC"

def parse_dt(value) -> pd.Timestamp:
    """Parse strings/datetimes into tz-aware UTC timestamps."""
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize(UTC)
    else:
        ts = ts.tz_convert(UTC)
    return ts

def to_utc(ts: datetime | pd.Timestamp) -> pd.Timestamp:
    """Ensure a timestamp is tz-aware UTC."""
    return parse_dt(ts)

def to_tz(ts: datetime | pd.Timestamp, tz: str) -> pd.Timestamp:
    """Convert a timestamp to a target timezone."""
    return parse_dt(ts).tz_convert(tz)

def is_business_day(ts: datetime | pd.Timestamp) -> bool:
    """Weekday test (Mon–Fri). For exchange calendars, plug in a calendar later."""
    d = parse_dt(ts).date()
    return bool(np.is_busday(np.datetime64(d)))

def next_business_day(ts: datetime | pd.Timestamp, n: int = 1) -> pd.Timestamp:
    """Jump forward by n business days (Mon–Fri)."""
    t = parse_dt(ts)
    offset = pd.tseries.offsets.BusinessDay(n)
    return (t + offset)

def prev_business_day(ts: datetime | pd.Timestamp, n: int = 1) -> pd.Timestamp:
    """Jump backward by n business days (Mon–Fri)."""
    t = parse_dt(ts)
    offset = pd.tseries.offsets.BusinessDay(-n)
    return (t + offset)

def floor_to_day(ts: datetime | pd.Timestamp) -> pd.Timestamp:
    """Floor timestamp to 00:00 UTC of the same day."""
    return parse_dt(ts).normalize()

def ensure_sorted_unique_index(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by index and drop duplicate timestamps (keep first)."""
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame index must be DatetimeIndex")
    df = df.sort_index()
    return df[~df.index.duplicated(keep="first")]

def resample_equity_daily(equity: Iterable[tuple]) -> pd.Series:
    """Given (dt, equity), forward-fill to business days for stable daily metrics."""
    df = pd.DataFrame(equity, columns=["dt", "equity"]).set_index("dt").sort_index()
    df.index = pd.to_datetime(df.index, utc=True)
    # Resample to business days and ffill the last known equity
    daily = df["equity"].resample("B").ffill()
    return daily