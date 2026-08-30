from __future__ import annotations

import math


def solar_power_from_irradiance(
    irradiance_wm2: float,
    capacity_kw: float = 45.0,
    efficiency: float = 0.18,
    system_derate: float = 0.85,
) -> float:
    """Physics-based PV estimate."""
    if irradiance_wm2 <= 0:
        return 0.0
    power = capacity_kw * (irradiance_wm2 / 1000.0) * (efficiency / 0.18) * system_derate
    return float(max(0.0, min(capacity_kw, power)))


def clear_sky_irradiance(day_of_year: int, hour: float) -> float:
    """Simple polar clear-sky proxy for early prototyping.

    Replace with irradiance from a real forecast/reanalysis product in the
    production data pipeline.
    """
    seasonal = max(0.0, 0.5 + 0.5 * math.sin(2 * math.pi * (day_of_year - 80) / 365.25))
    diurnal = max(0.0, math.cos(math.pi * (hour - 12.0) / 12.0))
    return 1000.0 * seasonal * diurnal
