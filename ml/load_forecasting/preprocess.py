from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

LAG_HOURS: Sequence[int] = (1, 2, 3, 6, 12, 24, 48, 168)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["timestamp"])
    df["hour"] = ts.dt.hour
    df["day_of_week"] = ts.dt.dayofweek
    df["month"] = ts.dt.month
    df["day_of_year"] = ts.dt.dayofyear
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)
    df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
    df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)
    df["annual_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
    df["annual_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)
    return df


def build_features(source_path: Path, output_path: Path) -> pd.DataFrame:
    df = pd.read_csv(source_path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df = add_time_features(df)

    for lag in LAG_HOURS:
        df[f"load_lag_{lag}"] = df["load_kw"].shift(lag)

    for window in (3, 24, 168):
        df[f"load_roll_{window}"] = df["load_kw"].rolling(window).mean()

    # Next-hour forecasting target.
    df["target_load_kw"] = df["load_kw"].shift(-1)

    df = df.dropna().reset_index(drop=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


FEATURES = [
    "temperature_c",
    "wind_speed_mps",
    "solar_radiation_wm2",
    "humidity_pct",
    "pressure_hpa",
    "occupancy",
    "heating_load_kw",
    "lab_load_kw",
    "flexible_load_kw",
    "hour",
    "day_of_week",
    "month",
    "day_of_year",
    "hour_sin",
    "hour_cos",
    "day_sin",
    "day_cos",
    "annual_sin",
    "annual_cos",
    *[f"load_lag_{x}" for x in LAG_HOURS],
    "load_roll_3",
    "load_roll_24",
    "load_roll_168",
]
