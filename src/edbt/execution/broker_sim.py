from .execution_handler import ExecutionHandler
from ..events import OrderEvent, FillEvent

class SimulatedBroker(ExecutionHandler):
    def __init__(self, events, data_handler, commission_per_share = 0.005, bps_slippage = 1):
        self.events = events
        self.data = data_handler
        self.commission = commission_per_share
        self.bps_slippage = bps_slippage

    def execute_order(self, order: OrderEvent):
        bar =  self.data.get_latest_bars(order.symbol, 1)[-1]
        base = bar.close
        slip = base * self.bps_slippage / 10000
        price = base + (slip if order.direction == "BUY" else -slip)
        commission = order.quantity * self.commission
        fill = FillEvent(
            dt = bar.dt, 
            symbol = order.symbol, 
            quantity = order.quantity,
            direction = order.direction,
            fill_price = price,
            commission = commission,
            slippage = slip
            )
        self.events.put(fill)