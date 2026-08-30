from datetime import datetime, timezone
from ..core.config import settings
from .state_service import state_service


class AlertService:
    def build(self, station: str) -> list[dict]:
        state = state_service.get(station)
        alerts = [
            {
                "id": "fuel-efficiency",
                "severity": "warning",
                "title": "High fuel consumption",
                "body": "Generator dispatch is above the modeled efficiency band.",
                "timestamp": "10:15 AM",
                "action": "Shift flexible load and re-run optimization",
            },
            {
                "id": "polar-night",
                "severity": "info",
                "title": "Polar night approaching",
                "body": "Solar contribution is expected to decline over the coming period.",
                "timestamp": "09:40 AM",
                "action": "Increase wind utilization and battery reserve",
            },
        ]
        if state.fuel_litres < settings.fuel_reserve_litres * 1.5:
            alerts.insert(0, {
                "id": "fuel-risk",
                "severity": "danger",
                "title": "Fuel reserve risk",
                "body": "Projected fuel inventory is approaching the conservation threshold.",
                "timestamp": "Now",
                "action": "Activate Fuel Conservation Mode",
            })
        if state.battery_soc < 25:
            alerts.insert(0, {
                "id": "battery-risk",
                "severity": "danger",
                "title": "Battery reserve low",
                "body": "Battery state of charge is below the configured reserve.",
                "timestamp": "Now",
                "action": "Stop discretionary discharge",
            })
        return alerts
