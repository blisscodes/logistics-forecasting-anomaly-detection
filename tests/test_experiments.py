import numpy as np
import pandas as pd

from src.experiments import CALENDAR_COLUMNS, LAG_COLUMNS, run_experiment
from src.features import build_features
from src.tracking import logged_ids


class MeanModel:
    def fit(self, X, y):
        self.mean_ = float(np.mean(y))
        return self

    def predict(self, X):
        return np.full(len(X), self.mean_)


def make_tables():
    idx = pd.date_range("2024-01-01", periods=70)
    frame = pd.DataFrame({"f": np.arange(70.0), "loads": [10.0] * 42 + [12.0] * 28}, index=idx)
    return {"train": frame.iloc[:42], "valid": frame.iloc[42:]}


def test_run_experiment_logs_and_needs_no_test_table(tmp_path):
    tables = make_tables()
    path = tmp_path / "runs.csv"
    bar = pd.Series(11.0, index=tables["valid"].index)
    pred, valid_mae, valid_wape, won = run_experiment(
        "x1", "Mean", MeanModel(), "f", ["f"], {}, tables, bar, path=path)
    assert valid_mae == 2.0
    assert logged_ids(path) == {"x1"}
    assert len(pred) == 28


def test_column_groups_cover_all_features():
    idx = pd.date_range("2024-01-01", periods=60)
    feats = build_features(pd.Series(1.0, index=idx))
    assert sorted(CALENDAR_COLUMNS + LAG_COLUMNS) == sorted(feats.columns)