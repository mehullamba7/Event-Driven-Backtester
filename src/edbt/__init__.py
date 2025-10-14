"""Event-Driven Backtester (edbt)."""
__version__ = "0.1.0"

# Re-exports for convenience
from .backtest import Engine, equity_to_metrics
from .data import DataHandler, HistoricCSVDataHandler
from .execution import ExecutionHandler, SimulatedBroker
from .portfolio import Position, Portfolio
from .strategy import Strategy, SMACrossoverStrategy
from .utils import EventQueue

__all__ = [
    "__version__",
    "Engine", "equity_to_metrics",
    "DataHandler", "HistoricCSVDataHandler",
    "ExecutionHandler", "SimulatedBroker",
    "Position", "Portfolio",
    "Strategy", "SMACrossoverStrategy",
    "EventQueue",
]