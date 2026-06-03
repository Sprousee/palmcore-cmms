import uuid
from typing import List

from sqlalchemy import Boolean, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)

    users: Mapped[List["User"]] = relationship(
        "User", back_populates="company", lazy="selectin"
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role", back_populates="company", lazy="selectin"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", back_populates="company", lazy="selectin"
    )
    plants: Mapped[List["Plant"]] = relationship(
        "Plant", back_populates="company", lazy="selectin"
    )
    categories: Mapped[List["EquipmentCategory"]] = relationship(
        "EquipmentCategory", back_populates="company", lazy="selectin"
    )
