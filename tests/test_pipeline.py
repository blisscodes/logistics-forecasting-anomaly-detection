import pandas as pd
import pytest

from src.data import build_daily, load_loads, validate_daily, validate_loads
from src.features import build_features


def make_loads(days=120, per_day=3):
    dates = pd.date_range("2024-01-01", periods=days).repeat(per_day)
    return pd.DataFrame({
        "load_id": [f"L{i:05d}" for i in range(len(dates))],
        "customer_id": "C1",
        "route_id": "R1",
        "load_date": dates,
    })


def test_good_data_passes():
    df = make_loads()
    assert validate_loads(df) is df


def test_missing_column_fails():
    with pytest.raises(ValueError, match="missing columns"):
        validate_loads(make_loads().drop(columns=["route_id"]))


def test_text_dates_fail():
    df = make_loads()
    df["load_date"] = df["load_date"].astype(str)
    with pytest.raises(ValueError, match="not a date"):
        validate_loads(df)


def test_null_key_fails():
    df = make_loads()
    df.loc[0, "route_id"] = None
    with pytest.raises(ValueError, match="nulls in key columns"):
        validate_loads(df)


def test_duplicate_id_fails():
    df = make_loads()
    with pytest.raises(ValueError, match="duplicate load_id"):
        validate_loads(pd.concat([df, df.head(1)]))


def test_daily_gap_fails():
    daily = build_daily(make_loads())
    with pytest.raises(ValueError, match="missing days"):
        validate_daily(daily.drop(daily.index[10]))


def test_build_daily_counts():
    daily = build_daily(make_loads(days=5, per_day=3))
    assert daily.tolist() == [3, 3, 3, 3, 3]


def test_chain_from_csv(tmp_path):
    path = tmp_path / "loads.csv"
    make_loads().to_csv(path, index=False)
    daily = build_daily(validate_loads(load_loads(path)))
    feats = build_features(daily)
    assert feats.shape == (120, 18)
    assert feats["roll_mean_28"].isna().sum() == 41
    assert feats.iloc[41:].isna().sum().sum() == 0