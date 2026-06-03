import decimal
import uuid
from datetime import date
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.purchase_order_item import PurchaseOrderItem
    from app.models.supplier import Supplier
    from app.models.user import User


class PurchaseOrder(Base, TimestampMixin):
    __tablename__ = "purchase_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    purchase_number: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    subtotal: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    taxes: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    total: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_delivery: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    company: Mapped["Company"] = relationship("Company", lazy="joined")
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier", back_populates="purchase_orders", lazy="joined")
    created_by_user: Mapped[Optional["User"]] = relationship("User", lazy="joined")
    items: Mapped[List["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem", back_populates="purchase_order", lazy="selectin", cascade="all, delete-orphan"
    )
