import pandas as pd
import pytest

from src.metrics import mae, scores, wape, window_mae, windows_won, verdict


def test_mae_known_example():
    assert mae([10, 20, 30], [12, 18, 33]) == pytest.approx(7 / 3)


def test_wape_known_example():
    assert wape([10, 20, 30], [12, 18, 33]) == pytest.approx(7 / 60)


def test_perfect_forecast_scores_zero():
    assert scores([5, 6, 7], [5, 6, 7]) == (0.0, "0.00%")


def test_scores_format():
    assert scores([10, 20, 30], [12, 18, 33]) == (2.33, "11.67%")


def test_works_with_pandas_series():
    idx = pd.date_range("2024-01-01", periods=3)
    assert mae(pd.Series([10, 20, 30], index=idx), pd.Series([12, 18, 33], index=idx)) == pytest.approx(7 / 3)


def test_length_mismatch_fails():
    with pytest.raises(ValueError, match="same non-zero length"):
        mae([1, 2, 3], [1, 2])


def test_nan_fails():
    with pytest.raises(ValueError, match="NaN"):
        wape([1, 2, 3], [1, float("nan"), 3])


def test_window_mae_known():
    actual = [10] * 28
    pred = [12] * 14 + [9] * 14
    assert window_mae(actual, pred) == [2.0, 1.0]


def test_windows_won_counts():
    actual = [10] * 28
    pred = [10] * 14 + [13] * 14
    bar = [11] * 14 + [11] * 14
    assert windows_won(actual, pred, bar) == 1


def test_window_length_must_divide():
    with pytest.raises(ValueError, match="multiple of 14"):
        window_mae([1] * 20, [1] * 20)

def test_verdict_rules():
    assert verdict(7.0, 5) == "better"
    assert verdict(7.0, 2) == "tied"
    assert verdict(7.2, 1) == "tied"
    assert verdict(7.5, 4) == "worse"
    assert verdict(6.5, 6) == "check for leakage"