from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from .model import RenewableForecastModel, add_time_features, RENEWABLE_FEATURES


def forecast_with_future_weather(
    current_history: pd.DataFrame,
    future_weather: pd.DataFrame,
    model: RenewableForecastModel,
) -> pd.DataFrame:
    """
    Forecast 15-minute renewable generation.

    future_weather MUST contain 96 future rows with the environmental features.
    In production these should come from a weather forecast service/model.
    """
    future = add_time_features(future_weather.copy().sort_values("timestamp"))
    pred = model.predict(future[RENEWABLE_FEATURES])
    pred = np.clip(pred, 0, None)

    return pd.DataFrame({
        "timestamp": future["timestamp"].values,
        f"forecast_{model.target}": pred,
    })


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--future-weather", type=Path, required=True,
                   help="CSV containing the next 96 15-minute weather/exogenous rows")
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    future = pd.read_csv(args.future_weather, parse_dates=["timestamp"])
    if len(future) < 96:
        raise ValueError("Need at least 96 future 15-minute rows.")
    future = future.head(96)

    model = RenewableForecastModel.load(args.model)
    out = forecast_with_future_weather(pd.DataFrame(), future, model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)
    print(out.to_string(index=False))
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
