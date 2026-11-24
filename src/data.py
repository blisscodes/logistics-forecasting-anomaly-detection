# Load the raw loads table and run basic checks.
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

REQUIRED_COLUMNS = ["load_id", "customer_id", "route_id", "load_date"]


def load_loads(path=RAW / "loads.csv"):
    return pd.read_csv(path, parse_dates=["load_date"])


def validate_loads(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"loads is missing columns: {missing}")
    if not pd.api.types.is_datetime64_any_dtype(df["load_date"]):
        raise ValueError("load_date is not a date column (unparseable values?)")
    if df["load_id"].duplicated().any():
        raise ValueError("loads has duplicate load_id values")
    nulls = df[REQUIRED_COLUMNS].isna().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        raise ValueError(f"nulls in key columns: {nulls.to_dict()}")
    return df

def validate_daily(daily):
    if not daily.index.is_unique or not daily.index.is_monotonic_increasing:
        raise ValueError("daily dates are not unique and in increasing order")
    full = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    if len(full) != len(daily):
        raise ValueError(f"daily series has {len(full) - len(daily)} missing days")
    return daily


def build_daily(df):
    daily = df.groupby("load_date").size().rename("loads")
    return validate_daily(daily)