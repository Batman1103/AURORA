from __future__ import annotations
import math


def clear_sky_irradiance(day_of_year: int, hour: float) -> float:
    """
    Calculate clear sky irradiance (W/m²) using a simplified model.
    
    Args:
        day_of_year: Day of year (1-365)
        hour: Hour of day (0-24)
    
    Returns:
        Clear sky irradiance in W/m²
    """
    # Simplified clear sky model
    # Solar noon is at hour 12
    hours_from_noon = hour - 12.0
    
    # Sun elevation angle (simplified)
    # Lowest in winter, highest in summer
    seasonal_factor = 1.0 + 0.4 * math.cos(2 * math.pi * (day_of_year - 80) / 365.0)
    
    # Cosine factor for time of day (peak at solar noon)
    time_factor = max(0.0, math.cos(math.radians(hours_from_noon * 15.0)))
    
    # Clear sky irradiance (W/m²) - max around 1000 W/m²
    irradiance = 1000.0 * seasonal_factor * time_factor
    
    return max(0.0, irradiance)


def solar_power_from_irradiance(irradiance_wm2: float, capacity_kw: float = 45.0, system_derate: float = 0.85) -> float:
    """
    Convert irradiance (W/m²) to solar power output.
    
    Args:
        irradiance_wm2: Irradiance in W/m²
        capacity_kw: System capacity in kW
        system_derate: System derate factor (efficiency, losses, etc.)
    
    Returns:
        Solar power in kW
    """
    # Assume 1 kW of capacity requires ~6-7 m² (typical PV panel area)
    system_area_m2 = capacity_kw * 6.5
    
    # Power = irradiance * area * system_derate / 1000 (convert W to kW)
    power_kw = (irradiance_wm2 * system_area_m2 * system_derate) / 1000.0
    
    return max(0.0, min(capacity_kw, power_kw))


def solar_power_from_availability(
    solar_availability: float,
    capacity_kw: float = 500.0,
    system_derate: float = 0.85,
) -> float:
    """Convert normalized Maitri solar availability into available PV power."""
    a = max(0.0, min(1.0, float(solar_availability)))
    return float(max(0.0, min(capacity_kw, capacity_kw * system_derate * a)))
