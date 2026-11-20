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
    if df["load_id"].duplicated().any():
        raise ValueError("loads has duplicate load_id values")
    return df


def build_daily(df):
    daily = df.groupby("load_date").size().rename("loads")
    full = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    if len(full) != len(daily):
        raise ValueError("daily series has missing days")
    return daily