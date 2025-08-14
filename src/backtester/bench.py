from __future__ import annotations
import time
from .datasets import make_synthetic_ticks
from .bars import time_bars

def main():
    df = make_synthetic_ticks(2_000_000)
    t0 = time.time()
    bars = time_bars(df, '1s')
    dt = time.time() - t0
    events_per_min = len(df) / dt / 60
    print(f"Resampled {len(df):,} ticks to {len(bars):,} 1s bars in {dt:.2f}s — ~{events_per_min:,.1f} events/min")

if __name__ == "__main__":
    main()
