from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipment import Equipment
from app.models.inventory_alert import InventoryAlert
from app.models.maintenance_backlog import MaintenanceBacklog
from app.models.maintenance_plan import MaintenancePlan
from app.models.maintenance_schedule import MaintenanceSchedule
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.spare_part import SparePart
from app.models.stock_movement import StockMovement
from app.models.technician import Technician
from app.models.work_order import WorkOrder
from app.models.work_order_cost import WorkOrderCost
from app.models.work_order_part import WorkOrderPart
from app.models.work_order_downtime import WorkOrderDowntime


class ReportsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _work_order_filters(
        self,
        company_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        plant_id: Optional[UUID] = None,
        equipment_id: Optional[UUID] = None,
        technician_id: Optional[UUID] = None,
        maintenance_type: Optional[str] = None,
    ):
        conditions = [WorkOrder.company_id == company_id, WorkOrder.deleted_at.is_(None)]
        if date_from:
            conditions.append(WorkOrder.created_at >= date_from)
        if date_to:
            conditions.append(WorkOrder.created_at <= date_to)
        if plant_id:
            conditions.append(WorkOrder.equipment.has(Equipment.plant_id == plant_id))
        if equipment_id:
            conditions.append(WorkOrder.equipment_id == equipment_id)
        if technician_id:
            conditions.append(WorkOrder.assigned_technician_id == technician_id)
        if maintenance_type:
            conditions.append(WorkOrder.type == maintenance_type)
        return conditions

    async def get_mttr_minutes(
        self,
        company_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        plant_id: Optional[UUID] = None,
        equipment_id: Optional[UUID] = None,
        technician_id: Optional[UUID] = None,
        maintenance_type: Optional[str] = None,
    ) -> Tuple[float, int]:
        conditions = self._work_order_filters(
            company_id,
            date_from=date_from,
            date_to=date_to,
            plant_id=plant_id,
            equipment_id=equipment_id,
            technician_id=technician_id,
            maintenance_type=maintenance_type,
        )
        stmt = (
            select(
                func.coalesce(func.sum(WorkOrderDowntime.total_minutes), 0),
                func.count(func.distinct(WorkOrderDowntime.work_order_id)),
            )
            .join(WorkOrder, WorkOrderDowntime.work_order_id == WorkOrder.id)
            .filter(WorkOrderDowntime.deleted_at.is_(None), *conditions)
        )
        result = await self.session.execute(stmt)
        total_minutes, failure_count = result.one()
        return float(total_minutes or 0), int(failure_count or 0)

    async def get_mtbf_minutes(
        self,
        company_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        plant_id: Optional[UUID] = None,
        equipment_id: Optional[UUID] = None,
        technician_id: Optional[UUID] = None,
        maintenance_type: Optional[str] = None,
    ) -> Tuple[float, int]:
        conditions = self._work_order_filters(
            company_id,
            date_from=date_from,
            date_to=date_to,
            plant_id=plant_id,
            equipment_id=equipment_id,
            technician_id=technician_id,
            maintenance_type=maintenance_type,
        )
        duration_stmt = (
            select(
                func.coalesce(
                    func.sum(
                        func.extract("epoch", WorkOrder.end_date - WorkOrder.start_date) / 60
                    ),
                    0,
                )
            )
            .filter(
                *conditions,
                WorkOrder.status == "Completed",
                WorkOrder.start_date.is_not(None),
                WorkOrder.end_date.is_not(None),
            )
        )
        failure_count_stmt = (
            select(func.coalesce(func.count(), 0))
            .filter(*conditions, WorkOrder.type == "corrective")
        )
        duration_result = await self.session.execute(duration_stmt)
        failures_result = await self.session.execute(failure_count_stmt)
        total_operational_minutes = float(duration_result.scalar_one() or 0)
        failure_count = int(failures_result.scalar_one() or 0)
        return total_operational_minutes, failure_count

    async def get_maintenance_cost_totals(
        self,
        company_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> Tuple[float, float, float]:
        cost_stmt = (
            select(func.coalesce(func.sum(WorkOrderCost.amount), 0))
            .join(WorkOrder, WorkOrderCost.work_order_id == WorkOrder.id)
            .filter(WorkOrderCost.deleted_at.is_(None), WorkOrder.deleted_at.is_(None), WorkOrder.company_id == company_id)
        )
        part_stmt = (
            select(func.coalesce(func.sum(WorkOrderPart.total_cost), 0))
            .join(WorkOrder, WorkOrderPart.work_order_id == WorkOrder.id)
            .filter(WorkOrderPart.deleted_at.is_(None), WorkOrder.deleted_at.is_(None), WorkOrder.company_id == company_id)
        )
        if date_from:
            cost_stmt = cost_stmt.filter(WorkOrder.created_at >= date_from)
            part_stmt = part_stmt.filter(WorkOrder.created_at >= date_from)
        if date_to:
            cost_stmt = cost_stmt.filter(WorkOrder.created_at <= date_to)
            part_stmt = part_stmt.filter(WorkOrder.created_at <= date_to)

        cost_total = float((await self.session.execute(cost_stmt)).scalar_one() or 0)
        parts_total = float((await self.session.execute(part_stmt)).scalar_one() or 0)
        return parts_total, cost_total, parts_total + cost_total

    async def get_preventive_compliance(
        self,
        company_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> Tuple[int, int]:
        stmt = (
            select(func.count())
            .select_from(MaintenanceSchedule)
            .join(MaintenancePlan, MaintenanceSchedule.maintenance_plan)
            .filter(
                MaintenanceSchedule.deleted_at.is_(None),
                MaintenancePlan.company_id == company_id,
            )
        )
        if date_from:
            stmt = stmt.filter(MaintenanceSchedule.scheduled_date >= date_from)
        if date_to:
            stmt = stmt.filter(MaintenanceSchedule.scheduled_date <= date_to)
        total = int((await self.session.execute(stmt)).scalar_one() or 0)

        completed_stmt = (
            select(func.count())
            .select_from(MaintenanceSchedule)
            .join(MaintenancePlan, MaintenanceSchedule.maintenance_plan)
            .filter(
                MaintenanceSchedule.deleted_at.is_(None),
                MaintenancePlan.company_id == company_id,
                MaintenanceSchedule.status == "completed",
            )
        )
        if date_from:
            completed_stmt = completed_stmt.filter(MaintenanceSchedule.scheduled_date >= date_from)
        if date_to:
            completed_stmt = completed_stmt.filter(MaintenanceSchedule.scheduled_date <= date_to)
        completed = int((await self.session.execute(completed_stmt)).scalar_one() or 0)
        return completed, total

    async def get_backlog_counts(self, company_id: UUID) -> List[Tuple[Optional[str], int]]:
        stmt = (
            select(MaintenanceBacklog.status, func.count())
            .filter(MaintenanceBacklog.company_id == company_id, MaintenanceBacklog.deleted_at.is_(None))
            .group_by(MaintenanceBacklog.status)
        )
        result = await self.session.execute(stmt)
        return [(row[0], int(row[1] or 0)) for row in result.fetchall()]

    async def get_technician_productivity(
        self,
        company_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Tuple[Optional[UUID], Optional[str], int, float, float]]:
        stmt = (
            select(
                Technician.id,
                Technician.name,
                func.count(WorkOrder.id),
                func.coalesce(
                    func.avg(func.extract("epoch", WorkOrder.end_date - WorkOrder.start_date) / 60), 0
                ),
                func.coalesce(func.sum(WorkOrderCost.amount), 0),
            )
            .join(Technician, Technician.id == WorkOrder.assigned_technician_id)
            .join(WorkOrderCost, WorkOrderCost.work_order_id == WorkOrder.id, isouter=True)
            .filter(
                WorkOrder.company_id == company_id,
                WorkOrder.deleted_at.is_(None),
                Technician.deleted_at.is_(None),
                WorkOrder.status == "Completed",
            )
            .group_by(Technician.id, Technician.name)
        )
        if date_from:
            stmt = stmt.filter(WorkOrder.created_at >= date_from)
        if date_to:
            stmt = stmt.filter(WorkOrder.created_at <= date_to)

        result = await self.session.execute(stmt)
        return [
            (
                row[0],
                row[1],
                int(row[2] or 0),
                float(row[3] or 0),
                float(row[4] or 0),
            )
            for row in result.fetchall()
        ]

    async def get_inventory_consumption(
        self,
        company_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Tuple[UUID, Optional[str], int, float]]:
        stmt = (
            select(
                SparePart.id,
                SparePart.name,
                func.coalesce(func.sum(StockMovement.quantity), 0),
                func.coalesce(func.sum(StockMovement.total_cost), 0),
            )
            .join(SparePart, StockMovement.spare_part_id == SparePart.id)
            .filter(
                StockMovement.company_id == company_id,
                StockMovement.deleted_at.is_(None),
                StockMovement.movement_type.in_(["out", "usage", "consumed"]),
            )
            .group_by(SparePart.id, SparePart.name)
        )
        if date_from:
            stmt = stmt.filter(StockMovement.created_at >= date_from)
        if date_to:
            stmt = stmt.filter(StockMovement.created_at <= date_to)

        result = await self.session.execute(stmt)
        return [
            (
                row[0],
                row[1],
                int(row[2] or 0),
                float(row[3] or 0),
            )
            for row in result.fetchall()
        ]
