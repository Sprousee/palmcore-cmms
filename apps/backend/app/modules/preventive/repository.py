from datetime import date
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import Date, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.equipment import Equipment
from app.models.maintenance_backlog import MaintenanceBacklog
from app.models.maintenance_plan import MaintenancePlan
from app.models.maintenance_schedule import MaintenanceSchedule
from app.models.equipment_hourmeter import EquipmentHourmeter


class PreventiveRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_plan_query(self, company_id: UUID):
        return select(MaintenancePlan).filter(
            MaintenancePlan.company_id == company_id,
            MaintenancePlan.deleted_at.is_(None),
        ).options(selectinload(MaintenancePlan.equipment))

    async def get_maintenance_plans(
        self,
        company_id: UUID,
        equipment_id: Optional[UUID] = None,
        frequency_type: Optional[str] = None,
        priority: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[MaintenancePlan], int]:
        query = self.get_plan_query(company_id)

        if equipment_id:
            query = query.filter(MaintenancePlan.equipment_id == equipment_id)
        if frequency_type:
            query = query.filter(MaintenancePlan.frequency_type == frequency_type)
        if priority:
            query = query.filter(MaintenancePlan.priority == priority)
        if is_active is not None:
            query = query.filter(MaintenancePlan.is_active == is_active)

        total_stmt = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_stmt)).scalar_one()

        result = await self.session.execute(query.limit(limit).offset(offset))
        return result.scalars().all(), total

    async def get_plan_by_id(self, plan_id: UUID, company_id: UUID) -> Optional[MaintenancePlan]:
        statement = (
            select(MaintenancePlan)
            .filter(
                MaintenancePlan.id == plan_id,
                MaintenancePlan.company_id == company_id,
                MaintenancePlan.deleted_at.is_(None),
            )
            .options(selectinload(MaintenancePlan.equipment))
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create_plan(self, plan: MaintenancePlan) -> MaintenancePlan:
        self.session.add(plan)
        await self.session.flush()
        return plan

    async def update_plan(self, plan: MaintenancePlan) -> MaintenancePlan:
        self.session.add(plan)
        await self.session.flush()
        return plan

    async def delete_plan(self, plan: MaintenancePlan) -> None:
        plan.deleted_at = func.now()
        self.session.add(plan)
        await self.session.flush()

    def get_schedule_query(self, company_id: UUID):
        return (
            select(MaintenanceSchedule)
            .join(MaintenancePlan)
            .filter(
                MaintenancePlan.company_id == company_id,
                MaintenancePlan.deleted_at.is_(None),
                MaintenanceSchedule.deleted_at.is_(None),
            )
            .options(selectinload(MaintenanceSchedule.maintenance_plan))
        )

    async def get_maintenance_schedules(
        self,
        company_id: UUID,
        plan_id: Optional[UUID] = None,
        status: Optional[str] = None,
        due_before: Optional[date] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[MaintenanceSchedule], int]:
        query = self.get_schedule_query(company_id)

        if plan_id:
            query = query.filter(MaintenanceSchedule.maintenance_plan_id == plan_id)
        if status:
            query = query.filter(MaintenanceSchedule.status == status)
        if due_before:
            query = query.filter(MaintenanceSchedule.scheduled_date <= due_before)

        total_stmt = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_stmt)).scalar_one()

        result = await self.session.execute(query.limit(limit).offset(offset))
        return result.scalars().all(), total

    async def create_schedule(self, schedule: MaintenanceSchedule) -> MaintenanceSchedule:
        self.session.add(schedule)
        await self.session.flush()
        return schedule

    async def get_schedule_by_id(
        self, schedule_id: UUID, company_id: UUID
    ) -> Optional[MaintenanceSchedule]:
        statement = (
            select(MaintenanceSchedule)
            .join(MaintenancePlan)
            .filter(
                MaintenanceSchedule.id == schedule_id,
                MaintenancePlan.company_id == company_id,
                MaintenanceSchedule.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_due_schedules(
        self,
        due_before: date,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[MaintenanceSchedule], int]:
        query = (
            select(MaintenanceSchedule)
            .join(MaintenancePlan)
            .filter(
                MaintenanceSchedule.status == "pending",
                MaintenanceSchedule.scheduled_date <= due_before,
                MaintenanceSchedule.deleted_at.is_(None),
                MaintenancePlan.deleted_at.is_(None),
            )
            .options(selectinload(MaintenanceSchedule.maintenance_plan))
        )

        total_stmt = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_stmt)).scalar_one()
        result = await self.session.execute(query.limit(limit).offset(offset))
        return result.scalars().all(), total

    async def create_hourmeter(self, hourmeter: EquipmentHourmeter) -> EquipmentHourmeter:
        self.session.add(hourmeter)
        await self.session.flush()
        return hourmeter

    async def get_hourmeters_by_equipment(
        self,
        equipment_id: UUID,
        company_id: UUID,
    ) -> list[EquipmentHourmeter]:
        statement = (
            select(EquipmentHourmeter)
            .join(Equipment)
            .filter(
                EquipmentHourmeter.equipment_id == equipment_id,
                Equipment.company_id == company_id,
            )
            .order_by(EquipmentHourmeter.recorded_at.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_due_backlog_entries(
        self,
        company_id: UUID,
        overdue_from: Optional[date] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[MaintenanceBacklog], int]:
        query = select(MaintenanceBacklog).filter(
            MaintenanceBacklog.company_id == company_id,
            MaintenanceBacklog.deleted_at.is_(None),
        )

        if overdue_from:
            query = query.filter(MaintenanceBacklog.scheduled_date <= overdue_from)
        if priority:
            query = query.filter(MaintenanceBacklog.priority == priority)
        if status:
            query = query.filter(MaintenanceBacklog.status == status)

        total_stmt = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(total_stmt)).scalar_one()

        result = await self.session.execute(query.limit(limit).offset(offset))
        return result.scalars().all(), total

    async def get_backlog_by_plan_and_equipment(
        self,
        company_id: UUID,
        maintenance_plan_id: UUID,
        equipment_id: UUID,
    ) -> Optional[MaintenanceBacklog]:
        statement = select(MaintenanceBacklog).filter(
            MaintenanceBacklog.company_id == company_id,
            MaintenanceBacklog.maintenance_plan_id == maintenance_plan_id,
            MaintenanceBacklog.equipment_id == equipment_id,
            MaintenanceBacklog.deleted_at.is_(None),
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create_backlog(self, backlog: MaintenanceBacklog) -> MaintenanceBacklog:
        self.session.add(backlog)
        await self.session.flush()
        return backlog

    async def update_backlog(self, backlog: MaintenanceBacklog) -> MaintenanceBacklog:
        self.session.add(backlog)
        await self.session.flush()
        return backlog

    async def get_equipment_by_id(self, equipment_id: UUID, company_id: UUID) -> Optional[Equipment]:
        statement = select(Equipment).filter(
            Equipment.id == equipment_id,
            Equipment.company_id == company_id,
            Equipment.deleted_at.is_(None),
        )
        result = await self.session.execute(statement)
        return result.scalars().first()
