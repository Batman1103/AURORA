from .state_service import state_service


class BatteryService:
    def __init__(self, forecast_service):
        self.forecast = forecast_service

    def status(self, station: str) -> dict:
        state = state_service.get(station)
        return {
            "station": station,
            "soc": round(state.battery_soc, 1),
            "capacityKwh": 800,
            "maxChargeKw": 180,
            "maxDischargeKw": 180,
            "minReservePct": 25,
            "status": "Operational",
        }
