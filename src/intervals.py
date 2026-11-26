# Prediction intervals from past forecast errors.
import numpy as np
import pandas as pd


def residual_offsets(actual, pred, level=0.8):
    if not 0 < level < 1:
        raise ValueError("level must be between 0 and 1")
    resid = np.asarray(actual, dtype=float) - np.asarray(pred, dtype=float)
    tail = (1 - level) / 2
    return float(np.quantile(resid, tail)), float(np.quantile(resid, 1 - tail))


def add_interval(pred, lower_offset, upper_offset):
    pred = pd.Series(pred)
    return pd.DataFrame({"pred": pred, "lower": pred + lower_offset, "upper": pred + upper_offset})


def coverage(actual, lower, upper):
    a = np.asarray(actual, dtype=float)
    return float(np.mean((a >= np.asarray(lower, dtype=float)) & (a <= np.asarray(upper, dtype=float))))