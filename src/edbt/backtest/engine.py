from ..utils.queue import EventQueue
from ..events import MarketEvent, SignalEvent, OrderEvent, FillEvent
from .logger import get_logger

class Engine:
    def __init__(self, data, strategy, portfolio, execution, logger=None):
        # Engine owns a queue by default; you can override from outside.
        self.events = EventQueue()
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution = execution
        self.logger = logger or get_logger("edbt.engine")

    def run(self):
        """
        Main event loop: step data, drain events, mark-to-market once per step.
        """
        while True:
            # 1) Advance data: enqueue MarketEvents
            self.data.update_bars()

            # 2) Drain events generated this step
            step_dt = None
            while not self.events.empty():
                ev = self.events.get_nowait()
                if ev is None:
                    break

                if isinstance(ev, MarketEvent):
                    # Keep the latest dt we saw this step (for mark-to-market)
                    step_dt = ev.dt if step_dt is None or ev.dt > step_dt else step_dt
                    self.strategy.on_market(ev)

                elif isinstance(ev, SignalEvent):
                    self.portfolio.on_signal(ev)

                elif isinstance(ev, OrderEvent):
                    self.execution.execute_order(ev)

                elif isinstance(ev, FillEvent):
                    self.portfolio.on_fill(ev)

            # 3) After processing the step, record equity snapshot once
            if step_dt is not None:
                self.portfolio.mark_to_market(step_dt)

            # 4) Exit when data exhausted AND queue has nothing left
            if not self.data.continue_backtest and self.events.empty():
                break