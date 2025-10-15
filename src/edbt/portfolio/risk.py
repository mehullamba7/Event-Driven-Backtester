# src/edbt/portfolio/risk.py
from __future__ import annotations

def dollars_to_qty(price: float, dollars: float, lot_size: int = 1, min_qty: int = 1) -> int:
    """Convert a dollar budget to whole-lot quantity."""
    if price <= 0:
        return 0
    raw = int(dollars // price)
    # round down to lot size and enforce minimum
    q = (raw // lot_size) * lot_size
    return max(q, 0 if min_qty <= 0 else min_qty if q > 0 else 0)

def clamp_qty(qty: int, max_qty: int | None = None) -> int:
    """Cap absolute quantity to a maximum (if provided)."""
    if max_qty is None:
        return qty
    sign = 1 if qty >= 0 else -1
    return sign * min(abs(qty), max_qty)

def clamp_notional(qty: int, price: float, max_notional: float | None = None) -> int:
    """Reduce quantity if position notional would exceed a cap."""
    if max_notional is None or price <= 0:
        return qty
    max_qty = int(max_notional // price)
    sign = 1 if qty >= 0 else -1
    return sign * min(abs(qty), max_qty)

def target_vol_qty(equity: float, price: float, sigma: float, target_vol: float) -> int:
    """
    Volatility targeting: set qty so that position contribution ~ target_vol of equity.
    Roughly: weight = target_vol / sigma ; dollars = equity * weight.
    """
    if sigma <= 0 or price <= 0 or equity <= 0:
        return 0
    dollars = equity * (target_vol / sigma)
    return int(dollars // price)

def pct_stop(entry_price: float, pct: float, side: str) -> float:
    """Return a stop price 'pct' away from entry. side='BUY' or 'SELL'."""
    if side.upper() == "BUY":
        return entry_price * (1 - abs(pct))
    else:
        return entry_price * (1 + abs(pct))

def atr_stop(entry_price: float, atr: float, k: float, side: str) -> float:
    """ATR-based stop: k * ATR away from entry."""
    if side.upper() == "BUY":
        return entry_price - k * atr
    else:
        return entry_price + k * atr