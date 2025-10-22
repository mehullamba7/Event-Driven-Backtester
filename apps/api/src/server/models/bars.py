from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from .common import PageMeta

class BarView(BaseModel):
    ts: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class BarsPage(BaseModel):
    items: List[BarView]
    next_page_token: Optional[str] = None