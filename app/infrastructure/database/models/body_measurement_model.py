"""SQLAlchemy ORM model for the patient_body_measurements table."""

from __future__ import annotations

import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base


class BodyMeasurementModel(Base):
    """ORM model mapped to the ``patient_body_measurements`` table.

    Stores one measurement event per row, allowing full time-series
    history per patient.
    """

    __tablename__ = "patient_body_measurements"

    # --- Primary key ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # --- Foreign key ---
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )

    # --- When the measurement was taken ---
    measured_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # --- Measurements ---
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    hip_cm: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Audit ---
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Indexes ---
    __table_args__ = (
        Index("ix_body_measurements_patient_id", "patient_id"),
        Index("ix_body_measurements_measured_at", "measured_at"),
        Index("ix_body_measurements_patient_measured", "patient_id", "measured_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<BodyMeasurementModel(id={self.id}, patient_id={self.patient_id}, "
            f"measured_at={self.measured_at})>"
        )
