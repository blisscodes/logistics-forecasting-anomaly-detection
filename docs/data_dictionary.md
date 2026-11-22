# Data Dictionary

Last updated 2026-11-22. Counts and ranges cover the full archive; shares,
averages, and patterns come from the training period unless noted.

## Dataset overview

- **Dataset:** Logistics Operations Database (2022-2024)
- **Source:** Kaggle, `yogape/logistics-operations-database`. The Kaggle page
  lists an MIT license; the archive itself does not state one.
- **Type:** synthetic simulation of a fictional Class 8 trucking company
- **Coverage:** 2022-01-01 to 2024-12-31 (1,096 consecutive days; every day
  has at least one load)
- **Scale:** 85,410 loads, 170,820 delivery events, 58 routes
- **Files:** 14 CSV tables plus `DATABASE_SCHEMA.txt`. The data is not
  included in this repository; see the README for setup.

## Table inventory

Descriptions come from the Kaggle page and `DATABASE_SCHEMA.txt`. Row counts
are from the archive and differ from the Kaggle description for several
tables (see Data quality notes).

| Table | Description | Rows | Notes |
|---|---|---:|---|
| drivers | Demographics, employment history, CDL information | 150 | Personal-looking fields; not used |
| trucks | Fleet specifications, acquisition dates, status | 120 | Not yet inspected |
| trailers | Equipment types and assignments | 180 | Not yet inspected |
| customers | Shipper accounts and contract terms | 200 | Not yet inspected |
| facilities | Terminals and warehouses with coordinates | 50 | Not yet inspected |
| routes | City pairs with distances and rate structures | 58 | Used for route grouping checks |
| loads | Shipment details, revenue, booking type | 85,410 | Primary table; source of the forecast target |
| trips | Driver-truck assignments and actual performance | 85,410 | One trip per load |
| fuel_purchases | Transaction-level fuel purchases | 196,442 | Contains fuel-card numbers; not used |
| maintenance_records | Service history, costs, downtime | 2,920 | Not yet inspected |
| delivery_events | Pickup and delivery timestamps, detention | 170,820 | One pickup and one delivery per load |
| safety_incidents | Accidents, violations, damage costs, claims | 170 | Candidate anomaly signal |
| driver_monthly_metrics | Monthly driver performance summaries | 4,464 | Not yet inspected |
| truck_utilization_metrics | Monthly equipment efficiency | 3,312 | Not yet inspected |

## Column definitions

Only tables used so far are documented; others are added when inspected.

### loads

| Column | Type | Description | Notes |
|---|---|---|---|
| `load_id` | string | Unique load identifier | Primary key |
| `customer_id` | string | Customer who booked the load | Foreign key to `customers`; no orphans found |
| `route_id` | string | Route used | Foreign key to `routes`; 58 distinct routes |
| `load_date` | date | Date of the load | Stored as text; parsed to a date. Counting rows per date gives the daily forecast target |
| `load_type` | string | Type of load | To verify |
| `weight_lbs` | number | Load weight in pounds | To verify range |
| `pieces` | number | Number of pieces | To verify |
| `revenue` | number | Load revenue in USD | To verify |
| `fuel_surcharge` | number | Fuel surcharge | To verify |
| `accessorial_charges` | number | Additional charges | To verify |
| `load_status` | string | Load status | Always `Completed` |
| `booking_type` | string | Booking type | To verify |

### delivery_events

| Column | Type | Description | Notes |
|---|---|---|---|
| `event_id` | string | Unique event identifier | Primary key |
| `load_id` | string | Load the event belongs to | Foreign key to `loads`, no orphans found; exactly one Pickup and one Delivery per load |
| `trip_id` | string | Trip the event belongs to | Foreign key to `trips`; one trip per load |
| `event_type` | string | `Pickup` or `Delivery` | |
| `facility_id` | string | Facility where the event occurred | Foreign key to `facilities` |
| `scheduled_datetime` | datetime | Scheduled time of the event | `YYYY-MM-DD HH:MM:SS.ffffff`, no timezone |
| `actual_datetime` | datetime | Actual time of the event | Same format as above |
| `detention_minutes` | integer | Detention time in minutes (waiting at the facility) | Range 0 to 239 (delivery), 0 to 179 (pickup); free-time rule not documented |
| `on_time_flag` | boolean | Whether the event counted as on time | True exactly when the absolute delay is 120 minutes or less; not used as a lateness label |
| `location_city`, `location_state` | string | Event location | To verify |

### Derived fields (defined by this project)

| Field | Definition | Notes |
|---|---|---|
| Daily load count | Number of `loads` rows per `load_date` | Forecast target, about 78 per day |
| `delay_min` | `actual_datetime` minus `scheduled_datetime`, in minutes | Positive means after schedule |
| Late | `delay_min` greater than 120 | 44.4% of deliveries and 33.3% of pickups in the training period |
| Early | `delay_min` less than -120 | 10.9% of deliveries and none of the pickups in the training period |

## Data quality notes

| Issue | Evidence | Handling |
|---|---|---|
| About 2% of IDs are null | `trips`: `driver_id` 1,714, `truck_id` 1,672, `trailer_id` 1,680. `fuel_purchases`: `driver_id` 3,988, `truck_id` 3,880. `safety_incidents`: 1 each | Not imputed; not needed for the target |
| `drivers.termination_date` is 82.7% null | 124 of 150 drivers | Legitimate: active drivers have no termination date |
| No duplicate rows | Checked on all 14 tables | None needed |
| `on_time_flag` mixes early and late | Equals absolute delay at most 120 minutes on both event types (training period) | Use the late and early definitions above |
| Delivery recorded before pickup | 486 loads (0.57%) by actual time; 175 by scheduled time. 467 of the 486 are on RTE00010 and RTE00015 (New York to Philadelphia, 92 miles) | Flag; exclude from duration features only. Timezones and multi-stop loads ruled out (one trip per load) |
| Timestamps have no timezone | No offset in the strings; scheduled gap shows no shift across time zones | Treat all times as one consistent clock |
| Delay and detention are uniformly distributed | Delivery delay -180 to +360 min, pickup -120 to +240; detention has a spike at 0 | Characteristic of a simulation; anomalies must be injected for evaluation |
| Archive differs from the Kaggle description | Transaction tables are about 1.5x the described sizes (85,410 vs 57,000+ loads); sequencing, on-time rate, and seasonality claims not seen | Treat the archive as the source of truth |

## Modeling considerations

- **Target:** company-wide daily load count. Splits and metrics are in the
  README.
- **Weak weekday effect, no seasonality:** weekday means range from 76.4
  (Sunday) to 80.0 (Tuesday), which is statistically detectable (p = 0.008)
  but explains about 2% of daily variance. There is no monthly pattern
  (p = 0.72), no Q4 peak, and no yearly trend (training-period means 78.3,
  77.2, 78.6). Simple averages are hard to beat; a weekday term may help
  slightly.
- **Routes are sparse:** 26% of route-days have zero loads (1.34 loads per
  route-day). Grouping by origin state also shows no signal beyond noise, so
  forecasts stay at the company level.
- **Anomaly signals available:** late and early rates and detention
  (`delivery_events`), incident and damage fields (`safety_incidents`:
  `incident_type`, `vehicle_damage_cost`, `cargo_damage_cost`,
  `claim_amount`), and daily volume. There is no customer-complaint field.
- **Not used as features:** driver names, license numbers, dates of birth,
  and fuel-card numbers.