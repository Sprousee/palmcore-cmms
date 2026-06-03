import uuid
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.equipment import Equipment
    from app.models.user import User
    from app.models.maintenance_schedule import MaintenanceSchedule
    from app.models.maintenance_backlog import MaintenanceBacklog


class MaintenancePlan(Base, TimestampMixin):
    __tablename__ = "maintenance_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    maintenance_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    frequency_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    frequency_value: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    auto_generate_work_order: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    company: Mapped["Company"] = relationship("Company", lazy="joined")
    equipment: Mapped[Optional["Equipment"]] = relationship("Equipment", lazy="joined")
    created_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by], lazy="joined")
    schedules: Mapped[List["MaintenanceSchedule"]] = relationship(
        "MaintenanceSchedule",
        back_populates="maintenance_plan",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    backlog_entries: Mapped[List["MaintenanceBacklog"]] = relationship(
        "MaintenanceBacklog",
        back_populates="maintenance_plan",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
