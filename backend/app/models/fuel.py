from dataclasses import dataclass


@dataclass(frozen=True)
class FuelInventory:
    capacity_litres: float = 350000.0
    reserve_litres: float = 30000.0
