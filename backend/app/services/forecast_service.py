from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

from ..core.config import settings
from simulation.simulator import StationSimulator
from ml.load_forecasting.model import LoadForecastModel
from ml.load_forecasting.predict import recursive_forecast
from ml.load_forecasting.preprocess import build_features
from ml.renewable_forecasting.solar import clear_sky_irradiance, solar_power_from_irradiance
from ml.renewable_forecasting.wind import turbine_power_from_wind


class ForecastService:
    def __init__(self) -> None:
        self.simulator = StationSimulator(settings.dataset_path)
        self.model = LoadForecastModel.load(settings.load_model_path)
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> dict[str, float]:
        path = settings.ml_dir / "artifacts" / "load_metrics.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return {"mae_kw": 0.0, "rmse_kw": 0.0, "mape_pct": 0.0, "r2": 0.0}

    def load_forecast(self, station: str, horizon: int = 24) -> pd.DataFrame:
        history = self.simulator.recent(station, hours=168)
        forecast = recursive_forecast(history, self.model, max(1, min(168, horizon)))
        forecast["station"] = station.lower()
        return forecast

    def renewable_forecast(self, station: str, horizon: int = 24) -> pd.DataFrame:
        history = self.simulator.latest(station)
        start = pd.Timestamp(history["timestamp"]) + pd.Timedelta(hours=1)
        rows = []
        wind_seed = float(history["wind_speed_mps"])
        for step in range(horizon):
            ts = start + pd.Timedelta(hours=step)
            irr = clear_sky_irradiance(int(ts.dayofyear), float(ts.hour))
            solar = solar_power_from_irradiance(irr, capacity_kw=45.0)
            # Slightly vary the persisted wind input to avoid a flat line while remaining deterministic.
            wind_speed = max(0.0, wind_seed + 1.4 * __import__("math").sin(step / 3.2))
            wind = turbine_power_from_wind(wind_speed, capacity_kw=70.0)
            rows.append({"timestamp": ts, "solar_kw": solar, "wind_kw": wind})
        return pd.DataFrame(rows)

    def combined_forecast(self, station: str, horizon: int = 24) -> pd.DataFrame:
        load = self.load_forecast(station, horizon).rename(columns={"forecast_load_kw": "load_kw"})
        renewable = self.renewable_forecast(station, horizon)
        merged = load.merge(renewable, on="timestamp", how="left")
        history = self.simulator.latest(station)
        merged["critical_load_kw"] = min(float(history["critical_load_kw"]), float(history["load_kw"]))
        merged["flexible_load_kw"] = float(history["flexible_load_kw"])
        return merged
