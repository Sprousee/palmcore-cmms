import uuid
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.plant import Plant
    from app.models.area import Area
    from app.models.equipment_category import EquipmentCategory
    from app.models.equipment_history import EquipmentHistory
    from app.models.attachment import Attachment


class Equipment(Base, TimestampMixin):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plant_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("plants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    area_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("equipment_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    criticality: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    installation_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    qr_code: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    company: Mapped["Company"] = relationship("Company", lazy="joined")
    plant: Mapped[Optional["Plant"]] = relationship("Plant", lazy="joined")
    area: Mapped[Optional["Area"]] = relationship("Area", lazy="joined")
    category: Mapped[Optional["EquipmentCategory"]] = relationship("EquipmentCategory", lazy="joined")
    history: Mapped[List["EquipmentHistory"]] = relationship(
        "EquipmentHistory", back_populates="equipment", lazy="selectin", cascade="all, delete-orphan"
    )
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", back_populates="equipment", lazy="selectin", cascade="all, delete-orphan"
    )
