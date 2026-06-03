import uuid
from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.equipment import Equipment
    from app.models.maintenance_plan import MaintenancePlan


class MaintenanceBacklog(Base, TimestampMixin):
    __tablename__ = "maintenance_backlog"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="SET NULL"), nullable=True, index=True
    )
    maintenance_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("maintenance_plans.id", ondelete="SET NULL"), nullable=True, index=True
    )
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    days_overdue: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    company: Mapped["Company"] = relationship("Company", lazy="joined")
    equipment: Mapped[Optional["Equipment"]] = relationship("Equipment", lazy="joined")
    maintenance_plan: Mapped[Optional["MaintenancePlan"]] = relationship(
        "MaintenancePlan", back_populates="backlog_entries", lazy="joined"
    )
