from dataclasses import dataclass

@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0