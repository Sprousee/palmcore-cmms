import decimal
import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.purchase_order import PurchaseOrder
    from app.models.spare_part import SparePart


class PurchaseOrderItem(Base, TimestampMixin):
    __tablename__ = "purchase_order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    spare_part_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("spare_parts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    unit_cost: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default="0")
    total_cost: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="items", lazy="joined")
    spare_part: Mapped[Optional["SparePart"]] = relationship("SparePart", lazy="joined")
