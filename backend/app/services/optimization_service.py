from __future__ import annotations

from datetime import datetime, timezone

from optimizer.dispatch import DispatchConfig, optimize_dispatch
from ..core.config import settings
from .forecast_service import ForecastService
from .state_service import state_service


class OptimizationService:
    def __init__(self, forecast_service: ForecastService, db_store):
        self.forecast = forecast_service
        self.db = db_store

    @staticmethod
    def horizon_to_hours(horizon: str) -> int:
        mapping = {"24 hours": 24, "7 days": 168, "30 days": 720, "180 days": 4320}
        return mapping.get(horizon.lower(), 24)

    def run(self, station: str, mode: str, horizon: str) -> dict:
        hours = self.horizon_to_hours(horizon)
        # Keep API responses compact for the dashboard; the solver can operate up to 180 days later.
        forecast_hours = min(hours, 48)
        combined = self.forecast.combined_forecast(station, forecast_hours)
        config = DispatchConfig(
            generator_capacity_kw=settings.generator_capacity_kw,
            generator_min_kw=settings.generator_min_kw,
            fuel_l_per_kwh=settings.generator_fuel_l_per_kwh,
        )
        dispatch, result = optimize_dispatch(combined, state_service.get(station).battery_soc, mode, config)
        state_service.set_mode(station, mode)
        state_service.mark_optimized(station)

        recommendations = [
            "Prioritize renewable generation before diesel/CHP.",
            "Keep the battery above the configured reserve threshold.",
            "Protect critical loads during deficit events.",
        ]
        if mode.lower() == "fuel conservation":
            recommendations.insert(0, "Shift flexible loads away from high-fuel periods.")
        if mode.lower() == "emergency":
            recommendations.insert(0, "Protect critical loads and minimize discretionary demand.")

        created_at = datetime.now(timezone.utc).isoformat()
        self.db.add_optimization_run(created_at, station, mode, hours, result["fuel_saved_litres"], result["reliability"])
        return {
            "station": station,
            "mode": mode,
            "horizon_hours": hours,
            **{k: round(v, 2) for k, v in result.items()},
            "dispatch": dispatch.to_dict(orient="records"),
            "recommendations": recommendations,
        }
