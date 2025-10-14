"""Strategies & base strategy interface."""
from .strategy import Strategy
from .sma_crossover import SMACrossoverStrategy

__all__ = ["Strategy", "SMACrossoverStrategy"]