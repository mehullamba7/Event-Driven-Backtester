from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Literal
from datetime import datetime
from .common import Timeframe

class StrategySpec(BaseModel):
    strategy_id: str
    version: str
    config: Dict

class CreateRunRequest(BaseModel):
    symbols: List[str]
    timeframe: Timeframe
    start_ts: datetime
    end_ts: datetime
    start_cash: float = 100_000
    seed: int = 42
    strategies: List[StrategySpec]
    engine_version: str

class CreateRunResponse(BaseModel):
    run_id: str
    status: Literal["queued","running","done","error"]

class RunStatusView(BaseModel):
    run_id: str
    status: str
    bars_total: int | None = None
    bars_processed: int | None = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_msg: Optional[str] = None