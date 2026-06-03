import uuid
from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.equipment import Equipment
    from app.models.technician import Technician
    from app.models.user import User
    from app.models.work_order_attachment import WorkOrderAttachment
    from app.models.work_order_cost import WorkOrderCost
    from app.models.work_order_downtime import WorkOrderDowntime
    from app.models.work_order_part import WorkOrderPart
    from app.models.work_order_task import WorkOrderTask


class WorkOrder(Base, TimestampMixin):
    __tablename__ = "work_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_technician_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("technicians.id", ondelete="SET NULL"), nullable=True, index=True
    )
    work_order_number: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    priority: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, index=True
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, index=True
    )
    downtime_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    company: Mapped["Company"] = relationship("Company", lazy="joined")
    equipment: Mapped[Optional["Equipment"]] = relationship("Equipment", lazy="joined")
    assigned_technician: Mapped[Optional["Technician"]] = relationship("Technician", lazy="joined")
    created_by_user: Mapped[Optional["User"]]
    approved_by_user: Mapped[Optional["User"]]
    created_by_user = relationship(
        "User", foreign_keys=[created_by], lazy="joined"
    )
    approved_by_user = relationship(
        "User", foreign_keys=[approved_by], lazy="joined"
    )
    tasks: Mapped[List["WorkOrderTask"]] = relationship(
        "WorkOrderTask",
        back_populates="work_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    parts: Mapped[List["WorkOrderPart"]] = relationship(
        "WorkOrderPart",
        back_populates="work_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    attachments: Mapped[List["WorkOrderAttachment"]] = relationship(
        "WorkOrderAttachment",
        back_populates="work_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    downtimes: Mapped[List["WorkOrderDowntime"]] = relationship(
        "WorkOrderDowntime",
        back_populates="work_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    costs: Mapped[List["WorkOrderCost"]] = relationship(
        "WorkOrderCost",
        back_populates="work_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
