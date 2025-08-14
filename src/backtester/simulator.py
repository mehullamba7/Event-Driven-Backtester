from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List
from .events import OrderEvent, FillEvent
from .costs import CostModel

@dataclass
class SimpleSimulator:
    cost_model: CostModel

    def match(self, orders: Iterable[OrderEvent]) -> List[FillEvent]:
        fills = []
        for o in orders:
            px = o.limit_price if o.limit_price is not None else 0.0
            fee = self.cost_model.apply(px, o.qty)
            fills.append(FillEvent(ts_ns=o.ts_ns, symbol=o.symbol, qty=o.qty, price=px, fee=fee))
        return fills
