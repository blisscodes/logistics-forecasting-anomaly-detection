# Model review: drivers and error patterns

Applies to the final model, the weekday profile (`weekday_profile_v1`). Numbers
come from the training and validation periods unless stated; the test period
was scored once, in the experiment log. The data is synthetic, so every finding
describes this simulated dataset, not real operations.

## Main drivers
The final model has one input: the weekday of the forecast date. Training-period
averages with approximate 95% ranges:

| Day | Mean loads | Range |
|---|---:|---|
| Mon | 78.4 | 76.9 to 79.9 |
| Tue | 80.0 | 78.5 to 81.4 |
| Wed | 76.9 | 75.5 to 78.4 |
| Thu | 78.9 | 77.5 to 80.4 |
| Fri | 77.5 | 76.2 to 78.9 |
| Sat | 77.2 | 75.8 to 78.7 |
| Sun | 76.4 | 74.9 to 77.9 |

Tuesday is associated with the highest volume and Sunday with the lowest (a
gap of 3.6 loads), but most neighboring ranges overlap, and the weekday
accounts for only about 2% of day-to-day variation.

The learned models (gradient boosting) relied most on recent-level inputs: the
7-day and 28-day averages and the 14- and 21-day lags. Shuffling the 7-day
average worsened MAE by 0.48 on training days and 0.23 on validation days.

## Error patterns
Errors of the final model on the training and validation days (1,012 days):
MAE 6.72 and an average error of +0.05 (no overall bias).

- **By weekday:** MAE ranges from 6.13 (Friday) to 7.02 (Monday). The spread of
  errors is similar across weekdays (standard deviation 7.7 to 8.8), so one
  interval width fits all days.
- **By season:** monthly MAE ranges from 5.45 (December) to 7.61 (June);
  quarterly MAE from 6.32 to 7.03. December's average error is -2.17 loads, but
  it rests on 62 days and is about what chance produces when comparing 12
  months.
- **Holidays and month-ends:** holidays have MAE 7.86 against 6.69 on other
  days (28 holidays); month-ends have an average error of -2.13 (33 days).
  Both samples are small and within ordinary noise.
- **Largest misses:** five days with errors of 24 to 31 loads (for example
  2022-05-18: 108 actual against a forecast of 76.9). About 8.2% of days miss
  by more than 15 loads, which is what random variation of this size produces
  (about 7.8%).
- **Route and region:** forecast errors are essentially unrelated to the daily
  mix of origin states or the average route distance (correlations between
  -0.08 and +0.06). This is a company-wide model, so errors cannot be measured
  per route.

## Follow-up fixes (not done)
1. Refit the weekday profile on more data as a new version (v2) when new
   periods arrive, keeping the one-look rule for any test period.
2. Alert echoes: each injected anomaly produced up to two extra alerts after it
   ended (the 3-day average). Try a shorter average, or alert on the first day
   only, on fresh injected draws, without reusing the draws that revealed it.
3. Check holidays and month-ends on more years; about 30 days each is too few to
   judge an effect.
4. Add route- or region-level signals for anomalies so an alert can say where a
   problem is; the forecast and current alerts are company-wide.
5. Validate on real operational data; every finding here describes a
   simulation.
6. Show the weekday explanation and the 80% interval in the dashboard
   (Dashboard and API milestone).