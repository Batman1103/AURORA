from dataclasses import dataclass


@dataclass
class StationState:
    station: str
    fuel_litres: float
    battery_soc: float
    mode: str = "Normal"
    scenario: str = "normal"
    last_optimization: str | None = None
