import pandas as pd
import pytest

from src.intervals import add_interval, coverage, residual_offsets


def test_residual_offsets_known_example():
    actual = list(range(1, 11))
    pred = [0] * 10
    lo, hi = residual_offsets(actual, pred, level=0.8)
    assert lo == pytest.approx(1.9)
    assert hi == pytest.approx(9.1)


def test_add_interval_shifts_the_forecast():
    band = add_interval(pd.Series([100.0, 110.0]), -10.0, 12.0)
    assert band["lower"].tolist() == [90.0, 100.0]
    assert band["upper"].tolist() == [112.0, 122.0]


def test_coverage_counts_inside_values():
    assert coverage([1, 5, 9, 20], [0, 0, 0, 0], [10, 10, 10, 10]) == 0.75


def test_invalid_level_fails():
    with pytest.raises(ValueError, match="between 0 and 1"):
        residual_offsets([1, 2, 3], [1, 2, 3], level=1.5)