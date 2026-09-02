from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .model import LoadForecastModel
from .preprocess import FEATURES, add_time_features, LAG_STEPS


def make_feature_row(work: pd.DataFrame, ts: pd.Timestamp) -> pd.DataFrame:
    row = work.iloc[-1].copy()
    row["timestamp"] = ts

    # For real operation, replace these persistence values with a weather forecast.
    # The forecast service should supply the next 96 rows of weather/exogenous data.
    for c in [
        "temperature_c", "wind_speed_ms", "wind_direction_deg", "pressure_mslp",
        "radiation_profile_value", "solar_availability"
    ]:
        row[c] = work[c].iloc[-1]

    temp = pd.DataFrame([row])
    temp = add_time_features(temp)

    for lag in LAG_STEPS:
        temp[f"load_lag_{lag}_15m"] = (
            work["station_load_kw"].iloc[-lag]
            if len(work) >= lag else work["station_load_kw"].iloc[0]
        )

    for window in (4, 16, 96):
        temp[f"load_roll_{window}"] = work["station_load_kw"].tail(window).mean()

    return temp


def recursive_forecast(history: pd.DataFrame, model: LoadForecastModel,
                       horizon: int = 96) -> pd.DataFrame:
    work = history.copy().sort_values("timestamp").reset_index(drop=True)
    work["timestamp"] = pd.to_datetime(work["timestamp"])

    if len(work) < 96:
        raise ValueError("At least 96 historical 15-minute rows are required.")

    output = []
    last_ts = work["timestamp"].iloc[-1]

    for step in range(1, horizon + 1):
        ts = last_ts + pd.Timedelta(minutes=15 * step)
        x = make_feature_row(work, ts)
        pred = float(model.model.predict(x[FEATURES])[0])
        pred = max(0.0, pred)

        row = work.iloc[-1].copy()
        row["timestamp"] = ts
        row["station_load_kw"] = pred
        work = pd.concat([work, pd.DataFrame([row])], ignore_index=True)

        output.append({
            "timestamp": ts,
            "forecast_load_kw": pred,
        })

    return pd.DataFrame(output)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path,
                   default=Path("data/AURORA_Maitri_15min_Forecasting_Dataset.csv"))
    p.add_argument("--model", type=Path,
                   default=Path("models/load_xgb_15min.joblib"))
    p.add_argument("--horizon", type=int, default=96)
    p.add_argument("--output", type=Path,
                   default=Path("artifacts/load_forecast_24h.csv"))
    args = p.parse_args()

    history = pd.read_csv(args.data, parse_dates=["timestamp"])
    model = LoadForecastModel.load(args.model)
    forecast = recursive_forecast(history.tail(200), model, args.horizon)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    forecast.to_csv(args.output, index=False)
    print(forecast.to_string(index=False))
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
