from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class EventType(Enum):
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"


@dataclass
class Event:
    dt: datetime


@dataclass
class MarketEvent(Event):
    symbol: str


@dataclass
class SignalEvent(Event):
    symbol: str
    direction: int
    strength: float = 1.0


@dataclass
class OrderEvent(Event):
    symbol: str
    order_type: str
    quantity: int
    direction: str


@dataclass
class FillEvent(Event):
    symbol: str
    quantity: int
    direction: str
    fill_price: float
    commission: float
    slippage: float = 0.0
