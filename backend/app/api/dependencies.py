from ..core.config import settings
from ..core.database import SQLiteStore
from ..services.forecast_service import ForecastService
from ..services.dashboard_service import DashboardService
from ..services.energy_service import EnergyService
from ..services.fuel_service import FuelService
from ..services.battery_service import BatteryService
from ..services.alert_service import AlertService
from ..services.optimization_service import OptimizationService

forecast_service = ForecastService()
db_store = SQLiteStore(settings.root_dir / "database" / "aurora.db")
dashboard_service = DashboardService(forecast_service)
energy_service = EnergyService(forecast_service)
fuel_service = FuelService(forecast_service)
battery_service = BatteryService(forecast_service)
alert_service = AlertService()
optimization_service = OptimizationService(forecast_service, db_store)
