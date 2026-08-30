from ..core.config import settings
from .state_service import state_service


class FuelService:
    def __init__(self, forecast_service):
        self.forecast = forecast_service

    def status(self, station: str) -> dict:
        state = state_service.get(station)
        current = self.forecast.simulator.latest(station)
        avg_daily = max(500.0, float(current["load_kw"]) * 24 * settings.generator_fuel_l_per_kwh * 0.55)
        days = state.fuel_litres / avg_daily
        return {
            "station": station,
            "fuelLitres": round(state.fuel_litres, 0),
            "reserveLitres": settings.fuel_reserve_litres,
            "capacityLitres": 350000,
            "dailyConsumptionLitres": round(avg_daily, 0),
            "daysToExhaustion": round(days, 0),
            "risk": "HIGH" if state.fuel_litres < settings.fuel_reserve_litres else ("MEDIUM" if state.fuel_litres < settings.fuel_reserve_litres * 2 else "LOW"),
        }
