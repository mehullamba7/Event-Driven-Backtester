# src/edbt/utils/enums.py
from __future__ import annotations
from enum import Enum

class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"

class SignalDir(Enum):
    SHORT = -1
    FLAT = 0
    LONG = 1

class OrderType(Enum):
    MKT = "MKT"
    LMT = "LMT"
    STOP = "STOP"

class AssetType(Enum):
    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"

def signal_to_side(direction: int | SignalDir) -> Side | None:
    """Map strategy direction (-1/0/+1) to broker side (SELL/None/BUY)."""
    if isinstance(direction, SignalDir):
        direction = direction.value
    if direction > 0:
        return Side.BUY
    if direction < 0:
        return Side.SELL
    return None