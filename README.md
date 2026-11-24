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

### Success criteria
Set on 2026-11-24, before any model was scored.

- **Bar:** the weekday-profile baseline on validation, MAE 7.16 and WAPE
  9.12%. It is the strongest simple baseline and never loses to the plain
  mean.
- **Better:** validation MAE at least 0.10 below the bar and lower in at
  least 4 of the 6 14-day windows.
- **Tied:** within 0.10 of the bar either way. A tie is reported as a tie.
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