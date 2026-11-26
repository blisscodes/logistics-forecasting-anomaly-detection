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
- **Metrics**:
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
| 004 | 2026-11-26 | Ridge (alpha 10), 18 features | 14-day | 7.33 | 9.33% | Done |
| 005 | 2026-11-26 | Ridge (alpha 10), 12 calendar features | 14-day | 7.28 | 9.28% | Done |
| 006 | 2026-11-26 | HistGradientBoosting (depth 3, rate 0.05, 200 iterations), 18 features | 14-day | 7.13 | 9.08% | Done |
| 007a | 2026-11-26 | Ridge (alpha 1), 18 features | 14-day | 7.32 | 9.33% | Done |
| 007b | 2026-11-26 | Ridge (alpha 100), 18 features | 14-day | 7.32 | 9.32% | Done |
| 007c | 2026-11-26 | Ridge (alpha 1000), 18 features | 14-day | 7.30 | 9.30% | Done |
| 008a | 2026-11-26 | HistGradientBoosting (depth 2), 18 features | 14-day | 7.17 | 9.13% | Done |
| 008b | 2026-11-26 | HistGradientBoosting (depth 4), 18 features | 14-day | 7.24 | 9.23% | Done |

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

### 004: Ridge, all features

**Date:** 2026-11-26 · **Code:** `notebooks/01_inventory.ipynb`

- **Goal:** first compact model on calendar and lag features.
- **Method:** standardized features, Ridge with alpha 10, fit on train only
  (887 rows), scored on the six validation windows.
- **Results:** MAE 7.33, WAPE 9.33%. Lower than 3 of 6 windows against the
  bar.
- **Observations:**
  - Worse than the bar (7.16) by the success rule, but the gap (about 0.17)
    is only about 1.5 times the window-to-window noise.
  - Much better than seasonal naive (10.98) and about equal to the plain mean
    (7.31).
  - Training MAE 6.69 is below the estimated noise floor, so the model fits
    noise. Its largest weights were month and day-of-year terms, which EDA
    found carry no seasonality.
- **Next:** the fixed experiment set (WB26).

### 005: Ridge, calendar features only

**Date:** 2026-11-26 · **Code:** `notebooks/01_inventory.ipynb`

- **Goal:** test whether lag and rolling features add anything.
- **Results:** MAE 7.28, WAPE 9.28%; lower than the bar in 2 of 6 windows.
- **Observations:** removing the lag features changed MAE from 7.33 to 7.28,
  so they did not help. Still worse than the bar (7.16).

### 006: Gradient boosting, all features

**Date:** 2026-11-26 · **Code:** `notebooks/01_inventory.ipynb`

- **Goal:** test whether a nonlinear model finds structure Ridge cannot.
- **Method:** depth 3, learning rate 0.05, 200 iterations, seed 42.
- **Results:** MAE 7.13, WAPE 9.08%; lower than the bar in 2 of 6 windows.
- **Observations:** tied with the bar (within 0.10). No evidence of structure
  beyond the weekday effect.

### 007: Ridge strength

**Date:** 2026-11-26 · **Code:** `notebooks/01_inventory.ipynb`

- **Goal:** test whether stronger regularization fixes the overfitting seen in 004.
- **Method:** same as 004 with alpha 1, 100, and 1000.
- **Results:** MAE 7.32, 7.32, and 7.30 (004 was 7.33 at alpha 10).
- **Observations:** a thousandfold change in strength moved MAE by 0.03, so
  regularization is not the limiting factor. All three are rated worse than
  the bar (7.16).

### 008: Gradient boosting depth

**Date:** 2026-11-26 · **Code:** `notebooks/01_inventory.ipynb`

- **Goal:** test whether tree depth matters.
- **Method:** as 006 with depth 2 and 4.
- **Results:** MAE 7.17 (depth 2) and 7.24 (depth 4); 006 at depth 3 was 7.13.
- **Observations:** all three depths are within 0.10 of the bar and rated
  tied; depth has no meaningful effect.

### Comparison of runs 002-008

- No run is rated better than the weekday-profile bar (7.16). Four runs are
  tied with it (003c, 006, 008a, 008b); the rest are worse.
- Splitting validation into two halves, the ranking of runs barely agrees
  (rank correlation 0.05): the weekday profile was best in the first half and
  eighth in the second. Differences among runs other than seasonal naive are
  noise.
- Seasonal naive is last in both halves; that difference is real.

## Planned experiments (fixed on 2026-11-26, before running)

Question: does anything beat the weekday-profile bar (validation MAE 7.16)?
All runs use the same split, the same 18 features unless stated, and
`SEED = 42`. The test period is not scored until the final model is chosen.

## Experiment set (completed 2026-11-26)

| ID | Model | Features | Settings | Validation MAE | Verdict |
|---|---|---|---|---:|---|
| 004 | Ridge (standardized) | 18 | alpha 10 | 7.33 | worse |
| 005 | Ridge (standardized) | 12 calendar | alpha 10 | 7.28 | worse |
| 006 | HistGradientBoosting | 18 | depth 3, rate 0.05, 200 iterations | 7.13 | tied |
| 007a-c | Ridge (standardized) | 18 | alpha 1, 100, 1000 | 7.32, 7.32, 7.30 | worse |
| 008a-b | HistGradientBoosting | 18 | depth 2, 4 | 7.17, 7.24 | tied |

**Final model:** weekday profile (validation MAE 7.16, WAPE 9.12%).

**Stop rule:** no runs beyond this table, no new features, and no test
scoring.

**Choosing the final model:** take the run rated better with the lowest
validation MAE (ties among better runs go to the simpler model). If no run is
rated better, the weekday-profile baseline is the final model. The choice and
a one-line reason go in the decision log.

### T1: Final model on the test period

**Date:** 2026-11-26 · **Code:** `notebooks/01_inventory.ipynb`

- **Goal:** one-time check of the final model on data never used for choices.
- **Method:** weekday profile fit on train; 80% interval offsets from
  validation residuals; baselines scored the same way.
- **Results:** final model MAE 7.24, WAPE 9.35%; training mean MAE 7.17; seasonal
  naive MAE 10.77; interval coverage 0.81.
- **Observations:** compared with validation (MAE 7.16) and the ranges set
  before scoring: ___.
- **Note:** test scored once; nothing changed afterward.

**Later:** prediction intervals from validation residuals, after the final
model is chosen.

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