"""DTOs for the Doctor bounded context."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.domain.enums.doctor_status import DoctorStatus
from app.domain.enums.gender import Gender


# ---------------------------------------------------------------------------
# Nested DTOs
# ---------------------------------------------------------------------------


class LicenseInfoDTO(BaseModel):
    """Physician medical license details."""

    license_number: str = Field(..., min_length=1, max_length=100)
    issuing_body: str = Field(..., min_length=1, max_length=200)
    issue_date: date | None = None
    expiration_date: date | None = None
    state: str | None = Field(None, max_length=10)


# ---------------------------------------------------------------------------
# Create DTO
# ---------------------------------------------------------------------------


class DoctorCreateDTO(BaseModel):
    """Input schema for registering a new doctor."""

    first_name: str = Field(..., min_length=1, max_length=100, examples=["Carlos"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Rivera"])
    date_of_birth: date | None = Field(None, examples=["1980-03-20"])
    gender: Gender = Field(Gender.UNKNOWN, examples=[Gender.MALE])
    specialty_id: uuid.UUID = Field(
        ..., description="UUID of the doctor's primary specialty."
    )
    license_info: LicenseInfoDTO | None = None
    contact_info: DoctorContactInfoDTO | None = None
    address: DoctorAddressDTO | None = None
    years_of_experience: int | None = Field(None, ge=0, le=80)
    bio: str | None = Field(None, max_length=2000)


class DoctorContactInfoDTO(BaseModel):
    """Contact information for a doctor."""

    phone_number: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=255)


class DoctorAddressDTO(BaseModel):
    """Work or home address for a doctor."""

    street_line_1: str | None = Field(None, max_length=200)
    street_line_2: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=60)


# Rebuild DoctorCreateDTO after forward-referenced nested models are defined
DoctorCreateDTO.model_rebuild()


# ---------------------------------------------------------------------------
# Update DTO
# ---------------------------------------------------------------------------


class DoctorUpdateDTO(BaseModel):
    """Input schema for partially updating a doctor record."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    gender: Gender | None = None
    specialty_id: uuid.UUID | None = None
    license_info: LicenseInfoDTO | None = None
    contact_info: DoctorContactInfoDTO | None = None
    address: DoctorAddressDTO | None = None
    years_of_experience: int | None = Field(None, ge=0, le=80)
    bio: str | None = Field(None, max_length=2000)
    status: DoctorStatus | None = None


# ---------------------------------------------------------------------------
# Search DTO
# ---------------------------------------------------------------------------


class DoctorSearchDTO(BaseModel):
    """Parameters for filtering the doctor list."""

    first_name: str | None = None
    last_name: str | None = None
    specialty_id: uuid.UUID | None = None
    status: DoctorStatus | None = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


# ---------------------------------------------------------------------------
# Response DTOs
# ---------------------------------------------------------------------------


class DoctorResponseDTO(BaseModel):
    """Output schema returned to API consumers for a single doctor."""

    id: uuid.UUID
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: date | None
    age: int | None
    gender: Gender
    specialty_id: uuid.UUID
    license_info: LicenseInfoDTO | None
    contact_info: DoctorContactInfoDTO | None
    address: DoctorAddressDTO | None
    years_of_experience: int | None
    bio: str | None
    status: DoctorStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedDoctorsResponseDTO(BaseModel):
    """Paginated list of doctors."""

    items: list[DoctorResponseDTO]
    total: int
    limit: int
    offset: int
