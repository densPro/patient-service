"""SQLAlchemy ORM model for the patients table."""

from __future__ import annotations

import uuid

from sqlalchemy import Date, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base


class PatientModel(Base):
    """ORM model mapped to the ``patients`` table.

    JSON columns are used for composite value objects (address,
    contact_info, emergency_contact, insurance_info) to keep the
    schema simple while still storing structured data.
    """

    __tablename__ = "patients"

    # --- Primary key ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # --- Demographics ---
    mrn: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[str] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown")
    marital_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="unknown"
    )

    # --- Identifiers ---
    ssn_last_four: Mapped[str | None] = mapped_column(String(4), nullable=True)
    national_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # --- Medical ---
    blood_type: Mapped[str] = mapped_column(
        String(10), nullable=False, default="unknown"
    )
    allergies: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True, default=list
    )
    chronic_conditions: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True, default=list
    )

    # --- Contact (JSON) ---
    contact_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    address: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    emergency_contact: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    insurance_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # --- Administrative ---
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )

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
        Index("ix_patients_mrn", "mrn"),
        Index("ix_patients_last_name", "last_name"),
        Index("ix_patients_date_of_birth", "date_of_birth"),
        Index("ix_patients_status", "status"),
        Index("ix_patients_last_name_first_name", "last_name", "first_name"),
    )

    def __repr__(self) -> str:
        return (
            f"<PatientModel(id={self.id}, mrn={self.mrn}, "
            f"name={self.first_name} {self.last_name})>"
        )
