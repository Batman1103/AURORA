from __future__ import annotations


def turbine_power_from_wind(
    wind_speed_mps: float,
    capacity_kw: float = 70.0,
    cut_in: float = 3.0,
    rated: float = 12.0,
    cut_out: float = 25.0,
) -> float:
    """Simplified wind-turbine power curve."""
    v = float(wind_speed_mps)
    if v < cut_in or v > cut_out:
        return 0.0
    if v >= rated:
        return float(capacity_kw)
    fraction = (v**3 - cut_in**3) / (rated**3 - cut_in**3)
    return float(max(0.0, min(capacity_kw, capacity_kw * fraction)))
