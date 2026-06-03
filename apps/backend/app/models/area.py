import uuid
from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.plant import Plant
    from app.models.equipment import Equipment


class Area(Base, TimestampMixin):
    __tablename__ = "areas"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plant_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(512), nullable=True)

    plant: Mapped["Plant"] = relationship("Plant", back_populates="areas", lazy="joined")
    equipment: Mapped[List["Equipment"]] = relationship("Equipment", back_populates="area", lazy="selectin")
