from ..utils.queue import EventQueue
from ..events import MarketEvent, SignalEvent, OrderEvent, FillEvent

class Engine:
    def __init__(self, data, strategy, portfolio, execution):
        self.events = EventQueue()
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution = execution

    def run(self):
        while True:
            # Step 1: advance data -> push MarketEvents
            self.data.update_bars()
            if not self.data.continue_backtest:
                break

            # Step 2: drain and route all events for this step
            while not self.events.empty():
                ev = self.events.get_nowait()
                if ev is None:
                    break
                if isinstance(ev, MarketEvent):
                    self.strategy.on_market(ev)
                elif isinstance(ev, SignalEvent):
                    self.portfolio.on_signal(ev)
                elif isinstance(ev, OrderEvent):
                    self.execution.execute_order(ev)
                elif isinstance(ev, FillEvent):
                    self.portfolio.on_fill(ev)