from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict
from ..config import MAX_CONCURRENT_RUNS

_executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_RUNS)
_futures: Dict[str, Future] = {}

def submit(run_id: str, fn, *args, **kwargs) -> None:
    if run_id in _futures and not _futures[run_id].done():
        return
    _futures[run_id] = _executor.submit(fn, *args, **kwargs)

def status(run_id: str) -> str:
    f = _futures.get(run_id)
    if not f: return "unknown"
    if f.running(): return "running"
    if f.done():
        return "error" if f.exception() else "done"
    return "queued"