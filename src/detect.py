# Rule-based anomaly detector. Kept separate from the forecasting code.
import pandas as pd

DIRECTION = {"volume": -1, "late_rate": 1, "detention": 1}
ROLL_DAYS = 3
QUANTILE = 0.99


def fit_baseline(clean):
    center = clean[list(DIRECTION)].median()
    scale = 1.4826 * (clean[list(DIRECTION)] - center).abs().median()
    return {"center": center.to_dict(), "scale": scale.to_dict()}


def score_signals(signals, base, roll=ROLL_DAYS):
    out = {}
    for name, sign in DIRECTION.items():
        z = (signals[name] - base["center"][name]) / base["scale"][name]
        out[name] = (sign * z).rolling(roll).mean()
    return pd.DataFrame(out)


def fit_thresholds(clean_scores, quantile=QUANTILE):
    return {k: float(v) for k, v in clean_scores.quantile(quantile).items()}


def find_alerts(scored, thresholds):
    return [(name, day) for name in thresholds
            for day in scored.index[scored[name] > thresholds[name]]]