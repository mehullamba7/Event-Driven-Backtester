# examples/run_sma.py
from pathlib import Path
import sys

# 1) Make 'src' importable for local dev without installation
ROOT = Path(__file__).resolve().parents[1]         # repo root
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# 2) Normal imports from your package under src/edbt
from edbt.utils.queue import EventQueue
from edbt.data.csv_data_handler import HistoricCSVDataHandler
from edbt.strategy.sma_crossover import SMACrossoverStrategy
from edbt.portfolio.portfolio import Portfolio
from edbt.execution.broker_sim import SimulatedBroker
from edbt.backtest.engine import Engine
from edbt.backtest.metrics import equity_to_metrics
from edbt.backtest.logger import get_logger

# 3) Create synthetic CSV if real data is missing
def ensure_synthetic_csv(symbol: str = "SPY", n_days: int = 300):
    import numpy as np
    import pandas as pd

    data_dir = ROOT / "examples" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_path = data_dir / f"{symbol}.csv"
    if csv_path.exists():
        return csv_path

    # simple geometric random walk with mild drift/vol
    rng = np.random.default_rng(42)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n_days)
    ret = rng.normal(loc=0.0005, scale=0.01, size=n_days)   # ~0.05% avg daily, 1% vol
    price = 100.0 * (1 + ret).cumprod()

    # make OHLCV around close
    close = price
    open_ = close * (1 + rng.normal(0, 0.002, n_days))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.003, n_days)))
    low  = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.003, n_days)))
    vol  = rng.integers(1_000_000, 3_000_000, n_days)

    df = pd.DataFrame({
        "dt": dates,
        "open": open_.round(4),
        "high": high.round(4),
        "low": low.round(4),
        "close": close.round(4),
        "volume": vol
    })
    df.to_csv(csv_path, index=False)
    return csv_path

if __name__ == "__main__":
    SYMBOL = "SPY"
    csv_path = ensure_synthetic_csv(SYMBOL)  # creates examples/data/SPY.csv if missing
    logger = get_logger("edbt.backtest")
    # Shared event queue
    events = EventQueue()

    # Wire components
    data = HistoricCSVDataHandler([SYMBOL], events, csv_dir=str(csv_path.parent))
    strat = SMACrossoverStrategy(data, events, symbol=SYMBOL, short=50, long=200)
    port = Portfolio(events, data, starting_cash=100_000, risk_per_trade=0.01, logger=logger)
    broker = SimulatedBroker(events, data, logger=logger, commission_per_share=0.005, bps_slippage=1)

    engine = Engine(data, strat, port, broker, logger)
    engine.events = events  # share the same queue instance
    engine.run()

    print(equity_to_metrics(port.equity_curve))