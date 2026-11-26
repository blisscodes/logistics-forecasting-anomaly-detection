# Save the final model as a small, versioned, checksummed artifact.
import hashlib
import json
from pathlib import Path

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