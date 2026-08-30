from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .model import LoadForecastModel
from .preprocess import LAG_HOURS, add_time_features, FEATURES


def recursive_forecast(history: pd.DataFrame, model: LoadForecastModel, horizon: int) -> pd.DataFrame:
    """Generate a recursive one-step-ahead forecast using the latest state.

    The method keeps lag features consistent by appending each prediction to the
    temporary history. Exogenous variables for the future horizon must already
    exist in `history`; the CLI therefore creates them from the final observations.
    For a production build, pass an actual weather forecast here.
    """
    work = history.copy().sort_values("timestamp").reset_index(drop=True)
    work["timestamp"] = pd.to_datetime(work["timestamp"])
    future_rows = []

    last_ts = work["timestamp"].iloc[-1]
    last_weather = work.iloc[-1].copy()

    for step in range(1, horizon + 1):
        ts = last_ts + pd.Timedelta(hours=step)
        row = last_weather.copy()
        row["timestamp"] = ts

        # Simple demo persistence for exogenous variables. Replace with real
        # weather/operational forecasts before SIH finalization.
        row["temperature_c"] = float(work["temperature_c"].iloc[-1])
        row["wind_speed_mps"] = float(work["wind_speed_mps"].iloc[-1])
        row["solar_radiation_wm2"] = float(work["solar_radiation_wm2"].iloc[-1])
        row["humidity_pct"] = float(work["humidity_pct"].iloc[-1])
        row["pressure_hpa"] = float(work["pressure_hpa"].iloc[-1])
        row["occupancy"] = float(work["occupancy"].iloc[-1])
        row["heating_load_kw"] = float(work["heating_load_kw"].iloc[-1])
        row["lab_load_kw"] = float(work["lab_load_kw"].iloc[-1])
        row["flexible_load_kw"] = float(work["flexible_load_kw"].iloc[-1])
        row["load_kw"] = float(work["load_kw"].iloc[-1])

        temp = pd.DataFrame([row])
        temp = add_time_features(temp)
        temp["load_lag_1"] = work["load_kw"].iloc[-1]
        for lag in LAG_HOURS:
            if lag == 1:
                continue
            temp[f"load_lag_{lag}"] = work["load_kw"].iloc[-lag] if len(work) >= lag else work["load_kw"].iloc[0]
        for window in (3, 24, 168):
            temp[f"load_roll_{window}"] = work["load_kw"].tail(window).mean()

        prediction = float(model.model.predict(temp[FEATURES])[0])
        row["load_kw"] = prediction
        future_rows.append({"timestamp": ts, "forecast_load_kw": prediction})
        work = pd.concat([work, pd.DataFrame([row])], ignore_index=True)

    return pd.DataFrame(future_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AURORA load forecast")
    parser.add_argument("--data", type=Path, default=Path("data/processed/station_energy.csv"))
    parser.add_argument("--model", type=Path, default=Path("models/load_model.joblib"))
    parser.add_argument("--horizon", type=int, default=24)
    parser.add_argument("--output", type=Path, default=Path("artifacts/load_forecast_24h.csv"))
    args = parser.parse_args()

    history = pd.read_csv(args.data, parse_dates=["timestamp"]).sort_values("timestamp")
    model = LoadForecastModel.load(args.model)
    forecast = recursive_forecast(history.tail(168).copy(), model, args.horizon)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    forecast.to_csv(args.output, index=False)
    print(forecast.to_string(index=False))
    print(f"Saved forecast to {args.output}")


if __name__ == "__main__":
    main()
