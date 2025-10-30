from __future__ import annotations
from fastapi import APIRouter, Query
from typing import Optional
from ..repositories.bars_repo import BarsRepo
from ..models.bars import BarView, BarsPage
from ..utils.pagination import encode_token, decode_token

router = APIRouter(prefix="/bars", tags=["bars"])
_repo = BarsRepo()

@router.get("", response_model=BarsPage)
def get_bars(
    instrument_id: str = Query(...),
    timeframe: str = Query(..., pattern="^(1m|5m|1h|1d)$"),
    start_ts: Optional[str] = Query(None),
    end_ts: Optional[str] = Query(None),
    page_size: int = Query(500, ge=1, le=5000),
    page_token: Optional[str] = Query(None),
):
    page_after = decode_token(page_token) if page_token else None
    df, next_ts = _repo.get_page(instrument_id, timeframe, start_ts, end_ts, page_size, page_after)
    items = [BarView(ts=r.ts.isoformat(), open=float(r.open), high=float(r.high),
                     low=float(r.low), close=float(r.close), volume=float(r.volume))
             for r in df.itertuples(index=False)]
    return BarsPage(items=items, next_page_token=(encode_token(next_ts) if next_ts else None))