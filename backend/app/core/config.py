from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]

@dataclass(frozen=True)
class Settings:
    app_name: str = "AURORA API"
    version: str = "1.0.0"
    root_dir: Path = ROOT_DIR
    ml_dir: Path = ROOT_DIR / "ml"
    dataset_path: Path = ROOT_DIR / "ml" / "data" / "processed" / "station_energy.csv"
    features_path: Path = ROOT_DIR / "ml" / "data" / "features" / "load_features.csv"
    load_model_path: Path = ROOT_DIR / "ml" / "models" / "load_model.joblib"
    seed_fuel_litres: float = 218400.0
    seed_battery_soc: float = 72.0
    fuel_reserve_litres: float = 30000.0
    generator_capacity_kw: float = 120.0
    generator_min_kw: float = 30.0
    generator_fuel_l_per_kwh: float = 0.29

settings = Settings()
