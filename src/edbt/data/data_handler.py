from abc import ABC, abstractmethod


class DataHandler(ABC):
    def __init__(self, symbols, events):
        self.symbols = symbols
        self.events = events
        self.continue_backtest = True

    @abstractmethod
    def get_latest_bars(self, symbol, N=1): ...
    @abstractmethod
    def update_bars(self): ...
