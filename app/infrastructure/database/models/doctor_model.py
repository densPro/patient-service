"""SQLAlchemy ORM model for the doctors table."""

from __future__ import annotations

import uuid

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base


class DoctorModel(Base):
    """ORM model mapped to the ``doctors`` table.

    JSON columns are used for composite value objects (license_info,
    contact_info, address) to keep the schema simple while still storing
    structured data — identical strategy to PatientModel.
    """

    __tablename__ = "doctors"

    # --- Primary key ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # --- Identity ---
    employee_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[str | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown")

    # --- Specialty FK ---
    specialty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("specialties.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # --- Professional (JSON) ---
    license_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    years_of_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Contact (JSON) ---
    contact_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    address: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # --- Administrative ---
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

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
        Index("ix_doctors_employee_id", "employee_id"),
        Index("ix_doctors_specialty_id", "specialty_id"),
        Index("ix_doctors_last_name", "last_name"),
        Index("ix_doctors_status", "status"),
        Index("ix_doctors_last_name_first_name", "last_name", "first_name"),
    )

    def __repr__(self) -> str:
        return (
            f"<DoctorModel(id={self.id}, employee_id={self.employee_id}, "
            f"name={self.first_name} {self.last_name})>"
        )
