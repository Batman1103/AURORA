from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

STATION_PROFILES = {
    "bharati": {
        "base_kw": 72.0,
        "critical_kw": 48.0,
        "max_lab_kw": 42.0,
        "max_flexible_kw": 26.0,
        "heating_coeff": 4.7,
        "inside_temp_c": 20.0,
        "occupancy_mean": 38.0,
        "thermal_mass": 0.85,
    },
    "maitri": {
        "base_kw": 68.0,
        "critical_kw": 44.0,
        "max_lab_kw": 38.0,
        "max_flexible_kw": 24.0,
        "heating_coeff": 4.9,
        "inside_temp_c": 20.0,
        "occupancy_mean": 32.0,
        "thermal_mass": 0.88,
    },
    "generic": {
        "base_kw": 60.0,
        "critical_kw": 40.0,
        "max_lab_kw": 35.0,
        "max_flexible_kw": 22.0,
        "heating_coeff": 4.5,
        "inside_temp_c": 20.0,
        "occupancy_mean": 30.0,
        "thermal_mass": 0.90,
    },
}


def _ar_noise(rng: np.random.Generator, n: int, sigma: float, rho: float) -> np.ndarray:
    out = np.zeros(n, dtype=float)
    eps = rng.normal(0, sigma, n)
    for i in range(1, n):
        out[i] = rho * out[i - 1] + eps[i]
    return out

