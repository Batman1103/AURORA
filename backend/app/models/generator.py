from dataclasses import dataclass


@dataclass(frozen=True)
class Generator:
    id: str
    name: str
    capacity_kw: float
    min_kw: float
    fuel_l_per_kwh: float
    status: str = "available"
