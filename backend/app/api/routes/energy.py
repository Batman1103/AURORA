from fastapi import APIRouter, Query
from ..dependencies import energy_service

router = APIRouter()

@router.get("/energy/live")
def live(station: str = Query("bharati")):
    return energy_service.live(station)
