from fastapi import APIRouter, Query
from ..dependencies import forecast_service

router = APIRouter()

@router.get("/forecast/load")
def load_forecast(station: str = Query("bharati"), horizon: int = Query(24, ge=1, le=168)):
    df = forecast_service.load_forecast(station, horizon)
    points = [{"timestamp": str(r.timestamp), "value_kw": round(float(r.forecast_load_kw), 2)} for r in df.itertuples()]
    return {"station": station, "horizon_hours": horizon, "model": "XGBoost", "points": points, "metrics": forecast_service.metrics}

@router.get("/forecast/renewable")
def renewable_forecast(station: str = Query("bharati"), horizon: int = Query(24, ge=1, le=168)):
    df = forecast_service.renewable_forecast(station, horizon)
    points = [{"timestamp": str(r.timestamp), "solar_kw": round(float(r.solar_kw), 2), "wind_kw": round(float(r.wind_kw), 2)} for r in df.itertuples()]
    return {"station": station, "horizon_hours": horizon, "points": points}
