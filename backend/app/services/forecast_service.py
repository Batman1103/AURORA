from __future__ import annotations

from pathlib import Path
import json
import pandas as pd
import numpy as np

from ..core.config import settings
from simulation.simulator import StationSimulator
from ml.load_forecasting.model import LoadForecastModel
from ml.load_forecasting.predict import recursive_forecast
from ml.load_forecasting.preprocess import build_features
from ml.renewable_forecasting.model import (
    RenewableForecastModel,
    add_time_features,
    RENEWABLE_FEATURES,
)


class ForecastService:
    def __init__(self) -> None:
        self.simulator = StationSimulator(settings.dataset_path)
        # Load the three trained models (15-minute resolution)
        self.load_model = LoadForecastModel.load(settings.load_model_path)
        self.solar_model = RenewableForecastModel.load(settings.solar_model_path)
        self.wind_model = RenewableForecastModel.load(settings.wind_model_path)
        self.interval_minutes = 15
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> dict[str, float]:
        path = settings.ml_dir / "artifacts" / "load_metrics.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return {"mae_kw": 0.0, "rmse_kw": 0.0, "mape_pct": 0.0, "r2": 0.0}

    def _hours_to_steps(self, horizon_hours: int) -> int:
        """Convert horizon in hours to number of 15-minute steps."""
        steps = int(max(1, horizon_hours * (60 // self.interval_minutes)))
        return steps

    def load_forecast(self, station: str, horizon: int = 24) -> pd.DataFrame:
        """
        Return load forecast as produced by the load model.

        The `horizon` parameter is provided in hours for backward compatibility
        and converted to 15-minute steps internally (hours * 4).
        """
        steps = self._hours_to_steps(horizon)
        # Provide ample history rows (15-minute rows) required by the model
        history = self.simulator.recent(station, hours=200)
        forecast = recursive_forecast(history, self.load_model, int(steps))
        forecast["station"] = station.lower()
        return forecast

    def _build_future_weather(self, station: str, steps: int) -> pd.DataFrame:
        """
        Build `steps` future 15-minute rows of environmental features required by
        the renewable models. Attempts to use matching timestamps from the
        historical Maitri dataset where possible; otherwise falls back to a
        persistence of the last-observed environmental row.

        TODO: Replace the persistence fallback with a real weather forecast
        provider in production.
        """
        key = station.lower()
        data = self.simulator._data
        if "station" in data.columns:
            subset = data[data["station"].str.lower() == key]
            if subset.empty:
                subset = data
        else:
            subset = data

        subset = subset.sort_values("timestamp").reset_index(drop=True)
        last_row = subset.iloc[-1]
        last_ts = pd.to_datetime(last_row["timestamp"])

        rows = []
        env_cols = [
            "temperature_c",
            "wind_speed_ms",
            "wind_direction_deg",
            "pressure_mslp",
            "radiation_profile_value",
            "solar_availability",
        ]

        for step in range(1, steps + 1):
            ts = last_ts + pd.Timedelta(minutes=self.interval_minutes * step)
            # Try to find a matching historical row for this timestamp
            match = subset[subset["timestamp"] == ts]
            if not match.empty:
                src = match.iloc[0]
                vals = {c: src.get(c, float(last_row.get(c, 0.0))) for c in env_cols}
            else:
                # Persistence fallback (clearly isolated)
                vals = {c: float(last_row.get(c, 0.0)) for c in env_cols}

            row = {"timestamp": ts}
            row.update(vals)
            rows.append(row)

        df = pd.DataFrame(rows)
        return df

    def renewable_forecast(self, station: str, horizon: int = 24) -> pd.DataFrame:
        """
        Produce renewable forecasts (solar_kw, wind_kw) for the given station.

        `horizon` is in hours for API compatibility; converted to 15-minute steps.
        """
        steps = self._hours_to_steps(horizon)

        future_weather = self._build_future_weather(station, steps)

        # Prepare features and predict using renewable models
        future_feats = add_time_features(future_weather.copy())

        # Solar
        solar_pred = self.solar_model.predict(future_feats[self.solar_model.features])
        solar_pred = np.clip(np.array(solar_pred, dtype=float), 0.0, 500.0)

        # Wind
        wind_pred = self.wind_model.predict(future_feats[self.wind_model.features])
        wind_pred = np.clip(np.array(wind_pred, dtype=float), 0.0, 500.0)

        out = pd.DataFrame({
            "timestamp": future_feats["timestamp"].values,
            "solar_kw": solar_pred,
            "wind_kw": wind_pred,
        })

        return out

    def combined_forecast(self, station: str, horizon: int = 24) -> pd.DataFrame:
        load = self.load_forecast(station, horizon).rename(columns={"forecast_load_kw": "load_kw"})
        renewable = self.renewable_forecast(station, horizon)
        merged = load.merge(renewable, on="timestamp", how="left")
        history = self.simulator.latest(station)
        merged["critical_load_kw"] = min(float(history["critical_load_kw"]), float(merged["load_kw"].iloc[0]))
        merged["flexible_load_kw"] = float(history["flexible_load_kw"])
        return merged
