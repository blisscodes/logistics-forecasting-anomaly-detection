# Build calendar and lag features from the daily series.
import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar


def make_calendar(idx):
    c = pd.DataFrame(index=idx)
    c["dow"] = idx.day_of_week
    c["month"] = idx.month
    c["week"] = idx.isocalendar().week.astype(int).to_numpy()
    c["doy"] = idx.day_of_year
    hol = USFederalHolidayCalendar().holidays(start=idx.min(), end=idx.max())
    c["is_month_end"] = idx.is_month_end.astype(int)
    c["is_holiday"] = idx.isin(hol).astype(int)
    for col, period in [("dow", 7), ("month", 12), ("doy", 365.25)]:
        c[col + "_sin"] = np.sin(2 * np.pi * c[col] / period)
        c[col + "_cos"] = np.cos(2 * np.pi * c[col] / period)
    return c


def make_lags(s):
    base = s.shift(14)
    f = pd.DataFrame({f"lag_{k}": s.shift(k) for k in (14, 21, 28)})
    f["roll_mean_7"] = base.rolling(7).mean()
    f["roll_mean_28"] = base.rolling(28).mean()
    f["roll_std_28"] = base.rolling(28).std()
    return f


def build_features(daily):
    return pd.concat([make_calendar(daily.index), make_lags(daily)], axis=1)