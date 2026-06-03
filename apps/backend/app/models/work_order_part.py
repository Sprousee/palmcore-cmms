import decimal
import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.work_order import WorkOrder


class WorkOrderPart(Base, TimestampMixin):
    __tablename__ = "work_order_parts"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    work_order_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    spare_part_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    unit_cost: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default="0")
    total_cost: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")

    work_order: Mapped["WorkOrder"] = relationship("WorkOrder", back_populates="parts", lazy="joined")
