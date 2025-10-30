from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Optional
from ..config import SQLITE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  payload_hash TEXT,
  bars_total INTEGER,
  bars_processed INTEGER,
  started_at TEXT,
  finished_at TEXT,
  error_msg TEXT
);
"""

class RunsRepo:
    def __init__(self, db_path: Path = SQLITE_PATH):
        self.db_path = db_path
        self._init()

    def _conn(self):
        return sqlite3.connect(str(self.db_path))

    def _init(self):
        with self._conn() as con:
            con.executescript(SCHEMA)
        self._migrate_add_payload_hash()

    def _migrate_add_payload_hash(self):
        """
        Add 'payload_hash' column and its index if they don't exist.
        - Uses PRAGMA table_info to introspect current schema.
        - ALTER TABLE adds a nullable TEXT column (safe for existing rows).
        - Creates an index for fast lookups on payload_hash.
        """
        with self._conn() as con:
            cur = con.execute("PRAGMA table_info(runs)")
            columns = [row[1] for row in cur.fetchall()]  # row[1] = column name
            if "payload_hash" not in columns:
                con.execute("ALTER TABLE runs ADD COLUMN payload_hash TEXT")
                con.execute("CREATE INDEX IF NOT EXISTS idx_runs_payload_hash ON runs(payload_hash)")

    def create(self, run_id: str, payload_json: str):
        with self._conn() as con:
            con.execute(
                "INSERT INTO runs (run_id, status, payload_json) VALUES (?, ?, ?)",
                (run_id, "queued", payload_json),
            )

    def create_with_hash(self, run_id: str, payload_json: str, payload_hash: str):
        """Create run with hash for idempotency."""
        with self._conn() as con:
            con.execute(
                "INSERT INTO runs (run_id, status, payload_json, payload_hash) VALUES (?, ?, ?, ?)",
                (run_id, "queued", payload_json, payload_hash),
            )

    def get_by_hash(self, payload_hash: str) -> Optional[dict]:
        """Find run by payload hash for idempotency (fast via index)."""
        with self._conn() as con:
            cur = con.execute(
                "SELECT run_id, status, bars_total, bars_processed, started_at, finished_at, error_msg "
                "FROM runs WHERE payload_hash = ?",
                (payload_hash,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return dict(
                run_id=row[0],
                status=row[1],
                bars_total=row[2],
                bars_processed=row[3],
                started_at=row[4],
                finished_at=row[5],
                error_msg=row[6],
            )

    def update_status(
        self,
        run_id: str,
        status: str,
        bars_total=None,
        bars_processed=None,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
        error_msg: Optional[str] = None,
    ):
        with self._conn() as con:
            con.execute(
                """UPDATE runs SET status=?, bars_total=?,
                   bars_processed=?, started_at=COALESCE(?, started_at),
                   finished_at=COALESCE(?, finished_at),
                   error_msg=COALESCE(?, error_msg)
                   WHERE run_id=?""",
                (status, bars_total, bars_processed, started_at, finished_at, error_msg, run_id),
            )

    def get(self, run_id: str) -> Optional[dict]:
        with self._conn() as con:
            cur = con.execute(
                "SELECT run_id,status,bars_total,bars_processed,started_at,finished_at,error_msg FROM runs WHERE run_id=?",
                (run_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return dict(
                run_id=row[0],
                status=row[1],
                bars_total=row[2],
                bars_processed=row[3],
                started_at=row[4],
                finished_at=row[5],
                error_msg=row[6],
            )