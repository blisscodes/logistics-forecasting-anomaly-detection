import json

import pandas as pd
import pytest

from src.artifact import (build_metadata, file_checksum, fit_weekday_means,
                          save_model, write_json)
from src.predict import forecast, load_model

MEANS = {str(i): 70.0 + i for i in range(7)}
GIT = {"commit": "abc", "uncommitted_changes": False}


def make_saved(tmp_path):
    folder = save_model("m", 1, MEANS, -10.0, 12.0, root=tmp_path)
    meta = build_metadata(folder, ["2022-01-01", "2022-12-31"],
                          ["2023-01-01", "2023-03-25"], {"mae": 7.16}, ["003c"], 42, GIT)
    write_json(folder / "metadata.json", meta)
    return folder


def test_fit_weekday_means_known():
    idx = pd.date_range("2024-01-01", periods=56)
    train = pd.Series(idx.day_of_week * 10.0, index=idx)
    assert fit_weekday_means(train) == {str(i): i * 10.0 for i in range(7)}


def test_save_refuses_to_overwrite(tmp_path):
    save_model("m", 1, MEANS, -10.0, 12.0, root=tmp_path)
    with pytest.raises(FileExistsError):
        save_model("m", 1, MEANS, -10.0, 12.0, root=tmp_path)


def test_checksum_changes_with_content(tmp_path):
    path = tmp_path / "a.json"
    write_json(path, {"x": 1})
    first = file_checksum(path)
    write_json(path, {"x": 2})
    assert file_checksum(path) != first


def test_round_trip_and_forecast(tmp_path):
    model = load_model(make_saved(tmp_path))
    out = forecast(model, "2024-01-01", days=7)
    assert out["pred"].tolist() == [70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0]
    assert out["lower"].iloc[0] == 60.0 and out["upper"].iloc[0] == 82.0


def test_forecast_length(tmp_path):
    model = load_model(make_saved(tmp_path))
    assert len(forecast(model, "2025-01-01")) == 14
    assert len(forecast(model, "2025-01-01", days=3)) == 3


def test_load_detects_tampering(tmp_path):
    folder = make_saved(tmp_path)
    path = folder / "model.json"
    data = json.loads(path.read_text())
    data["weekday_means"]["0"] = 999.0
    write_json(path, data)
    with pytest.raises(ValueError, match="checksum"):
        load_model(folder)


def test_metadata_has_required_keys(tmp_path):
    meta = json.loads((make_saved(tmp_path) / "metadata.json").read_text())
    for key in ["model_sha256", "training_period", "validation_metrics",
                "seed", "git", "environment", "experiments"]:
        assert key in meta