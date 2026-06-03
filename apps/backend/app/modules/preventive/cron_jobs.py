from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.preventive.repository import PreventiveRepository
from app.modules.preventive.service import PreventiveMaintenanceService
from app.modules.preventive.utils import calculate_days_overdue


async def run_preventive_maintenance_job(
    session: AsyncSession, reference_date: Optional[date] = None
) -> None:
    reference_date = reference_date or date.today()
    repo = PreventiveRepository(session)
    service = PreventiveMaintenanceService(session)

    schedules, _ = await repo.get_due_schedules(
        due_before=reference_date,
        limit=200,
        offset=0,
    )

    for schedule in schedules:
        if not schedule.maintenance_plan:
            continue

        days_overdue = calculate_days_overdue(schedule.scheduled_date, reference_date)
        await service.upsert_backlog_entry(
            company_id=schedule.maintenance_plan.company_id,
            maintenance_plan_id=schedule.maintenance_plan_id,
            equipment_id=schedule.maintenance_plan.equipment_id,
            scheduled_date=schedule.scheduled_date,
            days_overdue=days_overdue,
            priority=schedule.maintenance_plan.priority,
            status="overdue" if days_overdue > 0 else schedule.status,
        )
    await session.commit()
