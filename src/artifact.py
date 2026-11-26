import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.data import ROOT

MODELS = ROOT / "models"


def fit_weekday_means(train):
    prof = train.groupby(train.index.day_of_week).mean()
    return {str(int(k)): round(float(v), 6) for k, v in prof.items()}


def artifact_folder(name, version, root=MODELS):
    return Path(root) / f"{name}_v{version}"


def write_json(path, data):
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    Path(path).write_bytes(text.encode("utf-8"))


def file_checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_model(name, version, weekday_means, lower_offset, upper_offset,
               level=0.8, root=MODELS):
    folder = artifact_folder(name, version, root)
    if folder.exists():
        raise FileExistsError(f"{folder.name} already exists; use a new version")
    folder.mkdir(parents=True)
    model = {
        "type": "weekday_profile",
        "weekday_means": weekday_means,
        "interval": {
            "level": level,
            "lower_offset": round(float(lower_offset), 6),
            "upper_offset": round(float(upper_offset), 6),
        },
    }
    write_json(folder / "model.json", model)
    return folder

def git_info(cwd=ROOT):
    def run(*args):
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                              text=True, check=True).stdout.strip()
    try:
        return {"commit": run("rev-parse", "HEAD"),
                "uncommitted_changes": bool(run("status", "--porcelain"))}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": "unknown", "uncommitted_changes": None}


def build_metadata(folder, train_range, valid_range, valid_metrics, runs, seed, git):
    folder = Path(folder)
    return {
        "name": folder.name,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model_file": "model.json",
        "model_sha256": file_checksum(folder / "model.json"),
        "training_period": train_range,
        "validation_period": valid_range,
        "features": "none (weekday of the forecast date)",
        "seed": seed,
        "validation_metrics": valid_metrics,
        "test_result": "see docs/experiment_log.md, entry T1",
        "experiments": runs,
        "git": git,
        "environment": {"python": sys.version.split()[0],
                        "pandas": pd.__version__, "numpy": np.__version__},
    }