import numpy as np
import pandas as pd

from src.anomaly_eval import evaluate_draw, score_alerts
from src.detect import fit_baseline, fit_thresholds, score_signals


def make_clean(n=300, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n)
    return pd.DataFrame({"volume": 80 + rng.normal(0, 8, n),
                         "late_rate": 0.45 + rng.normal(0, 0.05, n),
                         "detention": 100 + rng.normal(0, 8, n)}, index=idx)


def test_score_alerts_toy_example():
    idx = pd.date_range("2024-08-01", periods=31)
    labels = pd.DataFrame([("volume", pd.Timestamp("2024-08-12"), pd.Timestamp("2024-08-16"))],
                          columns=["signal", "start", "end"])
    alerts = [("volume", pd.Timestamp("2024-08-13")), ("volume", pd.Timestamp("2024-08-20")),
              ("late_rate", pd.Timestamp("2024-08-14"))]
    r = score_alerts(alerts, labels, "volume", idx)
    assert r == {"alerts": 2, "correct": 1, "false_alerts": 1, "windows": 1,
                 "detected": 1, "clean_days": 26}


def test_other_signal_alerts_are_not_counted():
    idx = pd.date_range("2024-08-01", periods=31)
    labels = pd.DataFrame([("volume", pd.Timestamp("2024-08-12"), pd.Timestamp("2024-08-16"))],
                          columns=["signal", "start", "end"])
    r = score_alerts([("late_rate", pd.Timestamp("2024-08-13"))], labels, "volume", idx)
    assert r["alerts"] == 0 and r["detected"] == 0


def test_evaluate_draw_covers_every_signal_and_repeats():
    clean = make_clean()
    train, val = clean.iloc[:200], clean.iloc[200:284]
    base = fit_baseline(train)
    th = fit_thresholds(score_signals(train, base).dropna())
    a = evaluate_draw(train, val, base, th, 42)
    b = evaluate_draw(train, val, base, th, 42)
    assert set(a) == {"volume", "late_rate", "detention"} and a == b
    assert all(r["windows"] == 2 for r in a.values())