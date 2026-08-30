from pydantic import BaseModel, Field


class EnergyLive(BaseModel):
    timestamp: str
    load_kw: float
    solar_kw: float
    wind_kw: float
    diesel_kw: float
    battery_kw: float
    thermal_kw: float
    battery_soc: float
    fuel_litres: float
