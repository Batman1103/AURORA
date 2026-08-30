from __future__ import annotations

from ..core.config import settings
from .forecast_service import ForecastService
from .state_service import state_service


class DashboardService:
    def __init__(self, forecast_service: ForecastService):
        self.forecast = forecast_service

    def snapshot(self, station: str) -> dict:
        row = self.forecast.simulator.latest(station)
        state = state_service.get(station)
        load = float(row["load_kw"])
        solar = float(row["solar_kw"])
        wind = float(row["wind_kw"])
        renewable_pct = min(100.0, (solar + wind) / max(load, 1e-6) * 100.0)
        daily_consumption = max(1.0, load * 24 * settings.generator_fuel_l_per_kwh * 0.55)
        days = state.fuel_litres / daily_consumption
        return {
            "station": station,
            "timestamp": row["timestamp"].isoformat(),
            "loadKw": round(load, 2),
            "batterySoc": round(state.battery_soc, 1),
            "fuelLitres": round(state.fuel_litres, 0),
            "renewablePct": round(renewable_pct, 1),
            "daysToExhaustion": round(days, 0),
            "solarKw": round(solar, 2),
            "windKw": round(wind, 2),
            "thermalKw": round(float(row["heating_load_kw"]), 2),
            "mode": state.mode,
            "scenario": state.scenario,
            "model": "XGBoost",
            "metrics": self.forecast.metrics,
        }
