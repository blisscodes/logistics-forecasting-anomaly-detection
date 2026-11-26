import numpy as np
import pandas as pd

from src.detect import find_alerts, fit_baseline, fit_thresholds, score_signals


def make_clean(n=200, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n)
    return pd.DataFrame({
        "volume": 80 + rng.normal(0, 8, n),
        "late_rate": 0.45 + rng.normal(0, 0.05, n),
        "detention": 100 + rng.normal(0, 8, n),
    }, index=idx)


def test_baseline_center_and_scale():
    base = fit_baseline(make_clean())
    assert abs(base["center"]["volume"] - 80) < 3
    assert 6 < base["scale"]["volume"] < 10


def test_volume_drop_scores_high():
    clean = make_clean()
    base = fit_baseline(clean)
    dropped = clean.copy()
    dropped.iloc[100:105, 0] = 40.0
    scored = score_signals(dropped, base)
    assert scored["volume"].iloc[104] > 3
    assert scored["volume"].iloc[50] < 3


def test_thresholds_are_the_clean_quantile():
    clean = make_clean()
    scored = score_signals(clean, fit_baseline(clean)).dropna()
    th = fit_thresholds(scored, quantile=0.9)
    assert abs((scored["volume"] > th["volume"]).mean() - 0.1) < 0.02


def test_find_alerts_lists_exceedances_only():
    idx = pd.date_range("2024-01-01", periods=4)
    scored = pd.DataFrame({"volume": [0, 5, 0, 5.0], "late_rate": 0.0, "detention": 0.0}, index=idx)
    alerts = find_alerts(scored, {"volume": 1.0, "late_rate": 1.0, "detention": 1.0})
    assert alerts == [("volume", idx[1]), ("volume", idx[3])]