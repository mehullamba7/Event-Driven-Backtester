from __future__ import annotations
from typing import Dict, List, TypedDict
import pandas as pd
from .bar_stream import Bar

class Order(TypedDict):
    ts: pd.Timestamp
    instrument_id: str
    side: str            # "BUY"/"SELL"
    quantity: int
    strategy_id: str

class Fill(TypedDict):
    ts: pd.Timestamp
    instrument_id: str
    side: str
    quantity: int
    price: float
    commission: float
    slippage: float
    strategy_id: str

class PortfolioSnapshot(TypedDict):
    ts: pd.Timestamp
    cash: float
    equity: float
    positions: Dict[str, Dict[str, float]]  # symbol -> {quantity, avg_price, mtm_price}

class PortfolioEngine:
    def __init__(self, start_cash: float, risk_per_trade: float = 0.01, per_share_fee: float = 0.005, slip_bps: float = 1.0):
        self.cash: float = float(start_cash)
        self.positions: Dict[str, Dict[str, float]] = {}  # symbol -> {quantity, avg_price}
        self.risk_per_trade = risk_per_trade
        self.per_share_fee = per_share_fee
        self.slip_bps = slip_bps

    def _price_with_slippage(self, mid: float, side: str) -> tuple[float, float]:
        impact = mid * (self.slip_bps / 10_000.0)
        px = mid + impact if side == "BUY" else mid - impact
        return px, impact

    def on_signals(self, ts: pd.Timestamp, bars: Dict[str, "Bar"], signals: List[dict]) -> List[Order]:
        orders: List[Order] = []
        for sig in signals:
            s = sig["instrument_id"]
            side = "BUY" if sig["direction"] > 0 else "SELL"
            mid = bars[s].close
            # dollars at risk
            dollars = max(self.cash * self.risk_per_trade, 0.0)
            qty = int(dollars // mid)
            if qty <= 0:
                continue
            orders.append(Order(ts=ts, instrument_id=s, side=side, quantity=qty, strategy_id=sig["strategy_id"]))
        return orders

    def on_orders(self, ts: pd.Timestamp, bars: Dict[str, "Bar"], orders: List[Order]) -> List[Fill]:
        fills: List[Fill] = []
        for o in orders:
            mid = bars[o["instrument_id"]].close
            px, slip = self._price_with_slippage(mid, o["side"])
            commission = abs(o["quantity"]) * self.per_share_fee
            fills.append(Fill(ts=ts, instrument_id=o["instrument_id"], side=o["side"],
                              quantity=o["quantity"], price=float(px),
                              commission=float(commission), slippage=float(slip),
                              strategy_id=o["strategy_id"]))
        return fills

    def on_fills(self, fills: List[Fill]) -> None:
        for f in fills:
            pos = self.positions.setdefault(f["instrument_id"], {"quantity": 0, "avg_price": 0.0})
            qty = pos["quantity"]
            if f["side"] == "BUY":
                new_qty = qty + f["quantity"]
                pos["avg_price"] = ((pos["avg_price"] * qty) + (f["price"] * f["quantity"])) / max(new_qty, 1)
                pos["quantity"] = new_qty
                self.cash -= (f["price"] * f["quantity"] + f["commission"] + f["slippage"])
            else:
                pos["quantity"] = qty - f["quantity"]
                self.cash += (f["price"] * f["quantity"] - f["commission"] - f["slippage"])
                if pos["quantity"] == 0:
                    pos["avg_price"] = 0.0

    def snapshot(self, ts: pd.Timestamp, bars: Dict[str, "Bar"]) -> PortfolioSnapshot:
        equity = self.cash
        out = {}
        for s, p in self.positions.items():
            mtm = bars[s].close if s in bars else 0.0
            equity += p["quantity"] * mtm
            out[s] = {"quantity": int(p["quantity"]), "avg_price": float(p["avg_price"]), "mtm_price": float(mtm)}
        return {"ts": ts, "cash": float(self.cash), "equity": float(equity), "positions": out}