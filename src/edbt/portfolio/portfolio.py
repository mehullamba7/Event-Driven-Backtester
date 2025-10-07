from collections import defaultdict
from .position import Position
from ..events import SignalEvent, OrderEvent, FillEvent

class Portfolio:
    def __init__(self, events, data_handler, starting_cash = 100_000, risk_per_trade = 0.01):
        self.events = events
        self.data = data_handler
        self.cash = starting_cash
        self.holdings = defaultdict(lambda: Position(symbol = ""))
        self.equity_curve = []
        self.risk_per_trade = risk_per_trade

    def on_signal(self, event: SignalEvent):
        # 1) Get the most recent close to price the order
        bar = self.data.get_latest_bars(event.symbol, 1)
        if not bar:
            return
        price = float(bar[-1].close)

        # 2) Dollar risk budget = fraction of current cash
        risk_dollars = self.cash * self.risk_per_trade

        # 3) Convert dollars to whole-share quantity (never 0)
        qty = max(int(risk_dollars // max(price, 1e-12)), 1)

        # 4) Map direction to BUY/SELL
        direction = "BUY" if event.direction > 0 else "SELL"

        # 5) Emit an OrderEvent; execution will turn it into a FillEvent
        order = OrderEvent(
            dt=event.dt,
            symbol=event.symbol,
            order_type="MKT",
            quantity=qty,
            direction=direction,
        )
        self.events.put(order)
    
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
        equity = self.cash
        for sym, p in self.holdings.items():
            if p.quantity != 0:
                last_bar = self.data.get_latest_bars(sym, 1)
                if last_bar:
                    equity += p.quantity * float(last_bar[-1].close)
        self.equity_curve.append((event.dt, float(equity)))