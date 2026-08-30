from fastapi import APIRouter
from pydantic import BaseModel
from ...services.state_service import state_service

router = APIRouter()

class ScenarioRequest(BaseModel):
    station: str = "bharati"
    scenario: str = "normal"
    battery_soc: float | None = None
    fuel_litres: float | None = None

@router.post("/simulation/scenario")
def scenario(payload: ScenarioRequest):
    state = state_service.set_scenario(payload.station, payload.scenario, payload.battery_soc, payload.fuel_litres)
    return {"station": state.station, "scenario": state.scenario, "batterySoc": state.battery_soc, "fuelLitres": state.fuel_litres}
