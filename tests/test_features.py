import numpy as np
import pandas as pd
import pytest

from src.features import build_features, make_calendar, make_lags


def make_series(n=100):
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.Series(np.arange(n, dtype=float), index=idx, name="loads")


def poison_after(s, d):
    poisoned = s.copy()
    poisoned.loc[poisoned.index > d - pd.Timedelta(days=14)] = 9999
    return poisoned


def test_calendar_known_dates():
    idx = pd.to_datetime(["2024-03-15", "2024-02-29", "2024-07-04"])
    cal = make_calendar(idx)
    assert cal.loc["2024-03-15", "dow"] == 4
    assert cal.loc["2024-02-29", "is_month_end"] == 1
    assert cal.loc["2024-07-04", "is_holiday"] == 1
    assert cal.loc["2024-03-15", "is_holiday"] == 0


def test_calendar_columns():
    cal = make_calendar(pd.date_range("2025-01-01", periods=14))
    assert cal.shape == (14, 12)


def test_cyclical_monday():
    cal = make_calendar(pd.date_range("2024-03-11", periods=7))
    assert cal.loc["2024-03-11", "dow_sin"] == pytest.approx(0.0, abs=1e-12)
    assert cal.loc["2024-03-11", "dow_cos"] == pytest.approx(1.0)


def test_lag_values_are_exact():
    f = make_lags(make_series())
    assert f["lag_14"].iloc[50] == 36
    assert f["lag_21"].iloc[50] == 29
    assert f["lag_28"].iloc[50] == 22
    assert f["roll_mean_7"].iloc[50] == 33.0
    assert f["roll_mean_28"].iloc[50] == 22.5


def test_burn_in_counts():
    f = make_lags(make_series())
    assert f["lag_14"].isna().sum() == 14
    assert f["roll_mean_28"].isna().sum() == 41
    assert f["roll_std_28"].isna().sum() == 41


def test_features_ignore_the_recent_past():
    s = make_series()
    d = s.index[80]
    assert build_features(s).loc[d].equals(build_features(poison_after(s, d)).loc[d])


def test_leaky_control_is_caught():
    s = make_series()
    d = s.index[80]
    leaky = lambda x: x.shift(1).rolling(7).mean()
    assert leaky(s).loc[d] != leaky(poison_after(s, d)).loc[d]