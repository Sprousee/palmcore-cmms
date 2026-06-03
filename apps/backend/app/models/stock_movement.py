import decimal
import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.spare_part import SparePart
    from app.models.work_order import WorkOrder
    from app.models.user import User


class StockMovement(Base, TimestampMixin):
    __tablename__ = "stock_movements"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    spare_part_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("spare_parts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    movement_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    quantity_before: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    unit_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    performed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    spare_part: Mapped["SparePart"] = relationship("SparePart", back_populates="stock_movements", lazy="joined")
    work_order: Mapped[Optional["WorkOrder"]] = relationship("WorkOrder", lazy="joined")
    performed_by_user: Mapped[Optional["User"]] = relationship("User", lazy="joined")