def _seasonal_temperature(day_of_year: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    # Stylised Antarctic annual cycle with temporally correlated weather.
    seasonal = -17.0 - 12.0 * np.cos(2 * np.pi * (day_of_year - 185) / 365.25)
    return seasonal + _ar_noise(rng, len(day_of_year), 0.9, 0.92)


def _polar_light_fraction(day_of_year: np.ndarray) -> np.ndarray:
    # Smooth approximation of extreme seasonal daylight. Not an astronomical model.
    decl = np.sin(2 * np.pi * (day_of_year - 80) / 365.25)
    return np.clip(0.08 + 0.92 * (0.5 + 0.5 * decl), 0.0, 1.0)


def _solar_irradiance(day_of_year: np.ndarray, hour: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    daylight = _polar_light_fraction(day_of_year)
    phase = (hour - 12.0) / 6.0
    diurnal = np.clip(np.cos(phase * np.pi / 2), 0.0, 1.0)
    cloud_factor = np.clip(rng.normal(0.78, 0.18, len(day_of_year)), 0.08, 1.0)
    return 950.0 * daylight * diurnal * cloud_factor


def _wind_speed(rng: np.random.Generator, n: int) -> np.ndarray:
    base = 13.0 + _ar_noise(rng, n, 1.5, 0.88)
    gust = rng.normal(0.0, 1.2, n)
    return np.clip(base + gust, 0.0, 35.0)


def _occupancy(hour: np.ndarray, mean_people: float, rng: np.random.Generator) -> np.ndarray:
    daytime = ((hour >= 7) & (hour <= 19)).astype(float)
    cycle = np.where(daytime > 0, 1.10, 0.78)
    values = mean_people * cycle + rng.normal(0, 2.5, len(hour))
    return np.clip(values, 8, 55)


def _lab_load(hour: np.ndarray, day: np.ndarray, max_lab: float, rng: np.random.Generator) -> np.ndarray:
    working = (((hour >= 8) & (hour <= 18))).astype(float)
    weekday = (day < 5).astype(float)
    schedule = 0.20 + 0.80 * working * (0.55 + 0.45 * weekday)
    drift = rng.normal(1.0, 0.06, len(hour))
    return np.clip(max_lab * schedule * drift, 0, max_lab)


def _flexible_load(hour: np.ndarray, max_flexible: float, rng: np.random.Generator) -> np.ndarray:
    # Loads that AURORA can later shift/curtail in the optimizer.
    peak = ((hour >= 18) & (hour <= 22)).astype(float)
    shoulder = ((hour >= 10) & (hour < 18)).astype(float)
    schedule = 0.25 + 0.40 * shoulder + 0.55 * peak
    return np.clip(max_flexible * schedule * rng.normal(1.0, 0.08, len(hour)), 0, max_flexible)


def _solar_power(irradiance: np.ndarray, capacity_kw: float = 45.0) -> np.ndarray:
    return np.clip(capacity_kw * irradiance / 1000.0 * 0.85, 0, capacity_kw)


def _wind_power(wind_speed: np.ndarray, capacity_kw: float = 70.0) -> np.ndarray:
    # Simplified turbine curve.
    cut_in, rated, cut_out = 3.0, 12.0, 25.0
    out = np.zeros_like(wind_speed, dtype=float)
    ramp = (wind_speed >= cut_in) & (wind_speed < rated)
    rated_mask = (wind_speed >= rated) & (wind_speed <= cut_out)
    out[ramp] = capacity_kw * ((wind_speed[ramp] ** 3 - cut_in ** 3) / (rated ** 3 - cut_in ** 3))
    out[rated_mask] = capacity_kw
    return np.clip(out, 0, capacity_kw)


def generate_station_data(year: int, station: str, seed: int = 42) -> pd.DataFrame:
    profile = STATION_PROFILES.get(station.lower(), STATION_PROFILES["generic"])
    idx = pd.date_range(f"{year}-01-01 00:00:00", f"{year}-12-31 23:00:00", freq="h")
    rng = np.random.default_rng(seed)

    day_of_year = idx.dayofyear.to_numpy()
    hour = idx.hour.to_numpy()
    day_of_week = idx.dayofweek.to_numpy()

    temperature = _seasonal_temperature(day_of_year, rng)
    wind_speed = _wind_speed(rng, len(idx))
    solar_radiation = _solar_irradiance(day_of_year, hour, rng)
    humidity = np.clip(70 - 0.7 * temperature + rng.normal(0, 7, len(idx)), 35, 100)
    pressure = np.clip(rng.normal(985, 18, len(idx)), 920, 1040)
    occupancy = _occupancy(hour, profile["occupancy_mean"], rng)

    delta_temp = np.maximum(profile["inside_temp_c"] - temperature, 0)
    heating_load = profile["heating_coeff"] * delta_temp * profile["thermal_mass"]
    heating_load *= 1.0 + 0.08 * np.clip(wind_speed - 10, 0, None)
    heating_load += rng.normal(0, 3.5, len(idx))
    heating_load = np.clip(heating_load, 0, None)

    lab_load = _lab_load(hour, day_of_week, profile["max_lab_kw"], rng)
    flexible_load = _flexible_load(hour, profile["max_flexible_kw"], rng)
    occupancy_load = 0.75 * occupancy
    weather_aux = 0.10 * np.maximum(-temperature - 10, 0)

    base_variation = _ar_noise(rng, len(idx), 1.8, 0.90)
    load_kw = (
        profile["base_kw"]
        + occupancy_load
        + heating_load
        + lab_load
        + flexible_load
        + weather_aux
        + base_variation
    )
    load_kw = np.clip(load_kw, profile["critical_kw"] + 5, None)

    critical_load = np.minimum(
        profile["critical_kw"] + 0.20 * heating_load + 0.10 * lab_load,
        load_kw,
    )
    flexible_load = np.minimum(flexible_load, np.maximum(load_kw - critical_load, 0))

    solar_kw = _solar_power(solar_radiation)
    wind_kw = _wind_power(wind_speed)

    df = pd.DataFrame(
        {
            "timestamp": idx,
            "temperature_c": temperature,
            "wind_speed_mps": wind_speed,
            "solar_radiation_wm2": solar_radiation,
            "humidity_pct": humidity,
            "pressure_hpa": pressure,
            "occupancy": occupancy,
            "heating_load_kw": heating_load,
            "lab_load_kw": lab_load,
            "flexible_load_kw": flexible_load,
            "critical_load_kw": critical_load,
            "load_kw": load_kw,
            "solar_kw": solar_kw,
            "wind_kw": wind_kw,
            "station": station.lower(),
        }
    )
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AURORA synthetic station data")
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--station", choices=sorted(STATION_PROFILES), default="bharati")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/processed/station_energy.csv"))
    args = parser.parse_args()

    df = generate_station_data(args.year, args.station, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df):,} hourly records to {args.output}")
    print(f"Mean load: {df['load_kw'].mean():.1f} kW")
    print(f"Peak load: {df['load_kw'].max():.1f} kW")


if __name__ == "__main__":
    main()
