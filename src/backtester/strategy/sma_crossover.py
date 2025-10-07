import numpy as np
from .strategy import Strategy
from ..events import SignalEvent
from ..events import MarketEvent

class SMACrossoverStrategy(Strategy):
    def __init__(self, data_handler, events, symbol, short = 50, long = 200):
        super().__init__(data_handler, events)
        if not short < long:
            raise ValueError("short must be less than long")
        self.symbol = symbol
        self.short = short
        self.long = long
        self.short_sma = None
        self.long_sma = None
        self.in_market = 0 # -1, 0, 1
       
    def on_market(self, event: MarketEvent):
        if event.symbol != self.symbol:
            return
        bars = self.data.get_latest_bars(self.symbol, N = self.long)
        if len(bars) < self.long:
            return
        closes = np.array([b.close for b in bars], dtype=float)
        sma_s = closes[-self.short:].mean()
        sma_l = closes.mean()
        direction = 1 if sma_s > sma_l else -1
        if direction != self.in_market:
            self.in_market = direction
            self.events.put(SignalEvent(dt = event.dt, symbol = self.symbol, direction = direction))
