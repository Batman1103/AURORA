from .forecast_service import ForecastService
from .state_service import state_service


class EnergyService:
    def __init__(self, forecast_service: ForecastService):
        self.forecast = forecast_service

    def live(self, station: str) -> dict:
        row = self.forecast.simulator.latest(station)
        state = state_service.get(station)
        return {
            "timestamp": row["timestamp"].isoformat(),
            "load_kw": float(row["load_kw"]),
            "solar_kw": float(row["solar_kw"]),
            "wind_kw": float(row["wind_kw"]),
            "diesel_kw": max(0.0, float(row["load_kw"]) - float(row["solar_kw"]) - float(row["wind_kw"])),
            "battery_kw": -48.0 if state.battery_soc > 40 else 0.0,
            "thermal_kw": float(row["heating_load_kw"]),
            "battery_soc": state.battery_soc,
            "fuel_litres": state.fuel_litres,
        }
