from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from ..core.config import settings
from ..models.station import StationState


class StateService:
    def __init__(self) -> None:
        self._lock = Lock()
        self._states = {
            "bharati": StationState("bharati", settings.seed_fuel_litres, settings.seed_battery_soc),
            "maitri": StationState("maitri", settings.seed_fuel_litres * 0.91, 68.0),
            "generic": StationState("generic", settings.seed_fuel_litres * 0.82, 61.0),
        }

    def get(self, station: str) -> StationState:
        key = station.lower()
        with self._lock:
            if key not in self._states:
                self._states[key] = StationState(key, settings.seed_fuel_litres, settings.seed_battery_soc)
            return self._states[key]

    def set_mode(self, station: str, mode: str) -> None:
        self.get(station).mode = mode

    def set_scenario(self, station: str, scenario: str, battery_soc: float | None = None, fuel_litres: float | None = None) -> StationState:
        state = self.get(station)
        with self._lock:
            state.scenario = scenario
            if battery_soc is not None:
                state.battery_soc = float(max(5.0, min(95.0, battery_soc)))
            if fuel_litres is not None:
                state.fuel_litres = float(max(0.0, fuel_litres))
            return state

    def mark_optimized(self, station: str) -> None:
        self.get(station).last_optimization = datetime.now(timezone.utc).isoformat()


state_service = StateService()
