from fastapi import APIRouter
from ..dependencies import optimization_service
from ...schemas.optimization import OptimizationRequest

router = APIRouter()

@router.post("/optimization/run")
def run_optimization(payload: OptimizationRequest):
    return optimization_service.run(payload.station, payload.mode, payload.horizon)
