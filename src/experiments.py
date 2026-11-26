# Fit a model on train, score it on validation, and log the run.
# The test table is never passed in, so it cannot be used by accident.
import pandas as pd

from src.metrics import scores, windows_won
from src.tracking import log_run

CALENDAR_COLUMNS = ["dow", "month", "week", "doy", "is_month_end", "is_holiday",
                    "dow_sin", "dow_cos", "month_sin", "month_cos",
                    "doy_sin", "doy_cos"]
LAG_COLUMNS = ["lag_14", "lag_21", "lag_28", "roll_mean_7", "roll_mean_28",
               "roll_std_28"]


def run_experiment(run_id, model_name, model, feature_set, feature_cols,
                   settings, tables, bar_pred, notes="", path=None):
    train, valid = tables["train"], tables["valid"]
    model.fit(train[feature_cols], train["loads"])
    pred = pd.Series(model.predict(valid[feature_cols]), index=valid.index)
    valid_mae, valid_wape = scores(valid["loads"], pred)
    won = windows_won(valid["loads"], pred, bar_pred)
    kwargs = {} if path is None else {"path": path}
    log_run(run_id, model_name, feature_set, settings, valid_mae, valid_wape,
            won, notes, **kwargs)
    return pred, valid_mae, valid_wape, won