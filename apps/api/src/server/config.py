from __future__ import annotations
import os
from pathlib import Path

# roots (change via env vars if desired)
REPO_ROOT = Path(__file__).resolve().parents[4]

BARS_ROOT = Path(os.getenv("BARS_ROOT", REPO_ROOT / "data" / "bars"))
RUNS_ROOT = Path(os.getenv("RUNS_ROOT", REPO_ROOT / "runs"))
SQLITE_PATH = Path(os.getenv("SQLITE_PATH", REPO_ROOT / "runs" / "runs.sqlite"))

# limits
MAX_CONCURRENT_RUNS = int(os.getenv("MAX_CONCURRENT_RUNS", "2"))
DEFAULT_PAGE_SIZE = 500
MAX_PAGE_SIZE = 5000

# create dirs
BARS_ROOT.mkdir(parents=True, exist_ok=True)
RUNS_ROOT.mkdir(parents=True, exist_ok=True)