from fastapi import APIRouter, Query
from ..dependencies import dashboard_service

router = APIRouter()

@router.get("/dashboard")
def dashboard(station: str = Query("bharati")):
    return dashboard_service.snapshot(station)
