from backtester.datasets import make_synthetic_ticks
from backtester.bars import time_bars, volume_bars, tick_bars

def test_bar_builders():
    df = make_synthetic_ticks(10_000)
    tb = time_bars(df, '1s')
    vb = volume_bars(df, 100)
    kb = tick_bars(df, 100)
    assert len(tb) > 0 and len(vb) > 0 and len(kb) > 0
