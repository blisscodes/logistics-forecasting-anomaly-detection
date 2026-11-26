# Append one row per experiment run to reports/experiment_runs.csv.
import csv
import json
from datetime import date
from pathlib import Path

from src.config import SEED
from src.data import ROOT

RUNS_PATH = ROOT / "reports" / "experiment_runs.csv"
COLUMNS = ["run_id", "date", "model", "features", "settings", "seed",
           "valid_mae", "valid_wape", "windows_won", "notes"]


def logged_ids(path=RUNS_PATH):
    path = Path(path)
    if not path.exists():
        return set()
    with path.open(newline="") as f:
        return {row["run_id"] for row in csv.DictReader(f)}


def log_run(run_id, model, features, settings, valid_mae, valid_wape,
            windows_won, notes="", path=RUNS_PATH):
    path = Path(path)
    if run_id in logged_ids(path):
        raise ValueError(f"run {run_id} is already logged")
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with path.open("a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(COLUMNS)
        writer.writerow([run_id, date.today().isoformat(), model, features,
                         json.dumps(settings, sort_keys=True), SEED,
                         valid_mae, valid_wape, windows_won, notes])