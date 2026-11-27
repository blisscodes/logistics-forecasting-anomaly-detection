# Predictive Analytics & Anomaly Detection for Logistics Operations

Forecasts company-wide daily load volume 14 days ahead and flags unusual
delivery operations (late deliveries, detention time, volume drops), using a
synthetic trucking database. Portfolio project.

**Status:** in progress. Data inventory, baseline forecasts, calendar and lag
features, and a feature pipeline are done; modeling is next. Last updated
2026-11-20.

## Scope

### Forecast target
Forecast the company-wide number of loads per day (one row per `load_date`
in `loads.csv`) for the next 14 days, with a prediction interval.
Route-level forecasting is out of scope because route-day counts are sparse
(about 26% of route-days have zero loads).

### Evaluation
Data is split chronologically: train 2022-01-01 to 2024-07-16, validation
2024-07-17 to 2024-10-08 (84 days), test 2024-10-09 to 2024-12-31 (84 days).
Models are compared on validation using MAE and WAPE against a weekly
seasonal-naive baseline and a training-mean baseline. The test period is
scored once, after the model is chosen.

### Prediction intervals
Each forecast comes with an 80% interval: the forecast plus the 10th and
90th percentiles of the final model's validation errors (about -10.8 and
+12.5 loads). The width is the same for every day. Calibrating on one half of
the validation period and checking on the other gave coverage of 69% and 86%
against a nominal 80%. The intervals assume future errors look like the 84
validation errors and do not adapt to unusual days.

### Success criteria
Set on 2026-11-24, before any model was scored.

- **Bar:** the weekday-profile baseline on validation, MAE 7.16 and WAPE
  9.12%. It is the strongest simple baseline and never loses to the plain
  mean.
- **Better:** validation MAE at least 0.10 below the bar and lower in at
  least 4 of the 6 14-day windows.
- **Tied:** within 0.10 of the bar either way, or at least 0.10 lower but
  lower in fewer than 4 windows. A tie is reported as a tie.
- **Worse:** anything else.
- **Check first:** an MAE below 6.8 is under the estimated noise floor and
  is treated as a possible leak until shown otherwise.
- Every result is also reported against seasonal naive (MAE 10.98) and the
  plain mean (MAE 7.31).

### Anomaly evaluation
The dataset has no anomaly labels, so detectors are scored on anomalies
injected into a copy of the data with a fixed seed (`SEED = 42`). Each
injected anomaly is a window of consecutive days affecting one signal (for
example, load volume down 30% for 5 days).

- **Alert:** a day on which the detector flags a signal.
- **Correct alert:** an alert on the same signal on a day inside an
  injected window.
- **Precision:** correct alerts divided by all alerts.
- **Recall:** injected windows with at least one correct alert, divided by
  all injected windows.
- **Alert budget:** at most 10 alerts per day (initial design target, to be
  evaluated, not a proven capability).

Windows are scored as a whole, so catching any day of a multi-day anomaly
counts as detecting it. The injection settings are fixed before the detector
is built, so the detector is not tuned to the injection. Thresholds are set
on the training period and scored on validation. Injected anomalies make
these estimates optimistic; they say nothing about real operations.

### Anomaly definition
A day is flagged when a daily signal deviates strongly from its recent norm:
late-delivery rate and detention time (`delivery_events.csv`), safety
incidents and damage costs (`safety_incidents.csv`), or load volume
(`loads.csv`). Lateness is computed from `scheduled_datetime` and
`actual_datetime`; `on_time_flag` is not treated as ground truth.
The alert budget is at most 10 alerts per day. This is a design target to
evaluate, not a proven capability.

### Out of scope
- Route- or region-level forecasts
- Real-time streaming
- Publishing raw or processed data
- Using driver names, license numbers, dates of birth, or fuel-card
  numbers as features

## Data
Dataset: *Logistics Operations Database (2022–2024)* by `yogape` on Kaggle
(`yogape/logistics-operations-database`). It simulates a fictional Class 8
trucking company: 14 related CSV tables plus `DATABASE_SCHEMA.txt`. The
Kaggle page lists an MIT license; the archive itself does not state one.

The data is not included in this repository. To reproduce, download it from
Kaggle and extract the files into `data/raw/`.

The tables contain synthetic personal-looking fields (driver names, license
numbers, dates of birth, fuel-card numbers). They are not used as features
and are never published.

Record counts in the Kaggle description differ from the archive (for
example, 57,000+ loads described vs 85,410 in the archive); this project
uses the archive as provided.

## Setup
Requires Python 3.11 (developed on Windows, PowerShell).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then place the extracted dataset in `data/raw/` and open the notebooks in
`notebooks/`.

Build the features file (writes `data/processed/features.csv`):

```powershell
python -m src.pipeline
```

Run the tests:

```powershell
python -m pytest
```

