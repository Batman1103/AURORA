from fastapi import APIRouter, Query
from ..dependencies import battery_service

router = APIRouter()

@router.get("/battery/status")
def status(station: str = Query("bharati")):
    return battery_service.status(station)
