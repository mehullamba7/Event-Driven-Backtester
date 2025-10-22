import logging
from pathlib import Path
from ..config import RUNS_ROOT

def get_logger(name: str = "api", run_id: str | None = None) -> logging.Logger:
    logger = logging.getLogger(f"{name}{'' if not run_id else '.'+run_id}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    if run_id:
        log_dir = RUNS_ROOT / run_id
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_dir / "run.log", encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger