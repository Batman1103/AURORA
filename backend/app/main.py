from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logging import configure_logging
from .api.routes import dashboard, energy, forecasting, optimization, fuel, battery, alerts, simulation

configure_logging()

app = FastAPI(title=settings.app_name, version=settings.version, description="AURORA SIH26061 FastAPI backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(energy.router, prefix="/api", tags=["energy"])
app.include_router(forecasting.router, prefix="/api", tags=["forecasting"])
app.include_router(optimization.router, prefix="/api", tags=["optimization"])
app.include_router(fuel.router, prefix="/api", tags=["fuel"])
app.include_router(battery.router, prefix="/api", tags=["battery"])
app.include_router(alerts.router, prefix="/api", tags=["alerts"])
app.include_router(simulation.router, prefix="/api", tags=["simulation"])

@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "service": settings.app_name, "ml": "connected"}
