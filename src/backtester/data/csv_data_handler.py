import pandas as pd
from collections import deque
from pathlib import Path
from datetime import datetime
from .data_handler import DataHandler
from ..events import MarketEvent

class HistoricCSVDataHandler(DataHandler):
    def __init__(self, symbols, events, csv_dir):
        super().__init__(symbols, events)
        self.csv_dir = Path(csv_dir)
        self.symbol_data = {}
        self.latest_symbol_data = {s: deque(maxlen=1000) for s in symbols}
        for s in symbols:
            df = pd.read_csv(self.csv_dir / f"{s}.csv", parse_dates=[0])
            df.columns = ["dt","open","high","low","close","volume"][:len(df.columns)]
            df.sort_values("dt", inplace=True)
            self.symbol_data[s] = df.itertuples(index=False, name="Bar")

    def get_latest_bars(self, symbol, N=1):
        d = list(self.latest_symbol_data[symbol])
        return d[-N:]

    def update_bars(self):
        any_data = False
        for s in self.symbols:
            try:
                bar = next(self.symbol_data[s])
                self.latest_symbol_data[s].append(bar)
                self.events.put(MarketEvent(dt=bar.dt, symbol=s))
                any_data = True
            except StopIteration:
                continue
        if not any_data:
            self.continue_backtest = False