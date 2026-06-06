"""DTOs for body measurement endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BodyMeasurementCreateDTO(BaseModel):
    """Input DTO for recording a new body measurement.

    At least one measurement field must be provided.
    """

    height_cm: float | None = Field(None, ge=50.0, le=300.0, examples=[175.0])
    weight_kg: float | None = Field(None, ge=1.0, le=700.0, examples=[72.5])
    waist_cm: float | None = Field(None, ge=20.0, le=300.0, examples=[85.0])
    hip_cm: float | None = Field(None, ge=20.0, le=300.0, examples=[98.0])
    measured_at: datetime | None = Field(
        None,
        description="When the measurement was taken. Defaults to now if omitted.",
        examples=["2026-06-05T10:00:00Z"],
    )


class TDEEResponseDTO(BaseModel):
    """Total Daily Energy Expenditure breakdown for different activity levels."""
    sedentary: float | None = None
    lightly_active: float | None = None
    moderately_active: float | None = None
    very_active: float | None = None

class BodyMeasurementResponseDTO(BaseModel):
    """Output DTO for a single body measurement record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    measured_at: datetime
    height_cm: float | None = None
    height_m: float | None = None
    weight_kg: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None
    bmi: float | None = None
    bmi_category: str | None = None
    healthy_weight: float | None = None
    minimum_weight: float | None = None
    maximum_weight: float | None = None
    bmr_harris_benedict: float | None = None
    bmr_mifflin_st_jeor: float | None = None
    tdee_harris_benedict: TDEEResponseDTO | None = None
    tdee_mifflin_st_jeor: TDEEResponseDTO | None = None
    created_at: datetime




class PaginatedMeasurementsResponseDTO(BaseModel):
    """Paginated list of body measurements."""

    items: list[BodyMeasurementResponseDTO]
    total: int
    limit: int
    offset: int
