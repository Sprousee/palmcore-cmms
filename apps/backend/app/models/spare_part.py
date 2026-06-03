import uuid
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.purchase_order_item import PurchaseOrderItem
    from app.models.stock_movement import StockMovement
    from app.models.inventory_alert import InventoryAlert


class SparePart(Base, TimestampMixin):
    __tablename__ = "spare_parts"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    part_number: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    unit_measure: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    minimum_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    maximum_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    unit_cost: Mapped[Optional[Numeric]] = mapped_column(Numeric(12, 2), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    qr_code: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    company: Mapped["Company"] = relationship("Company", lazy="joined")
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement", back_populates="spare_part", lazy="selectin", cascade="all, delete-orphan"
    )
    purchase_items: Mapped[List["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem", back_populates="spare_part", lazy="selectin"
    )
    alerts: Mapped[List["InventoryAlert"]] = relationship(
        "InventoryAlert", back_populates="spare_part", lazy="selectin", cascade="all, delete-orphan"
    )
