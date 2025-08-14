from backtester.validation import purged_walk_forward_split

def test_purged_walk_forward_split():
    n = 1000
    splits = list(purged_walk_forward_split(n, 5, embargo=10))
    assert len(splits) == 5
    for tr, te in splits:
        assert set(tr).isdisjoint(set(te))
