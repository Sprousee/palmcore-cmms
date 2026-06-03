from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_permission
from app.modules.reports.schema import (
    BacklogStatusResponse,
    InventoryConsumptionResponse,
    KpiResponse,
    MaintenanceCostResponse,
    TechnicianProductivityResponse,
)
from app.modules.reports.service import ReportsService

reports_router = APIRouter()


@reports_router.get(
    "/reports/kpis",
    response_model=KpiResponse,
    dependencies=[Depends(require_permission("reports:read"))],
)
async def get_kpis(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    plant_id: Optional[UUID] = Query(None),
    equipment_id: Optional[UUID] = Query(None),
    technician_id: Optional[UUID] = Query(None),
    maintenance_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KpiResponse:
    service = ReportsService(db)
    return await service.get_kpis(
        current_user,
        date_from=date_from,
        date_to=date_to,
        plant_id=plant_id,
        equipment_id=equipment_id,
        technician_id=technician_id,
        maintenance_type=maintenance_type,
    )


@reports_router.get(
    "/reports/mttr",
    response_model=KpiResponse,
    dependencies=[Depends(require_permission("reports:read"))],
)
async def get_mttr(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KpiResponse:
    service = ReportsService(db)
    return await service.get_kpis(current_user, date_from=date_from, date_to=date_to)


@reports_router.get(
    "/reports/mtbf",
    response_model=KpiResponse,
    dependencies=[Depends(require_permission("reports:read"))],
)
async def get_mtbf(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KpiResponse:
    service = ReportsService(db)
    return await service.get_kpis(current_user, date_from=date_from, date_to=date_to)


@reports_router.get(
    "/reports/availability",
    response_model=KpiResponse,
    dependencies=[Depends(require_permission("reports:read"))],
)
async def get_availability(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KpiResponse:
    service = ReportsService(db)
    return await service.get_kpis(current_user, date_from=date_from, date_to=date_to)


@reports_router.get(
    "/reports/costs",
    response_model=MaintenanceCostResponse,
    dependencies=[Depends(require_permission("reports:read"))],
)
async def get_costs(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MaintenanceCostResponse:
    service = ReportsService(db)
    return await service.get_maintenance_costs(current_user, date_from=date_from, date_to=date_to)


@reports_router.get(
    "/reports/backlog",
    response_model=List[BacklogStatusResponse],
    dependencies=[Depends(require_permission("reports:read"))],
)
async def get_backlog(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[BacklogStatusResponse]:
    service = ReportsService(db)
    return await service.get_backlog(current_user)


@reports_router.get(
    "/reports/technicians",
    response_model=List[TechnicianProductivityResponse],
    dependencies=[Depends(require_permission("reports:read"))],
)
async def get_technician_productivity(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[TechnicianProductivityResponse]:
    service = ReportsService(db)
    return await service.get_technician_productivity(
        current_user,
        date_from=date_from,
        date_to=date_to,
    )


@reports_router.get(
    "/reports/inventory-consumption",
    response_model=List[InventoryConsumptionResponse],
    dependencies=[Depends(require_permission("reports:read"))],
)
async def get_inventory_consumption(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[InventoryConsumptionResponse]:
    service = ReportsService(db)
    return await service.get_inventory_consumption(
        current_user,
        date_from=date_from,
        date_to=date_to,
    )
