import pandas as pd

from src.features import build_features
from src.splits import make_model_tables, make_splits


def make_daily(start="2022-01-01", end="2024-12-31"):
    return pd.Series(1, index=pd.date_range(start, end), name="loads")


def test_splits_match_the_saved_dates():
    assert make_splits(make_daily()) == {
        "train": ["2022-01-01", "2024-07-16"],
        "valid": ["2024-07-17", "2024-10-08"],
        "test": ["2024-10-09", "2024-12-31"],
    }


def test_splits_are_contiguous_and_do_not_overlap():
    s = make_splits(make_daily("2023-01-01", "2023-12-31"))
    day = pd.Timedelta(days=1)
    assert pd.Timestamp(s["train"][1]) + day == pd.Timestamp(s["valid"][0])
    assert pd.Timestamp(s["valid"][1]) + day == pd.Timestamp(s["test"][0])


def test_model_tables_drop_burn_in():
    daily = make_daily()
    frame = build_features(daily).join(daily)
    tables = make_model_tables(frame, make_splits(daily))
    assert {k: v.shape for k, v in tables.items()} == {
        "train": (887, 19), "valid": (84, 19), "test": (84, 19)}
    assert tables["train"].index.min() == pd.Timestamp("2022-02-11")