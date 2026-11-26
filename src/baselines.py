# Simple baselines used as the bar for models.
import numpy as np
import pandas as pd


def seasonal_naive_14(daily, index):
    pos = np.arange(len(index)) % 14
    lag = np.where(pos < 7, 7, 14)
    return pd.Series(
        [daily.loc[d - pd.Timedelta(days=int(k))] for d, k in zip(index, lag)],
        index=index,
    )


def train_mean(train, index):
    return pd.Series(train.mean(), index=index)


def weekday_profile(train, index):
    prof = train.groupby(train.index.day_of_week).mean()
    return pd.Series(prof.loc[index.day_of_week].values, index=index)