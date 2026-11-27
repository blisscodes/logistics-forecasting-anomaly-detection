# Score the frozen detector on injected anomalies.
import pandas as pd

from src.anomalies import inject
from src.detect import DIRECTION, find_alerts, score_signals


def score_alerts(alerts, labels, signal, index):
    days = [d for s, d in alerts if s == signal]
    windows = labels[labels["signal"] == signal]
    inside = pd.Series(False, index=index)
    for _, w in windows.iterrows():
        inside[w["start"]:w["end"]] = True
    correct = sum(bool(inside.get(d, False)) for d in days)
    detected = sum(any(w["start"] <= d <= w["end"] for d in days)
                   for _, w in windows.iterrows())
    return {"alerts": len(days), "correct": correct,
            "false_alerts": len(days) - correct, "windows": len(windows),
            "detected": detected, "clean_days": int((~inside).sum())}


def evaluate_draw(train_signals, val_signals, base, thresholds, seed):
    injected, labels = inject(val_signals, seed)
    context = pd.concat([train_signals.iloc[-2:], injected])
    scored = score_signals(context, base).loc[val_signals.index]
    alerts = find_alerts(scored, thresholds)
    return {s: score_alerts(alerts, labels, s, val_signals.index) for s in DIRECTION}


def evaluate_all(train_signals, val_signals, base, thresholds, seeds):
    rows = []
    for seed in seeds:
        for signal, r in evaluate_draw(train_signals, val_signals, base, thresholds, seed).items():
            rows.append({"seed": seed, "signal": signal, **r})
    return pd.DataFrame(rows)