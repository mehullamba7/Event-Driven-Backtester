from __future__ import annotations
from typing import List, Dict, TypedDict
import pandas as pd
from .bar_stream import Bar

class Signal(TypedDict):
    ts: pd.Timestamp
    instrument_id: str
    strategy_id: str
    direction: int          # -1, 0, +1
    strength: float

class SimpleSMACrossover:
    """
    Phase-1 built-in SMA crossover (short < long). Per-symbol state.
    """
    id = "sma_crossover"
    version = "1.0.0"

    def __init__(self, symbols: list[str], short: int, long: int):
        assert short < long
        self.symbols = symbols
        self.short = short
        self.long = long
        self.history: Dict[str, list[float]] = {s: [] for s in symbols}
        self.state_dir: Dict[str, int] = {s: 0 for s in symbols}  # -1/0/+1

    def on_bar(self, ts: pd.Timestamp, bars: Dict[str, "Bar"]) -> List[Signal]:
        sigs: List[Signal] = []
        for s, b in bars.items():
            h = self.history[s]
            h.append(b.close)
            if len(h) < self.long:  # warmup
                continue
            sma_s = sum(h[-self.short:]) / self.short
            sma_l = sum(h[-self.long:]) / self.long
            direction = 1 if sma_s > sma_l else -1
            if direction != self.state_dir[s]:
                self.state_dir[s] = direction
                sigs.append(Signal(ts=ts, instrument_id=s, strategy_id=self.id, direction=direction, strength=1.0))
        return sigs