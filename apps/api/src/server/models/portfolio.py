from __future__ import annotations
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class PositionView(BaseModel):
    instrument_id: str
    quantity: int
    avg_price: float
    mtm_price: float

class PortfolioSnapshotView(BaseModel):
    run_id: str
    ts: datetime
    cash: float
    equity: float
    positions: List[PositionView]
    exposures: Dict[str, float] = {}