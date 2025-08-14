from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class MarketDataEvent:
    ts_ns: int
    symbol: str
    price: float
    size: float
    side: str  # 'bid' or 'ask'

@dataclass(frozen=True)
class SignalEvent:
    ts_ns: int
    symbol: str
    signal: float  # e.g., z-score or signed strength

@dataclass(frozen=True)
class OrderEvent:
    ts_ns: int
    symbol: str
    qty: int
    side: str  # 'buy' or 'sell'
    limit_price: Optional[float] = None

@dataclass(frozen=True)
class FillEvent:
    ts_ns: int
    symbol: str
    qty: int
    price: float
    fee: float = 0.0
