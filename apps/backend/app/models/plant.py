import uuid
from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.area import Area
    from app.models.company import Company


class Plant(Base, TimestampMixin):
    __tablename__ = "plants"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(128), nullable=True)
    department: Mapped[str] = mapped_column(String(128), nullable=True)
    address: Mapped[str] = mapped_column(String(512), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="plants", lazy="joined")
    areas: Mapped[List["Area"]] = relationship("Area", back_populates="plant", lazy="selectin")
