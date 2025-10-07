from abc import ABC, abstractmethod
from ..events import MarketEvent


class Strategy(ABC):
    def __init__(self, data_handler, events):
        self.data = data_handler
        self.events = events

    @abstractmethod
    def on_market(self, event: MarketEvent): ...
