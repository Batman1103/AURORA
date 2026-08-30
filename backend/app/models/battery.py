from dataclasses import dataclass


@dataclass(frozen=True)
class Battery:
    capacity_kwh: float = 800.0
    max_charge_kw: float = 180.0
    max_discharge_kw: float = 180.0
    min_soc_pct: float = 25.0
    max_soc_pct: float = 95.0
