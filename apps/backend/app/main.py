from fastapi import FastAPI

from app.core.config import settings
from app.modules.auth.router import auth_router
from app.modules.equipment.router import equipment_router
from app.modules.inventory.router import inventory_router
from app.modules.preventive.router import preventive_router
from app.modules.preventive.scheduler import start_preventive_scheduler
from app.modules.reports.router import reports_router
from app.modules.reports.scheduler import start_reports_scheduler

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(equipment_router, tags=["equipment"])
app.include_router(preventive_router, tags=["preventive"])
app.include_router(inventory_router, tags=["inventory"])
app.include_router(reports_router, tags=["reports"])


@app.on_event("startup")
async def on_startup() -> None:
    start_preventive_scheduler()
    start_reports_scheduler()
