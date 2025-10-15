# src/edbt/execution/fees.py
from __future__ import annotations

def per_share(quantity: int, rate: float = 0.005, min_fee: float = 0.0) -> float:
    """
    Commission = rate * shares, with an optional minimum per order.
    """
    fee = abs(quantity) * float(rate)
    return max(fee, float(min_fee))

def percentage_notional(price: float, quantity: int, rate_bps: float = 1.0, min_fee: float = 0.0) -> float:
    """
    Commission = notional * (bps/10000), with optional minimum.
    """
    notional = abs(quantity) * float(price)
    fee = notional * (rate_bps / 10_000.0)
    return max(fee, float(min_fee))

def combined(price: float, quantity: int,
             per_share_rate: float = 0.0, percent_bps: float = 0.0, min_fee: float = 0.0) -> float:
    """
    Combine per-share and percentage components, apply a single minimum.
    """
    fee_ps = per_share(quantity, rate=per_share_rate, min_fee=0.0)
    fee_pct = percentage_notional(price, quantity, rate_bps=percent_bps, min_fee=0.0)
    return max(fee_ps + fee_pct, float(min_fee))