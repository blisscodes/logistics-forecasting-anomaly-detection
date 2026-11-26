import numpy as np
import pandas as pd

from src.baselines import seasonal_naive_14, train_mean, weekday_profile


def make_daily(n=100):
    return pd.Series(np.arange(n, dtype=float), index=pd.date_range("2024-01-01", periods=n))


def test_seasonal_naive_uses_lag_7_then_14():
    daily = make_daily()
    pred = seasonal_naive_14(daily, daily.index[70:84])
    assert pred.iloc[0] == 63 and pred.iloc[6] == 69
    assert pred.iloc[7] == 63 and pred.iloc[13] == 69


def test_train_mean_is_constant():
    daily = make_daily(10)
    pred = train_mean(daily, pd.date_range("2024-02-01", periods=3))
    assert pred.tolist() == [4.5, 4.5, 4.5]


def test_weekday_profile_repeats_each_weekday():
    idx = pd.date_range("2024-01-01", periods=56)
    train = pd.Series(idx.day_of_week * 10.0, index=idx)
    pred = weekday_profile(train, pd.date_range("2024-03-01", periods=7))
    assert pred.tolist() == [(d.day_of_week * 10.0) for d in pred.index]