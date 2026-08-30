from fastapi import APIRouter, Query
from ..dependencies import fuel_service

router = APIRouter()

@router.get("/fuel/status")
def status(station: str = Query("bharati")):
    return fuel_service.status(station)
