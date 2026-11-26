import pandas as pd
import pytest

from src.tracking import COLUMNS, log_run


def test_log_run_writes_header_once(tmp_path):
    path = tmp_path / "runs.csv"
    log_run("a", "Ridge", "all18", {"alpha": 1}, 7.3, "9.3%", 2, path=path)
    log_run("b", "Ridge", "calendar12", {"alpha": 2}, 7.4, "9.4%", 1, path=path)
    df = pd.read_csv(path)
    assert list(df.columns) == COLUMNS
    assert df["run_id"].tolist() == ["a", "b"]


def test_settings_are_stored_as_json(tmp_path):
    path = tmp_path / "runs.csv"
    log_run("a", "Ridge", "all18", {"alpha": 1, "scaler": "standard"}, 7.3, "9.3%", 2, path=path)
    assert pd.read_csv(path)["settings"][0] == '{"alpha": 1, "scaler": "standard"}'


def test_duplicate_run_id_fails(tmp_path):
    path = tmp_path / "runs.csv"
    log_run("a", "Ridge", "all18", {}, 7.3, "9.3%", 2, path=path)
    with pytest.raises(ValueError, match="already logged"):
        log_run("a", "Ridge", "all18", {}, 7.3, "9.3%", 2, path=path)