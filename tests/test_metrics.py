import pandas as pd
import pytest

from src.metrics import mae, scores, wape


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