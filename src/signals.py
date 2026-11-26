# Daily operational signals built from loads and delivery events.
import pandas as pd

from src.data import RAW

WARMUP_DAYS = 5
LATE_MINUTES = 120
EVENT_COLUMNS = ["event_type", "scheduled_datetime", "actual_datetime", "detention_minutes"]


def load_events(path=RAW / "delivery_events.csv"):
    return pd.read_csv(path, parse_dates=["scheduled_datetime", "actual_datetime"])


def build_signals(daily, events):
    missing = [c for c in EVENT_COLUMNS if c not in events.columns]
    if missing:
        raise ValueError(f"delivery events are missing columns: {missing}")
    d = events[events["event_type"] == "Delivery"].copy()
    delay = (d["actual_datetime"] - d["scheduled_datetime"]).dt.total_seconds() / 60
    d["late"] = delay > LATE_MINUTES
    d["day"] = d["actual_datetime"].dt.normalize()
    by_day = d.groupby("day")
    signals = pd.DataFrame({
        "volume": daily,
        "late_rate": by_day["late"].mean(),
        "detention": by_day["detention_minutes"].mean(),
    })
    signals = signals.loc[daily.index].iloc[WARMUP_DAYS:]
    if signals.isna().any().any():
        raise ValueError("signals have missing days")
    return signals