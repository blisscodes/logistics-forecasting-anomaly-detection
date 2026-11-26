# Load the saved model and forecast the next days.
import argparse
import json
from pathlib import Path

import pandas as pd

from src.artifact import MODELS, file_checksum


def load_model(folder):
    folder = Path(folder)
    meta = json.loads((folder / "metadata.json").read_text())
    if file_checksum(folder / "model.json") != meta["model_sha256"]:
        raise ValueError("model.json does not match its recorded checksum")
    return json.loads((folder / "model.json").read_text())


def forecast(model, start, days=14):
    dates = pd.date_range(start, periods=days)
    means = model["weekday_means"]
    pred = pd.Series([means[str(d.day_of_week)] for d in dates], index=dates)
    band = model["interval"]
    return pd.DataFrame({"pred": pred,
                         "lower": pred + band["lower_offset"],
                         "upper": pred + band["upper_offset"]})


def main():
    parser = argparse.ArgumentParser(description="14-day load forecast")
    parser.add_argument("--start", required=True)
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--model", default=str(MODELS / "weekday_profile_v1"))
    args = parser.parse_args()
    print(forecast(load_model(args.model), args.start, args.days).round(1).to_string())


if __name__ == "__main__":
    main()