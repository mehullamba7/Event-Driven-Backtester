from collections import defaultdict
from .position import Position
from ..events import SignalEvent, OrderEvent, FillEvent
from ..utils.enums import signal_to_side
from ..portfolio.risk import dollars_to_qty, clamp_qty, clamp_notional
from ..backtest.logger import get_logger, log_order, log_fill

class Portfolio:
    def __init__(
        self,
        events,
        data_handler,
        starting_cash: float = 100_000.0,
        risk_per_trade: float = 0.01,
        max_qty: int | None = None,
        max_notional: float | None = None,
        logger=None,
    ):
        # Shared handles
        self.events = events
        self.data = data_handler

        # Account state
        self.cash: float = float(starting_cash)
        self.holdings = defaultdict(lambda: Position(symbol=""))
        self.equity_curve: list[tuple] = []

        # Risk/sizing controls
        self.risk_per_trade = float(risk_per_trade)
        self.max_qty = max_qty
        self.max_notional = max_notional

        # Logger
        self.logger = logger or get_logger("edbt.portfolio")

    def _latest_price(self, symbol: str) -> float | None:
        bar = self.data.get_latest_bars(symbol, 1)
        if not bar:
            return None
        return float(bar[-1].close)
    
    def _compute_equity(self, symbol: str) -> float:
        #cash plus unrelasied stock holdings
        equity = self.cash
        for sym, p in self.holdings.items():
            if p.quantity != 0:
                price = self._latest_price(sym)
                if price is not None:
                    equity += p.quantity * price
        return equity
    
    def mark_to_market(self, dt):
        """Record equity snapshot at time dt (call once per bar step)."""
        equity = self._compute_equity()
        self.equity_curve.append((dt, equity))

    def on_signal(self, event: SignalEvent):
        side = signal_to_side(event.direction)  # BUY/SELL/None
        if side is None:
            return  # flat signals ignored in this basic portfolio

        price = self._latest_price(event.symbol)
        if price is None or price <= 0:
            return

        # Budget (dollars) and quantity
        risk_dollars = max(self.cash * self.risk_per_trade, 0.0)
        qty = dollars_to_qty(price, risk_dollars, lot_size=1, min_qty=1)
        qty = clamp_qty(qty, self.max_qty)
        qty = clamp_notional(qty, price, self.max_notional)
        if qty <= 0:
            return

        order = OrderEvent(
            dt=event.dt,
            symbol=event.symbol,
            order_type="MKT",
            quantity=qty,
            direction=side.value,   # "BUY" or "SELL"
        )
        self.events.put(order)
        log_order(self.logger, order)
    
    def on_fill(self, event: FillEvent):
        # 1) Fetch or initialize position for this symbol
        pos = self.holdings[event.symbol]
        if pos.symbol == "":
            pos.symbol = event.symbol

        # 2) Signed quantity: buys are +, sells are -
        signed_qty = event.quantity if event.direction == "BUY" else -event.quantity

        # 3) Transaction costs
        total_fees = float(event.commission) + float(event.slippage)
        trade_cash_flow = event.fill_price * event.quantity

        if signed_qty > 0:
            # BUY: update VWAP-style avg price and quantity
            new_qty = pos.quantity + signed_qty
            pos.avg_price = (
                (pos.avg_price * pos.quantity) + (event.fill_price * event.quantity)
            ) / max(new_qty, 1)
            pos.quantity = new_qty
            # Deduct cash (price*qty + fees)
            self.cash -= (trade_cash_flow + total_fees)
        else:
            # SELL: reduce quantity; add cash proceeds minus fees
            pos.quantity += signed_qty  # signed_qty is negative here
            self.cash += (trade_cash_flow - total_fees)

            # Optional: if flat, you may reset avg_price to 0.0
            if pos.quantity == 0:
                pos.avg_price = 0.0
        
        # 4) Mark-to-market total equity (cash + sum of positions @ latest price)
        # Record equity at fill time
        eq = self._compute_equity()
        self.equity_curve.append((event.dt, eq))

        # Log
        log_fill(self.logger, event)