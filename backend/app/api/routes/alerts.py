from fastapi import APIRouter, Query
from ..dependencies import alert_service

router = APIRouter()

@router.get("/alerts")
def alerts(station: str = Query("bharati")):
    return {"station": station, "alerts": alert_service.build(station)}
