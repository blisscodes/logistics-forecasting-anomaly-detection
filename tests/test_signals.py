import pandas as pd
import pytest

from src.signals import WARMUP_DAYS, build_signals


def make_events(days=10, per_day=4):
    rows = []
    for day in pd.date_range("2024-01-01", periods=days):
        for j in range(per_day):
            sched = day + pd.Timedelta(hours=10)
            late = j == 0
            actual = sched + pd.Timedelta(minutes=180 if late else 30)
            rows.append(("Delivery", sched, actual, 100 + 10 * j))
            rows.append(("Pickup", sched, actual, 0))
    return pd.DataFrame(rows, columns=["event_type", "scheduled_datetime",
                                       "actual_datetime", "detention_minutes"])


def make_daily(days=10):
    return pd.Series(80, index=pd.date_range("2024-01-01", periods=days), name="loads")


def test_signal_values_and_pickups_ignored():
    signals = build_signals(make_daily(), make_events())
    assert len(signals) == 10 - WARMUP_DAYS
    assert (signals["volume"] == 80).all()
    assert (signals["late_rate"] == 0.25).all()
    assert (signals["detention"] == 115.0).all()


def test_missing_column_fails():
    with pytest.raises(ValueError, match="missing columns"):
        build_signals(make_daily(), make_events().drop(columns=["detention_minutes"]))


def test_missing_day_fails():
    events = make_events()
    gone = events["actual_datetime"].dt.normalize() == pd.Timestamp("2024-01-08")
    with pytest.raises(ValueError, match="missing days"):
        build_signals(make_daily(), events[~gone])