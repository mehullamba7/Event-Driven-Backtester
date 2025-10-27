from __future__ import annotations
from pathlib import Path
import pandas as pd
from ..config import RUNS_ROOT

class StateRepo:
    def snapshots_path(self, run_id: str) -> Path:
        return RUNS_ROOT / run_id / "snapshots.parquet"

    def positions_path(self, run_id: str) -> Path:
        return RUNS_ROOT / run_id / "positions.parquet"

    def write_snapshots(self, run_id: str, df: pd.DataFrame) -> None:
        p = self.snapshots_path(run_id); p.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(p, index=False)

    def write_positions(self, run_id: str, df: pd.DataFrame) -> None:
        p = self.positions_path(run_id); p.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(p, index=False)

    def read_snapshot_at_or_before(self, run_id: str, ts_iso: str | None) -> dict | None:
        p = self.snapshots_path(run_id)
        if not p.exists(): return None
        df = pd.read_parquet(p)
        if ts_iso:
            df = df[df["ts"] <= pd.Timestamp(ts_iso, tz="UTC")]
        if df.empty: return None
        row = df.sort_values("ts").iloc[-1]
        return dict(ts=row["ts"].to_pydatetime(), cash=float(row["cash"]), equity=float(row["equity"]))

    def read_positions_between(self, run_id: str, start_ts: str, end_ts: str) -> pd.DataFrame:
        p = self.positions_path(run_id)
        if not p.exists(): return pd.DataFrame(columns=["ts","instrument_id","quantity","avg_price","mtm_price"])
        df = pd.read_parquet(p)
        m = (df["ts"] >= pd.Timestamp(start_ts, tz="UTC")) & (df["ts"] <= pd.Timestamp(end_ts, tz="UTC"))
        return df[m].sort_values(["ts","instrument_id"])