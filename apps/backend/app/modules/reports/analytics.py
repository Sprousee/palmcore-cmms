from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipment import Equipment
from app.models.purchase_order import PurchaseOrder
from app.models.stock_movement import StockMovement
from app.models.technician import Technician
from app.models.work_order import WorkOrder
from app.models.work_order_downtime import WorkOrderDowntime
from app.models.work_order_part import WorkOrderPart


async def failure_trends(
    session: AsyncSession,
    company_id: UUID,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> List[Tuple[str, int]]:
    stmt = (
        select(func.date_trunc("month", WorkOrder.created_at).label("period"), func.count())
        .filter(
            WorkOrder.company_id == company_id,
            WorkOrder.deleted_at.is_(None),
            WorkOrder.type == "corrective",
        )
        .group_by("period")
        .order_by("period")
    )
    if date_from:
        stmt = stmt.filter(WorkOrder.created_at >= date_from)
    if date_to:
        stmt = stmt.filter(WorkOrder.created_at <= date_to)
    result = await session.execute(stmt)
    return [(row[0].strftime("%Y-%m") if row[0] else "", int(row[1] or 0)) for row in result.fetchall()]


async def critical_equipment(
    session: AsyncSession,
    company_id: UUID,
    limit: int = 10,
) -> List[Tuple[Optional[UUID], Optional[str], int, int]]:
    stmt = (
        select(
            Equipment.id,
            Equipment.name,
            func.coalesce(func.sum(WorkOrderDowntime.total_minutes), 0),
            func.count(WorkOrder.id),
        )
        .join(WorkOrder, WorkOrder.equipment_id == Equipment.id)
        .join(WorkOrderDowntime, WorkOrderDowntime.work_order_id == WorkOrder.id)
        .filter(Equipment.company_id == company_id, Equipment.deleted_at.is_(None), WorkOrder.deleted_at.is_(None))
        .group_by(Equipment.id, Equipment.name)
        .order_by(func.sum(WorkOrderDowntime.total_minutes).desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [
        (row[0], row[1], int(row[2] or 0), int(row[3] or 0)) for row in result.fetchall()
    ]


async def technician_productivity_trend(
    session: AsyncSession,
    company_id: UUID,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> List[Tuple[str, int]]:
    stmt = (
        select(func.date_trunc("month", WorkOrder.created_at).label("period"), func.count(WorkOrder.id))
        .join(Technician, Technician.id == WorkOrder.assigned_technician_id)
        .filter(WorkOrder.company_id == company_id, WorkOrder.deleted_at.is_(None))
        .group_by("period")
        .order_by("period")
    )
    if date_from:
        stmt = stmt.filter(WorkOrder.created_at >= date_from)
    if date_to:
        stmt = stmt.filter(WorkOrder.created_at <= date_to)
    result = await session.execute(stmt)
    return [(row[0].strftime("%Y-%m") if row[0] else "", int(row[1] or 0)) for row in result.fetchall()]


async def inventory_consumption_history(
    session: AsyncSession,
    company_id: UUID,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> List[Tuple[str, int]]:
    stmt = (
        select(func.date_trunc("month", StockMovement.created_at).label("period"), func.coalesce(func.sum(StockMovement.quantity), 0))
        .filter(
            StockMovement.company_id == company_id,
            StockMovement.deleted_at.is_(None),
            StockMovement.movement_type.in_(["out", "usage", "consumed"]),
        )
        .group_by("period")
        .order_by("period")
    )
    if date_from:
        stmt = stmt.filter(StockMovement.created_at >= date_from)
    if date_to:
        stmt = stmt.filter(StockMovement.created_at <= date_to)
    result = await session.execute(stmt)
    return [(row[0].strftime("%Y-%m") if row[0] else "", int(row[1] or 0)) for row in result.fetchall()]


async def refresh_report_cache(session: AsyncSession) -> None:
    # Placeholder for future cache refresh or materialized view updates.
    await session.commit()
