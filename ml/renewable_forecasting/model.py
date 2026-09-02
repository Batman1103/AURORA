from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import joblib
import pandas as pd
from xgboost import XGBRegressor


RENEWABLE_FEATURES = [
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
]


@dataclass
class RenewableForecastModel:
    model: XGBRegressor
    source: str
    target: str
    features: list[str]

    def predict(self, frame: pd.DataFrame):
        return self.model.predict(frame[self.features]).astype(float)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "source": self.source,
            "target": self.target,
            "features": self.features,
            "interval_minutes": 15,
        }, path)

    @classmethod
    def load(cls, path: Path):
        x = joblib.load(path)
        return cls(x["model"], x["source"], x["target"], x["features"])


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["timestamp"])
    df["hour"] = ts.dt.hour
    df["minute"] = ts.dt.minute
    df["month"] = ts.dt.month
    df["day_of_year"] = ts.dt.dayofyear
    mins = df.hour * 60 + df.minute
    import numpy as np
    df["hour_sin"] = np.sin(2*np.pi*mins/(24*60))
    df["hour_cos"] = np.cos(2*np.pi*mins/(24*60))
    df["doy_sin"] = np.sin(2*np.pi*df.day_of_year/365.25)
    df["doy_cos"] = np.cos(2*np.pi*df.day_of_year/365.25)
    return df


def make_model(target: str, seed: int = 42) -> RenewableForecastModel:
    model = XGBRegressor(
        n_estimators=450,
        max_depth=6,
        learning_rate=0.05,
        min_child_weight=3,
        subsample=0.85,
        colsample_bytree=0.90,
        objective="reg:squarederror",
        tree_method="hist",
        n_jobs=4,
        random_state=seed,
    )
    return RenewableForecastModel(model, "Maitri simulation", target,
                                  list(RENEWABLE_FEATURES))
