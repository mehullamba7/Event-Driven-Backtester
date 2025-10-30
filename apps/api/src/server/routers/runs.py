from __future__ import annotations
from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
from ..models.runs import CreateRunRequest, CreateRunResponse, RunStatusView
from ..repositories.runs_repo import RunsRepo
from ..jobs.executor import submit
from ..jobs.tasks import compute_replay
from ..services.run_manager import RunManager
from ..utils.idempotency import run_hash

router = APIRouter(prefix="/runs", tags=["runs"])
_runs = RunsRepo()
_mgr = RunManager()

@router.post("/compute/replay", response_model=CreateRunResponse, status_code=202)
def post_replay(req: CreateRunRequest):
    payload = req.model_dump()
    # idempotency: hash payload
    key = run_hash(payload)
    # naive dedupe: reuse key as run_id? keep uuid to avoid collision; store hash if you expand schema later.
    run_id = _mgr.create_run(payload)
    submit(run_id, compute_replay, run_id, payload)
    return CreateRunResponse(run_id=run_id, status="queued")

@router.get("/{run_id}/status", response_model=RunStatusView)
def get_status(run_id: str):
    row = _runs.get(run_id)
    if not row: raise HTTPException(status_code=404, detail="run not found")
    return RunStatusView(**row)