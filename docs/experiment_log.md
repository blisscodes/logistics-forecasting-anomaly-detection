# Experiment Log

This document records modeling experiments, evaluation results, and observations.

## Evaluation Approach

- **Forecast target:** Daily completed-load volume
- **Forecast horizon:** 14 days
- **Validation strategy:** Time-based evaluation (no random shuffling)
- **Baseline model:** Weekly seasonal naive forecast
- **Primary metrics:** MAE and WAPE

## Experiment Records

### Experiment 001 — Baseline

**Status:** Preliminary result available

- **Model:** Weekly seasonal naive
- **Training period:** To be documented
- **Evaluation period:** To be documented
- **Forecast horizon:** Preliminary one-step evaluation
- **MAE:** 9.95 loads/day
- **WAPE:** 12.76%

**Observations:**
- This is a preliminary one-step holdout result.
- It is not yet a proper rolling-origin 14-day evaluation.
- We will use it as a reference when evaluating more advanced models.

## Future Experiments

Record each new model or meaningful configuration change as a separate experiment.

| Experiment | Model | Purpose | Status |
|---|---|---|---|
| 002 | To be determined | Establish a stronger forecasting benchmark | Planned |
| 003 | To be determined | Evaluate additional forecasting approaches | Planned |