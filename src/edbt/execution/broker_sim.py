from .execution_handler import ExecutionHandler
from ..events import OrderEvent, FillEvent
from .slippage import fixed_bps
from .fees import per_share
from ..backtest.logger import log_fill, get_logger

class SimulatedBroker(ExecutionHandler):
    def __init__(self, events, data_handler, commission_per_share = 0.005, bps_slippage = 1, logger = None):
        self.events = events
        self.data = data_handler
        self.commission = commission_per_share
        self.bps_slippage = bps_slippage
        self.logger = logger or get_logger("edbt.execution")

    def execute_order(self, order: OrderEvent):
        bar = self.data.get_latest_bars(order.symbol, 1)
        if not bar:
            return
        bar = bar[-1]
        ref_price = float(bar.close)

        # Slippage model (returns (exec_price, slip_per_share))
        exec_price, slip_per_share = fixed_bps(ref_price, order.direction, self.bps_slippage)

        # Fee model (per-share commission)
        commission = per_share(order.quantity, rate=self.commission, min_fee=0.0)

        fill = FillEvent(
            dt=bar.dt,
            symbol=order.symbol,
            quantity=order.quantity,
            direction=order.direction,    # "BUY" | "SELL"
            fill_price=exec_price,
            commission=commission,
            slippage=slip_per_share,      # per-share slip recorded for transparency
        )
        self.events.put(fill)
        log_fill(self.logger, fill)