# src/edbt/backtest/logger.py
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Mapping

def get_logger(name: str = "edbt", level: int = logging.INFO, log_dir: str | Path | None = None) -> logging.Logger:
    """
    Create a structured logger. If log_dir is provided, also write to file.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(level)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    if log_dir:
        p = Path(log_dir)
        p.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(p / f"{name}.log", encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger

def log_json(logger: logging.Logger, event: str, payload: Mapping[str, Any], level: int = logging.INFO) -> None:
    """Emit a JSON line for downstream tools or quick grep."""
    line = json.dumps({"event": event, **payload}, default=str)
    logger.log(level, line)

# Convenience wrappers
def log_signal(logger: logging.Logger, dt, symbol: str, direction: int, strength: float = 1.0):
    log_json(logger, "signal", {"dt": dt, "symbol": symbol, "direction": direction, "strength": strength})

def log_order(logger: logging.Logger, order):
    log_json(logger, "order", {
        "dt": getattr(order, "dt", None),
        "symbol": getattr(order, "symbol", None),
        "qty": getattr(order, "quantity", None),
        "side": getattr(order, "direction", None),
        "type": getattr(order, "order_type", None),
    })

def log_fill(logger: logging.Logger, fill):
    log_json(logger, "fill", {
        "dt": getattr(fill, "dt", None),
        "symbol": getattr(fill, "symbol", None),
        "qty": getattr(fill, "quantity", None),
        "side": getattr(fill, "direction", None),
        "price": getattr(fill, "fill_price", None),
        "commission": getattr(fill, "commission", None),
        "slippage": getattr(fill, "slippage", None),
    })

def log_metrics(logger: logging.Logger, metrics: Mapping[str, Any]):
    log_json(logger, "metrics", metrics)