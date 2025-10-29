from __future__ import annotations
from ..services.run_manager import RunManager
from ..observability.logger import get_logger

def compute_replay(run_id: str, payload: dict):
    logger = get_logger("job", run_id)
    try:
        RunManager().execute(run_id, payload)
    except Exception as e:
        logger.exception("Run failed: %s", e)
        # best-effort status mark
        from ..repositories.runs_repo import RunsRepo
        RunsRepo().update_status(run_id, "error", error_msg=str(e))