from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reports.kpis import (
    calculate_availability,
    calculate_mtbf,
    calculate_mttr,
    calculate_preventive_compliance,
)
from app.modules.reports.repository import ReportsRepository
from app.modules.reports.schema import (
    BacklogStatusResponse,
    InventoryConsumptionResponse,
    KpiResponse,
    MaintenanceCostResponse,
    TechnicianProductivityResponse,
)
from app.models.user import User


class ReportsService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ReportsRepository(db)

    async def get_kpis(
        self,
        user: User,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        plant_id: Optional[UUID] = None,
        equipment_id: Optional[UUID] = None,
        technician_id: Optional[UUID] = None,
        maintenance_type: Optional[str] = None,
    ) -> KpiResponse:
        mttr_total, repair_count = await self.repo.get_mttr_minutes(
            user.company_id,
            date_from=date_from,
            date_to=date_to,
            plant_id=plant_id,
            equipment_id=equipment_id,
            technician_id=technician_id,
            maintenance_type=maintenance_type,
        )
        mtbf_total, failure_count = await self.repo.get_mtbf_minutes(
            user.company_id,
            date_from=date_from,
            date_to=date_to,
            plant_id=plant_id,
            equipment_id=equipment_id,
            technician_id=technician_id,
            maintenance_type=maintenance_type,
        )
        parts_cost, labor_cost, total_cost = await self.repo.get_maintenance_cost_totals(
            user.company_id,
            date_from=date_from,
            date_to=date_to,
        )
        completed_preventive, total_preventive = await self.repo.get_preventive_compliance(
            user.company_id,
            date_from=date_from,
            date_to=date_to,
        )
        backlog_items = await self.repo.get_backlog_counts(user.company_id)
        backlog_count = sum(count for _, count in backlog_items)
        mttr = calculate_mttr(mttr_total, repair_count)
        mtbf = calculate_mtbf(mtbf_total, failure_count)
        return KpiResponse(
            mttr_minutes=mttr,
            mtbf_minutes=mtbf,
            availability_percent=calculate_availability(mtbf, mttr),
            maintenance_costs=total_cost,
            preventive_compliance_percent=calculate_preventive_compliance(
                completed_preventive, total_preventive
            ),
            backlog_count=backlog_count,
            reactive_work_orders=failure_count,
            preventive_work_orders=total_preventive,
        )

    async def get_maintenance_costs(
        self,
        user: User,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> MaintenanceCostResponse:
        parts_cost, labor_cost, total_cost = await self.repo.get_maintenance_cost_totals(
            user.company_id,
            date_from=date_from,
            date_to=date_to,
        )
        return MaintenanceCostResponse(
            parts_cost=parts_cost,
            labor_cost=labor_cost,
            total_cost=total_cost,
        )

    async def get_backlog(self, user: User) -> List[BacklogStatusResponse]:
        backlog_items = await self.repo.get_backlog_counts(user.company_id)
        return [BacklogStatusResponse(status=status, count=count) for status, count in backlog_items]

    async def get_technician_productivity(
        self,
        user: User,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[TechnicianProductivityResponse]:
        productivity = await self.repo.get_technician_productivity(
            user.company_id,
            date_from=date_from,
            date_to=date_to,
        )
        return [
            TechnicianProductivityResponse(
                technician_id=technician_id,
                technician_name=technician_name,
                completed_work_orders=completed_work_orders,
                average_duration_minutes=average_duration_minutes,
                total_cost=total_cost,
            )
            for technician_id, technician_name, completed_work_orders, average_duration_minutes, total_cost in productivity
        ]

    async def get_inventory_consumption(
        self,
        user: User,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[InventoryConsumptionResponse]:
        consumption = await self.repo.get_inventory_consumption(
            user.company_id,
            date_from=date_from,
            date_to=date_to,
        )
        return [
            InventoryConsumptionResponse(
                spare_part_id=spare_part_id,
                spare_part_name=spare_part_name,
                total_quantity=total_quantity,
                total_cost=total_cost,
            )
            for spare_part_id, spare_part_name, total_quantity, total_cost in consumption
        ]

    async def get_report_export(self, user: User, report_type: str):
        if report_type not in {"kpis", "costs", "inventory"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported report export type.")
        return report_type
