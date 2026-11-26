# Forecast error metrics (lower is better).
import numpy as np


def _clean(actual, pred):
    a = np.asarray(actual, dtype=float)
    p = np.asarray(pred, dtype=float)
    if a.shape != p.shape or a.size == 0:
        raise ValueError("actual and pred must have the same non-zero length")
    if np.isnan(a).any() or np.isnan(p).any():
        raise ValueError("actual or pred contains NaN")
    return a, p


def mae(actual, pred):
    a, p = _clean(actual, pred)
    return float(np.mean(np.abs(a - p)))


def wape(actual, pred):
    a, p = _clean(actual, pred)
    return float(np.abs(a - p).sum() / np.abs(a).sum())


def scores(actual, pred):
    return round(mae(actual, pred), 2), f"{wape(actual, pred):.2%}"


def window_mae(actual, pred, size=14):
    a, p = _clean(actual, pred)
    errs = np.abs(a - p)
    if len(errs) % size:
        raise ValueError(f"length {len(errs)} is not a multiple of {size}")
    return [float(x) for x in errs.reshape(-1, size).mean(axis=1)]


def windows_won(actual, pred, bar_pred, size=14):
    mine = window_mae(actual, pred, size)
    bar = window_mae(actual, bar_pred, size)
    return sum(m < b for m, b in zip(mine, bar))