import numpy as np
import pandas as pd
import pytest

from src.anomalies import inject, make_all_labels, place_windows


def make_signals(n=84):
    idx = pd.date_range("2024-07-17", periods=n)
    return pd.DataFrame({"volume": 80.0, "late_rate": 0.45, "detention": 100.0}, index=idx)


def test_same_seed_same_labels():
    assert inject(make_signals(), 42)[1].equals(inject(make_signals(), 42)[1])


def test_different_seed_different_labels():
    assert not inject(make_signals(), 42)[1].equals(inject(make_signals(), 43)[1])


def test_input_is_not_changed():
    s = make_signals()
    before = s.copy()
    inject(s, 42)
    assert s.equals(before)


def test_effect_sizes_and_untouched_days():
    s = make_signals()
    out, labels = inject(s, 42)
    row = labels[labels.signal == "volume"].iloc[0]
    assert (out.loc[row.start:row.end, "volume"] == 64.0).all()
    row = labels[labels.signal == "late_rate"].iloc[0]
    assert np.allclose(out.loc[row.start:row.end, "late_rate"], 0.55)
    row = labels[labels.signal == "detention"].iloc[0]
    assert (out.loc[row.start:row.end, "detention"] == 130.0).all()
    hit = pd.Series(False, index=s.index)
    for _, r in labels[labels.signal == "volume"].iterrows():
        hit[r.start:r.end] = True
    assert (out.loc[~hit, "volume"] == 80.0).all()


def test_windows_do_not_overlap_within_a_signal():
    labels = inject(make_signals(), 42)[1]
    for _, g in labels.groupby("signal"):
        g = g.sort_values("start")
        assert (g["start"].iloc[1:].values > g["end"].iloc[:-1].values).all()


def test_impossible_placement_fails():
    with pytest.raises(ValueError, match="could not place"):
        place_windows(10, 5, 3, np.random.default_rng(1))