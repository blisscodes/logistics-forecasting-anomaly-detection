# Synthetic anomalies injected into copies of the daily signals.
import numpy as np
import pandas as pd

ANOMALY_TYPES = {
    "volume": {"length": 5, "factor": 0.8},
    "late_rate": {"length": 4, "add": 0.10},
    "detention": {"length": 5, "add": 30.0},
}
WINDOWS_PER_TYPE = 2
MIN_GAP = 7


def place_windows(n_days, length, count, rng, min_gap=MIN_GAP):
    starts = []
    for _ in range(1000):
        s = int(rng.integers(0, n_days - length + 1))
        if all(abs(s - t) >= length + min_gap for t in starts):
            starts.append(s)
        if len(starts) == count:
            return sorted(starts)
    raise ValueError("could not place the windows without overlap")


def inject(signals, seed, types=ANOMALY_TYPES, count=WINDOWS_PER_TYPE):
    rng = np.random.default_rng(seed)
    out = signals.copy()
    labels = []
    for name, cfg in types.items():
        for s in place_windows(len(out), cfg["length"], count, rng):
            idx = out.index[s:s + cfg["length"]]
            if "factor" in cfg:
                out.loc[idx, name] = out.loc[idx, name] * cfg["factor"]
            else:
                out.loc[idx, name] = out.loc[idx, name] + cfg["add"]
            labels.append((name, idx[0], idx[-1]))
    if "late_rate" in out:
        out["late_rate"] = out["late_rate"].clip(upper=1.0)
    return out, pd.DataFrame(labels, columns=["signal", "start", "end"])


def make_all_labels(signals, seeds):
    frames = []
    for seed in seeds:
        _, labels = inject(signals, seed)
        frames.append(labels.assign(seed=seed))
    return pd.concat(frames, ignore_index=True)