import uuid
from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.equipment import Equipment


class EquipmentCategory(Base, TimestampMixin):
    __tablename__ = "equipment_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(512), nullable=True)
    color: Mapped[str] = mapped_column(String(64), nullable=True)
    icon: Mapped[str] = mapped_column(String(128), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="categories", lazy="joined")
    equipment: Mapped[List["Equipment"]] = relationship("Equipment", back_populates="category", lazy="selectin")
