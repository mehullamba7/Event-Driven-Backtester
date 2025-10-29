from __future__ import annotations
import json, uuid
import pandas as pd
from datetime import datetime, timezone
from ..repositories.runs_repo import RunsRepo
from ..repositories.bars_repo import BarsRepo
from ..repositories.state_repo import StateRepo
from ..services.bar_stream import BarStream
from ..services.strategy_engine import SimpleSMACrossover
from ..services.portfolio_engine import PortfolioEngine
from ..observability.logger import get_logger

class RunManager:
    def __init__(self):
        self.runs = RunsRepo()
        self.bars = BarsRepo()
        self.state = StateRepo()

    def create_run(self, payload: dict) -> str:
        run_id = str(uuid.uuid4())
        self.runs.create(run_id, json.dumps(payload))
        return run_id

    def execute(self, run_id: str, payload: dict):
        logger = get_logger("run", run_id)
        self.runs.update_status(run_id, "running", started_at=datetime.now(timezone.utc).isoformat())
        symbols = payload["symbols"]; tf = payload["timeframe"]
        start_ts = payload["start_ts"]; end_ts = payload["end_ts"]
        start_cash = float(payload["start_cash"])

        stream = BarStream(self.bars, symbols, tf, start_ts, end_ts)
        strat_specs = payload["strategies"]
        # Phase-1 supports only SMA crossover spec
        sma_spec = next((s for s in strat_specs if s["strategy_id"]=="sma_crossover"), None)
        if sma_spec is None:
            raise ValueError("Phase-1 requires sma_crossover strategy")
        short = int(sma_spec["config"].get("short", 50))
        long = int(sma_spec["config"].get("long", 200))
        sma = SimpleSMACrossover(symbols, short, long)
        port = PortfolioEngine(start_cash=start_cash)

        snapshots_rows = []
        positions_rows = []
        bars_total = 0
        for _ in stream: bars_total += 1
        self.runs.update_status(run_id, "running", bars_total=bars_total)
        # restart iterator
        stream = BarStream(self.bars, symbols, tf, start_ts, end_ts)

        processed = 0
        for ts, bars in stream:
            sigs = sma.on_bar(ts, bars)
            orders = port.on_signals(ts, bars, sigs)
            fills = port.on_orders(ts, bars, orders)
            port.on_fills(fills)
            snap = port.snapshot(ts, bars)
            snapshots_rows.append({"ts": snap["ts"], "cash": snap["cash"], "equity": snap["equity"]})
            for s, p in snap["positions"].items():
                positions_rows.append({"ts": ts, "instrument_id": s, "quantity": p["quantity"],
                                       "avg_price": p["avg_price"], "mtm_price": p["mtm_price"]})
            processed += 1
            if processed % 100 == 0:
                self.runs.update_status(run_id, "running", bars_total=bars_total, bars_processed=processed)

        # persist artifacts
        snaps_df = pd.DataFrame(snapshots_rows)
        snaps_df["ts"] = pd.to_datetime(snaps_df["ts"], utc=True)
        pos_df = pd.DataFrame(positions_rows) if positions_rows else pd.DataFrame(columns=["ts","instrument_id","quantity","avg_price","mtm_price"])
        if not pos_df.empty:
            pos_df["ts"] = pd.to_datetime(pos_df["ts"], utc=True)
        self.state.write_snapshots(run_id, snaps_df)
        self.state.write_positions(run_id, pos_df)

        self.runs.update_status(run_id, "done", bars_total=bars_total, bars_processed=processed,
                                finished_at=datetime.now(timezone.utc).isoformat())
        logger.info("Run %s completed: %d bars", run_id, processed)