from pydantic import BaseModel


class ForecastPoint(BaseModel):
    timestamp: str
    value_kw: float


class LoadForecastResponse(BaseModel):
    station: str
    horizon_hours: int
    model: str
    points: list[ForecastPoint]
    metrics: dict[str, float]


class RenewablePoint(BaseModel):
    timestamp: str
    solar_kw: float
    wind_kw: float


class RenewableForecastResponse(BaseModel):
    station: str
    horizon_hours: int
    points: list[RenewablePoint]