Developed with Python 3.11.0. Exact package versions are pinned in
`requirements.txt`.

## Repository structure
```text
data/        raw and processed data (not tracked by Git)
notebooks/   exploration and experiments
src/         data loading, features, and the pipeline
tests/       tests (planned)
app/         API and dashboard (planned)
docs/        data_dictionary.md, experiment_log.md
```

## Limitations
- The data is synthetic, so results describe this simulation, not real
  operations.
- Daily load volume shows only a weak weekday effect and no seasonal or
  yearly pattern in the training period, so a simple average is a strong
  baseline.
- `on_time_flag` marks an event as on time only when it falls within 120
  minutes of schedule in either direction, so it mixes early and late
  arrivals. Lateness is computed from `scheduled_datetime` and
  `actual_datetime` instead.
- The dataset has no anomaly labels. Anomaly evaluation will use injected
  anomalies, which gives an optimistic estimate.
- Delay and detention values appear uniformly distributed rather than
  clustered around typical values, which is characteristic of a simulation;
  anomaly evaluation relies on injected anomalies.
- The dataset description states that timestamps are properly sequenced,
  but 0.6% of loads (mostly on two short New York–Philadelphia routes) have
  delivery recorded before pickup.

## Results

Forecast of company-wide daily loads, 14 days ahead. MAE is the average miss
in loads per day (lower is better), on the 84-day validation period.

| Method | MAE | WAPE |
|---|---:|---:|
| Weekly seasonal naive (14-day) | 10.98 | 13.98% |
| Plain training mean | 7.31 | 9.31% |
| **Weekday profile (final model)** | **7.16** | **9.12%** |
| Gradient boosting, depth 3 (best learned model) | 7.13 | 9.08% |
| Ridge, all features | 7.33 | 9.33% |

Eleven runs were tracked in `reports/experiment_runs.csv`. None beat the
weekday profile by the pre-set margin (0.10), so the simplest model was kept.
Daily volume behaves like random counts around a stable average with a weak
weekday effect, which is why seasonal naive is the clear loser and learned
models cannot improve on a weekday average.

**Test period (scored once):** MAE 7.24, interval coverage 0.81.

Forecast with the saved model:

```powershell
python -m src.predict --start 2025-01-01
```

Each forecast comes with an 80% interval of about -10.8 to +12.5 loads.

### Injected anomalies
Three types are injected into a copy of the validation signals (daily load
volume, late-delivery rate, and average detention):

| Type | Change | Length | Size in typical day-to-day variation |
|---|---|---|---|
| Volume drop | 20% fewer loads | 5 days | about 1.8 |
| Late-rate spike | +10 percentage points | 4 days | about 1.8 |
| Detention rise | +30 minutes | 5 days | about 3.4 |

Each draw places two windows per type, at least 7 days apart within a type,
using a fixed seed; results are averaged over 20 draws (seeds 42 to 61). The
injection settings were fixed on 2026-11-28, before the detector was built,
and are not changed afterward. The original signals are never modified, and
the labels are stored separately from all training and feature data.

### Anomaly detector
For each signal, a day's score is how many typical day-to-day variations it
sits from the training median (robust, using the median absolute deviation)
in the harmful direction (volume down, late rate up, detention up), averaged
over 3 days. A signal alerts when its score exceeds the 99th percentile of the
same score on the clean training days (volume 1.26, late rate 1.26,
detention 1.35). On clean training days this raises about 1.1% of signal-days
(30 of 2,763). Thresholds were frozen on 2026-11-28 before any evaluation on
the injected validation data.

### Anomaly detection results
The frozen detector (thresholds set on clean training days) was scored on 20
random draws of injected anomalies in the validation signals (120 windows):

| Signal | Windows detected | Alerts | Correct alerts | Precision |
|---|---:|---:|---:|---:|
| Volume drop (20%, 5 days) | 39 of 40 | 133 | 117 | 0.88 |
| Late-rate spike (+10 points, 4 days) | 38 of 40 | 119 | 95 | 0.80 |
| Detention rise (+30 minutes, 5 days) | 40 of 40 | 215 | 161 | 0.75 |
| **All** | **117 of 120 (0.98)** | 467 | 373 | **0.80** |

All 94 alerts counted as false fell within two days after a window ended (the
3-day average carries an anomaly forward); none fell on days away from an
anomaly. On validation days with no injection the detector raised no alerts
(0 of 252 signal-days). At most 3 alerts can fire per day, under the budget of
10.

Limitations: anomalies are simple step changes in daily totals; the 20 draws
reuse the same 84 days and are not independent; the data contains no real
anomalies, so the real false-alarm rate is unknown; alerts echo for two days
after an anomaly; smaller anomalies than those injected would be missed;
signals are company-wide, so alerts cannot say which route or region; and the
detector is not yet connected to the API or dashboard.