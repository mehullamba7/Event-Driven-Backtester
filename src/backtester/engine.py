from __future__ import annotations
from collections import deque
from typing import Callable, Deque
from .events import MarketDataEvent, SignalEvent, OrderEvent, FillEvent
from .simulator import SimpleSimulator

class Engine:
    def __init__(self, simulator: SimpleSimulator):
        self.sim = simulator
        self.market_q: Deque[MarketDataEvent] = deque()
        self.signal_q: Deque[SignalEvent] = deque()
        self.order_q: Deque[OrderEvent] = deque()
        self.fill_q: Deque[FillEvent] = deque()

    def on_market(self, handler: Callable[[MarketDataEvent], None]):
        self._on_market = handler

    def on_signal(self, handler: Callable[[SignalEvent], None]):
        self._on_signal = handler

    def on_order(self, handler: Callable[[OrderEvent], None]):
        self._on_order = handler

    def pump(self):
        while self.market_q:
            ev = self.market_q.popleft()
            if hasattr(self, "_on_market"):
                self._on_market(ev)
        while self.signal_q:
            sv = self.signal_q.popleft()
            if hasattr(self, "_on_signal"):
                self._on_signal(sv)
        if self.order_q:
            fills = self.sim.match(self.order_q)
            self.order_q.clear()
            self.fill_q.extend(fills)
