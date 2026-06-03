from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_permission
from app.modules.preventive.schema import (
    BacklogResponse,
    HourmeterCreate,
    HourmeterResponse,
    MaintenancePlanCreate,
    MaintenancePlanResponse,
    MaintenancePlanUpdate,
    ScheduleResponse,
)
from app.modules.preventive.service import PreventiveMaintenanceService


preventive_router = APIRouter()


@preventive_router.get("/maintenance-plans", response_model=List[MaintenancePlanResponse])
async def list_maintenance_plans(
    equipment_id: Optional[UUID] = Query(None),
    frequency_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[MaintenancePlanResponse]:
    service = PreventiveMaintenanceService(db)
    plans, _ = await service.list_plans(
        current_user,
        equipment_id=equipment_id,
        frequency_type=frequency_type,
        priority=priority,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return [MaintenancePlanResponse.from_orm(plan) for plan in plans]


@preventive_router.post(
    "/maintenance-plans",
    response_model=MaintenancePlanResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("preventive:write"))],
)
async def create_maintenance_plan(
    payload: MaintenancePlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MaintenancePlanResponse:
    service = PreventiveMaintenanceService(db)
    return await service.create_plan(current_user, payload)


@preventive_router.put(
    "/maintenance-plans/{plan_id}",
    response_model=MaintenancePlanResponse,
    dependencies=[Depends(require_permission("preventive:write"))],
)
async def update_maintenance_plan(
    plan_id: UUID,
    payload: MaintenancePlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MaintenancePlanResponse:
    service = PreventiveMaintenanceService(db)
    return await service.update_plan(current_user, plan_id, payload)


@preventive_router.delete(
    "/maintenance-plans/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("preventive:write"))],
)
async def delete_maintenance_plan(
    plan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = PreventiveMaintenanceService(db)
    await service.delete_plan(current_user, plan_id)


@preventive_router.get("/maintenance-schedules", response_model=List[ScheduleResponse])
async def list_maintenance_schedules(
    plan_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    due_before: Optional[date] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ScheduleResponse]:
    service = PreventiveMaintenanceService(db)
    schedules, _ = await service.list_schedules(
        current_user,
        plan_id=plan_id,
        status=status,
        due_before=due_before,
        limit=limit,
        offset=offset,
    )
    return [ScheduleResponse.from_orm(schedule) for schedule in schedules]


@preventive_router.post(
    "/hourmeters",
    response_model=HourmeterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("preventive:write"))],
)
async def create_hourmeter(
    payload: HourmeterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HourmeterResponse:
    service = PreventiveMaintenanceService(db)
    return await service.create_hourmeter(current_user, payload)


@preventive_router.get("/hourmeters/{equipment_id}", response_model=List[HourmeterResponse])
async def get_hourmeters(
    equipment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[HourmeterResponse]:
    service = PreventiveMaintenanceService(db)
    return await service.get_hourmeters(current_user, equipment_id)


@preventive_router.get("/maintenance-backlog", response_model=List[BacklogResponse])
async def list_maintenance_backlog(
    overdue_from: Optional[date] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[BacklogResponse]:
    service = PreventiveMaintenanceService(db)
    backlog, _ = await service.list_backlog(
        current_user,
        overdue_from=overdue_from,
        priority=priority,
        status=status,
        limit=limit,
        offset=offset,
    )
    return [BacklogResponse.from_orm(item) for item in backlog]
