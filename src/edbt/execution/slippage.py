# src/edbt/execution/slippage.py
from __future__ import annotations
from typing import Literal

Side = Literal["BUY", "SELL"]

def fixed_bps(price: float, side: Side, bps: float) -> tuple[float, float]:
    """
    Simple symmetric slippage: price impact = price * bps/10000.
    Returns (exec_price, slip_per_share).
    """
    impact = price * (bps / 10_000.0)
    exec_price = price + impact if side == "BUY" else price - impact
    return exec_price, impact

def half_spread(price: float, side: Side, spread_bps: float) -> tuple[float, float]:
    """
    Cross the spread: pay/receive half-spread.
    """
    half = price * (spread_bps / 10_000.0) / 2.0
    exec_price = price + half if side == "BUY" else price - half
    return exec_price, half

def participation_bps(price: float, side: Side, qty: int, bar_volume: int,
                      base_bps: float = 1.0, max_participation: float = 0.1) -> tuple[float, float]:
    """
    Scale slippage with participation. If qty > max_participation * volume,
    increase bps proportionally.
    """
    if bar_volume <= 0 or qty <= 0:
        return price, 0.0
    participation = qty / float(bar_volume)
    factor = max(1.0, participation / max_participation)
    bps = base_bps * factor
    impact = price * (bps / 10_000.0)
    exec_price = price + impact if side == "BUY" else price - impact
    return exec_price, impact