from __future__ import annotations

from typing import Sequence
import numpy as np
import pandas as pd

# At 15-minute resolution these are numbers of 15-minute intervals.
LAG_STEPS: Sequence[int] = (1, 4, 16, 96)

FEATURES = [
    "temperature_c",
    "wind_speed_ms",
    "wind_direction_deg",
    "pressure_mslp",
    "radiation_profile_value",
    "solar_availability",
    "hour",
    "minute",
    "month",
    "day_of_year",
    "hour_sin",
    "hour_cos",
    "doy_sin",
    "doy_cos",
    *[f"load_lag_{x}_15m" for x in LAG_STEPS],
    "load_roll_4",
    "load_roll_16",
    "load_roll_96",
]


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["timestamp"])
    df["hour"] = ts.dt.hour
    df["minute"] = ts.dt.minute
    df["month"] = ts.dt.month
    df["day_of_year"] = ts.dt.dayofyear

    minutes = df["hour"] * 60 + df["minute"]
    df["hour_sin"] = np.sin(2 * np.pi * minutes / (24 * 60))
    df["hour_cos"] = np.cos(2 * np.pi * minutes / (24 * 60))
    df["doy_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_time_features(df.sort_values("timestamp").reset_index(drop=True))

    for lag in LAG_STEPS:
        df[f"load_lag_{lag}_15m"] = df["station_load_kw"].shift(lag)

    for window in (4, 16, 96):
        df[f"load_roll_{window}"] = (
            df["station_load_kw"].rolling(window).mean()
        )

    # Predict the NEXT 15-minute load, not the current value.
    df["target_load_kw"] = df["station_load_kw"].shift(-1)

    return df.dropna(subset=FEATURES + ["target_load_kw"]).reset_index(drop=True)


def load_training_data(path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    required = {
        "timestamp", "station_load_kw", "temperature_c", "wind_speed_ms",
        "wind_direction_deg", "pressure_mslp",
        "radiation_profile_value", "solar_availability"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    return build_features(df)
