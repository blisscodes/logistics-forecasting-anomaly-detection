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