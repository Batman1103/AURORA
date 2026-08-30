from pydantic import BaseModel, Field


class OptimizationRequest(BaseModel):
    station: str = "bharati"
    mode: str = "Normal"
    horizon: str = "24 Hours"


class DispatchPoint(BaseModel):
    timestamp: str
    load_kw: float
    solar_kw: float
    wind_kw: float
    battery_kw: float
    diesel_kw: float
    flexible_load_kw: float


class OptimizationResponse(BaseModel):
    station: str
    mode: str
    horizon_hours: int
    fuel_saved_litres: float
    reliability: float
    renewable_utilization: float
    baseline_fuel_litres: float
    optimized_fuel_litres: float
    dispatch: list[DispatchPoint]
    recommendations: list[str]
