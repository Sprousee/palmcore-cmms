from datetime import date
from typing import Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.preventive.repository import PreventiveRepository
from app.modules.preventive.schema import (
    BacklogResponse,
    HourmeterCreate,
    HourmeterResponse,
    MaintenancePlanCreate,
    MaintenancePlanResponse,
    MaintenancePlanUpdate,
    ScheduleResponse,
)
from app.models.equipment_hourmeter import EquipmentHourmeter
from app.models.maintenance_backlog import MaintenanceBacklog
from app.models.maintenance_plan import MaintenancePlan
from app.models.maintenance_schedule import MaintenanceSchedule
from app.models.user import User


class PreventiveMaintenanceService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = PreventiveRepository(db)
        self.db = db

    async def list_plans(
        self,
        user: User,
        equipment_id: Optional[UUID] = None,
        frequency_type: Optional[str] = None,
        priority: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[MaintenancePlan], int]:
        return await self.repo.get_maintenance_plans(
            user.company_id,
            equipment_id=equipment_id,
            frequency_type=frequency_type,
            priority=priority,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

    async def get_plan(self, user: User, plan_id: UUID) -> MaintenancePlan:
        plan = await self.repo.get_plan_by_id(plan_id, user.company_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance plan not found.")
        return plan

    async def create_plan(
        self, user: User, payload: MaintenancePlanCreate
    ) -> MaintenancePlanResponse:
        if payload.equipment_id:
            equipment = await self.repo.get_equipment_by_id(payload.equipment_id, user.company_id)
            if not equipment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Equipment not found for this tenant.",
                )

        plan = MaintenancePlan(
            company_id=user.company_id,
            equipment_id=payload.equipment_id,
            name=payload.name,
            description=payload.description,
            maintenance_type=payload.maintenance_type,
            frequency_type=payload.frequency_type,
            frequency_value=payload.frequency_value,
            estimated_duration=payload.estimated_duration,
            priority=payload.priority,
            auto_generate_work_order=payload.auto_generate_work_order,
            is_active=payload.is_active,
            created_by=user.id,
        )
        await self.repo.create_plan(plan)
        await self.db.commit()
        return MaintenancePlanResponse.from_orm(plan)

    async def update_plan(
        self, user: User, plan_id: UUID, payload: MaintenancePlanUpdate
    ) -> MaintenancePlanResponse:
        plan = await self.get_plan(user, plan_id)

        if payload.equipment_id is not None:
            equipment = await self.repo.get_equipment_by_id(payload.equipment_id, user.company_id)
            if not equipment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Equipment not found for this tenant.",
                )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(plan, field, value)

        await self.repo.update_plan(plan)
        await self.db.commit()
        return MaintenancePlanResponse.from_orm(plan)

    async def delete_plan(self, user: User, plan_id: UUID) -> None:
        plan = await self.get_plan(user, plan_id)
        await self.repo.delete_plan(plan)
        await self.db.commit()

    async def list_schedules(
        self,
        user: User,
        plan_id: Optional[UUID] = None,
        status: Optional[str] = None,
        due_before: Optional[date] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[MaintenanceSchedule], int]:
        return await self.repo.get_maintenance_schedules(
            user.company_id,
            plan_id=plan_id,
            status=status,
            due_before=due_before,
            limit=limit,
            offset=offset,
        )

    async def create_hourmeter(self, user: User, payload: HourmeterCreate) -> HourmeterResponse:
        equipment = await self.repo.get_equipment_by_id(payload.equipment_id, user.company_id)
        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found for this tenant.",
            )

        hourmeter = EquipmentHourmeter(
            equipment_id=payload.equipment_id,
            current_hours=payload.current_hours,
            last_recorded_hours=payload.last_recorded_hours,
            recorded_at=payload.recorded_at,
            recorded_by=payload.recorded_by,
        )
        await self.repo.create_hourmeter(hourmeter)
        await self.db.commit()
        return HourmeterResponse.from_orm(hourmeter)

    async def get_hourmeters(self, user: User, equipment_id: UUID) -> list[HourmeterResponse]:
        equipment = await self.repo.get_equipment_by_id(equipment_id, user.company_id)
        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found for this tenant.",
            )

        records = await self.repo.get_hourmeters_by_equipment(equipment_id, user.company_id)
        return [HourmeterResponse.from_orm(record) for record in records]

    async def list_backlog(
        self,
        user: User,
        overdue_from: Optional[date] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[MaintenanceBacklog], int]:
        return await self.repo.get_due_backlog_entries(
            user.company_id,
            overdue_from=overdue_from,
            priority=priority,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def upsert_backlog_entry(
        self,
        company_id: UUID,
        maintenance_plan_id: UUID,
        equipment_id: UUID,
        scheduled_date: Optional[date],
        days_overdue: Optional[int],
        priority: Optional[str],
        status: Optional[str],
    ) -> MaintenanceBacklog:
        backlog = await self.repo.get_backlog_by_plan_and_equipment(
            company_id, maintenance_plan_id, equipment_id
        )
        if backlog:
            backlog.scheduled_date = scheduled_date
            backlog.days_overdue = days_overdue
            backlog.priority = priority
            backlog.status = status
            await self.repo.update_backlog(backlog)
            return backlog

        backlog = MaintenanceBacklog(
            company_id=company_id,
            equipment_id=equipment_id,
            maintenance_plan_id=maintenance_plan_id,
            scheduled_date=scheduled_date,
            days_overdue=days_overdue,
            priority=priority,
            status=status,
        )
        await self.repo.create_backlog(backlog)
        return backlog

    async def generate_backlog_for_due_schedules(
        self,
        company_id: UUID,
        schedules: list[MaintenanceSchedule],
    ) -> list[MaintenanceBacklog]:
        backlog_items = []
        for schedule in schedules:
            if schedule.maintenance_plan:
                days_overdue = None
                if schedule.scheduled_date:
                    days_overdue = (date.today() - schedule.scheduled_date).days
                backlog = await self.upsert_backlog_entry(
                    company_id=company_id,
                    maintenance_plan_id=schedule.maintenance_plan_id,
                    equipment_id=schedule.maintenance_plan.equipment_id,
                    scheduled_date=schedule.scheduled_date,
                    days_overdue=days_overdue,
                    priority=schedule.maintenance_plan.priority,
                    status="overdue" if days_overdue and days_overdue > 0 else schedule.status,
                )
                backlog_items.append(backlog)
        await self.db.commit()
        return backlog_items
