# Experiment Log

Record of forecasting experiments: what was run, on which data, and how it
scored. Decisions and their reasoning are tracked separately and are not
part of this log.

## Evaluation setup

Shared by all experiments unless an entry says otherwise.

- **Target:** company-wide number of loads per day (`load_date` in
  `loads.csv`)
- **Horizon:** 14 days
- **Split** (chronological, no shuffling):
  - Train: 2022-01-01 to 2024-07-16 (928 days)
  - Validation: 2024-07-17 to 2024-10-08 (84 days)
  - Test: 2024-10-09 to 2024-12-31 (84 days), not yet scored
- **Metrics** (lower is better):
  - MAE: mean absolute error, in loads per day
  - WAPE: total absolute error divided by total actual loads
- **Evaluation modes:**
  - *One-step:* each day is predicted using actuals up to the previous day.
  - *14-day:* the validation period is cut into six 14-day windows, and each
    window is forecast using only data before its first day.

## Results summary

All scores are on the validation period.

| ID | Date | Method | Mode | MAE | WAPE | Status |
|---|---|---|---|---:|---:|---|
| 001 | 2026-11-18 | Weekly seasonal naive | One-step | 9.95 | 12.76% | Superseded |
| 002a | 2026-11-18 | Weekly seasonal naive | One-step | 10.21 | 13.01% | Done |
| 002b | 2026-11-18 | Weekly seasonal naive | 14-day | 10.98 | 13.98% | Done |
| 003a | 2026-11-19 | Training mean | 14-day | 7.31 | 9.31% | Done |
| 003b | 2026-11-19 | Trailing 28-day mean | 14-day | 7.27 | 9.27% | Done |
| 003c | 2026-11-19 | Weekday profile | 14-day | 7.16 | 9.12% | Done |

## Experiments

### 001: Weekly seasonal naive, preliminary

**Status:** Superseded by 002.

- **Result:** MAE 9.95, WAPE 12.76% (one-step).
- **Setup:** holdout dates were not recorded.
- **Notes:** the result cannot be reproduced or compared with later
  experiments. Kept for history; do not cite.

### 002: Weekly seasonal naive

**Date:** 2026-11-18 · **Code:** `notebooks/01_inventory.ipynb`

- **Goal:** establish the benchmark that planners' current method sets.
- **Method:** predict each day with the same weekday one week earlier. In
  14-day mode, days 8-14 of a window use the value 14 days earlier, because
  the intervening week is not yet known.
- **Results:** one-step MAE 10.21, WAPE 13.01%; 14-day MAE 10.98, WAPE
  13.98%.
- **Observations:**
  - The 14-day mode matches the real forecast horizon; one-step is an
    optimistic reference.
  - A 13-week validation period (2024-07-03 to 2024-10-01) gave 9.99 /
    12.79% (one-step) and 11.02 / 14.11% (14-day). Scores depend on the
    evaluation window, so do not compare scores across different splits.

### 003: Average baselines

**Date:** 2026-11-19 · **Code:** `notebooks/01_inventory.ipynb`

- **Goal:** check whether a plain average is a fairer benchmark than
  seasonal naive.
- **Method:** (a) mean of the training period (77.9 loads/day), fitted once;
  (b) mean of the 28 days before each window; (c) mean per weekday,
  computed on the training period only.
- **Results:** see the summary table.
- **Observations:**
  - All three beat 14-day seasonal naive by roughly 3.7 to 3.8 MAE.
  - The training mean beat 14-day seasonal naive in 5 of 6 windows and tied
    in one.
  - The weekday profile is only slightly better than the plain mean (7.16
    vs 7.31), consistent with little weekly pattern in the training data.
  - One validation period only; per-window scores vary.
- **Implication:** models should be compared against an MAE of about 7.2 to
  7.3, not only against seasonal naive.

## Planned

- 004: one compact model on calendar features and lags of at least 14 days,
  compared with 003 on the same validation windows.
- 005: prediction intervals from validation residuals, with a coverage check.
- Anomaly detection is evaluated in its own entries once synthetic
  anomalies exist.

<!-- Template for new entries:
### NNN: Short name
**Date:** YYYY-MM-DD · **Code:** path to notebook or script
- **Goal:**
- **Method:**
- **Setup:** differences from the evaluation setup above, if any
- **Results:**
- **Observations:**
- **Next:**
-->