# Chronological train / validation / test split by date.
import json
from pathlib import Path

from src.data import PROCESSED

VALID_DAYS = 84
TEST_DAYS = 84


def make_splits(daily):
    dates = daily.index
    test = dates[-TEST_DAYS:]
    valid = dates[-(TEST_DAYS + VALID_DAYS):-TEST_DAYS]
    train = dates[:-(TEST_DAYS + VALID_DAYS)]
    return {
        name: [str(idx.min().date()), str(idx.max().date())]
        for name, idx in [("train", train), ("valid", valid), ("test", test)]
    }


def save_splits(splits, path=PROCESSED / "splits.json"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(splits, indent=2))


def load_splits(path=PROCESSED / "splits.json"):
    return json.loads(Path(path).read_text())


def make_model_tables(frame, splits):
    frame = frame.dropna()
    return {name: frame.loc[start:end] for name, (start, end) in splits.items()}