from __future__ import annotations


def solar_power_from_availability(
    solar_availability: float,
    capacity_kw: float = 500.0,
    system_derate: float = 0.85,
) -> float:
    """Convert normalized Maitri solar availability into available PV power."""
    a = max(0.0, min(1.0, float(solar_availability)))
    return float(max(0.0, min(capacity_kw, capacity_kw * system_derate * a)))
