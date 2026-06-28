"""SQLAlchemy ORM model for the specialties table."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base


class SpecialtyModel(Base):
    """ORM model mapped to the ``specialties`` table.

    This is the catalogue of medical specialties.  Doctors reference
    this table via a foreign key on ``specialty_id``.
    """

    __tablename__ = "specialties"

    # --- Primary key ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # --- Identity ---
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="other")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # --- Timestamps ---
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Indexes ---
    __table_args__ = (
        Index("ix_specialties_code", "code"),
        Index("ix_specialties_category", "category"),
        Index("ix_specialties_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<SpecialtyModel(id={self.id}, code={self.code}, name={self.name})>"
