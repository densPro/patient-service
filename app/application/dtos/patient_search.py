"""DTO for patient search query parameters."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums.patient_status import PatientStatus


class PatientSearchDTO(BaseModel):
    """Query-parameter DTO for searching / filtering patients."""

    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    date_of_birth: str | None = Field(None, examples=["1990-05-15"])
    mrn: str | None = Field(None, max_length=50)
    status: PatientStatus | None = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
